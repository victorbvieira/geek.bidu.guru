"""
Repositorio para Session.
"""

from datetime import datetime, timedelta
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Session
from app.models.session import DeviceType
from app.repositories.base import BaseRepository


class SessionRepository(BaseRepository[Session]):
    """Repositorio com operacoes especificas de Session."""

    def __init__(self, db: AsyncSession):
        super().__init__(Session, db)

    async def get_by_session_id(self, session_id: str) -> Session | None:
        """Busca por session_id."""
        result = await self.db.execute(
            select(Session).where(Session.session_id == session_id)
        )
        return result.scalar_one_or_none()

    async def get_by_post(
        self, post_id: UUID, skip: int = 0, limit: int = 100
    ) -> list[Session]:
        """Lista sessoes por post."""
        result = await self.db.execute(
            select(Session)
            .where(Session.post_id == post_id)
            .order_by(Session.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def count_unique_visitors(self, days: int = 30) -> int:
        """Conta visitantes unicos no periodo."""
        since = datetime.utcnow() - timedelta(days=days)
        result = await self.db.execute(
            select(func.count(func.distinct(Session.session_id))).where(
                Session.created_at >= since
            )
        )
        return result.scalar_one()

    async def count_new_users(self, days: int = 30) -> int:
        """Conta novos usuarios no periodo."""
        since = datetime.utcnow() - timedelta(days=days)
        result = await self.db.execute(
            select(func.count())
            .select_from(Session)
            .where(
                Session.created_at >= since,
                Session.is_new_user == True,  # noqa: E712
            )
        )
        return result.scalar_one()

    async def get_by_device_type(self, days: int = 30) -> list[dict]:
        """Agrupa sessoes por tipo de dispositivo."""
        since = datetime.utcnow() - timedelta(days=days)

        result = await self.db.execute(
            select(
                Session.device_type,
                func.count().label("count"),
            )
            .where(Session.created_at >= since)
            .group_by(Session.device_type)
        )

        total = sum(row.count for row in result)
        return [
            {
                "device_type": row.device_type.value if row.device_type else "unknown",
                "count": row.count,
                "percentage": round(row.count / total * 100, 2) if total > 0 else 0,
            }
            for row in result
        ]

    async def get_avg_engagement(self, post_id: UUID | None = None) -> dict:
        """Calcula media de engajamento."""
        query = select(
            func.avg(Session.time_on_page).label("avg_time"),
            func.avg(Session.scroll_depth).label("avg_scroll"),
        )

        if post_id:
            query = query.where(Session.post_id == post_id)

        result = await self.db.execute(query)
        row = result.one()

        return {
            "avg_time_on_page": round(float(row.avg_time or 0), 2),
            "avg_scroll_depth": round(float(row.avg_scroll or 0), 2),
        }
