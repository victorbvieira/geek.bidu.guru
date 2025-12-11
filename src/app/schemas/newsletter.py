"""
Schemas para NewsletterSignup (inscricoes em newsletter).
"""

from datetime import datetime
from uuid import UUID

from pydantic import EmailStr, Field

from app.schemas.base import BaseSchema, IDSchema


# -----------------------------------------------------------------------------
# Create
# -----------------------------------------------------------------------------


class NewsletterCreate(BaseSchema):
    """Schema para inscricao em newsletter."""

    email: EmailStr = Field(..., description="Email do inscrito")
    name: str | None = Field(None, max_length=200, description="Nome do inscrito")
    source: str | None = Field(None, max_length=100, description="Origem da inscricao")


class NewsletterSubscribe(BaseSchema):
    """Schema simplificado para formulario publico."""

    email: EmailStr = Field(..., description="Email do inscrito")
    name: str | None = Field(None, max_length=200, description="Nome (opcional)")


# -----------------------------------------------------------------------------
# Update
# -----------------------------------------------------------------------------


class NewsletterUpdate(BaseSchema):
    """Schema para atualizacao de inscricao."""

    name: str | None = Field(None, max_length=200)
    is_active: bool | None = None


# -----------------------------------------------------------------------------
# Response
# -----------------------------------------------------------------------------


class NewsletterResponse(IDSchema):
    """Schema de resposta completa de Newsletter."""

    email: EmailStr
    name: str | None
    source: str | None
    is_active: bool
    subscribed_at: datetime
    unsubscribed_at: datetime | None


class NewsletterBrief(BaseSchema):
    """Schema resumido de Newsletter."""

    id: UUID
    email: EmailStr
    name: str | None
    is_active: bool
    subscribed_at: datetime


class NewsletterPublicResponse(BaseSchema):
    """Resposta publica apos inscricao."""

    message: str = "Inscricao realizada com sucesso!"
    email: EmailStr


# -----------------------------------------------------------------------------
# Analytics
# -----------------------------------------------------------------------------


class NewsletterStats(BaseSchema):
    """Estatisticas de newsletter."""

    total_subscribers: int
    active_subscribers: int
    unsubscribed: int
    subscriptions_today: int
    subscriptions_week: int
    subscriptions_month: int


class NewsletterBySource(BaseSchema):
    """Inscricoes agrupadas por origem."""

    source: str | None
    count: int
    percentage: float


class NewsletterByPeriod(BaseSchema):
    """Inscricoes agrupadas por periodo."""

    date: str  # YYYY-MM-DD
    subscriptions: int
    unsubscriptions: int
