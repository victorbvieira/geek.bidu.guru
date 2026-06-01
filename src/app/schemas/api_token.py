"""
Schemas Pydantic para ApiToken.

Importante: o valor completo do token (`token`) só aparece em ApiTokenWithSecret,
retornado UMA VEZ na criação. Todas as outras leituras retornam apenas metadata
(via ApiTokenResponse), sem o valor — apenas o prefixo para identificação.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ApiTokenCreate(BaseModel):
    """Input para criar token novo."""

    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Descrição amigável do token (ex.: 'paperclip-agents', 'n8n-daily-cron')",
    )
    expires_in_days: int | None = Field(
        default=365,
        ge=1,
        le=3650,
        description="Validade em dias. None ou omitido = não expira (use com cuidado).",
    )


class ApiTokenResponse(BaseModel):
    """Metadata de um token. NÃO contém o valor secreto."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    name: str
    token_prefix: str = Field(
        ...,
        description="Primeiros caracteres do token, para identificação. Ex.: 'pcat_a3f1b2c4'",
    )
    expires_at: datetime | None
    last_used_at: datetime | None
    revoked_at: datetime | None
    created_at: datetime
    created_by_user_id: UUID | None


class ApiTokenWithSecret(ApiTokenResponse):
    """Resposta da criação — inclui o valor completo do token (uma única vez)."""

    token: str = Field(
        ...,
        description="Valor completo do token. Apareça APENAS na resposta da criação. "
        "Guarde imediatamente — não é possível recuperar depois.",
    )


class ApiTokenList(BaseModel):
    """Lista de tokens (sem secrets)."""

    items: list[ApiTokenResponse]
    total: int
