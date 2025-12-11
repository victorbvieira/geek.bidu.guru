"""
Schemas para Session (tracking de visitantes).
"""

from datetime import datetime
from uuid import UUID

from pydantic import Field

from app.models.session import DeviceType
from app.schemas.base import BaseSchema, IDSchema


# -----------------------------------------------------------------------------
# Create
# -----------------------------------------------------------------------------


class SessionCreate(BaseSchema):
    """Schema para registro de sessao."""

    session_id: str = Field(..., max_length=100, description="ID unico da sessao")
    post_id: UUID | None = Field(None, description="ID do post visitado")
    user_agent: str | None = Field(None, description="User agent do navegador")
    referer: str | None = Field(None, description="Referer URL")
    ip_address: str | None = Field(None, max_length=45, description="IP do visitante")
    country: str | None = Field(None, max_length=2, description="Codigo do pais (ISO)")
    device_type: DeviceType = Field(default=DeviceType.UNKNOWN, description="Tipo de dispositivo")
    is_new_user: bool = Field(default=True, description="Se eh um novo visitante")


class SessionUpdate(BaseSchema):
    """Schema para atualizacao de sessao (engagement)."""

    time_on_page: int | None = Field(None, ge=0, description="Tempo na pagina (segundos)")
    scroll_depth: int | None = Field(None, ge=0, le=100, description="Profundidade de scroll (%)")


# -----------------------------------------------------------------------------
# Response
# -----------------------------------------------------------------------------


class SessionResponse(SessionCreate, IDSchema):
    """Schema de resposta completa de Session."""

    time_on_page: int | None
    scroll_depth: int | None
    created_at: datetime


class SessionBrief(BaseSchema):
    """Schema resumido de Session."""

    id: UUID
    session_id: str
    post_id: UUID | None
    device_type: DeviceType
    is_new_user: bool
    created_at: datetime


# -----------------------------------------------------------------------------
# Analytics
# -----------------------------------------------------------------------------


class SessionStats(BaseSchema):
    """Estatisticas de sessoes."""

    total_sessions: int
    unique_visitors: int
    new_users: int
    returning_users: int
    avg_time_on_page: float
    avg_scroll_depth: float


class SessionsByDevice(BaseSchema):
    """Sessoes agrupadas por dispositivo."""

    device_type: DeviceType
    count: int
    percentage: float


class SessionsByCountry(BaseSchema):
    """Sessoes agrupadas por pais."""

    country: str | None
    count: int
    percentage: float


class SessionsByPost(BaseSchema):
    """Sessoes agrupadas por post."""

    post_id: UUID | None
    post_title: str | None
    sessions: int
    avg_time_on_page: float
    avg_scroll_depth: float


class SessionAnalytics(BaseSchema):
    """Analytics completo de sessoes."""

    stats: SessionStats
    by_device: list[SessionsByDevice]
    by_country: list[SessionsByCountry]
    top_posts: list[SessionsByPost]
