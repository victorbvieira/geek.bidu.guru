"""
Schemas para Category (categorias de posts).
"""

from uuid import UUID

from pydantic import Field

from app.schemas.base import BaseSchema, ResponseSchema


# -----------------------------------------------------------------------------
# Base
# -----------------------------------------------------------------------------


class CategoryBase(BaseSchema):
    """Campos compartilhados de Category."""

    name: str = Field(..., min_length=2, max_length=100, description="Nome da categoria")
    slug: str = Field(..., min_length=2, max_length=120, description="Slug para URL")
    description: str | None = Field(None, max_length=500, description="Descricao")
    parent_id: UUID | None = Field(None, description="ID da categoria pai")


# -----------------------------------------------------------------------------
# Create
# -----------------------------------------------------------------------------


class CategoryCreate(CategoryBase):
    """Schema para criacao de categoria."""

    pass


# -----------------------------------------------------------------------------
# Update
# -----------------------------------------------------------------------------


class CategoryUpdate(BaseSchema):
    """Schema para atualizacao de categoria (todos campos opcionais)."""

    name: str | None = Field(None, min_length=2, max_length=100)
    slug: str | None = Field(None, min_length=2, max_length=120)
    description: str | None = Field(None, max_length=500)
    parent_id: UUID | None = None


# -----------------------------------------------------------------------------
# Response
# -----------------------------------------------------------------------------


class CategoryResponse(CategoryBase, ResponseSchema):
    """Schema de resposta completa de Category."""

    pass


class CategoryBrief(BaseSchema):
    """Schema resumido de Category."""

    id: UUID
    name: str
    slug: str


class CategoryWithChildren(CategoryResponse):
    """Schema de categoria com subcategorias."""

    children: list["CategoryBrief"] = []


class CategoryTree(BaseSchema):
    """Schema para arvore de categorias."""

    id: UUID
    name: str
    slug: str
    children: list["CategoryTree"] = []
