"""
Modelo de Categoria.

Categorias hierarquicas para organizar posts e produtos.
"""

import uuid
from typing import TYPE_CHECKING, Optional

from sqlalchemy import ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.post import Post


class Category(Base, UUIDMixin, TimestampMixin):
    """
    Categoria de posts.

    Suporta hierarquia (subcategorias) atraves de parent_id.

    Atributos:
        id: UUID primary key
        name: Nome da categoria
        slug: Slug unico para URL
        description: Descricao da categoria
        image_url: URL da imagem de capa da categoria
        seo_title: Titulo para SEO (meta title)
        seo_description: Descricao para SEO (meta description)
        parent_id: ID da categoria pai (para subcategorias)
        created_at: Data de criacao
        updated_at: Data de atualizacao
    """

    __tablename__ = "categories"

    # Campos basicos
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    slug: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Campos de imagem e SEO
    image_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    seo_focus_keyword: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    seo_title: Mapped[Optional[str]] = mapped_column(String(60), nullable=True)
    seo_description: Mapped[Optional[str]] = mapped_column(String(160), nullable=True)

    # Auto-referencia para hierarquia
    parent_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("categories.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Relacionamentos
    parent: Mapped[Optional["Category"]] = relationship(
        "Category",
        remote_side="Category.id",
        back_populates="children",
        lazy="selectin",
    )

    children: Mapped[list["Category"]] = relationship(
        "Category",
        back_populates="parent",
        lazy="selectin",
    )

    posts: Mapped[list["Post"]] = relationship(
        "Post",
        back_populates="category",
        lazy="selectin",
    )

    # Indices
    __table_args__ = (
        Index("idx_categories_slug", "slug"),
        Index("idx_categories_parent", "parent_id"),
    )

    def __repr__(self) -> str:
        return f"<Category {self.name} ({self.slug})>"

    @property
    def full_path(self) -> str:
        """Retorna o caminho completo da categoria (ex: 'games/xbox')."""
        if self.parent:
            return f"{self.parent.full_path}/{self.slug}"
        return self.slug
