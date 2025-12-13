"""
Repositorio para Category.
"""

from uuid import UUID

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Category
from app.repositories.base import BaseRepository


class CategoryRepository(BaseRepository[Category]):
    """Repositorio com operacoes especificas de Category."""

    def __init__(self, db: AsyncSession):
        super().__init__(Category, db)

    async def search(
        self,
        query: str,
        skip: int = 0,
        limit: int = 20,
    ) -> list[Category]:
        """
        Busca categorias por nome ou descricao.

        Args:
            query: Termo de busca
            skip: Offset para paginacao
            limit: Limite de resultados

        Returns:
            Lista de categorias que correspondem a busca
        """
        search_term = f"%{query}%"
        result = await self.db.execute(
            select(Category)
            .where(
                or_(
                    Category.name.ilike(search_term),
                    Category.slug.ilike(search_term),
                    Category.description.ilike(search_term),
                )
            )
            .order_by(Category.name)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def count_search(self, query: str) -> int:
        """
        Conta total de categorias que correspondem a busca.

        Args:
            query: Termo de busca

        Returns:
            Total de categorias encontradas
        """
        search_term = f"%{query}%"
        result = await self.db.execute(
            select(func.count(Category.id)).where(
                or_(
                    Category.name.ilike(search_term),
                    Category.slug.ilike(search_term),
                    Category.description.ilike(search_term),
                )
            )
        )
        return result.scalar_one()

    async def get_paginated(
        self,
        skip: int = 0,
        limit: int = 20,
    ) -> list[Category]:
        """
        Lista categorias com paginacao.

        Args:
            skip: Offset para paginacao
            limit: Limite de resultados

        Returns:
            Lista de categorias
        """
        result = await self.db.execute(
            select(Category)
            .order_by(Category.name)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

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
