"""
Repositorio para Category.
"""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Category
from app.repositories.base import BaseRepository


class CategoryRepository(BaseRepository[Category]):
    """Repositorio com operacoes especificas de Category."""

    def __init__(self, db: AsyncSession):
        super().__init__(Category, db)

    async def get_by_slug(self, slug: str) -> Category | None:
        """Busca categoria por slug."""
        result = await self.db.execute(
            select(Category).where(Category.slug == slug)
        )
        return result.scalar_one_or_none()

    async def get_all(self) -> list[Category]:
        """Lista todas as categorias ordenadas por nome."""
        result = await self.db.execute(
            select(Category).order_by(Category.name)
        )
        return list(result.scalars().all())

    async def get_root_categories(self) -> list[Category]:
        """Lista categorias raiz (sem parent)."""
        result = await self.db.execute(
            select(Category)
            .where(Category.parent_id == None)  # noqa: E711
            .order_by(Category.name)
        )
        return list(result.scalars().all())

    async def get_children(self, parent_id: UUID) -> list[Category]:
        """Lista subcategorias de uma categoria."""
        result = await self.db.execute(
            select(Category)
            .where(Category.parent_id == parent_id)
            .order_by(Category.name)
        )
        return list(result.scalars().all())

    async def slug_exists(self, slug: str, exclude_id: UUID | None = None) -> bool:
        """Verifica se slug ja existe."""
        query = select(Category).where(Category.slug == slug)
        if exclude_id:
            query = query.where(Category.id != exclude_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none() is not None
