"""
Endpoints para Post.
"""

from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status

from app.api.deps import Pagination, PostRepo
from app.models.post import PostStatus, PostType
from app.schemas import (
    MessageResponse,
    PaginatedResponse,
    PostCreate,
    PostResponse,
    PostUpdate,
    PostUpdateStatus,
)

router = APIRouter(prefix="/posts", tags=["posts"])


@router.get("", response_model=PaginatedResponse)
async def list_posts(
    repo: PostRepo,
    pagination: Pagination,
    status_filter: PostStatus | None = Query(None, alias="status"),
    type_filter: PostType | None = Query(None, alias="type"),
):
    """Lista posts com paginacao e filtros."""
    if status_filter:
        posts = await repo.get_by_status(
            status=status_filter,
            skip=pagination["skip"],
            limit=pagination["limit"],
        )
    else:
        posts = await repo.get_multi(
            skip=pagination["skip"],
            limit=pagination["limit"],
            order_by="created_at",
        )

    total = await repo.count()

    return PaginatedResponse.create(
        items=[PostResponse.model_validate(p) for p in posts],
        total=total,
        page=pagination["page"],
        per_page=pagination["per_page"],
    )


@router.get("/published", response_model=PaginatedResponse)
async def list_published_posts(
    repo: PostRepo,
    pagination: Pagination,
    category_id: UUID | None = None,
    post_type: PostType | None = Query(None, alias="type"),
):
    """Lista posts publicados (para frontend publico)."""
    posts = await repo.get_published(
        skip=pagination["skip"],
        limit=pagination["limit"],
        category_id=category_id,
        post_type=post_type,
    )
    total = await repo.count_published(category_id=category_id, post_type=post_type)

    return PaginatedResponse.create(
        items=[PostResponse.model_validate(p) for p in posts],
        total=total,
        page=pagination["page"],
        per_page=pagination["per_page"],
    )


@router.get("/{post_id}", response_model=PostResponse)
async def get_post(post_id: UUID, repo: PostRepo):
    """Busca post por ID."""
    post = await repo.get_with_relations(post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post nao encontrado",
        )
    return PostResponse.model_validate(post)


@router.get("/slug/{slug}", response_model=PostResponse)
async def get_post_by_slug(slug: str, repo: PostRepo):
    """Busca post por slug."""
    post = await repo.get_by_slug(slug)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post nao encontrado",
        )
    return PostResponse.model_validate(post)


@router.post("", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(data: PostCreate, repo: PostRepo):
    """Cria novo post."""
    # Verificar slug duplicado
    if await repo.slug_exists(data.slug):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Slug ja existe",
        )

    post = await repo.create(data.model_dump())
    return PostResponse.model_validate(post)


@router.patch("/{post_id}", response_model=PostResponse)
async def update_post(post_id: UUID, data: PostUpdate, repo: PostRepo):
    """Atualiza post."""
    post = await repo.get(post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post nao encontrado",
        )

    # Verificar slug duplicado
    if data.slug and await repo.slug_exists(data.slug, exclude_id=post_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Slug ja existe",
        )

    update_data = data.model_dump(exclude_unset=True)
    post = await repo.update(post, update_data)
    return PostResponse.model_validate(post)


@router.patch("/{post_id}/status", response_model=PostResponse)
async def update_post_status(
    post_id: UUID, data: PostUpdateStatus, repo: PostRepo
):
    """Atualiza status do post."""
    post = await repo.get(post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post nao encontrado",
        )

    update_data = data.model_dump(exclude_unset=True)
    post = await repo.update(post, update_data)
    return PostResponse.model_validate(post)


@router.post("/{post_id}/view", response_model=MessageResponse)
async def increment_view(post_id: UUID, repo: PostRepo):
    """Incrementa contador de views."""
    if not await repo.exists(post_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post nao encontrado",
        )

    await repo.increment_view_count(post_id)
    return MessageResponse(message="View registrada")


@router.delete("/{post_id}", response_model=MessageResponse)
async def delete_post(post_id: UUID, repo: PostRepo):
    """Remove post."""
    if not await repo.exists(post_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post nao encontrado",
        )

    await repo.delete(post_id)
    return MessageResponse(message="Post removido com sucesso")
