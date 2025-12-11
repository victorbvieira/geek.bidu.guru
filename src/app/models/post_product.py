"""
Modelo de relacionamento Post-Product (N:N).

Tabela intermediaria para associar produtos a posts,
com ordenacao (position) para listicles.
"""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Index, Integer, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import UUIDMixin

if TYPE_CHECKING:
    from app.models.post import Post
    from app.models.product import Product


class PostProduct(Base, UUIDMixin):
    """
    Relacionamento N:N entre Post e Product.

    Permite que um post tenha multiplos produtos (listicles)
    e um produto apareca em multiplos posts.

    Atributos:
        id: UUID primary key
        post_id: ID do post
        product_id: ID do produto
        position: Posicao do produto no post (para ordenacao)
        created_at: Data de criacao
    """

    __tablename__ = "post_products"

    # Foreign Keys
    post_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("posts.id", ondelete="CASCADE"),
        nullable=False,
    )
    product_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Posicao para ordenacao (em listicles)
    position: Mapped[int] = mapped_column(Integer, default=0, server_default="0")

    # Timestamp simples (sem updated_at)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        default=datetime.utcnow,
    )

    # Relacionamentos
    post: Mapped["Post"] = relationship(
        "Post",
        back_populates="post_products",
        lazy="selectin",
    )

    product: Mapped["Product"] = relationship(
        "Product",
        back_populates="post_products",
        lazy="selectin",
    )

    # Constraints e Indices
    __table_args__ = (
        UniqueConstraint("post_id", "product_id", name="uq_post_product"),
        Index("idx_post_products_post", "post_id"),
        Index("idx_post_products_product", "product_id"),
        Index("idx_post_products_position", "post_id", "position"),
    )

    def __repr__(self) -> str:
        return f"<PostProduct post={self.post_id} product={self.product_id} pos={self.position}>"
