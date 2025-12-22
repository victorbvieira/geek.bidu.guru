"""
Endpoints REST para integracao com Instagram.

Este modulo implementa as APIs internas que sao consumidas pelo
workflow n8n do Flow A (Post Diario Automatico).

AUTENTICACAO:
    Todos os endpoints requerem autenticacao JWT.
    Roles permitidos: ADMIN, AUTOMATION

Endpoints disponiveis:
    GET    /instagram/product/random              - Busca produto aleatorio para posting
    GET    /instagram/template/{id}               - Renderiza template HTML do produto
    POST   /instagram/generate-image              - Gera imagem PNG do produto (template + screenshot)
    PATCH  /instagram/products/{id}/mark-posted   - Marca produto como postado
    GET    /instagram/products/{id}/info          - Retorna info de publicacao do produto
    GET    /instagram/products/{id}/history       - Retorna historico de publicacoes
    GET    /instagram/stats                       - Estatisticas de posting
    POST   /instagram/utils/html-to-image         - Converte HTML em imagem (baixo nivel)
    POST   /instagram/utils/resize-image          - Redimensiona imagem

Uso tipico (Flow A do n8n - simplificado):
    1. GET /instagram/product/random - Seleciona produto
    2. POST /instagram/generate-image - Gera imagem PNG diretamente (combina template + screenshot)
    3. [n8n] Publica no Instagram via Graph API
    4. PATCH /instagram/products/{id}/mark-posted - Registra publicacao

Uso alternativo (mais controle):
    1. GET /instagram/product/random - Seleciona produto
    2. GET /instagram/template/{id} - Gera HTML renderizado do template
    3. POST /instagram/utils/html-to-image - Converte para imagem
    4. POST /instagram/utils/resize-image - Ajusta tamanho se necessario (opcional)
    5. [n8n] Publica no Instagram via Graph API
    6. PATCH /instagram/products/{id}/mark-posted - Registra publicacao
"""

import base64
import mimetypes
import re
from io import BytesIO
from pathlib import Path
from uuid import UUID

import httpx

from fastapi import APIRouter, Depends, File, HTTPException, Query, Request, UploadFile, status
from fastapi.responses import HTMLResponse
from PIL import Image

from app.api.deps import ProductRepo
from app.config import settings
from app.core.deps import require_role
from app.models.user import UserRole
from app.schemas.instagram import (
    GenerateImageRequest,
    GenerateImageResponse,
    HtmlToImageRequest,
    HtmlToImageResponse,
    InstagramPostHistoryListResponse,
    InstagramPostHistoryResponse,
    MarkPostedRequest,
    MarkPostedResponse,
    PostingStatsResponse,
    ProductForPostingResponse,
    ProductInstagramInfoResponse,
    ResizeImageRequest,
    ResizeImageResponse,
)

# Router com prefixo /instagram e tag para documentacao OpenAPI
router = APIRouter(prefix="/instagram", tags=["instagram"])

# Roles permitidos para acessar estes endpoints
ALLOWED_ROLES = [UserRole.ADMIN, UserRole.AUTOMATION]

# Diretorio de arquivos estaticos (para conversao de imagens/fontes para base64)
STATIC_DIR = Path(__file__).parent.parent.parent.parent / "static"


# =============================================================================
# Funcoes Auxiliares para Conversao de Imagens/Fontes para Base64
# =============================================================================


def _file_to_data_uri(file_path: Path) -> str:
    """
    Converte arquivo local para data URI base64.

    Usado para embutir imagens e fontes diretamente no HTML,
    permitindo que o Playwright renderize sem precisar de servidor web.

    Args:
        file_path: Caminho absoluto para o arquivo

    Returns:
        Data URI no formato: data:mime/type;base64,<conteudo>

    Raises:
        FileNotFoundError: Se o arquivo nao existir
    """
    if not file_path.exists():
        raise FileNotFoundError(f"Arquivo nao encontrado: {file_path}")

    # Determina o tipo MIME
    mime_type, _ = mimetypes.guess_type(str(file_path))
    if not mime_type:
        # Fallback para tipos comuns
        suffix = file_path.suffix.lower()
        mime_map = {
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".gif": "image/gif",
            ".webp": "image/webp",
            ".ttf": "font/ttf",
            ".woff": "font/woff",
            ".woff2": "font/woff2",
        }
        mime_type = mime_map.get(suffix, "application/octet-stream")

    # Le e converte para base64
    with open(file_path, "rb") as f:
        content = f.read()

    b64_content = base64.b64encode(content).decode("utf-8")
    return f"data:{mime_type};base64,{b64_content}"


