"""
Endpoints para tracking de cliques e redirect de afiliados.
"""

from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, Request, status
from fastapi.responses import RedirectResponse

from app.api.deps import ClickRepo, ProductRepo
from app.schemas import ClickAnalytics, ClickResponse, ClicksByPeriod, ClicksByProduct

router = APIRouter(prefix="/clicks", tags=["clicks"])


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

    Este endpoint e chamado quando usuario clica em um link de produto.
    """
    # Buscar produto pelo redirect_slug
    product = await product_repo.get_by_redirect_slug(redirect_slug)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produto nao encontrado",
        )

    # Registrar clique
    click_data = {
        "product_id": product.id,
        "post_id": post_id,
        "session_id": request.cookies.get("session_id"),
        "user_agent": request.headers.get("user-agent"),
        "referer": request.headers.get("referer"),
        "ip_address": request.client.host if request.client else None,
    }

    await click_repo.create(click_data)

    # Incrementar contador no produto
    await product_repo.increment_click_count(product.id)

    # Redirecionar para URL do afiliado
    return RedirectResponse(
        url=product.affiliate_url_raw,
        status_code=status.HTTP_302_FOUND,
    )


# -----------------------------------------------------------------------------
# Endpoints administrativos / Analytics
# -----------------------------------------------------------------------------


@router.get("/product/{product_id}", response_model=list[ClickResponse])
async def list_product_clicks(
    product_id: UUID,
    click_repo: ClickRepo,
    product_repo: ProductRepo,
    skip: int = 0,
    limit: int = 100,
):
    """Lista cliques de um produto (admin)."""
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
    """Retorna analytics de cliques (admin)."""
    # Total de cliques
    total = await click_repo.count()

    # Cliques por dia
    clicks_by_day = await click_repo.get_clicks_by_day(days=days)

    # Top produtos
    top_products_raw = await click_repo.get_top_products(days=days, limit=10)

    # Formatar resposta
    top_products = [
        ClicksByProduct(
            product_id=UUID(p["product_id"]),
            product_name="",  # Seria necessario join com products
            product_slug="",
            clicks=p["clicks"],
        )
        for p in top_products_raw
    ]

    return ClickAnalytics(
        total_clicks=total,
        unique_sessions=0,  # Implementar se necessario
        top_products=top_products,
        top_posts=[],  # Implementar se necessario
        clicks_by_day=[ClicksByPeriod(**c) for c in clicks_by_day],
    )


@router.get("/product/{product_id}/count")
async def get_product_click_count(
    product_id: UUID,
    click_repo: ClickRepo,
    product_repo: ProductRepo,
    days: int = Query(30, ge=1, le=365),
):
    """Retorna contagem de cliques de um produto."""
    if not await product_repo.exists(product_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produto nao encontrado",
        )

    total = await click_repo.count_by_product(product_id)
    period = await click_repo.count_by_product_period(product_id, days=days)

    return {
        "product_id": str(product_id),
        "total_clicks": total,
        f"clicks_last_{days}_days": period,
    }
