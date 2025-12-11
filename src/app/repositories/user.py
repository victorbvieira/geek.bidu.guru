"""
Repositorio para User.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """Repositorio com operacoes especificas de User."""

    def __init__(self, db: AsyncSession):
        super().__init__(User, db)

    async def get_by_email(self, email: str) -> User | None:
        """Busca usuario por email."""
        result = await self.db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()

    async def get_active_users(
        self, skip: int = 0, limit: int = 100
    ) -> list[User]:
        """Lista apenas usuarios ativos."""
        result = await self.db.execute(
            select(User)
            .where(User.is_active == True)  # noqa: E712
            .order_by(User.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def email_exists(self, email: str) -> bool:
        """Verifica se email ja esta cadastrado."""
        user = await self.get_by_email(email)
        return user is not None
