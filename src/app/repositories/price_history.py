"""
Repositorio para PriceHistory.

Fornece operacoes de CRUD e consultas especializadas para
historico de precos de produtos.
"""

from datetime import datetime, timedelta, UTC
from decimal import Decimal
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.price_history import PriceHistory
from app.models.product import Product
from app.repositories.base import BaseRepository


class PriceHistoryRepository(BaseRepository[PriceHistory]):
    """Repositorio com operacoes especificas de PriceHistory."""

    def __init__(self, db: AsyncSession):
        super().__init__(PriceHistory, db)

    async def get_by_product(
        self,
        product_id: UUID,
        skip: int = 0,
        limit: int = 50,
    ) -> list[PriceHistory]:
        """
        Busca historico de precos de um produto especifico.

        Retorna ordenado do mais recente para o mais antigo.

        Args:
            product_id: UUID do produto
            skip: Offset para paginacao
            limit: Limite de resultados

        Returns:
            Lista de registros de historico
        """
        result = await self.db.execute(
            select(PriceHistory)
            .where(PriceHistory.product_id == product_id)
            .order_by(PriceHistory.recorded_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def count_by_product(self, product_id: UUID) -> int:
        """
        Conta registros de historico de um produto.

        Args:
            product_id: UUID do produto

        Returns:
            Quantidade de registros
        """
        result = await self.db.execute(
            select(func.count())
            .select_from(PriceHistory)
            .where(PriceHistory.product_id == product_id)
        )
        return result.scalar_one()

    async def get_latest_price(self, product_id: UUID) -> PriceHistory | None:
        """
        Busca o registro de preco mais recente de um produto.

        Args:
            product_id: UUID do produto

        Returns:
            Registro mais recente ou None
        """
        result = await self.db.execute(
            select(PriceHistory)
            .where(PriceHistory.product_id == product_id)
            .order_by(PriceHistory.recorded_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def get_price_drops(
        self,
        days: int = 7,
        min_drop_percent: float = 10.0,
        limit: int = 20,
    ) -> list[PriceHistory]:
        """
        Busca produtos com quedas de preco significativas.

        Util para identificar promocoes e ofertas.

        Args:
            days: Periodo a considerar em dias
            min_drop_percent: Percentual minimo de queda
            limit: Limite de resultados

        Returns:
            Lista de registros com quedas de preco
        """
        cutoff_date = datetime.now(UTC) - timedelta(days=days)

        # Busca registros recentes com queda de preco
        result = await self.db.execute(
            select(PriceHistory)
            .where(
                PriceHistory.recorded_at >= cutoff_date,
                PriceHistory.previous_price.isnot(None),
                PriceHistory.previous_price > 0,
                # Calcula percentual de queda: ((previous - current) / previous) * 100
                (
                    (PriceHistory.previous_price - PriceHistory.price)
                    / PriceHistory.previous_price
                    * 100
                ) >= min_drop_percent,
            )
            .order_by(
                # Ordena pela maior queda percentual
                (
                    (PriceHistory.previous_price - PriceHistory.price)
                    / PriceHistory.previous_price
                ).desc()
            )
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_lowest_price(self, product_id: UUID) -> PriceHistory | None:
        """
        Busca o menor preco ja registrado para um produto.

        Args:
            product_id: UUID do produto

        Returns:
            Registro com menor preco ou None
        """
        result = await self.db.execute(
            select(PriceHistory)
            .where(PriceHistory.product_id == product_id)
            .order_by(PriceHistory.price.asc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def get_highest_price(self, product_id: UUID) -> PriceHistory | None:
        """
        Busca o maior preco ja registrado para um produto.

        Args:
            product_id: UUID do produto

        Returns:
            Registro com maior preco ou None
        """
        result = await self.db.execute(
            select(PriceHistory)
            .where(PriceHistory.product_id == product_id)
            .order_by(PriceHistory.price.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def get_average_price(self, product_id: UUID) -> float | None:
        """
        Calcula o preco medio de um produto.

        Args:
            product_id: UUID do produto

        Returns:
            Preco medio ou None se nao houver registros
        """
        result = await self.db.execute(
            select(func.avg(PriceHistory.price))
            .where(PriceHistory.product_id == product_id)
        )
        avg = result.scalar_one()
        return float(avg) if avg else None

    async def create_price_record(
        self,
        product_id: UUID,
        price: Decimal,
        previous_price: Decimal | None = None,
        source: str = "manual",
        notes: str | None = None,
    ) -> PriceHistory:
        """
        Cria um novo registro de historico de preco.

        Args:
            product_id: UUID do produto
            price: Novo preco
            previous_price: Preco anterior (opcional, sera buscado se nao fornecido)
            source: Fonte da atualizacao (manual, api_amazon, etc)
            notes: Observacoes opcionais

        Returns:
            Registro criado
        """
        # Se nao foi fornecido previous_price, busca o ultimo registrado
        if previous_price is None:
            latest = await self.get_latest_price(product_id)
            if latest:
                previous_price = latest.price

        record = PriceHistory(
            product_id=product_id,
            price=price,
            previous_price=previous_price,
            source=source,
            notes=notes,
            recorded_at=datetime.now(UTC),
        )
        self.db.add(record)
        await self.db.commit()
        await self.db.refresh(record)
        return record

    async def get_price_trend(
        self,
        product_id: UUID,
        days: int = 30,
    ) -> list[dict]:
        """
        Busca tendencia de precos de um produto para grafico.

        Args:
            product_id: UUID do produto
            days: Periodo em dias

        Returns:
            Lista de dicts com date e price para grafico
        """
        cutoff_date = datetime.now(UTC) - timedelta(days=days)

        result = await self.db.execute(
            select(PriceHistory)
            .where(
                PriceHistory.product_id == product_id,
                PriceHistory.recorded_at >= cutoff_date,
            )
            .order_by(PriceHistory.recorded_at.asc())
        )
        records = result.scalars().all()

        return [
            {
                "date": record.recorded_at.isoformat(),
                "price": float(record.price),
            }
            for record in records
        ]

    async def has_history(self, product_id: UUID) -> bool:
        """
        Verifica se um produto tem historico de precos.

        Args:
            product_id: UUID do produto

        Returns:
            True se existe pelo menos um registro
        """
        result = await self.db.execute(
            select(func.count())
            .select_from(PriceHistory)
            .where(PriceHistory.product_id == product_id)
        )
        return result.scalar_one() > 0

    async def is_current_price_lowest(self, product_id: UUID, current_price: Decimal) -> bool:
        """
        Verifica se o preco atual e o mais baixo ja registrado.

        Util para exibir badges de "menor preco historico".

        Args:
            product_id: UUID do produto
            current_price: Preco atual a comparar

        Returns:
            True se for o menor preco historico
        """
        lowest = await self.get_lowest_price(product_id)
        if not lowest:
            return True  # Sem historico, e o primeiro registro
        return current_price <= lowest.price
