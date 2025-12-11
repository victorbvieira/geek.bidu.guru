"""
Endpoints para Product.
"""

from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status

from app.api.deps import Pagination, ProductRepo
from app.models.product import PriceRange, ProductPlatform
from app.schemas import (
    MessageResponse,
    PaginatedResponse,
    ProductCreate,
    ProductResponse,
    ProductUpdate,
    ProductUpdatePrice,
)

router = APIRouter(prefix="/products", tags=["products"])


@router.get("", response_model=PaginatedResponse)
async def list_products(
    repo: ProductRepo,
    pagination: Pagination,
    platform: ProductPlatform | None = None,
    price_range: PriceRange | None = None,
):
    """Lista produtos com paginacao e filtros."""
    if platform:
        products = await repo.get_by_platform(
            platform=platform,
            skip=pagination["skip"],
            limit=pagination["limit"],
        )
    else:
        products = await repo.get_multi(
            skip=pagination["skip"],
            limit=pagination["limit"],
            order_by="created_at",
        )

    total = await repo.count()

    return PaginatedResponse.create(
        items=[ProductResponse.model_validate(p) for p in products],
        total=total,
        page=pagination["page"],
        per_page=pagination["per_page"],
    )


@router.get("/available", response_model=PaginatedResponse)
async def list_available_products(
    repo: ProductRepo,
    pagination: Pagination,
    platform: ProductPlatform | None = None,
    price_range: PriceRange | None = None,
):
    """Lista produtos disponiveis."""
    products = await repo.get_available(
        skip=pagination["skip"],
        limit=pagination["limit"],
        platform=platform,
        price_range=price_range,
    )
    total = await repo.count()

    return PaginatedResponse.create(
        items=[ProductResponse.model_validate(p) for p in products],
        total=total,
        page=pagination["page"],
        per_page=pagination["per_page"],
    )


@router.get("/top-clicked", response_model=list[ProductResponse])
async def list_top_clicked(
    repo: ProductRepo,
    limit: int = Query(10, ge=1, le=50),
):
    """Lista produtos mais clicados."""
    products = await repo.get_top_clicked(limit=limit)
    return [ProductResponse.model_validate(p) for p in products]


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(product_id: UUID, repo: ProductRepo):
    """Busca produto por ID."""
    product = await repo.get(product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produto nao encontrado",
        )
    return ProductResponse.model_validate(product)


@router.get("/slug/{slug}", response_model=ProductResponse)
async def get_product_by_slug(slug: str, repo: ProductRepo):
    """Busca produto por slug."""
    product = await repo.get_by_slug(slug)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produto nao encontrado",
        )
    return ProductResponse.model_validate(product)


@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(data: ProductCreate, repo: ProductRepo):
    """Cria novo produto."""
    # Verificar slugs duplicados
    if await repo.slug_exists(data.slug):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Slug ja existe",
        )

    if await repo.redirect_slug_exists(data.affiliate_redirect_slug):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Redirect slug ja existe",
        )

    product = await repo.create(data.model_dump())
    return ProductResponse.model_validate(product)


@router.patch("/{product_id}", response_model=ProductResponse)
async def update_product(product_id: UUID, data: ProductUpdate, repo: ProductRepo):
    """Atualiza produto."""
    product = await repo.get(product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produto nao encontrado",
        )

    # Verificar slug duplicado
    if data.slug and await repo.slug_exists(data.slug, exclude_id=product_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Slug ja existe",
        )

    update_data = data.model_dump(exclude_unset=True)
    product = await repo.update(product, update_data)
    return ProductResponse.model_validate(product)


@router.patch("/{product_id}/price", response_model=ProductResponse)
async def update_product_price(
    product_id: UUID, data: ProductUpdatePrice, repo: ProductRepo
):
    """Atualiza preco do produto."""
    product = await repo.get(product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produto nao encontrado",
        )

    update_data = data.model_dump(exclude_unset=True)
    product = await repo.update(product, update_data)
    return ProductResponse.model_validate(product)


@router.delete("/{product_id}", response_model=MessageResponse)
async def delete_product(product_id: UUID, repo: ProductRepo):
    """Remove produto."""
    if not await repo.exists(product_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produto nao encontrado",
        )

    await repo.delete(product_id)
    return MessageResponse(message="Produto removido com sucesso")
