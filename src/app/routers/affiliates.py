"""
Rotas publicas de redirect para afiliados.

Este modulo implementa o endpoint /goto/{slug} que:
1. Registra cliques em produtos de afiliados
2. Redireciona o usuario para a URL do afiliado (Amazon, ML, Shopee)

A URL curta /goto/{slug} e mais amigavel para SEO e compartilhamento
do que a URL completa da API.

Exemplo:
    /goto/funko-vader-amazon -> Amazon (com tracking)
    /goto/camiseta-python-ml -> Mercado Livre (com tracking)
"""

from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, Request, status
from fastapi.responses import RedirectResponse

from app.api.deps import ClickRepo, ProductRepo

router = APIRouter(tags=["affiliates"])


@router.get("/goto/{redirect_slug}")
async def redirect_to_affiliate(
    redirect_slug: str,
    request: Request,
    product_repo: ProductRepo,
    click_repo: ClickRepo,
    post_id: UUID | None = Query(None, description="Post de origem do clique"),
):
    """
    Redireciona para URL de afiliado e registra o clique.

    Este endpoint e a URL publica principal para links de afiliados.
    Quando um visitante clica em um produto no site, ele passa por aqui:

    1. Sistema encontra o produto pelo redirect_slug
    2. Registra informacoes do clique (tracking)
    3. Incrementa contador de cliques no produto
    4. Redireciona (302) para URL de afiliado

    Args:
        redirect_slug: Slug unico do produto para redirect
                       Ex: funko-vader-amazon, camiseta-python-ml
        request: Request do FastAPI (captura headers para tracking)
        product_repo: Repositorio de produtos injetado
        click_repo: Repositorio de cliques injetado
        post_id: UUID do post de origem (opcional, para analytics)

    Returns:
        RedirectResponse 302 para URL de afiliado

    Raises:
        HTTPException 404: Produto nao encontrado

    Tracking Capturado:
        - product_id: ID do produto clicado
        - post_id: Post de origem (se houver)
        - session_id: Cookie de sessao do visitante
        - user_agent: Navegador/dispositivo
        - referer: Pagina de onde veio o clique
        - ip_address: IP do visitante (geo)

    Exemplo de Uso:
        <a href="/goto/funko-vader-amazon?post_id=123">
            Ver na Amazon
        </a>

    Notas:
        - Usa redirect 302 (temporario) para permitir mudanca de URL
        - O tracking nao bloqueia o redirect
        - Links na plataforma do afiliado (Amazon, etc.) ja tem tag de afiliado
    """
    # Busca produto pelo redirect_slug
    product = await product_repo.get_by_redirect_slug(redirect_slug)

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produto nao encontrado",
        )

    # Captura dados para tracking
    click_data = {
        "product_id": product.id,
        "post_id": post_id,
        "session_id": request.cookies.get("session_id"),
        "user_agent": request.headers.get("user-agent"),
        "referer": request.headers.get("referer"),
        "ip_address": request.client.host if request.client else None,
    }

    # Registra clique no banco
    await click_repo.create(click_data)

    # Incrementa contador desnormalizado no produto
    await product_repo.increment_click_count(product.id)

    # Redireciona para URL do afiliado (302 = temporario)
    return RedirectResponse(
        url=product.affiliate_url_raw,
        status_code=status.HTTP_302_FOUND,
    )