async def _url_to_data_uri(url: str) -> str:
    """
    Baixa imagem de URL externa e converte para data URI base64.

    Usado para embutir imagem do produto diretamente no HTML,
    permitindo que o Playwright renderize sem fazer requests externos.

    Args:
        url: URL da imagem externa

    Returns:
        Data URI no formato: data:mime/type;base64,<conteudo>

    Raises:
        HTTPException: Se falhar ao baixar a imagem
    """
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, follow_redirects=True)
            response.raise_for_status()

            # Determina tipo MIME do response ou da URL
            content_type = response.headers.get("content-type", "").split(";")[0]
            if not content_type or content_type == "application/octet-stream":
                # Tenta determinar pela extensao da URL
                mime_type, _ = mimetypes.guess_type(url)
                content_type = mime_type or "image/png"

            b64_content = base64.b64encode(response.content).decode("utf-8")
            return f"data:{content_type};base64,{b64_content}"

    except httpx.HTTPError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Erro ao baixar imagem do produto: {str(e)}",
        )


def _prepare_template_with_embedded_assets(
    html_content: str,
    product_image_data_uri: str,
) -> str:
    """
    Prepara HTML do template com todos os assets embutidos como data URIs.

    Substitui referencias a arquivos estaticos locais (/static/...) e
    a imagem do produto por data URIs base64, permitindo renderizacao
    offline com Playwright.

    Args:
        html_content: HTML do template com referencias a arquivos
        product_image_data_uri: Data URI da imagem do produto

    Returns:
        HTML com todos os assets embutidos como base64
    """
    # Mapeamento de arquivos estaticos locais para seus caminhos
    static_files = {
        "/static/images/template/instagram_01.png": STATIC_DIR / "images" / "template" / "instagram_01.png",
        "/static/logo/mascot-only.png": STATIC_DIR / "logo" / "mascot-only.png",
        "/static/fonts/Bungee-Regular.ttf": STATIC_DIR / "fonts" / "Bungee-Regular.ttf",
        "/static/fonts/PressStart2P-Regular.ttf": STATIC_DIR / "fonts" / "PressStart2P-Regular.ttf",
    }

    # Substitui cada arquivo estatico por seu data URI
    for url_path, file_path in static_files.items():
        if url_path in html_content:
            try:
                data_uri = _file_to_data_uri(file_path)
                html_content = html_content.replace(url_path, data_uri)
            except FileNotFoundError:
                # Se arquivo nao existir, mantem URL original (fallback)
                pass

    # Substitui a imagem do produto
    # O template usa {{ product_image_url }} que ja foi renderizado com a URL real
    # Precisamos encontrar essa URL e substituir pelo data URI
    # Como a URL pode variar, usamos a tag <img> com class="product-image"

    # Pattern para encontrar o src da imagem do produto
    # Exemplo: <img src="https://..." alt="..." class="product-image">
    pattern = r'(<img\s+[^>]*class="product-image"[^>]*src=")([^"]+)(")'

    def replace_product_image(match):
        return match.group(1) + product_image_data_uri + match.group(3)

    html_content = re.sub(pattern, replace_product_image, html_content)

    # Tenta pattern alternativo caso src venha antes de class
    pattern_alt = r'(<img\s+src=")([^"]+)("[^>]*class="product-image")'

    html_content = re.sub(pattern_alt, replace_product_image, html_content)

    return html_content


# =============================================================================
# Endpoints de Selecao de Produto
# =============================================================================


