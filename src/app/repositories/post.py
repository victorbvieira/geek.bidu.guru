"""
Repositorio para Post.
"""

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Post
from app.models.post import PostStatus, PostType
from app.models.post_product import PostProduct
from app.repositories.base import BaseRepository


class PostRepository(BaseRepository[Post]):
    """Repositorio com operacoes especificas de Post."""

    def __init__(self, db: AsyncSession):
        super().__init__(Post, db)

    async def get_by_slug(self, slug: str) -> Post | None:
        """Busca post por slug."""
        result = await self.db.execute(
            select(Post).where(Post.slug == slug)
        )
        return result.scalar_one_or_none()

    async def get_with_relations(self, id: UUID) -> Post | None:
        """Busca post com category e author carregados."""
        result = await self.db.execute(
            select(Post)
            .where(Post.id == id)
            .options(
                selectinload(Post.category),
                selectinload(Post.author),
            )
        )
        return result.scalar_one_or_none()

    async def get_published(
        self,
        skip: int = 0,
        limit: int = 20,
        category_id: UUID | None = None,
        post_type: PostType | None = None,
    ) -> list[Post]:
        """Lista posts publicados."""
        query = select(Post).where(
            Post.status == PostStatus.PUBLISHED,
            Post.publish_at <= datetime.now(UTC),
        )

        if category_id:
            query = query.where(Post.category_id == category_id)

        if post_type:
            query = query.where(Post.type == post_type)

        query = query.order_by(Post.publish_at.desc()).offset(skip).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def count_published(
        self,
        category_id: UUID | None = None,
        post_type: PostType | None = None,
    ) -> int:
        """Conta posts publicados."""
        query = select(func.count()).select_from(Post).where(
            Post.status == PostStatus.PUBLISHED,
            Post.publish_at <= datetime.now(UTC),
        )

        if category_id:
            query = query.where(Post.category_id == category_id)

        if post_type:
            query = query.where(Post.type == post_type)

        result = await self.db.execute(query)
        return result.scalar_one()

    async def get_by_status(
        self, status: PostStatus, skip: int = 0, limit: int = 20
    ) -> list[Post]:
        """Lista posts por status."""
        result = await self.db.execute(
            select(Post)
            .where(Post.status == status)
            .order_by(Post.updated_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def increment_view_count(self, id: UUID) -> None:
        """Incrementa contador de views."""
        post = await self.get(id)
        if post:
            post.view_count = (post.view_count or 0) + 1
            await self.db.commit()

    async def increment_click_count(self, id: UUID) -> None:
        """Incrementa contador de cliques."""
        post = await self.get(id)
        if post:
            post.click_count = (post.click_count or 0) + 1
            await self.db.commit()

    async def slug_exists(self, slug: str, exclude_id: UUID | None = None) -> bool:
        """Verifica se slug ja existe."""
        query = select(Post).where(Post.slug == slug)
        if exclude_id:
            query = query.where(Post.id != exclude_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none() is not None

    async def search(
        self,
        query: str,
        skip: int = 0,
        limit: int = 20,
    ) -> list[Post]:
        """
        Busca posts publicados por termo.

        Busca em: title, subtitle, content, seo_focus_keyword.
        Retorna apenas posts publicados.
        """
        search_term = f"%{query.lower()}%"
        stmt = (
            select(Post)
            .where(
                Post.status == PostStatus.PUBLISHED,
                Post.publish_at <= datetime.now(UTC),
            )
            .where(
                func.lower(Post.title).like(search_term)
                | func.lower(Post.subtitle).like(search_term)
                | func.lower(Post.content).like(search_term)
                | func.lower(Post.seo_focus_keyword).like(search_term)
            )
            .order_by(Post.publish_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def count_search(self, query: str) -> int:
        """Conta resultados de busca."""
        search_term = f"%{query.lower()}%"
        stmt = (
            select(func.count())
            .select_from(Post)
            .where(
                Post.status == PostStatus.PUBLISHED,
                Post.publish_at <= datetime.now(UTC),
            )
            .where(
                func.lower(Post.title).like(search_term)
                | func.lower(Post.subtitle).like(search_term)
                | func.lower(Post.content).like(search_term)
                | func.lower(Post.seo_focus_keyword).like(search_term)
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one()

    # -------------------------------------------------------------------------
    # Gerenciamento de Produtos vinculados (PostProduct)
    # -------------------------------------------------------------------------

    async def get_post_products(self, post_id: UUID) -> list[PostProduct]:
        """Busca produtos vinculados a um post, ordenados por posicao."""
        result = await self.db.execute(
            select(PostProduct)
            .where(PostProduct.post_id == post_id)
            .order_by(PostProduct.position)
        )
        return list(result.scalars().all())

    async def get_post_product_ids(self, post_id: UUID) -> list[UUID]:
        """Retorna lista de IDs de produtos vinculados a um post."""
        result = await self.db.execute(
            select(PostProduct.product_id)
            .where(PostProduct.post_id == post_id)
            .order_by(PostProduct.position)
        )
        return list(result.scalars().all())

    async def set_post_products(
        self, post_id: UUID, product_ids: list[UUID]
    ) -> None:
        """
        Define os produtos vinculados a um post.

        Remove vinculos antigos e cria novos na ordem fornecida.
        """
        from sqlalchemy import delete

        # Remove vinculos antigos
        await self.db.execute(
            delete(PostProduct).where(PostProduct.post_id == post_id)
        )

        # Cria novos vinculos com posicao
        for position, product_id in enumerate(product_ids):
            post_product = PostProduct(
                post_id=post_id,
                product_id=product_id,
                position=position,
            )
            self.db.add(post_product)

        await self.db.commit()

    async def add_product_to_post(
        self, post_id: UUID, product_id: UUID, position: int | None = None
    ) -> PostProduct:
        """Adiciona um produto a um post."""
        # Se posicao nao fornecida, adiciona no final
        if position is None:
            result = await self.db.execute(
                select(func.coalesce(func.max(PostProduct.position), -1) + 1)
                .where(PostProduct.post_id == post_id)
            )
            position = result.scalar_one()

        post_product = PostProduct(
            post_id=post_id,
            product_id=product_id,
            position=position,
        )
        self.db.add(post_product)
        await self.db.commit()
        await self.db.refresh(post_product)
        return post_product

    async def remove_product_from_post(
        self, post_id: UUID, product_id: UUID
    ) -> bool:
        """Remove um produto de um post."""
        from sqlalchemy import delete

        result = await self.db.execute(
            delete(PostProduct).where(
                PostProduct.post_id == post_id,
                PostProduct.product_id == product_id,
            )
        )
        await self.db.commit()
        return result.rowcount > 0
