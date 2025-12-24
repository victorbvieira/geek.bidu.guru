"""
Modelo de Inscricao em Newsletter.

Registra emails cadastrados para newsletter com suporte a double opt-in.
O fluxo é:
1. Usuario se inscreve -> email_verified=False, verification_token gerado
2. Usuario clica no link de confirmacao -> email_verified=True, token removido
3. Apenas inscritos verificados (email_verified=True E is_active=True) recebem newsletter
"""

import secrets
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import Boolean, DateTime, Index, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.models.base import UUIDMixin, utc_now


def generate_verification_token() -> str:
    """Gera um token seguro para verificacao de email."""
    return secrets.token_urlsafe(32)


class NewsletterSignup(Base, UUIDMixin):
    """
    Inscricao em newsletter com double opt-in.

    Atributos:
        id: UUID primary key
        email: Email do inscrito (unico)
        name: Nome do inscrito (opcional)
        session_id: ID da sessao de origem
        source: Fonte da inscricao (homepage, post, popup)
        is_active: Se a inscricao esta ativa (pode receber emails)
        email_verified: Se o email foi verificado (double opt-in)
        verification_token: Token para verificacao de email
        verification_sent_at: Quando o email de verificacao foi enviado
        verified_at: Quando o email foi verificado
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

    # Verificacao de email (double opt-in)
    email_verified: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default="false"
    )
    verification_token: Mapped[Optional[str]] = mapped_column(
        String(64), nullable=True, index=True
    )
    verification_sent_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    verified_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

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
        Index("idx_newsletter_verified", "email_verified"),
    )

    def __repr__(self) -> str:
        status = "verified" if self.email_verified else "pending"
        if not self.is_active:
            status = "inactive"
        return f"<NewsletterSignup {self.email} ({status})>"

    def generate_verification_token(self) -> str:
        """
        Gera e armazena um novo token de verificacao.

        Returns:
            Token gerado (para uso na URL)
        """
        self.verification_token = generate_verification_token()
        self.verification_sent_at = utc_now()
        return self.verification_token

    def verify_email(self) -> None:
        """Marca o email como verificado."""
        self.email_verified = True
        self.verified_at = utc_now()
        self.verification_token = None  # Remove token apos uso

    def is_token_expired(self, expire_hours: int = 48) -> bool:
        """
        Verifica se o token de verificacao expirou.

        Args:
            expire_hours: Horas ate expiracao do token

        Returns:
            True se expirado ou sem token, False se valido
        """
        if not self.verification_sent_at:
            return True

        expiration_time = self.verification_sent_at + timedelta(hours=expire_hours)
        return utc_now() > expiration_time

    def unsubscribe(self) -> None:
        """Marca a inscricao como cancelada."""
        self.is_active = False
        self.unsubscribed_at = utc_now()
