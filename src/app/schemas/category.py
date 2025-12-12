"""
Schemas para Category (categorias de posts).
"""

import re
from uuid import UUID

from pydantic import Field, field_validator

from app.schemas.base import BaseSchema, ResponseSchema
from app.utils.sanitize import sanitize_text, sanitize_slug


# -----------------------------------------------------------------------------
# Base
# -----------------------------------------------------------------------------


class CategoryBase(BaseSchema):
    """Campos compartilhados de Category."""

    name: str = Field(..., min_length=2, max_length=100, description="Nome da categoria")
    slug: str = Field(..., min_length=2, max_length=120, description="Slug para URL")
    description: str | None = Field(None, max_length=500, description="Descricao")
    parent_id: UUID | None = Field(None, description="ID da categoria pai")

    @field_validator("name")
    @classmethod
    def sanitize_name(cls, v: str) -> str:
        """Sanitiza nome removendo scripts/HTML malicioso."""
        sanitized = sanitize_text(v)
        if not sanitized or len(sanitized) < 2:
            raise ValueError("Nome invalido apos sanitizacao")
        return sanitized

    @field_validator("slug")
    @classmethod
    def validate_and_sanitize_slug(cls, v: str) -> str:
        """Valida e sanitiza slug."""
        # Sanitiza primeiro
        sanitized = sanitize_slug(v)
        if not sanitized or len(sanitized) < 2:
            raise ValueError("Slug invalido - deve conter apenas letras minusculas, numeros e hifens")

        # Valida formato
        if not re.match(r"^[a-z0-9]+(?:-[a-z0-9]+)*$", sanitized):
            raise ValueError("Slug deve conter apenas letras minusculas, numeros e hifens")

        return sanitized

    @field_validator("description")
    @classmethod
    def sanitize_description(cls, v: str | None) -> str | None:
        """Sanitiza descricao removendo scripts/HTML malicioso."""
        if v is None:
            return None
        return sanitize_text(v)


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

    @field_validator("name")
    @classmethod
    def sanitize_name(cls, v: str | None) -> str | None:
        """Sanitiza nome removendo scripts/HTML malicioso."""
        if v is None:
            return None
        sanitized = sanitize_text(v)
        if not sanitized or len(sanitized) < 2:
            raise ValueError("Nome invalido apos sanitizacao")
        return sanitized

    @field_validator("slug")
    @classmethod
    def validate_and_sanitize_slug(cls, v: str | None) -> str | None:
        """Valida e sanitiza slug."""
        if v is None:
            return None
        # Sanitiza primeiro
        sanitized = sanitize_slug(v)
        if not sanitized or len(sanitized) < 2:
            raise ValueError("Slug invalido - deve conter apenas letras minusculas, numeros e hifens")

        # Valida formato
        if not re.match(r"^[a-z0-9]+(?:-[a-z0-9]+)*$", sanitized):
            raise ValueError("Slug deve conter apenas letras minusculas, numeros e hifens")

        return sanitized

    @field_validator("description")
    @classmethod
    def sanitize_description(cls, v: str | None) -> str | None:
        """Sanitiza descricao removendo scripts/HTML malicioso."""
        if v is None:
            return None
        return sanitize_text(v)


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
