"""
Schemas para User (usuarios admin/editor/author).
"""

from uuid import UUID

from pydantic import EmailStr, Field

from app.models.user import UserRole
from app.schemas.base import BaseSchema, ResponseSchema


# -----------------------------------------------------------------------------
# Base
# -----------------------------------------------------------------------------


class UserBase(BaseSchema):
    """Campos compartilhados de User."""

    name: str = Field(..., min_length=2, max_length=200, description="Nome do usuario")
    email: EmailStr = Field(..., description="Email do usuario")
    role: UserRole = Field(default=UserRole.AUTHOR, description="Role do usuario")


# -----------------------------------------------------------------------------
# Create
# -----------------------------------------------------------------------------


class UserCreate(UserBase):
    """Schema para criacao de usuario."""

    password: str = Field(
        ...,
        min_length=8,
        max_length=100,
        description="Senha (minimo 8 caracteres)",
    )


# -----------------------------------------------------------------------------
# Update
# -----------------------------------------------------------------------------


class UserUpdate(BaseSchema):
    """Schema para atualizacao de usuario (todos campos opcionais)."""

    name: str | None = Field(None, min_length=2, max_length=200)
    email: EmailStr | None = None
    role: UserRole | None = None
    is_active: bool | None = None


class UserUpdatePassword(BaseSchema):
    """Schema para atualizacao de senha."""

    current_password: str = Field(..., description="Senha atual")
    new_password: str = Field(
        ...,
        min_length=8,
        max_length=100,
        description="Nova senha (minimo 8 caracteres)",
    )


# -----------------------------------------------------------------------------
# Response
# -----------------------------------------------------------------------------


class UserResponse(UserBase, ResponseSchema):
    """Schema de resposta completa de User."""

    is_active: bool


class UserBrief(BaseSchema):
    """Schema resumido de User (para listagens)."""

    id: UUID
    name: str
    email: EmailStr
    role: UserRole


# -----------------------------------------------------------------------------
# Auth
# -----------------------------------------------------------------------------


class UserLogin(BaseSchema):
    """Schema para login."""

    email: EmailStr
    password: str


class TokenResponse(BaseSchema):
    """Schema de resposta com token JWT."""

    access_token: str
    token_type: str = "bearer"
    expires_in: int = Field(..., description="Tempo de expiracao em segundos")


class TokenPayload(BaseSchema):
    """Payload do token JWT."""

    sub: str  # user_id
    exp: int  # expiration timestamp
    role: str
