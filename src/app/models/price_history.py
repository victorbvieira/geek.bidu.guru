"""
Modelo de Historico de Precos.

Armazena o historico de alteracoes de precos dos produtos para:
- Analise de variacao de precos ao longo do tempo
- Identificacao de promocoes e melhores momentos para compra
- Comparativo de precos para oferecer alertas aos usuarios
"""

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Optional
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, Index, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.product import Product


class PriceHistory(Base, UUIDMixin, TimestampMixin):
    """
    Historico de precos de um produto.

    Cada registro representa uma alteracao de preco detectada,
    permitindo rastrear a evolucao de precos ao longo do tempo.

    Atributos:
        id: UUID primary key
        product_id: ID do produto relacionado
        price: Preco registrado neste momento
        previous_price: Preco anterior (para calcular variacao)
        currency: Moeda (BRL)
        source: Fonte da atualizacao (manual, api, scraper, etc)
        notes: Observacoes opcionais sobre a mudanca
        recorded_at: Data/hora do registro do preco
        created_at: Data de criacao do registro
        updated_at: Data de atualizacao do registro

    Relacionamentos:
        product: Produto ao qual este historico pertence
    """

    __tablename__ = "price_history"

    # Relacionamento com produto
    product_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Dados do preco
    price: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        comment="Preco registrado neste momento"
    )
    previous_price: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(10, 2),
        nullable=True,
        comment="Preco anterior para calcular variacao"
    )
    currency: Mapped[str] = mapped_column(
        String(3),
        default="BRL",
        server_default="BRL",
        comment="Moeda do preco (sempre BRL)"
    )

    # Metadados da atualizacao
    source: Mapped[str] = mapped_column(
        String(50),
        default="manual",
        server_default="manual",
        comment="Fonte da atualizacao: manual, api_amazon, api_ml, scraper, etc"
    )
    notes: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Observacoes sobre a alteracao de preco"
    )

    # Timestamp especifico do registro de preco
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        comment="Data/hora em que o preco foi registrado"
    )

    # Relacionamento
    product: Mapped["Product"] = relationship(
        "Product",
        back_populates="price_history",
        lazy="joined",
    )

    # Indices para consultas frequentes
    __table_args__ = (
        Index("idx_price_history_product_id", "product_id"),
        Index("idx_price_history_recorded_at", "recorded_at"),
        Index("idx_price_history_product_recorded", "product_id", "recorded_at"),
    )

    def __repr__(self) -> str:
        return f"<PriceHistory product_id={self.product_id} price={self.price} recorded_at={self.recorded_at}>"

    @property
    def price_change(self) -> Optional[Decimal]:
        """
        Calcula a diferenca entre preco atual e anterior.

        Returns:
            Diferenca de preco (positivo = aumento, negativo = reducao)
            ou None se nao houver preco anterior
        """
        if self.previous_price is None:
            return None
        return self.price - self.previous_price

    @property
    def price_change_percent(self) -> Optional[float]:
        """
        Calcula a variacao percentual do preco.

        Returns:
            Percentual de variacao (positivo = aumento, negativo = reducao)
            ou None se nao houver preco anterior ou preco anterior for zero
        """
        if self.previous_price is None or self.previous_price == 0:
            return None
        change = float(self.price - self.previous_price)
        return (change / float(self.previous_price)) * 100

    @property
    def is_price_drop(self) -> bool:
        """Verifica se houve reducao de preco."""
        change = self.price_change
        return change is not None and change < 0

    @property
    def is_price_increase(self) -> bool:
        """Verifica se houve aumento de preco."""
        change = self.price_change
        return change is not None and change > 0
