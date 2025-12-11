"""
Repositorio para AffiliateClick.
"""

from datetime import datetime, timedelta
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import AffiliateClick
from app.repositories.base import BaseRepository


class ClickRepository(BaseRepository[AffiliateClick]):
    """Repositorio com operacoes especificas de AffiliateClick."""

    def __init__(self, db: AsyncSession):
        super().__init__(AffiliateClick, db)

    async def get_by_product(
        self, product_id: UUID, skip: int = 0, limit: int = 100
    ) -> list[AffiliateClick]:
        """Lista cliques por produto."""
        result = await self.db.execute(
            select(AffiliateClick)
            .where(AffiliateClick.product_id == product_id)
            .order_by(AffiliateClick.clicked_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def count_by_product(self, product_id: UUID) -> int:
        """Conta cliques de um produto."""
        result = await self.db.execute(
            select(func.count())
            .select_from(AffiliateClick)
            .where(AffiliateClick.product_id == product_id)
        )
        return result.scalar_one()

    async def count_by_product_period(
        self, product_id: UUID, days: int = 30
    ) -> int:
        """Conta cliques de um produto nos ultimos N dias."""
        since = datetime.utcnow() - timedelta(days=days)
        result = await self.db.execute(
            select(func.count())
            .select_from(AffiliateClick)
            .where(
                AffiliateClick.product_id == product_id,
                AffiliateClick.clicked_at >= since,
            )
        )
        return result.scalar_one()

    async def get_clicks_by_day(
        self, product_id: UUID | None = None, days: int = 30
    ) -> list[dict]:
        """Agrupa cliques por dia."""
        since = datetime.utcnow() - timedelta(days=days)

        query = select(
            func.date(AffiliateClick.clicked_at).label("date"),
            func.count().label("clicks"),
        ).where(AffiliateClick.clicked_at >= since)

        if product_id:
            query = query.where(AffiliateClick.product_id == product_id)

        query = query.group_by(func.date(AffiliateClick.clicked_at)).order_by(
            func.date(AffiliateClick.clicked_at)
        )

        result = await self.db.execute(query)
        return [{"date": str(row.date), "clicks": row.clicks} for row in result]

    async def get_top_products(self, days: int = 30, limit: int = 10) -> list[dict]:
        """Lista produtos mais clicados no periodo."""
        since = datetime.utcnow() - timedelta(days=days)

        result = await self.db.execute(
            select(
                AffiliateClick.product_id,
                func.count().label("clicks"),
            )
            .where(AffiliateClick.clicked_at >= since)
            .group_by(AffiliateClick.product_id)
            .order_by(func.count().desc())
            .limit(limit)
        )
        return [
            {"product_id": str(row.product_id), "clicks": row.clicks}
            for row in result
        ]