@router.get(
    "/product/random",
    response_model=ProductForPostingResponse,
    dependencies=[Depends(require_role(*ALLOWED_ROLES))],
)
async def get_random_product_for_posting(
    repo: ProductRepo,
    days_since_last_post: int = Query(
        default=30,
        ge=1,
        le=365,
        description="Dias minimos desde o ultimo post do produto",
    ),
):
    """
    Busca produto aleatorio elegivel para posting no Instagram.

    **Autenticacao**: Requer token JWT com role ADMIN ou AUTOMATION.

    Criterios de selecao:
    - Status: available (disponivel para venda)
    - Imagem: Possui main_image_url (obrigatorio para post visual)
    - Recencia: Nao foi postado nos ultimos X dias (ou nunca postado)
    - Prioridade: Produtos menos postados tem preferencia

    O algoritmo prioriza produtos que:
    1. Nunca foram postados (post_count = 0)
    2. Tem menor post_count
    3. Aleatorio entre os de mesmo post_count

    Args:
        repo: Repositorio de produtos (injetado automaticamente)
        days_since_last_post: Dias minimos desde o ultimo post (default: 30)

    Returns:
        ProductForPostingResponse com dados do produto selecionado,
        incluindo metadados Instagram pre-configurados se disponiveis.

    Raises:
        HTTPException 401: Token invalido ou ausente
        HTTPException 403: Role nao autorizado
        HTTPException 404: Se nao houver produtos elegiveis
    """
    product = await repo.get_random_for_posting(
        days_since_last_post=days_since_last_post,
    )

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nenhum produto disponivel para posting. "
                   "Verifique se existem produtos com imagem e "
                   "que nao foram postados recentemente.",
        )

    return ProductForPostingResponse.model_validate(product)


# =============================================================================
# Endpoints de Template HTML
# =============================================================================


@router.get(
    "/template/{product_id}",
    response_class=HTMLResponse,
    dependencies=[Depends(require_role(*ALLOWED_ROLES))],
)
async def render_instagram_template(
    request: Request,
    product_id: UUID,
    repo: ProductRepo,
    headline: str | None = Query(None, description="Override da headline"),
    title: str | None = Query(None, description="Override do titulo"),
    badge: str | None = Query(None, description="Override do badge"),
):
    """
    Renderiza template HTML do produto para Instagram.

    **Autenticacao**: Requer token JWT com role ADMIN ou AUTOMATION.

    Gera o HTML completo do template de post Instagram com os dados
    do produto. Este HTML pode ser passado para /utils/html-to-image
    para converter em imagem.

    Args:
        request: Request do FastAPI (para templates)
        product_id: UUID do produto
        repo: Repositorio de produtos (injetado automaticamente)
        headline: Override da headline (usa instagram_headline do produto se None)
        title: Override do titulo (usa instagram_title ou name se None)
        badge: Override do badge (usa instagram_badge do produto se None)

    Returns:
        HTML renderizado do template Instagram (1080x1080)

    Raises:
        HTTPException 401: Token invalido ou ausente
        HTTPException 403: Role nao autorizado
        HTTPException 404: Se o produto nao for encontrado
    """
    from fastapi.templating import Jinja2Templates
    from pathlib import Path

    product = await repo.get(product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produto nao encontrado",
        )

    # Configura Jinja2
    templates_dir = Path(__file__).parent.parent.parent.parent / "templates"
    templates = Jinja2Templates(directory=str(templates_dir))

    # Prepara dados do preco (com formatacao de milhar usando ponto)
    price_integer = None
    price_cents = None
    if product.price:
        price_float = float(product.price)
        price_int = int(price_float)
        # Formata com separador de milhar (ponto) - ex: 1.234
        price_integer = f"{price_int:,}".replace(",", ".")
        price_cents = f"{int((price_float - price_int) * 100):02d}"

    # Usa metadados Instagram do produto ou overrides
    template_data = {
        "request": request,
        "product_name": product.name,
        "product_image_url": product.main_image_url,
        "price": product.price,
        "price_integer": price_integer,
        "price_cents": price_cents,
        "headline": headline or product.instagram_headline or "OFERTA IMPERDÍVEL!",
        "title": title or product.instagram_title or product.name,
        "badge": badge or product.instagram_badge,
        "hashtags": product.instagram_hashtags or [],
        "redirect_slug": product.affiliate_redirect_slug,
        "logo_url": f"{settings.app_url}/static/logo/mascot-only.png",
    }

    return templates.TemplateResponse(
        "instagram/post_produto.html",
        template_data,
    )


