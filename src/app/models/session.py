"""
Modelo de Sessao de Visitante.

Registra visitas a paginas para analytics de engajamento.
"""

import enum
import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Index, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import UUIDMixin

if TYPE_CHECKING:
    from app.models.post import Post


class DeviceType(str, enum.Enum):
    """Tipos de dispositivo."""

    MOBILE = "mobile"
    DESKTOP = "desktop"
    TABLET = "tablet"
    UNKNOWN = "unknown"


class Session(Base, UUIDMixin):
    """
    Sessao de visitante.

    Registra visitas a paginas com informacoes de engajamento.

    Atributos:
        id: UUID primary key
        session_id: ID unico da sessao (cookie)
        post_id: ID do post visitado (se houver)
        user_agent: User agent do navegador
        referer: Pagina de origem
        ip_address: IP do usuario
        country: Codigo do pais (ISO 3166-1 alpha-2)
        device_type: Tipo de dispositivo
        time_on_page: Tempo na pagina em segundos
        scroll_depth: Profundidade de scroll (0-100%)
        is_new_user: Se e um usuario novo
        created_at: Data/hora da visita
    """

    __tablename__ = "sessions"

    # Identificacao
    session_id: Mapped[str] = mapped_column(String(100), nullable=False)

    # Pagina visitada
    post_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("posts.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Informacoes do navegador
    user_agent: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    referer: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)

    # Localizacao e dispositivo
    country: Mapped[Optional[str]] = mapped_column(String(2), nullable=True)
    device_type: Mapped[DeviceType] = mapped_column(
        Enum(DeviceType, name="device_type"),
        default=DeviceType.UNKNOWN,
    )

    # Engajamento
    time_on_page: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    scroll_depth: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Usuario novo ou recorrente
    is_new_user: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")

    # Timestamp
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        default=datetime.utcnow,
    )

    # Relacionamentos
    post: Mapped[Optional["Post"]] = relationship(
        "Post",
        back_populates="sessions",
        lazy="selectin",
    )

    # Indices
    __table_args__ = (
        Index("idx_sessions_session_id", "session_id"),
        Index("idx_sessions_post", "post_id"),
        Index("idx_sessions_created_at", "created_at"),
        Index("idx_sessions_new_user", "is_new_user"),
        Index("idx_sessions_device", "device_type"),
    )

    def __repr__(self) -> str:
        return f"<Session {self.session_id[:8]} at={self.created_at}>"
