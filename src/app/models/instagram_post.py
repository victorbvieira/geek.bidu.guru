"""
Modelo de Histórico de Publicações Instagram.

Armazena o histórico detalhado de cada publicação de produto no Instagram,
incluindo o IG Media ID retornado pela Graph API para rastreamento.
"""

from datetime import datetime
from typing import TYPE_CHECKING, Optional
from uuid import UUID as PyUUID

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.product import Product


class InstagramPostHistory(Base, UUIDMixin, TimestampMixin):
    """
    Histórico de publicações de produtos no Instagram.

    Cada registro representa uma publicação individual de um produto,
    permitindo rastrear múltiplas publicações do mesmo produto ao longo do tempo.

    Atributos:
        id: UUID primary key
        product_id: UUID do produto publicado (FK)
        ig_media_id: ID da mídia retornado pela Graph API do Instagram
        post_url: URL do post no Instagram (permalink)
        caption: Caption utilizada na publicação
        hashtags: Hashtags utilizadas (JSON array)
        posted_at: Data/hora da publicação no Instagram
        created_at: Data de criação do registro
        updated_at: Data de atualização do registro

    Relacionamentos:
        product: Produto associado a esta publicação
    """

    __tablename__ = "instagram_post_history"

    # Relacionamento com Product
    product_id: Mapped[PyUUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="UUID do produto publicado",
    )

    # Dados do Instagram
    ig_media_id: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        index=True,
        comment="ID da mídia retornado pela Graph API do Instagram",
    )

    post_url: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        comment="URL do post no Instagram (permalink)",
    )

    caption: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Caption utilizada na publicação",
    )

    # Data da publicação (pode ser diferente de created_at se registrado posteriormente)
    posted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        comment="Data/hora da publicação no Instagram",
    )

    # Relacionamento
    product: Mapped["Product"] = relationship(
        "Product",
        back_populates="instagram_posts",
        lazy="selectin",
    )

    # Índices
    __table_args__ = (
        Index("idx_instagram_posts_product_id", "product_id"),
        Index("idx_instagram_posts_ig_media_id", "ig_media_id"),
        Index("idx_instagram_posts_posted_at", "posted_at"),
    )

    def __repr__(self) -> str:
        return f"<InstagramPostHistory product_id={self.product_id} ig_media_id={self.ig_media_id}>"