# =============================================================================
# Endpoints de Controle de Posts
# =============================================================================


@router.patch(
    "/products/{product_id}/mark-posted",
    response_model=MarkPostedResponse,
    dependencies=[Depends(require_role(*ALLOWED_ROLES))],
)
async def mark_product_as_posted(
    product_id: UUID,
    request: MarkPostedRequest,
    repo: ProductRepo,
):
    """
    Marca produto como postado em uma rede social.

    **Autenticacao**: Requer token JWT com role ADMIN ou AUTOMATION.

    Deve ser chamado apos a publicacao bem-sucedida do post
    no Instagram (ou outra plataforma).

    Atualiza os seguintes campos do produto:
    - last_post_date: Data/hora atual (UTC)
    - post_count: Incrementa em 1
    - last_post_platform: Nome da plataforma (ex: "instagram")
    - last_post_url: URL do post publicado (opcional)
    - last_ig_media_id: IG Media ID (apenas para Instagram)

    Para Instagram, também cria um registro no histórico de publicações
    na tabela instagram_post_history.

    Args:
        product_id: UUID do produto postado
        request: Dados do post (MarkPostedRequest)
        repo: Repositorio de produtos (injetado automaticamente)

    Returns:
        MarkPostedResponse confirmando a atualizacao

    Raises:
        HTTPException 401: Token invalido ou ausente
        HTTPException 403: Role nao autorizado
        HTTPException 404: Se o produto nao for encontrado

    Body (JSON):
        {
            "platform": "instagram",
            "post_url": "https://instagram.com/p/xxx",
            "ig_media_id": "17841400000000000",
            "caption": "Caption do post..."
        }
    """
    try:
        product, history_record = await repo.mark_as_posted(
            product_id=product_id,
            platform=request.platform,
            post_url=request.post_url,
            ig_media_id=request.ig_media_id,
            caption=request.caption,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )

    return MarkPostedResponse(
        success=True,
        product_id=product.id,
        last_post_date=product.last_post_date,
        post_count=product.post_count,
        ig_media_id=request.ig_media_id,
        history_id=history_record.id if history_record else None,
    )


# =============================================================================
# Endpoints de Estatisticas
# =============================================================================


@router.get(
    "/stats",
    response_model=PostingStatsResponse,
    dependencies=[Depends(require_role(*ALLOWED_ROLES))],
)
async def get_posting_stats(
    repo: ProductRepo,
    days_since_last_post: int = Query(
        default=30,
        ge=1,
        le=365,
        description="Dias considerados para elegibilidade",
    ),
):
    """
    Retorna estatisticas de posting de produtos.

    **Autenticacao**: Requer token JWT com role ADMIN ou AUTOMATION.

    Util para monitoramento do workflow n8n e dashboards.

    Args:
        repo: Repositorio de produtos (injetado automaticamente)
        days_since_last_post: Dias para considerar elegibilidade

    Returns:
        PostingStatsResponse com metricas

    Raises:
        HTTPException 401: Token invalido ou ausente
        HTTPException 403: Role nao autorizado
    """
    available_count = await repo.count_available_for_posting(
        days_since_last_post=days_since_last_post,
    )
    total_count = await repo.count()

    return PostingStatsResponse(
        available_for_posting=available_count,
        total_products=total_count,
        days_since_last_post=days_since_last_post,
    )


# =============================================================================
# Endpoints de Histórico de Publicações
# =============================================================================


@router.get(
    "/products/{product_id}/info",
    response_model=ProductInstagramInfoResponse,
    dependencies=[Depends(require_role(*ALLOWED_ROLES))],
)
async def get_product_instagram_info(
    product_id: UUID,
    repo: ProductRepo,
):
    """
    Retorna informações de Instagram de um produto.

    **Autenticacao**: Requer token JWT com role ADMIN ou AUTOMATION.

    Inclui:
    - last_ig_media_id: IG Media ID da última publicação
    - last_post_date: Data/hora da última publicação
    - post_count: Total de publicações
    - last_post_url: URL da última publicação
    - history: Últimas 5 publicações do histórico

    Args:
        product_id: UUID do produto
        repo: Repositório de produtos (injetado automaticamente)

    Returns:
        ProductInstagramInfoResponse com informações do produto

    Raises:
        HTTPException 401: Token invalido ou ausente
        HTTPException 403: Role nao autorizado
        HTTPException 404: Se o produto nao for encontrado
    """
    product = await repo.get(product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produto nao encontrado",
        )

    # Busca histórico de publicações
    history = await repo.get_instagram_post_history(product_id, limit=5)

    return ProductInstagramInfoResponse(
        product_id=product.id,
        last_ig_media_id=product.last_ig_media_id,
        last_post_date=product.last_post_date,
        post_count=product.post_count,
        last_post_url=product.last_post_url,
        history=[InstagramPostHistoryResponse.model_validate(h) for h in history],
    )


