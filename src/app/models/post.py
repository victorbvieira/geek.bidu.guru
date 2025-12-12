"""
Modelo de Post (Artigo/Listicle/Guide).

Posts sao o conteudo principal do site, contendo
produtos de afiliados e otimizados para SEO.
"""

import enum
import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import JSONBType, TimestampMixin, UUIDMixin, utc_now

if TYPE_CHECKING:
    from app.models.category import Category
    from app.models.click import AffiliateClick
    from app.models.post_product import PostProduct
    from app.models.session import Session
    from app.models.user import User


class PostType(str, enum.Enum):
    """Tipos de post disponiveis."""

    PRODUCT_SINGLE = "product_single"  # Post sobre um unico produto
    LISTICLE = "listicle"  # Lista de produtos (Top 10, etc.)
    GUIDE = "guide"  # Guia de compra


class PostStatus(str, enum.Enum):
    """Status do post no workflow editorial."""

    DRAFT = "draft"  # Rascunho
    REVIEW = "review"  # Em revisao
    SCHEDULED = "scheduled"  # Agendado para publicacao
    PUBLISHED = "published"  # Publicado
    ARCHIVED = "archived"  # Arquivado


class Post(Base, UUIDMixin, TimestampMixin):
    """
    Post/Artigo do blog.

    Atributos:
        id: UUID primary key
        type: Tipo do post (product_single, listicle, guide)
        title: Titulo do post
        slug: Slug unico para URL
        subtitle: Subtitulo opcional
        content: Conteudo em Markdown/HTML
        featured_image_url: URL da imagem destacada
        seo_focus_keyword: Keyword principal para SEO
        seo_title: Titulo para SEO (max 60 chars)
        seo_description: Meta description (max 160 chars)
        category_id: ID da categoria
        author_id: ID do autor
        tags: Lista de tags (JSONB)
        status: Status do post
        publish_at: Data de publicacao
        shared: Se ja foi compartilhado em redes sociais
        view_count: Contador de visualizacoes (desnormalizado)
        click_count: Contador de cliques em afiliados (desnormalizado)
        created_at: Data de criacao
        updated_at: Data de atualizacao
    """

    __tablename__ = "posts"

    # Campos principais
    type: Mapped[PostType] = mapped_column(
        Enum(PostType, name="post_type", values_callable=lambda x: [e.value for e in x]),
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    subtitle: Mapped[Optional[str]] = mapped_column(String(300), nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    featured_image_url: Mapped[Optional[str]] = mapped_column(
        String(500), nullable=True
    )

    # SEO
    seo_focus_keyword: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True
    )
    seo_title: Mapped[Optional[str]] = mapped_column(String(60), nullable=True)
    seo_description: Mapped[Optional[str]] = mapped_column(String(160), nullable=True)

    # Relacionamentos (FK)
    category_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("categories.id", ondelete="SET NULL"),
        nullable=True,
    )
    author_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Tags (array JSON - usa JSONBType para compatibilidade com SQLite em testes)
    tags: Mapped[list] = mapped_column(JSONBType, default=list, server_default="[]")

    # Status e publicacao
    status: Mapped[PostStatus] = mapped_column(
        Enum(PostStatus, name="post_status", values_callable=lambda x: [e.value for e in x]),
        default=PostStatus.DRAFT,
    )
    publish_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    shared: Mapped[bool] = mapped_column(Boolean, default=False)

    # Metricas (desnormalizadas para performance)
    view_count: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    click_count: Mapped[int] = mapped_column(Integer, default=0, server_default="0")

    # Relacionamentos
    category: Mapped[Optional["Category"]] = relationship(
        "Category",
        back_populates="posts",
        lazy="selectin",
    )

    author: Mapped[Optional["User"]] = relationship(
        "User",
        back_populates="posts",
        lazy="selectin",
    )

    post_products: Mapped[list["PostProduct"]] = relationship(
        "PostProduct",
        back_populates="post",
        lazy="selectin",
        cascade="all, delete-orphan",
    )

    clicks: Mapped[list["AffiliateClick"]] = relationship(
        "AffiliateClick",
        back_populates="post",
        lazy="selectin",
    )

    sessions: Mapped[list["Session"]] = relationship(
        "Session",
        back_populates="post",
        lazy="selectin",
    )

    # Indices
    __table_args__ = (
        Index("idx_posts_slug", "slug"),
        Index("idx_posts_status", "status"),
        Index("idx_posts_type", "type"),
        Index("idx_posts_category", "category_id"),
        Index("idx_posts_author", "author_id"),
        Index("idx_posts_publish_at", "publish_at"),
        Index("idx_posts_tags", "tags", postgresql_using="gin"),
        Index("idx_posts_status_publish", "status", "publish_at"),
    )

    def __repr__(self) -> str:
        return f"<Post {self.slug} ({self.status.value})>"

    @property
    def is_published(self) -> bool:
        """Verifica se o post esta publicado e a data ja passou."""
        if self.status != PostStatus.PUBLISHED:
            return False
        if self.publish_at and self.publish_at > utc_now():
            return False
        return True
