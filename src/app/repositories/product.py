"""
Repositorio para Product.
"""

from datetime import datetime, timedelta, UTC
from uuid import UUID

from sqlalchemy import cast, func, or_, select
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Product
from app.models.product import PriceRange, ProductAvailability, ProductPlatform
from app.repositories.base import BaseRepository


class ProductRepository(BaseRepository[Product]):
    """Repositorio com operacoes especificas de Product."""

    def __init__(self, db: AsyncSession):
        super().__init__(Product, db)

    async def get_all_active(self) -> list[Product]:
        """
        Lista todos os produtos ativos (disponiveis).

        Usado para selecao de produtos em formularios do admin.

        Returns:
            Lista de todos os produtos disponiveis, ordenados por nome
        """
        result = await self.db.execute(
            select(Product)
            .where(Product.availability == ProductAvailability.AVAILABLE)
            .order_by(Product.name)
        )
        return list(result.scalars().all())

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

        Busca em: name, short_description, platform_product_id.
        """
        search_term = f"%{query.lower()}%"
        stmt = (
            select(Product)
            .where(
                func.lower(Product.name).like(search_term)
                | func.lower(Product.short_description).like(search_term)
                | func.lower(Product.platform_product_id).like(search_term)
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
                | func.lower(Product.platform_product_id).like(search_term)
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
        # Busca produtos onde a categoria esta na lista de categorias
        # Usa operador @> do JSONB com cast explicito para evitar erro de tipo
        category_json = cast([category_slug], JSONB)
        stmt = (
            select(Product)
            .where(Product.categories.op("@>")(category_json))
            .where(Product.availability == ProductAvailability.AVAILABLE)
            .order_by(Product.internal_score.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def count_by_category(self, category_slug: str) -> int:
        """Conta produtos de uma categoria."""
        # Usa operador @> do JSONB com cast explicito para evitar erro de tipo
        category_json = cast([category_slug], JSONB)
        stmt = (
            select(func.count())
            .select_from(Product)
            .where(Product.categories.op("@>")(category_json))
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

    async def get_by_max_price(
        self,
        max_price: float,
        skip: int = 0,
        limit: int = 20,
    ) -> list[Product]:
        """
        Busca produtos disponiveis ate um preco maximo.

        Args:
            max_price: Preco maximo em reais
            skip: Offset para paginacao
            limit: Limite de resultados

        Returns:
            Lista de produtos com preco ate o valor especificado
        """
        stmt = (
            select(Product)
            .where(
                Product.availability == ProductAvailability.AVAILABLE,
                Product.price.isnot(None),
                Product.price <= max_price,
            )
            .order_by(Product.price.asc(), Product.internal_score.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def count_by_max_price(self, max_price: float) -> int:
        """
        Conta produtos disponiveis ate um preco maximo.

        Args:
            max_price: Preco maximo em reais

        Returns:
            Quantidade de produtos
        """
        stmt = (
            select(func.count())
            .select_from(Product)
            .where(
                Product.availability == ProductAvailability.AVAILABLE,
                Product.price.isnot(None),
                Product.price <= max_price,
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one()

    # ==========================================================================
    # Metodos para controle de posts em redes sociais (Instagram, TikTok, etc)
    # ==========================================================================

    async def get_random_for_posting(
        self,
        days_since_last_post: int = 30,
        availability: ProductAvailability = ProductAvailability.AVAILABLE,
    ) -> Product | None:
        """
        Busca produto aleatorio elegivel para posting em redes sociais.

        Criterios de selecao:
        - Esta disponivel (availability = available)
        - Tem imagem principal (main_image_url nao nulo)
        - Nao foi postado nos ultimos X dias (ou nunca foi postado)
        - Prioriza produtos menos postados (post_count mais baixo)
        - Aleatorio entre os menos postados

        Args:
            days_since_last_post: Dias minimos desde o ultimo post (default: 30)
            availability: Status de disponibilidade requerido

        Returns:
            Produto elegivel ou None se nao houver produtos disponiveis
        """
        cutoff_date = datetime.now(UTC) - timedelta(days=days_since_last_post)

        stmt = (
            select(Product)
            .where(Product.availability == availability)
            .where(Product.main_image_url.isnot(None))
            .where(
                or_(
                    Product.last_post_date.is_(None),
                    Product.last_post_date < cutoff_date
                )
            )
            .order_by(Product.post_count.asc(), func.random())
            .limit(1)
        )

        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def mark_as_posted(
        self,
        product_id: UUID,
        platform: str,
        post_url: str | None = None,
    ) -> Product:
        """
        Marca produto como postado em uma rede social.

        Atualiza:
        - last_post_date: Data/hora atual
        - post_count: Incrementa em 1
        - last_post_platform: Plataforma usada (instagram, tiktok, etc)
        - last_post_url: URL do post publicado (opcional)

        Args:
            product_id: UUID do produto
            platform: Nome da plataforma (ex: "instagram", "tiktok")
            post_url: URL do post publicado (opcional)

        Returns:
            Produto atualizado

        Raises:
            ValueError: Se produto nao for encontrado
        """
        product = await self.get(product_id)
        if not product:
            raise ValueError("Produto nao encontrado")

        product.last_post_date = datetime.now(UTC)
        product.post_count = (product.post_count or 0) + 1
        product.last_post_platform = platform
        product.last_post_url = post_url

        await self.db.commit()
        await self.db.refresh(product)
        return product

    async def count_available_for_posting(
        self,
        days_since_last_post: int = 30,
    ) -> int:
        """
        Conta quantos produtos estao elegiveis para posting.

        Args:
            days_since_last_post: Dias minimos desde o ultimo post

        Returns:
            Quantidade de produtos elegiveis
        """
        cutoff_date = datetime.now(UTC) - timedelta(days=days_since_last_post)

        stmt = (
            select(func.count())
            .select_from(Product)
            .where(Product.availability == ProductAvailability.AVAILABLE)
            .where(Product.main_image_url.isnot(None))
            .where(
                or_(
                    Product.last_post_date.is_(None),
                    Product.last_post_date < cutoff_date
                )
            )
        )

        result = await self.db.execute(stmt)
        return result.scalar_one()