@router.get(
    "/products/{product_id}/history",
    response_model=InstagramPostHistoryListResponse,
    dependencies=[Depends(require_role(*ALLOWED_ROLES))],
)
async def get_product_instagram_history(
    product_id: UUID,
    repo: ProductRepo,
    limit: int = Query(default=20, ge=1, le=100, description="Número máximo de registros"),
):
    """
    Retorna histórico completo de publicações Instagram de um produto.

    **Autenticacao**: Requer token JWT com role ADMIN ou AUTOMATION.

    Args:
        product_id: UUID do produto
        repo: Repositório de produtos (injetado automaticamente)
        limit: Número máximo de registros (default: 20, max: 100)

    Returns:
        InstagramPostHistoryListResponse com lista de publicações

    Raises:
        HTTPException 401: Token invalido ou ausente
        HTTPException 403: Role nao autorizado
        HTTPException 404: Se o produto nao for encontrado
    """
    product = await repo.get(product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produto nao encontrado",
        )

    history = await repo.get_instagram_post_history(product_id, limit=limit)

    return InstagramPostHistoryListResponse(
        items=[InstagramPostHistoryResponse.model_validate(h) for h in history],
        total=len(history),
    )


# =============================================================================
# Endpoints de Geracao de Imagem
# =============================================================================


