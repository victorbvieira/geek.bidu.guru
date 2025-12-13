"""
Repositorio para Product.
"""

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Product
from app.models.product import PriceRange, ProductAvailability, ProductPlatform
from app.repositories.base import BaseRepository


class ProductRepository(BaseRepository[Product]):
    """Repositorio com operacoes especificas de Product."""

    def __init__(self, db: AsyncSession):
        super().__init__(Product, db)

    async def get_by_slug(self, slug: str) -> Product | None:
        """Busca produto por slug."""
        result = await self.db.execute(
            select(Product).where(Product.slug == slug)
        )
        return result.scalar_one_or_none()

    async def get_by_redirect_slug(self, redirect_slug: str) -> Product | None:
        """Busca produto por slug de redirect (para cliques)."""
        result = await self.db.execute(
            select(Product).where(Product.affiliate_redirect_slug == redirect_slug)
        )
        return result.scalar_one_or_none()

    async def get_available(
        self,
        skip: int = 0,
        limit: int = 20,
        platform: ProductPlatform | None = None,
        price_range: PriceRange | None = None,
    ) -> list[Product]:
        """Lista produtos disponiveis."""
        query = select(Product).where(
            Product.availability == ProductAvailability.AVAILABLE
        )

        if platform:
            query = query.where(Product.platform == platform)

        if price_range:
            query = query.where(Product.price_range == price_range)

        query = query.order_by(Product.internal_score.desc()).offset(skip).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_top_clicked(self, limit: int = 10) -> list[Product]:
        """Lista produtos mais clicados."""
        result = await self.db.execute(
            select(Product)
            .where(Product.availability == ProductAvailability.AVAILABLE)
            .order_by(Product.click_count.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_by_platform(
        self, platform: ProductPlatform, skip: int = 0, limit: int = 20
    ) -> list[Product]:
        """Lista produtos por plataforma."""
        result = await self.db.execute(
            select(Product)
            .where(Product.platform == platform)
            .order_by(Product.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def increment_click_count(self, id: UUID) -> None:
        """Incrementa contador de cliques."""
        product = await self.get(id)
        if product:
            product.click_count = (product.click_count or 0) + 1
            await self.db.commit()

    async def update_availability(
        self, id: UUID, availability: ProductAvailability
    ) -> Product | None:
        """Atualiza disponibilidade do produto."""
        product = await self.get(id)
        if product:
            product.availability = availability
            await self.db.commit()
            await self.db.refresh(product)
        return product

    async def slug_exists(self, slug: str, exclude_id: UUID | None = None) -> bool:
        """Verifica se slug ja existe."""
        query = select(Product).where(Product.slug == slug)
        if exclude_id:
            query = query.where(Product.id != exclude_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none() is not None

    async def redirect_slug_exists(
        self, redirect_slug: str, exclude_id: UUID | None = None
    ) -> bool:
        """Verifica se redirect_slug ja existe."""
        query = select(Product).where(
            Product.affiliate_redirect_slug == redirect_slug
        )
        if exclude_id:
            query = query.where(Product.id != exclude_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none() is not None

    async def sum_clicks(self) -> int:
        """Retorna a soma total de clicks de todos os produtos."""
        result = await self.db.execute(
            select(func.coalesce(func.sum(Product.click_count), 0))
        )
        return result.scalar() or 0

    async def search(
        self,
        query: str,
        skip: int = 0,
        limit: int = 20,
    ) -> list[Product]:
        """
        Busca produtos por termo.

        Busca em: name, short_description, tags.
        """
        search_term = f"%{query.lower()}%"
        stmt = (
            select(Product)
            .where(
                func.lower(Product.name).like(search_term)
                | func.lower(Product.short_description).like(search_term)
            )
            .order_by(Product.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def count_search(self, query: str) -> int:
        """Conta resultados de busca de produtos."""
        search_term = f"%{query.lower()}%"
        stmt = (
            select(func.count())
            .select_from(Product)
            .where(
                func.lower(Product.name).like(search_term)
                | func.lower(Product.short_description).like(search_term)
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one()

    async def get_ids_by_slugs(self, slugs: list[str]) -> list[UUID]:
        """
        Busca IDs de produtos por lista de slugs.

        Args:
            slugs: Lista de slugs de produtos

        Returns:
            Lista de UUIDs dos produtos encontrados (na ordem dos slugs)
        """
        if not slugs:
            return []

        result = await self.db.execute(
            select(Product.id, Product.slug).where(Product.slug.in_(slugs))
        )
        rows = result.all()

        # Cria mapa slug -> id
        slug_to_id = {row.slug: row.id for row in rows}

        # Retorna IDs na ordem dos slugs originais
        return [slug_to_id[slug] for slug in slugs if slug in slug_to_id]

    async def get_by_category(
        self,
        category_slug: str,
        skip: int = 0,
        limit: int = 20,
    ) -> list[Product]:
        """
        Busca produtos que pertencem a uma categoria.

        Os produtos armazenam categorias como lista de slugs em JSONB.

        Args:
            category_slug: Slug da categoria
            skip: Offset para paginacao
            limit: Limite de resultados

        Returns:
            Lista de produtos da categoria
        """
        # Busca produtos onde a categoria esta na lista de categorias (JSONB @> operator)
        stmt = (
            select(Product)
            .where(Product.categories.contains([category_slug]))
            .where(Product.availability == ProductAvailability.AVAILABLE)
            .order_by(Product.internal_score.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def count_by_category(self, category_slug: str) -> int:
        """Conta produtos de uma categoria."""
        stmt = (
            select(func.count())
            .select_from(Product)
            .where(Product.categories.contains([category_slug]))
            .where(Product.availability == ProductAvailability.AVAILABLE)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one()

    async def platform_product_exists(
        self,
        platform: ProductPlatform,
        platform_product_id: str,
        exclude_id: UUID | None = None,
    ) -> bool:
        """
        Verifica se ja existe um produto com o mesmo ID de plataforma.

        Evita duplicidade de produtos da mesma plataforma.

        Args:
            platform: Plataforma do produto
            platform_product_id: ID do produto na plataforma
            exclude_id: ID a excluir da verificacao (para updates)

        Returns:
            True se ja existe outro produto com esse ID de plataforma
        """
        if not platform_product_id:
            return False

        query = select(Product).where(
            Product.platform == platform,
            Product.platform_product_id == platform_product_id,
        )
        if exclude_id:
            query = query.where(Product.id != exclude_id)

        result = await self.db.execute(query)
        return result.scalar_one_or_none() is not None
