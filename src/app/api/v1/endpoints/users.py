"""
Endpoints para User.
"""

from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from passlib.hash import bcrypt

from app.api.deps import Pagination, UserRepo
from app.schemas import (
    MessageResponse,
    PaginatedResponse,
    UserCreate,
    UserResponse,
    UserUpdate,
)

router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=PaginatedResponse)
async def list_users(
    repo: UserRepo,
    pagination: Pagination,
):
    """Lista usuarios com paginacao."""
    users = await repo.get_multi(
        skip=pagination["skip"],
        limit=pagination["limit"],
        order_by="created_at",
    )
    total = await repo.count()

    return PaginatedResponse.create(
        items=[UserResponse.model_validate(u) for u in users],
        total=total,
        page=pagination["page"],
        per_page=pagination["per_page"],
    )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: UUID, repo: UserRepo):
    """Busca usuario por ID."""
    user = await repo.get(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario nao encontrado",
        )
    return UserResponse.model_validate(user)


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(data: UserCreate, repo: UserRepo):
    """Cria novo usuario."""
    # Verificar se email ja existe
    if await repo.email_exists(data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email ja cadastrado",
        )

    # Hash da senha
    user_data = data.model_dump()
    user_data["password_hash"] = bcrypt.hash(user_data.pop("password"))

    user = await repo.create(user_data)
    return UserResponse.model_validate(user)


@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(user_id: UUID, data: UserUpdate, repo: UserRepo):
    """Atualiza usuario."""
    user = await repo.get(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario nao encontrado",
        )

    # Verificar email duplicado
    if data.email and data.email != user.email:
        if await repo.email_exists(data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email ja cadastrado",
            )

    update_data = data.model_dump(exclude_unset=True)
    user = await repo.update(user, update_data)
    return UserResponse.model_validate(user)


@router.delete("/{user_id}", response_model=MessageResponse)
async def delete_user(user_id: UUID, repo: UserRepo):
    """Remove usuario."""
    if not await repo.exists(user_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario nao encontrado",
        )

    await repo.delete(user_id)
    return MessageResponse(message="Usuario removido com sucesso")