@router.post(
    "/generate-image",
    response_model=GenerateImageResponse,
    dependencies=[Depends(require_role(*ALLOWED_ROLES))],
)
async def generate_instagram_image(
    request_obj: Request,
    data: GenerateImageRequest,
    repo: ProductRepo,
):
    """
    Gera imagem de post Instagram a partir de um produto.

    **Autenticacao**: Requer token JWT com role ADMIN ou AUTOMATION.

    Este endpoint combina a renderizacao do template HTML com a conversao
    para imagem em uma unica chamada. Ideal para uso no workflow n8n.

    Fluxo interno:
    1. Busca o produto pelo ID
    2. Renderiza o template HTML com os dados do produto
    3. Converte o HTML para imagem PNG usando Playwright
    4. Retorna a imagem em base64

    Se os campos de conteudo (headline, title, badge, hashtags) nao forem
    passados no request, usa os dados pre-cadastrados do produto.

    Args:
        request_obj: Request do FastAPI (para templates)
        data: Dados para geracao (GenerateImageRequest)
        repo: Repositorio de produtos (injetado automaticamente)

    Returns:
        GenerateImageResponse com imagem em base64

    Raises:
        HTTPException 401: Token invalido ou ausente
        HTTPException 403: Role nao autorizado
        HTTPException 404: Se o produto nao for encontrado
        HTTPException 500: Erro na renderizacao

    Body (JSON):
        {
            "product_id": "uuid",
            "headline": "DESPERTE SEU HEROI!",    // opcional
            "title": "Material Escolar Epico!",   // opcional
            "badge": "NOVO NA LOJA!",             // opcional
            "hashtags": ["Vingadores", "Marvel"]  // opcional
        }
    """
    # Busca o produto
    product = await repo.get(data.product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produto nao encontrado",
        )

    # Verifica se produto tem imagem
    if not product.main_image_url:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Produto nao possui imagem principal (main_image_url)",
        )

    # Baixa a imagem do produto e converte para data URI
    # Isso e necessario pois o Playwright nao carrega URLs externas com set_content()
    product_image_data_uri = await _url_to_data_uri(product.main_image_url)

    # Prepara dados do preco (com formatacao de milhar usando ponto)
    price_integer = None
    price_cents = None
    if product.price:
        price_float = float(product.price)
        price_int = int(price_float)
        price_integer = f"{price_int:,}".replace(",", ".")
        price_cents = f"{int((price_float - price_int) * 100):02d}"

    # Usa dados do request ou fallback para dados do produto
    headline = data.headline or product.instagram_headline or "OFERTA IMPERDÍVEL!"
    title = data.title or product.instagram_title or product.name
    badge = data.badge or product.instagram_badge
    hashtags = data.hashtags or product.instagram_hashtags or []

    # Configura Jinja2
    from fastapi.templating import Jinja2Templates

    templates_dir = Path(__file__).parent.parent.parent.parent / "templates"
    templates = Jinja2Templates(directory=str(templates_dir))

    # Prepara dados do template
    # Nota: product_image_url usa URL original aqui, sera substituida depois
    template_data = {
        "request": request_obj,
        "product_name": product.name,
        "product_image_url": product.main_image_url,  # Sera substituido por data URI
        "price": product.price,
        "price_integer": price_integer,
        "price_cents": price_cents,
        "headline": headline,
        "title": title,
        "badge": badge,
        "hashtags": hashtags,
        "redirect_slug": product.affiliate_redirect_slug,
        "logo_url": "/static/logo/mascot-only.png",  # URL relativa, sera convertida
    }

    # Renderiza o template HTML
    html_content = templates.get_template("instagram/post_produto.html").render(
        **template_data
    )

    # Substitui todos os assets por data URIs (imagens, fontes, produto)
    # Isso permite que o Playwright renderize sem precisar de servidor web
    html_content = _prepare_template_with_embedded_assets(
        html_content=html_content,
        product_image_data_uri=product_image_data_uri,
    )

    # Converte HTML para imagem usando Playwright
    try:
        from playwright.async_api import async_playwright
    except ImportError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Playwright nao instalado. Execute: pip install playwright && playwright install chromium",
        )

    try:
        async with async_playwright() as p:
            # Inicia browser em modo headless com flags para ambiente containerizado
            browser = await p.chromium.launch(
                headless=True,
                args=[
                    "--no-sandbox",  # Necessario para rodar como root em containers
                    "--disable-setuid-sandbox",
                    "--disable-dev-shm-usage",  # Evita problemas de memoria compartilhada
                    "--disable-gpu",  # Desabilita GPU (nao disponivel em containers)
                    "--single-process",  # Reduz uso de memoria
                    "--no-zygote",  # Evita fork de processos (mais estavel em containers)
                ],
            )
            page = await browser.new_page(
                viewport={"width": 1080, "height": 1080}
            )

            # Renderiza HTML com todos os assets embutidos como base64
            await page.set_content(html_content, wait_until="load")

            # Aguarda um pouco para garantir que fontes foram carregadas
            await page.wait_for_timeout(500)

            screenshot = await page.screenshot(
                type="png",
                full_page=False,
            )

            await browser.close()

        # Converte para base64
        image_base64 = base64.b64encode(screenshot).decode("utf-8")
        file_size_kb = len(screenshot) // 1024

        return GenerateImageResponse(
            success=True,
            image_base64=image_base64,
            image_url=None,  # Nao salvamos em storage por enquanto
            format="png",
            width=1080,
            height=1080,
            file_size_kb=file_size_kb,
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao gerar imagem: {str(e)}",
        )


# =============================================================================
# Endpoints Utilitarios (HTML -> Imagem, Resize)
# =============================================================================


