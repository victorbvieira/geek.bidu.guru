"""
Endpoints para Category.
"""

from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from app.api.deps import CategoryRepo, Pagination
from app.schemas import (
    CategoryCreate,
    CategoryResponse,
    CategoryUpdate,
    MessageResponse,
    PaginatedResponse,
)

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("", response_model=PaginatedResponse)
async def list_categories(
    repo: CategoryRepo,
    pagination: Pagination,
):
    """Lista categorias com paginacao."""
    categories = await repo.get_multi(
        skip=pagination["skip"],
        limit=pagination["limit"],
        order_by="name",
        desc=False,
    )
    total = await repo.count()

    return PaginatedResponse.create(
        items=[CategoryResponse.model_validate(c) for c in categories],
        total=total,
        page=pagination["page"],
        per_page=pagination["per_page"],
    )


@router.get("/root", response_model=list[CategoryResponse])
async def list_root_categories(repo: CategoryRepo):
    """Lista apenas categorias raiz (sem parent)."""
    categories = await repo.get_root_categories()
    return [CategoryResponse.model_validate(c) for c in categories]


@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(category_id: UUID, repo: CategoryRepo):
    """Busca categoria por ID."""
    category = await repo.get(category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Categoria nao encontrada",
        )
    return CategoryResponse.model_validate(category)


@router.get("/slug/{slug}", response_model=CategoryResponse)
async def get_category_by_slug(slug: str, repo: CategoryRepo):
    """Busca categoria por slug."""
    category = await repo.get_by_slug(slug)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Categoria nao encontrada",
        )
    return CategoryResponse.model_validate(category)


@router.get("/{category_id}/children", response_model=list[CategoryResponse])
async def list_subcategories(category_id: UUID, repo: CategoryRepo):
    """Lista subcategorias de uma categoria."""
    # Verificar se categoria existe
    if not await repo.exists(category_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Categoria nao encontrada",
        )

    children = await repo.get_children(category_id)
    return [CategoryResponse.model_validate(c) for c in children]


@router.post("", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(data: CategoryCreate, repo: CategoryRepo):
    """Cria nova categoria."""
    # Verificar slug duplicado
    if await repo.slug_exists(data.slug):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Slug ja existe",
        )

    # Verificar parent existe
    if data.parent_id and not await repo.exists(data.parent_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Categoria pai nao encontrada",
        )

    category = await repo.create(data.model_dump())
    return CategoryResponse.model_validate(category)


@router.patch("/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: UUID, data: CategoryUpdate, repo: CategoryRepo
):
    """Atualiza categoria."""
    category = await repo.get(category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Categoria nao encontrada",
        )

    # Verificar slug duplicado
    if data.slug and await repo.slug_exists(data.slug, exclude_id=category_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Slug ja existe",
        )

    # Verificar parent existe e nao eh a propria categoria
    if data.parent_id:
        if data.parent_id == category_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Categoria nao pode ser pai de si mesma",
            )
        if not await repo.exists(data.parent_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Categoria pai nao encontrada",
            )

    update_data = data.model_dump(exclude_unset=True)
    category = await repo.update(category, update_data)
    return CategoryResponse.model_validate(category)


@router.delete("/{category_id}", response_model=MessageResponse)
async def delete_category(category_id: UUID, repo: CategoryRepo):
    """Remove categoria."""
    if not await repo.exists(category_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Categoria nao encontrada",
        )

    await repo.delete(category_id)
    return MessageResponse(message="Categoria removida com sucesso")
