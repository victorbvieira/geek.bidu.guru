"""
Repositorio para NewsletterSignup.
"""

from datetime import datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import NewsletterSignup
from app.repositories.base import BaseRepository


class NewsletterRepository(BaseRepository[NewsletterSignup]):
    """Repositorio com operacoes especificas de NewsletterSignup."""

    def __init__(self, db: AsyncSession):
        super().__init__(NewsletterSignup, db)

    async def get_by_email(self, email: str) -> NewsletterSignup | None:
        """Busca inscricao por email."""
        result = await self.db.execute(
            select(NewsletterSignup).where(NewsletterSignup.email == email)
        )
        return result.scalar_one_or_none()

    async def email_exists(self, email: str) -> bool:
        """Verifica se email ja esta inscrito."""
        signup = await self.get_by_email(email)
        return signup is not None

    async def get_active_subscribers(
        self, skip: int = 0, limit: int = 100
    ) -> list[NewsletterSignup]:
        """Lista inscritos ativos."""
        result = await self.db.execute(
            select(NewsletterSignup)
            .where(NewsletterSignup.is_active == True)  # noqa: E712
            .order_by(NewsletterSignup.subscribed_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def count_active(self) -> int:
        """Conta inscritos ativos."""
        result = await self.db.execute(
            select(func.count())
            .select_from(NewsletterSignup)
            .where(NewsletterSignup.is_active == True)  # noqa: E712
        )
        return result.scalar_one()

    async def unsubscribe(self, email: str) -> NewsletterSignup | None:
        """Desinscreve por email."""
        signup = await self.get_by_email(email)
        if signup:
            signup.is_active = False
            signup.unsubscribed_at = datetime.utcnow()
            await self.db.commit()
            await self.db.refresh(signup)
        return signup

    async def resubscribe(self, email: str) -> NewsletterSignup | None:
        """Reinscreve por email."""
        signup = await self.get_by_email(email)
        if signup:
            signup.is_active = True
            signup.unsubscribed_at = None
            await self.db.commit()
            await self.db.refresh(signup)
        return signup

    async def get_stats(self) -> dict:
        """Retorna estatisticas de newsletter."""
        now = datetime.utcnow()
        today = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_ago = now - timedelta(days=7)
        month_ago = now - timedelta(days=30)

        total = await self.count()
        active = await self.count_active()

        # Inscricoes hoje
        result = await self.db.execute(
            select(func.count())
            .select_from(NewsletterSignup)
            .where(NewsletterSignup.subscribed_at >= today)
        )
        today_count = result.scalar_one()

        # Inscricoes na semana
        result = await self.db.execute(
            select(func.count())
            .select_from(NewsletterSignup)
            .where(NewsletterSignup.subscribed_at >= week_ago)
        )
        week_count = result.scalar_one()

        # Inscricoes no mes
        result = await self.db.execute(
            select(func.count())
            .select_from(NewsletterSignup)
            .where(NewsletterSignup.subscribed_at >= month_ago)
        )
        month_count = result.scalar_one()

        return {
            "total_subscribers": total,
            "active_subscribers": active,
            "unsubscribed": total - active,
            "subscriptions_today": today_count,
            "subscriptions_week": week_count,
            "subscriptions_month": month_count,
        }