@router.post(
    "/utils/html-to-image",
    response_model=HtmlToImageResponse,
    dependencies=[Depends(require_role(*ALLOWED_ROLES))],
)
async def convert_html_to_image(request: HtmlToImageRequest):
    """
    Converte HTML em imagem PNG.

    **Autenticacao**: Requer token JWT com role ADMIN ou AUTOMATION.

    Utiliza Playwright para renderizar HTML e capturar screenshot.
    Ideal para converter templates de posts em imagens.

    Args:
        request: HTML e configuracoes de renderizacao

    Returns:
        HtmlToImageResponse com imagem em base64

    Raises:
        HTTPException 401: Token invalido ou ausente
        HTTPException 403: Role nao autorizado
        HTTPException 500: Erro na renderizacao

    Body (JSON):
        {
            "html": "<html>...</html>",
            "width": 1080,
            "height": 1080,
            "format": "png"
        }
    """
    try:
        from playwright.async_api import async_playwright
    except ImportError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Playwright nao instalado. Execute: pip install playwright && playwright install chromium",
        )

    try:
        async with async_playwright() as p:
            # Inicia browser em modo headless com flags para ambiente containerizado
            browser = await p.chromium.launch(
                headless=True,
                args=[
                    "--no-sandbox",  # Necessario para rodar como root em containers
                    "--disable-setuid-sandbox",
                    "--disable-dev-shm-usage",  # Evita problemas de memoria compartilhada
                    "--disable-gpu",  # Desabilita GPU (nao disponivel em containers)
                    "--single-process",  # Reduz uso de memoria
                    "--no-zygote",  # Evita fork de processos (mais estavel em containers)
                ],
            )
            page = await browser.new_page(
                viewport={"width": request.width, "height": request.height}
            )

            # Define conteudo HTML
            await page.set_content(request.html, wait_until="networkidle")

            # Captura screenshot
            screenshot = await page.screenshot(
                type=request.format,
                full_page=False,
            )

            await browser.close()

        # Converte para base64
        image_base64 = base64.b64encode(screenshot).decode("utf-8")
        file_size_kb = len(screenshot) // 1024

        return HtmlToImageResponse(
            success=True,
            image_base64=image_base64,
            format=request.format,
            width=request.width,
            height=request.height,
            file_size_kb=file_size_kb,
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao renderizar HTML: {str(e)}",
        )


@router.post(
    "/utils/resize-image",
    response_model=ResizeImageResponse,
    dependencies=[Depends(require_role(*ALLOWED_ROLES))],
)
async def resize_image(
    file: UploadFile = File(..., description="Imagem para redimensionar"),
    width: int = Query(1080, ge=100, le=4096, description="Largura desejada"),
    height: int = Query(1080, ge=100, le=4096, description="Altura desejada"),
    quality: int = Query(85, ge=1, le=100, description="Qualidade JPEG (1-100)"),
    maintain_aspect: bool = Query(True, description="Manter proporcao original"),
):
    """
    Redimensiona imagem para dimensoes especificadas.

    **Autenticacao**: Requer token JWT com role ADMIN ou AUTOMATION.

    Aceita PNG, JPEG, WEBP. Retorna imagem otimizada em base64.

    Args:
        file: Arquivo de imagem (multipart/form-data)
        width: Largura desejada em pixels
        height: Altura desejada em pixels
        quality: Qualidade de compressao (para JPEG)
        maintain_aspect: Se deve manter proporcao original

    Returns:
        ResizeImageResponse com imagem redimensionada em base64

    Raises:
        HTTPException 400: Formato de imagem invalido
        HTTPException 401: Token invalido ou ausente
        HTTPException 403: Role nao autorizado
        HTTPException 500: Erro no processamento
    """
    # Valida tipo de arquivo
    allowed_types = ["image/png", "image/jpeg", "image/webp"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Formato invalido. Permitidos: {allowed_types}",
        )

    try:
        # Lê imagem
        contents = await file.read()
        img = Image.open(BytesIO(contents))

        # Converte para RGB se necessario
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")

        # Calcula novo tamanho
        if maintain_aspect:
            img.thumbnail((width, height), Image.Resampling.LANCZOS)
            new_width, new_height = img.size
        else:
            img = img.resize((width, height), Image.Resampling.LANCZOS)
            new_width, new_height = width, height

        # Salva em buffer
        buffer = BytesIO()
        img.save(buffer, format="JPEG", quality=quality, optimize=True)
        buffer.seek(0)

        # Converte para base64
        image_bytes = buffer.getvalue()
        image_base64 = base64.b64encode(image_bytes).decode("utf-8")
        file_size_kb = len(image_bytes) // 1024

        return ResizeImageResponse(
            success=True,
            image_base64=image_base64,
            format="jpeg",
            width=new_width,
            height=new_height,
            file_size_kb=file_size_kb,
            original_size_kb=len(contents) // 1024,
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao processar imagem: {str(e)}",
        )
