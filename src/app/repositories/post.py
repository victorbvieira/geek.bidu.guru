"""
Repositorio para Post.
"""

from datetime import datetime
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Post
from app.models.post import PostStatus, PostType
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
            Post.publish_at <= datetime.utcnow(),
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
            Post.publish_at <= datetime.utcnow(),
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
