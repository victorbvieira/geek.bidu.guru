"""
Repositorio para NewsletterSignup.

Suporta double opt-in: inscritos precisam verificar email antes de
serem considerados ativos para receber newsletters.
"""

from datetime import UTC, datetime, timedelta
from typing import Optional

from sqlalchemy import and_, func, select
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

    async def get_by_token(self, token: str) -> NewsletterSignup | None:
        """
        Busca inscricao por token de verificacao.

        Args:
            token: Token de verificacao enviado por email

        Returns:
            NewsletterSignup se encontrado, None caso contrario
        """
        result = await self.db.execute(
            select(NewsletterSignup).where(
                NewsletterSignup.verification_token == token
            )
        )
        return result.scalar_one_or_none()

    async def email_exists(self, email: str) -> bool:
        """Verifica se email ja esta inscrito."""
        signup = await self.get_by_email(email)
        return signup is not None

    async def get_active_subscribers(
        self, skip: int = 0, limit: int = 100
    ) -> list[NewsletterSignup]:
        """Lista inscritos ativos E verificados (prontos para receber newsletter)."""
        result = await self.db.execute(
            select(NewsletterSignup)
            .where(
                and_(
                    NewsletterSignup.is_active == True,  # noqa: E712
                    NewsletterSignup.email_verified == True,  # noqa: E712
                )
            )
            .order_by(NewsletterSignup.subscribed_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_pending_verification(
        self, skip: int = 0, limit: int = 100
    ) -> list[NewsletterSignup]:
        """Lista inscritos que ainda nao verificaram o email."""
        result = await self.db.execute(
            select(NewsletterSignup)
            .where(
                and_(
                    NewsletterSignup.is_active == True,  # noqa: E712
                    NewsletterSignup.email_verified == False,  # noqa: E712
                )
            )
            .order_by(NewsletterSignup.subscribed_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def count_active(self) -> int:
        """Conta inscritos ativos (independente de verificacao)."""
        result = await self.db.execute(
            select(func.count())
            .select_from(NewsletterSignup)
            .where(NewsletterSignup.is_active == True)  # noqa: E712
        )
        return result.scalar_one()

    async def count_verified(self) -> int:
        """Conta inscritos ativos E verificados."""
        result = await self.db.execute(
            select(func.count())
            .select_from(NewsletterSignup)
            .where(
                and_(
                    NewsletterSignup.is_active == True,  # noqa: E712
                    NewsletterSignup.email_verified == True,  # noqa: E712
                )
            )
        )
        return result.scalar_one()

    async def count_pending_verification(self) -> int:
        """Conta inscritos ativos que ainda nao verificaram."""
        result = await self.db.execute(
            select(func.count())
            .select_from(NewsletterSignup)
            .where(
                and_(
                    NewsletterSignup.is_active == True,  # noqa: E712
                    NewsletterSignup.email_verified == False,  # noqa: E712
                )
            )
        )
        return result.scalar_one()

    async def verify_email(self, token: str) -> Optional[NewsletterSignup]:
        """
        Verifica email usando token.

        Args:
            token: Token de verificacao

        Returns:
            NewsletterSignup se verificado com sucesso, None se token invalido
        """
        signup = await self.get_by_token(token)
        if signup:
            signup.verify_email()
            await self.db.commit()
            await self.db.refresh(signup)
        return signup

    async def unsubscribe(self, email: str) -> NewsletterSignup | None:
        """Desinscreve por email."""
        signup = await self.get_by_email(email)
        if signup:
            signup.is_active = False
            signup.unsubscribed_at = datetime.now(UTC)
            await self.db.commit()
            await self.db.refresh(signup)
        return signup

    async def resubscribe(self, email: str) -> NewsletterSignup | None:
        """Reinscreve por email (mantem status de verificacao)."""
        signup = await self.get_by_email(email)
        if signup:
            signup.is_active = True
            signup.unsubscribed_at = None
            await self.db.commit()
            await self.db.refresh(signup)
        return signup

    async def get_stats(self) -> dict:
        """Retorna estatisticas de newsletter."""
        now = datetime.now(UTC)
        today = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_ago = now - timedelta(days=7)
        month_ago = now - timedelta(days=30)

        total = await self.count()
        active = await self.count_active()
        verified = await self.count_verified()
        pending = await self.count_pending_verification()

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
            "verified_subscribers": verified,
            "pending_verification": pending,
            "unsubscribed": total - active,
            "subscriptions_today": today_count,
            "subscriptions_week": week_count,
            "subscriptions_month": month_count,
        }
