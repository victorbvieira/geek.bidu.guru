"""
Schemas para AffiliateClick (tracking de cliques).
"""

from datetime import datetime
from uuid import UUID

from pydantic import Field

from app.schemas.base import BaseSchema, IDSchema


# -----------------------------------------------------------------------------
# Create
# -----------------------------------------------------------------------------


class ClickCreate(BaseSchema):
    """Schema para registro de clique (interno)."""

    product_id: UUID = Field(..., description="ID do produto clicado")
    post_id: UUID | None = Field(None, description="ID do post de origem")
    session_id: str | None = Field(None, max_length=100, description="ID da sessao")
    user_agent: str | None = Field(None, description="User agent do navegador")
    referer: str | None = Field(None, description="Referer URL")
    ip_address: str | None = Field(None, max_length=45, description="IP do visitante")


# -----------------------------------------------------------------------------
# Response
# -----------------------------------------------------------------------------


class ClickResponse(ClickCreate, IDSchema):
    """Schema de resposta completa de Click."""

    clicked_at: datetime


class ClickBrief(BaseSchema):
    """Schema resumido de Click."""

    id: UUID
    product_id: UUID
    post_id: UUID | None
    clicked_at: datetime


# -----------------------------------------------------------------------------
# Analytics
# -----------------------------------------------------------------------------


class ClickStats(BaseSchema):
    """Estatisticas de cliques para um produto."""

    product_id: UUID
    total_clicks: int
    clicks_today: int
    clicks_week: int
    clicks_month: int


class ClicksByPeriod(BaseSchema):
    """Cliques agrupados por periodo."""

    date: str  # YYYY-MM-DD
    clicks: int


class ClicksByProduct(BaseSchema):
    """Cliques agrupados por produto."""

    product_id: UUID
    product_name: str
    product_slug: str
    clicks: int


class ClicksByPost(BaseSchema):
    """Cliques agrupados por post de origem."""

    post_id: UUID | None
    post_title: str | None
    clicks: int


class ClickAnalytics(BaseSchema):
    """Analytics completo de cliques."""

    total_clicks: int
    unique_sessions: int
    top_products: list[ClicksByProduct]
    top_posts: list[ClicksByPost]
    clicks_by_day: list[ClicksByPeriod]
