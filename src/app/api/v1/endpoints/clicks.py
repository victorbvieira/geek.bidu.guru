"""
Endpoints para tracking de cliques e redirect de afiliados.

Este módulo implementa o sistema de rastreamento de cliques em links
de afiliados, incluindo o endpoint de redirect (/goto/{slug}).

Endpoints:
    GET    /clicks/go/{slug}        - Redireciona para afiliado (público)
    GET    /clicks/product/{id}     - Lista cliques de um produto (admin)
    GET    /clicks/analytics        - Analytics de cliques (admin)
    GET    /clicks/product/{id}/count - Contagem de cliques (admin)

Sistema de Redirect:
    O sistema /goto/{slug} funciona assim:
    1. Usuário clica em link: /goto/funko-vader
    2. Sistema registra o clique (produto, post de origem, sessão, etc.)
    3. Incrementa contador de cliques no produto
    4. Redireciona para URL de afiliado (Amazon, ML, Shopee)

Dados capturados em cada clique:
    - product_id: Produto clicado
    - post_id: Post de origem (se houver)
    - session_id: ID da sessão do visitante (cookie)
    - user_agent: Navegador/dispositivo
    - referer: Página de origem
    - ip_address: IP do visitante (para geolocalização)

Analytics disponíveis:
    - Total de cliques
    - Cliques por dia/período
    - Top produtos mais clicados
    - Top posts que geram cliques
"""

from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, Request, status
from fastapi.responses import RedirectResponse

from app.api.deps import ClickRepo, ProductRepo
from app.schemas import ClickAnalytics, ClickResponse, ClicksByPeriod, ClicksByProduct

# Router com prefixo /clicks e tag para documentação OpenAPI
router = APIRouter(prefix="/clicks", tags=["clicks"])


# =============================================================================
# Endpoint de Redirect (Público)
# =============================================================================


@router.get("/go/{redirect_slug}")
async def redirect_to_affiliate(
    redirect_slug: str,
    request: Request,
    product_repo: ProductRepo,
    click_repo: ClickRepo,
    post_id: UUID | None = Query(None, description="Post de origem"),
):
    """
    Redireciona para URL de afiliado e registra o clique.

    Este é o endpoint principal do sistema de afiliados. Quando um usuário
    clica em um produto no site, ele passa por este endpoint que:
    1. Registra o clique com informações de tracking
    2. Incrementa o contador de cliques do produto
    3. Redireciona para a URL de afiliado (Amazon, ML, Shopee)

    Args:
        redirect_slug: Slug único do produto (ex: funko-vader-amazon)
        request: Request do FastAPI (para capturar headers)
        product_repo: Repositório de produtos
        click_repo: Repositório de cliques
        post_id: UUID do post de origem (opcional, passado via query)

    Returns:
        RedirectResponse 302 para URL de afiliado

    Raises:
        HTTPException 404: Se produto não for encontrado

    Query Parameters:
        post_id (UUID): Post de onde veio o clique (opcional)

    Exemplo de uso no frontend:
        <a href="/api/v1/clicks/go/funko-vader?post_id=123">Comprar</a>

    Tracking capturado:
        - Produto clicado (via redirect_slug)
        - Post de origem (via query param)
        - Sessão do usuário (via cookie session_id)
        - User agent (navegador/dispositivo)
        - Referer (página anterior)
        - IP do visitante (geolocalização)

    Notas:
        - Usa redirect 302 (temporário) para permitir mudanças de URL
        - O tracking é assíncrono para não impactar performance
    """
    # Busca produto pelo redirect_slug (ex: funko-vader-amazon)
    product = await product_repo.get_by_redirect_slug(redirect_slug)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produto nao encontrado",
        )

    # Monta dados do clique com informações de tracking
    click_data = {
        "product_id": product.id,
        "post_id": post_id,  # Post de origem (se passou pelo param)
        "session_id": request.cookies.get("session_id"),  # Sessão do visitante
        "user_agent": request.headers.get("user-agent"),  # Navegador/dispositivo
        "referer": request.headers.get("referer"),  # Página anterior
        "ip_address": request.client.host if request.client else None,  # IP
    }

    # Registra clique no banco (assíncrono)
    await click_repo.create(click_data)

    # Incrementa contador desnormalizado no produto (para queries rápidas)
    await product_repo.increment_click_count(product.id)

    # Redireciona para URL do afiliado
    # 302 (temporário) permite mudança de URL sem afetar SEO
    return RedirectResponse(
        url=product.affiliate_url_raw,
        status_code=status.HTTP_302_FOUND,
    )


