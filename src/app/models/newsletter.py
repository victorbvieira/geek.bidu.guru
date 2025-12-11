"""
Modelo de Inscricao em Newsletter.

Registra emails cadastrados para newsletter.
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, Index, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.models.base import UUIDMixin, utc_now


class NewsletterSignup(Base, UUIDMixin):
    """
    Inscricao em newsletter.

    Atributos:
        id: UUID primary key
        email: Email do inscrito (unico)
        name: Nome do inscrito (opcional)
        session_id: ID da sessao de origem
        source: Fonte da inscricao (homepage, post, popup)
        is_active: Se a inscricao esta ativa
        subscribed_at: Data de inscricao
        unsubscribed_at: Data de cancelamento (se houver)
    """

    __tablename__ = "newsletter_signups"

    # Campos principais
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    name: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)

    # Origem
    session_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    source: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")

    # Timestamps
    subscribed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        default=utc_now,
    )
    unsubscribed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Indices
    __table_args__ = (
        Index("idx_newsletter_email", "email"),
        Index("idx_newsletter_active", "is_active"),
        Index("idx_newsletter_subscribed_at", "subscribed_at"),
    )

    def __repr__(self) -> str:
        status = "active" if self.is_active else "inactive"
        return f"<NewsletterSignup {self.email} ({status})>"

    def unsubscribe(self) -> None:
        """Marca a inscricao como cancelada."""
        self.is_active = False
        self.unsubscribed_at = utc_now()
