"""
Modelo de Produto (Afiliado).

Produtos das plataformas de afiliados (Amazon, Mercado Livre, Shopee).
"""

import enum
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, Enum, Index, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import JSONBType, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.click import AffiliateClick
    from app.models.instagram_post import InstagramPostHistory
    from app.models.post_product import PostProduct


class ProductPlatform(str, enum.Enum):
    """Plataformas de afiliados suportadas."""

    AMAZON = "amazon"
    MERCADOLIVRE = "mercadolivre"
    SHOPEE = "shopee"


class ProductAvailability(str, enum.Enum):
    """Status de disponibilidade do produto."""

    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    UNKNOWN = "unknown"


class PriceRange(str, enum.Enum):
    """Faixas de preco para filtros."""

    RANGE_0_50 = "0-50"
    RANGE_50_100 = "50-100"
    RANGE_100_200 = "100-200"
    RANGE_200_PLUS = "200+"


class Product(Base, UUIDMixin, TimestampMixin):
    """
    Produto de afiliado.

    Atributos:
        id: UUID primary key
        name: Nome do produto
        slug: Slug unico para URL
        short_description: Descricao curta (para cards)
        long_description: Descricao completa
        price: Preco atual
        currency: Moeda (BRL)
        price_range: Faixa de preco para filtros
        main_image_url: URL da imagem principal
        images: Lista de URLs de imagens (JSONB)
        affiliate_url_raw: URL original de afiliado
        affiliate_redirect_slug: Slug para /goto/{slug}
        platform: Plataforma (amazon, mercadolivre, shopee)
        platform_product_id: ID do produto na plataforma
        categories: Categorias do produto (JSONB)
        tags: Tags do produto (JSONB)
        availability: Disponibilidade
        rating: Avaliacao (0-5)
        review_count: Numero de avaliacoes
        internal_score: Score interno para curadoria
        last_price_update: Data da ultima atualizacao de preco
        click_count: Contador de cliques (desnormalizado)
        created_at: Data de criacao
        updated_at: Data de atualizacao
    """

    __tablename__ = "products"

    # Campos principais
    name: Mapped[str] = mapped_column(String(300), nullable=False)
    slug: Mapped[str] = mapped_column(String(350), unique=True, nullable=False)

    # Descricoes
    short_description: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    long_description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Preco
    price: Mapped[Optional[float]] = mapped_column(Numeric(10, 2), nullable=True)
    currency: Mapped[str] = mapped_column(String(3), default="BRL", server_default="BRL")
    price_range: Mapped[Optional[PriceRange]] = mapped_column(
        Enum(PriceRange, name="price_range", values_callable=lambda x: [e.value for e in x]),
        nullable=True,
    )

    # Imagens (JSONBType para compatibilidade com SQLite em testes)
    main_image_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    images: Mapped[list] = mapped_column(JSONBType, default=list, server_default="[]")

    # Afiliado
    affiliate_url_raw: Mapped[str] = mapped_column(Text, nullable=False)
    affiliate_redirect_slug: Mapped[str] = mapped_column(
        String(150), unique=True, nullable=False
    )
    platform: Mapped[ProductPlatform] = mapped_column(
        Enum(ProductPlatform, name="product_platform", values_callable=lambda x: [e.value for e in x]),
        nullable=False,
    )
    platform_product_id: Mapped[Optional[str]] = mapped_column(
        String(200), nullable=True
    )

    # Categorias e Tags (JSONBType para flexibilidade e compatibilidade com SQLite)
    categories: Mapped[list] = mapped_column(JSONBType, default=list, server_default="[]")
    tags: Mapped[list] = mapped_column(JSONBType, default=list, server_default="[]")

    # Disponibilidade e avaliacao
    availability: Mapped[ProductAvailability] = mapped_column(
        Enum(ProductAvailability, name="product_availability", values_callable=lambda x: [e.value for e in x]),
        default=ProductAvailability.UNKNOWN,
    )
    rating: Mapped[Optional[float]] = mapped_column(Numeric(3, 2), nullable=True)
    review_count: Mapped[int] = mapped_column(Integer, default=0, server_default="0")

    # Score interno (curadoria)
    internal_score: Mapped[float] = mapped_column(
        Numeric(5, 2), default=0, server_default="0"
    )

    # Atualizacao de preco
    last_price_update: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Metricas (desnormalizadas)
    click_count: Mapped[int] = mapped_column(Integer, default=0, server_default="0")

    # Controle de publicacao em redes sociais
    last_post_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
        comment="Data do ultimo post sobre este produto"
    )
    post_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        server_default="0",
        comment="Quantidade de vezes que foi postado"
    )
    last_post_platform: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="Plataforma do ultimo post (instagram, tiktok, etc)"
    )
    last_post_url: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        comment="URL do ultimo post publicado"
    )
    last_ig_media_id: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="IG Media ID do ultimo post no Instagram (retornado pela Graph API)"
    )

    # ==========================================================================
    # Metadados para posts em redes sociais (pre-configurados no cadastro)
    # Estes campos permitem preparar o conteudo do post antecipadamente
    # ==========================================================================
    instagram_headline: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="Headline de impacto para Instagram (ex: OFERTA IMPERDIVEL!)"
    )
    instagram_title: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="Titulo curto para Instagram (se diferente do nome)"
    )
    instagram_badge: Mapped[Optional[str]] = mapped_column(
        String(30),
        nullable=True,
        comment="Texto do badge (ex: NOVO!, BEST SELLER)"
    )
    instagram_caption: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Caption pre-definida para posts Instagram"
    )
    instagram_hashtags: Mapped[list] = mapped_column(
        JSONBType,
        default=list,
        server_default="[]",
        comment="Lista de hashtags para Instagram"
    )

    # Relacionamentos
    post_products: Mapped[list["PostProduct"]] = relationship(
        "PostProduct",
        back_populates="product",
        lazy="selectin",
        cascade="all, delete-orphan",
    )

    clicks: Mapped[list["AffiliateClick"]] = relationship(
        "AffiliateClick",
        back_populates="product",
        lazy="selectin",
    )

    instagram_posts: Mapped[list["InstagramPostHistory"]] = relationship(
        "InstagramPostHistory",
        back_populates="product",
        lazy="selectin",
        cascade="all, delete-orphan",
        order_by="desc(InstagramPostHistory.posted_at)",
    )

    # Indices
    __table_args__ = (
        Index("idx_products_slug", "slug"),
        Index("idx_products_platform", "platform"),
        Index("idx_products_availability", "availability"),
        Index("idx_products_price_range", "price_range"),
        Index("idx_products_internal_score", "internal_score"),
        Index("idx_products_redirect_slug", "affiliate_redirect_slug"),
        Index("idx_products_platform_id", "platform", "platform_product_id"),
        Index("idx_products_categories", "categories", postgresql_using="gin"),
        Index("idx_products_tags", "tags", postgresql_using="gin"),
    )

    def __repr__(self) -> str:
        return f"<Product {self.name[:50]} ({self.platform.value})>"

    @property
    def redirect_url(self) -> str:
        """Retorna a URL de redirect para o produto."""
        return f"/goto/{self.affiliate_redirect_slug}"

    def update_price_range(self) -> None:
        """Atualiza a faixa de preco baseado no preco atual."""
        if self.price is None:
            self.price_range = None
        elif self.price < 50:
            self.price_range = PriceRange.RANGE_0_50
        elif self.price < 100:
            self.price_range = PriceRange.RANGE_50_100
        elif self.price < 200:
            self.price_range = PriceRange.RANGE_100_200
        else:
            self.price_range = PriceRange.RANGE_200_PLUS