# =============================================================================
# Endpoints Administrativos / Analytics
# =============================================================================


@router.get("/product/{product_id}", response_model=list[ClickResponse])
async def list_product_clicks(
    product_id: UUID,
    click_repo: ClickRepo,
    product_repo: ProductRepo,
    skip: int = 0,
    limit: int = 100,
):
    """
    Lista cliques de um produto específico (admin).

    Retorna histórico detalhado de cliques para análise.

    Args:
        product_id: UUID do produto
        click_repo: Repositório de cliques
        product_repo: Repositório de produtos
        skip: Offset para paginação
        limit: Limite de registros

    Returns:
        Lista de cliques com detalhes

    Raises:
        HTTPException 404: Se produto não for encontrado

    Query Parameters:
        skip (int): Offset (default: 0)
        limit (int): Limite (default: 100)

    Uso:
        - Análise de performance por produto
        - Debug de tracking
        - Auditoria de cliques
    """
    # Verifica se produto existe
    if not await product_repo.exists(product_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produto nao encontrado",
        )

    clicks = await click_repo.get_by_product(product_id, skip=skip, limit=limit)
    return [ClickResponse.model_validate(c) for c in clicks]


@router.get("/analytics", response_model=ClickAnalytics)
async def get_click_analytics(
    click_repo: ClickRepo,
    days: int = Query(30, ge=1, le=365),
):
    """
    Retorna analytics de cliques (admin).

    Fornece visão geral de performance do sistema de afiliados.

    Args:
        click_repo: Repositório de cliques
        days: Período de análise em dias (1-365)

    Returns:
        ClickAnalytics contendo:
        - total_clicks: Total de cliques no período
        - unique_sessions: Sessões únicas (TODO)
        - top_products: Produtos mais clicados
        - top_posts: Posts que mais geram cliques (TODO)
        - clicks_by_day: Série temporal de cliques

    Query Parameters:
        days (int): Período em dias (default: 30, max: 365)

    Uso:
        - Dashboard administrativo
        - Relatórios de performance
        - Identificação de produtos populares
        - Análise de tendências

    TODO:
        - Adicionar autenticação (apenas admin)
        - Implementar unique_sessions
        - Implementar top_posts com join
        - Adicionar breakdown por plataforma
    """
    # Total de cliques
    total = await click_repo.count()

    # Série temporal de cliques por dia
    clicks_by_day = await click_repo.get_clicks_by_day(days=days)

    # Top produtos mais clicados
    top_products_raw = await click_repo.get_top_products(days=days, limit=10)

    # Formata resposta dos top produtos
    # TODO: Fazer join com products para obter nome e slug
    top_products = [
        ClicksByProduct(
            product_id=UUID(p["product_id"]),
            product_name="",  # Requer join com products
            product_slug="",  # Requer join com products
            clicks=p["clicks"],
        )
        for p in top_products_raw
    ]

    return ClickAnalytics(
        total_clicks=total,
        unique_sessions=0,  # TODO: Implementar contagem de sessões únicas
        top_products=top_products,
        top_posts=[],  # TODO: Implementar com join em posts
        clicks_by_day=[ClicksByPeriod(**c) for c in clicks_by_day],
    )


@router.get("/product/{product_id}/count")
async def get_product_click_count(
    product_id: UUID,
    click_repo: ClickRepo,
    product_repo: ProductRepo,
    days: int = Query(30, ge=1, le=365),
):
    """
    Retorna contagem de cliques de um produto específico.

    Endpoint simples para obter métricas de um produto.

    Args:
        product_id: UUID do produto
        click_repo: Repositório de cliques
        product_repo: Repositório de produtos
        days: Período para contagem parcial

    Returns:
        Dicionário com contagens:
        - product_id: ID do produto
        - total_clicks: Total histórico
        - clicks_last_N_days: Cliques no período

    Raises:
        HTTPException 404: Se produto não for encontrado

    Query Parameters:
        days (int): Período em dias (default: 30)

    Exemplo de resposta:
        {
            "product_id": "123...",
            "total_clicks": 1500,
            "clicks_last_30_days": 250
        }
    """
    # Verifica se produto existe
    if not await product_repo.exists(product_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produto nao encontrado",
        )

    # Total histórico
    total = await click_repo.count_by_product(product_id)

    # Cliques no período
    period = await click_repo.count_by_product_period(product_id, days=days)

    return {
        "product_id": str(product_id),
        "total_clicks": total,
        f"clicks_last_{days}_days": period,
    }
