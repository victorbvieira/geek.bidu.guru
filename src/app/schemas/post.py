"""
Schemas para Post (artigos/listicles/guides).
"""

from datetime import datetime
from uuid import UUID

from pydantic import Field, field_validator

from app.models.post import PostStatus, PostType
from app.schemas.base import BaseSchema, ResponseSchema
from app.schemas.category import CategoryBrief
from app.schemas.user import UserBrief


# -----------------------------------------------------------------------------
# Base
# -----------------------------------------------------------------------------


class PostBase(BaseSchema):
    """Campos compartilhados de Post."""

    type: PostType = Field(..., description="Tipo do post")
    title: str = Field(..., min_length=5, max_length=200, description="Titulo do post")
    slug: str = Field(..., min_length=5, max_length=250, description="Slug para URL")
    subtitle: str | None = Field(None, max_length=300, description="Subtitulo")
    content: str = Field(..., min_length=10, description="Conteudo HTML/Markdown")
    featured_image_url: str | None = Field(None, max_length=500, description="URL imagem destaque")


# -----------------------------------------------------------------------------
# SEO
# -----------------------------------------------------------------------------


class PostSEO(BaseSchema):
    """Campos SEO do post."""

    seo_focus_keyword: str | None = Field(None, max_length=100, description="Keyword principal")
    seo_title: str | None = Field(None, max_length=60, description="Titulo SEO (max 60 chars)")
    seo_description: str | None = Field(None, max_length=160, description="Meta description")

    @field_validator("seo_title")
    @classmethod
    def validate_seo_title(cls, v: str | None) -> str | None:
        if v and len(v) > 60:
            raise ValueError("SEO title deve ter no maximo 60 caracteres")
        return v

    @field_validator("seo_description")
    @classmethod
    def validate_seo_description(cls, v: str | None) -> str | None:
        if v and len(v) > 160:
            raise ValueError("SEO description deve ter no maximo 160 caracteres")
        return v


# -----------------------------------------------------------------------------
# Create
# -----------------------------------------------------------------------------


class PostCreate(PostBase, PostSEO):
    """Schema para criacao de post."""

    category_id: UUID | None = None
    tags: list[str] = Field(default_factory=list, description="Tags do post")
    status: PostStatus = Field(default=PostStatus.DRAFT, description="Status do post")
    publish_at: datetime | None = Field(None, description="Data de publicacao agendada")


# -----------------------------------------------------------------------------
# Update
# -----------------------------------------------------------------------------


class PostUpdate(BaseSchema):
    """Schema para atualizacao de post (todos campos opcionais)."""

    type: PostType | None = None
    title: str | None = Field(None, min_length=5, max_length=200)
    slug: str | None = Field(None, min_length=5, max_length=250)
    subtitle: str | None = Field(None, max_length=300)
    content: str | None = Field(None, min_length=10)
    featured_image_url: str | None = None
    seo_focus_keyword: str | None = None
    seo_title: str | None = Field(None, max_length=60)
    seo_description: str | None = Field(None, max_length=160)
    category_id: UUID | None = None
    tags: list[str] | None = None
    status: PostStatus | None = None
    publish_at: datetime | None = None


class PostUpdateStatus(BaseSchema):
    """Schema para atualizacao de status do post."""

    status: PostStatus
    publish_at: datetime | None = None


# -----------------------------------------------------------------------------
# Response
# -----------------------------------------------------------------------------


class PostResponse(PostBase, PostSEO, ResponseSchema):
    """Schema de resposta completa de Post."""

    category_id: UUID | None
    author_id: UUID | None
    tags: list[str]
    status: PostStatus
    publish_at: datetime | None
    shared: bool
    view_count: int
    click_count: int


class PostWithRelations(PostResponse):
    """Schema de post com relacoes carregadas."""

    category: CategoryBrief | None = None
    author: UserBrief | None = None


class PostBrief(BaseSchema):
    """Schema resumido de Post (para listagens)."""

    id: UUID
    type: PostType
    title: str
    slug: str
    featured_image_url: str | None
    status: PostStatus
    publish_at: datetime | None
    view_count: int
    click_count: int
    created_at: datetime


class PostPublic(BaseSchema):
    """Schema de post para exibicao publica (frontend)."""

    id: UUID
    type: PostType
    title: str
    slug: str
    subtitle: str | None
    content: str
    featured_image_url: str | None
    seo_title: str | None
    seo_description: str | None
    category: CategoryBrief | None = None
    author: UserBrief | None = None
    tags: list[str]
    publish_at: datetime | None
    created_at: datetime
