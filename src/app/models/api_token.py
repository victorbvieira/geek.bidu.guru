"""
Modelo de API Token para autenticação de longa duração.

Permite que usuários (especialmente os de role `automation`) tenham tokens
persistentes para acessar a API sem dependerem do fluxo JWT login/refresh,
que tem expiração curta (24h access, 7d refresh).

Cada token tem:
- Um valor completo no formato `pcat_<32_hex_chars>` (44 chars, 128 bits de entropia)
- Apenas o `token_hash` (sha256) é armazenado no banco — o valor completo
  é retornado UMA VEZ na criação e nunca mais pode ser recuperado
- Um `token_prefix` (primeiros caracteres) é armazenado em claro para
  identificação na UI/auditoria sem expor o token
- `expires_at` opcional (None = não expira)
- `revoked_at` para soft revoke (mantém audit trail)

Uso na autenticação: cliente envia `Authorization: Bearer pcat_<token>`.
O `get_current_user` detecta pelo prefixo `pcat_` e valida via hash.
"""

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.user import User


class ApiToken(Base, UUIDMixin, TimestampMixin):
    """API Token de longa duração para autenticação fora do fluxo JWT padrão."""

    __tablename__ = "api_tokens"

    user_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    token_hash: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    token_prefix: Mapped[str] = mapped_column(String(16), nullable=False)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_by_user_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    user: Mapped["User"] = relationship("User", foreign_keys=[user_id], lazy="selectin")

    __table_args__ = (
        Index("idx_api_tokens_user", "user_id"),
        Index("idx_api_tokens_hash", "token_hash"),
        Index("idx_api_tokens_active", "user_id", "revoked_at"),
    )

    def __repr__(self) -> str:
        return f"<ApiToken {self.token_prefix}... user={self.user_id}>"
