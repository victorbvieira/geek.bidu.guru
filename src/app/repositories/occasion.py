"""
Repositorio para Occasion.
"""

from uuid import UUID

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Occasion
from app.repositories.base import BaseRepository


class OccasionRepository(BaseRepository[Occasion]):
    """Repositorio com operacoes especificas de Occasion."""

    def __init__(self, db: AsyncSession):
        super().__init__(Occasion, db)

    async def get_by_slug(self, slug: str) -> Occasion | None:
        """Busca ocasiao por slug."""
        result = await self.db.execute(
            select(Occasion).where(Occasion.slug == slug)
        )
        return result.scalar_one_or_none()

    async def get_active(
        self,
        skip: int = 0,
        limit: int = 20,
    ) -> list[Occasion]:
        """Lista ocasioes ativas ordenadas por display_order."""
        result = await self.db.execute(
            select(Occasion)
            .where(Occasion.is_active == True)  # noqa: E712
            .order_by(Occasion.display_order, Occasion.name)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def count_active(self) -> int:
        """Conta ocasioes ativas."""
        result = await self.db.execute(
            select(func.count())
            .select_from(Occasion)
            .where(Occasion.is_active == True)  # noqa: E712
        )
        return result.scalar_one()

    async def get_all_ordered(self) -> list[Occasion]:
        """Lista todas as ocasioes ordenadas por display_order."""
        result = await self.db.execute(
            select(Occasion)
            .order_by(Occasion.display_order, Occasion.name)
        )
        return list(result.scalars().all())

    async def get_paginated(
        self,
        skip: int = 0,
        limit: int = 20,
    ) -> list[Occasion]:
        """Lista ocasioes com paginacao."""
        result = await self.db.execute(
            select(Occasion)
            .order_by(Occasion.display_order, Occasion.name)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def search(
        self,
        query: str,
        skip: int = 0,
        limit: int = 20,
    ) -> list[Occasion]:
        """Busca ocasioes por nome, slug ou descricao."""
        search_term = f"%{query}%"
        result = await self.db.execute(
            select(Occasion)
            .where(
                or_(
                    Occasion.name.ilike(search_term),
                    Occasion.slug.ilike(search_term),
                    Occasion.description.ilike(search_term),
                )
            )
            .order_by(Occasion.display_order, Occasion.name)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def count_search(self, query: str) -> int:
        """Conta resultados de busca."""
        search_term = f"%{query}%"
        result = await self.db.execute(
            select(func.count())
            .select_from(Occasion)
            .where(
                or_(
                    Occasion.name.ilike(search_term),
                    Occasion.slug.ilike(search_term),
                    Occasion.description.ilike(search_term),
                )
            )
        )
        return result.scalar_one()

    async def slug_exists(self, slug: str, exclude_id: UUID | None = None) -> bool:
        """Verifica se slug ja existe."""
        query = select(Occasion).where(Occasion.slug == slug)
        if exclude_id:
            query = query.where(Occasion.id != exclude_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none() is not None
