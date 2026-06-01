"""
Repositório para ApiToken.
"""

from datetime import datetime
from uuid import UUID

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.api_token import ApiToken
from app.repositories.base import BaseRepository


class ApiTokenRepository(BaseRepository[ApiToken]):
    """Repositório com operações específicas de ApiToken."""

    def __init__(self, db: AsyncSession):
        super().__init__(ApiToken, db)

    async def get_by_hash(self, token_hash: str) -> ApiToken | None:
        """Busca token pelo hash sha256 (usado na autenticação)."""
        result = await self.db.execute(
            select(ApiToken).where(ApiToken.token_hash == token_hash)
        )
        return result.scalar_one_or_none()

    async def list_by_user(self, user_id: UUID, include_revoked: bool = False) -> list[ApiToken]:
        """Lista tokens de um usuário (mais recentes primeiro)."""
        stmt = select(ApiToken).where(ApiToken.user_id == user_id)
        if not include_revoked:
            stmt = stmt.where(ApiToken.revoked_at.is_(None))
        stmt = stmt.order_by(ApiToken.created_at.desc())
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def count_by_user(self, user_id: UUID, include_revoked: bool = False) -> int:
        """Conta tokens de um usuário."""
        stmt = select(func.count()).select_from(ApiToken).where(ApiToken.user_id == user_id)
        if not include_revoked:
            stmt = stmt.where(ApiToken.revoked_at.is_(None))
        result = await self.db.execute(stmt)
        return result.scalar_one()

    async def mark_used(self, token_id: UUID, now: datetime) -> None:
        """Atualiza last_used_at do token (chamado após auth bem-sucedida)."""
        await self.db.execute(
            update(ApiToken).where(ApiToken.id == token_id).values(last_used_at=now)
        )
        await self.db.commit()

    async def revoke(self, token_id: UUID, now: datetime) -> bool:
        """Revoga token (soft — preserva audit trail). Retorna True se algo mudou."""
        result = await self.db.execute(
            update(ApiToken)
            .where(ApiToken.id == token_id, ApiToken.revoked_at.is_(None))
            .values(revoked_at=now)
        )
        await self.db.commit()
        return result.rowcount > 0
