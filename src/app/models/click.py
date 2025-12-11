"""
Modelo de Click em Link de Afiliado.

Registra cada clique em links de afiliados para analytics.
"""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, ForeignKey, Index, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import UUIDMixin, utc_now

if TYPE_CHECKING:
    from app.models.post import Post
    from app.models.product import Product


class AffiliateClick(Base, UUIDMixin):
    """
    Registro de clique em link de afiliado.

    Usado para tracking e analytics de conversao.

    Atributos:
        id: UUID primary key
        product_id: ID do produto clicado
        post_id: ID do post de origem (se houver)
        session_id: ID da sessao do usuario
        user_agent: User agent do navegador
        referer: Pagina de origem
        ip_address: IP do usuario (para geo-localizacao)
        clicked_at: Data/hora do clique
    """

    __tablename__ = "affiliate_clicks"

    # Foreign Keys
    product_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
    )
    post_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("posts.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Informacoes da sessao
    session_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    referer: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)

    # Timestamp do clique
    clicked_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        default=utc_now,
    )

    # Relacionamentos
    product: Mapped["Product"] = relationship(
        "Product",
        back_populates="clicks",
        lazy="selectin",
    )

    post: Mapped[Optional["Post"]] = relationship(
        "Post",
        back_populates="clicks",
        lazy="selectin",
    )

    # Indices
    __table_args__ = (
        Index("idx_clicks_product", "product_id"),
        Index("idx_clicks_post", "post_id"),
        Index("idx_clicks_clicked_at", "clicked_at"),
        Index("idx_clicks_session", "session_id"),
        Index("idx_clicks_analytics", "product_id", "clicked_at"),
    )

    def __repr__(self) -> str:
        return f"<AffiliateClick product={self.product_id} at={self.clicked_at}>"
