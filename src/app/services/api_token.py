"""
Service de geração e validação de API Tokens.

Formato do token:
    pcat_<32_hex_chars>
    = 5 + 32 = 37 caracteres totais (legíveis, fáceis de copiar/colar)
    = 128 bits de entropia (32 hex = 16 bytes random)

Prefixo armazenado (claro): primeiros 13 chars (pcat_ + 8 hex) — suficiente
pra distinguir tokens visualmente sem expor o secret.

Hash armazenado: sha256 do token completo.
"""

import hashlib
import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from uuid import UUID

from app.models.api_token import ApiToken
from app.repositories.api_token import ApiTokenRepository

TOKEN_SCHEME = "pcat"
TOKEN_RANDOM_BYTES = 16  # 16 bytes => 32 hex chars
TOKEN_PREFIX_LENGTH = 13  # 'pcat_' + 8 hex chars


@dataclass
class GeneratedToken:
    """Resultado da geração — contém o token em CLARO (apenas aqui)."""

    record: ApiToken
    token: str  # valor completo, retornado uma única vez


def hash_token(token: str) -> str:
    """Calcula sha256 hex do token."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def is_paperclip_token(value: str) -> bool:
    """Checa se a string parece ser um API token (não JWT)."""
    return value.startswith(f"{TOKEN_SCHEME}_")


def _generate_random_token() -> tuple[str, str, str]:
    """Gera token novo. Retorna (token_completo, hash, prefixo)."""
    random_hex = secrets.token_hex(TOKEN_RANDOM_BYTES)
    token = f"{TOKEN_SCHEME}_{random_hex}"
    return token, hash_token(token), token[:TOKEN_PREFIX_LENGTH]


async def create_api_token(
    repo: ApiTokenRepository,
    *,
    user_id: UUID,
    name: str,
    expires_in_days: int | None,
    created_by_user_id: UUID | None,
) -> GeneratedToken:
    """Cria token novo para um user. Persiste apenas o hash."""
    token, token_hash, prefix = _generate_random_token()

    expires_at: datetime | None = None
    if expires_in_days is not None:
        expires_at = datetime.now(timezone.utc) + timedelta(days=expires_in_days)

    record = ApiToken(
        user_id=user_id,
        name=name,
        token_hash=token_hash,
        token_prefix=prefix,
        expires_at=expires_at,
        created_by_user_id=created_by_user_id,
    )
    record = await repo.create(record)
    return GeneratedToken(record=record, token=token)


async def validate_api_token(
    repo: ApiTokenRepository, token: str
) -> ApiToken | None:
    """
    Valida token (formato pcat_*). Retorna ApiToken ativo ou None.

    Retorna None se:
    - Formato inválido
    - Token não existe no banco (sha mismatch)
    - Foi revogado
    - Expirou
    """
    if not is_paperclip_token(token):
        return None

    record = await repo.get_by_hash(hash_token(token))
    if record is None:
        return None

    now = datetime.now(timezone.utc)
    if record.revoked_at is not None:
        return None
    if record.expires_at is not None and record.expires_at <= now:
        return None

    return record
