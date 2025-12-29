"""
Schemas para Product (produtos de afiliados).
"""

import re
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import Field, field_validator

from app.models.product import PriceRange, ProductAvailability, ProductPlatform
from app.schemas.base import BaseSchema, ResponseSchema
from app.utils.sanitize import sanitize_text, sanitize_slug


# -----------------------------------------------------------------------------
# Base
# -----------------------------------------------------------------------------


class ProductBase(BaseSchema):
    """Campos compartilhados de Product."""

    name: str = Field(..., min_length=5, max_length=300, description="Nome do produto")
    slug: str = Field(..., min_length=5, max_length=350, description="Slug para URL")
    short_description: str | None = Field(None, max_length=500, description="Descricao curta")
    long_description: str | None = Field(None, description="Descricao longa")
    price: Decimal | None = Field(None, ge=0, decimal_places=2, description="Preco atual")
    currency: str = Field(default="BRL", max_length=3, description="Moeda")
    price_range: PriceRange | None = Field(None, description="Faixa de preco")
    main_image_url: str | None = Field(None, max_length=500, description="URL imagem principal")
    images: list[str] = Field(default_factory=list, description="URLs imagens adicionais")

    @field_validator("name")
    @classmethod
    def sanitize_name(cls, v: str) -> str:
        """Sanitiza nome removendo scripts/HTML malicioso."""
        sanitized = sanitize_text(v)
        if not sanitized or len(sanitized) < 5:
            raise ValueError("Nome invalido apos sanitizacao")
        return sanitized

    @field_validator("slug")
    @classmethod
    def validate_and_sanitize_slug(cls, v: str) -> str:
        """Valida e sanitiza slug."""
        sanitized = sanitize_slug(v)
        if not sanitized or len(sanitized) < 5:
            raise ValueError("Slug invalido - deve conter apenas letras minusculas, numeros e hifens")

        if not re.match(r"^[a-z0-9]+(?:-[a-z0-9]+)*$", sanitized):
            raise ValueError("Slug deve conter apenas letras minusculas, numeros e hifens")

        return sanitized

    @field_validator("short_description")
    @classmethod
    def sanitize_short_description(cls, v: str | None) -> str | None:
        """Sanitiza descricao curta removendo scripts/HTML malicioso."""
        if v is None:
            return None
        return sanitize_text(v)


# -----------------------------------------------------------------------------
# Affiliate
# -----------------------------------------------------------------------------


class ProductAffiliate(BaseSchema):
    """Campos de afiliado do produto."""

    affiliate_url_raw: str = Field(..., description="URL completa do afiliado")
    affiliate_redirect_slug: str = Field(..., max_length=150, description="Slug para redirect")
    platform: ProductPlatform = Field(..., description="Plataforma (amazon, mercadolivre, shopee)")
    platform_product_id: str | None = Field(None, max_length=200, description="ID na plataforma")


# -----------------------------------------------------------------------------
# Create
# -----------------------------------------------------------------------------


class ProductCreate(ProductBase, ProductAffiliate):
    """Schema para criacao de produto."""

    categories: list[str] = Field(default_factory=list, description="Categorias do produto")
    tags: list[str] = Field(default_factory=list, description="Tags do produto")
    availability: ProductAvailability = Field(
        default=ProductAvailability.UNKNOWN,
        description="Disponibilidade",
    )
    rating: Decimal | None = Field(None, ge=0, le=5, decimal_places=2, description="Rating 0-5")
    review_count: int = Field(default=0, ge=0, description="Numero de reviews")

    # Metadados Instagram (pre-configuracao para posts futuros)
    instagram_headline: str | None = Field(
        None, max_length=40, description="Headline de impacto para Instagram (max 40 chars)"
    )
    instagram_title: str | None = Field(
        None, max_length=100, description="Titulo curto para Instagram"
    )
    instagram_badge: str | None = Field(
        None, max_length=20, description="Texto do badge (ex: NOVO!) (max 20 chars)"
    )
    instagram_caption: str | None = Field(
        None, description="Caption pre-definida para posts"
    )
    instagram_hashtags: list[str] = Field(
        default_factory=list, description="Lista de hashtags (sem #)"
    )

    @field_validator("affiliate_redirect_slug")
    @classmethod
    def validate_redirect_slug(cls, v: str) -> str:
        """Garante que slug nao tem caracteres especiais."""
        import re
        if not re.match(r"^[a-z0-9-]+$", v):
            raise ValueError("Slug deve conter apenas letras minusculas, numeros e hifens")
        return v


# -----------------------------------------------------------------------------
# Update
# -----------------------------------------------------------------------------


class ProductUpdate(BaseSchema):
    """Schema para atualizacao de produto (todos campos opcionais)."""

    name: str | None = Field(None, min_length=5, max_length=300)
    slug: str | None = Field(None, min_length=5, max_length=350)
    short_description: str | None = Field(None, max_length=500)
    long_description: str | None = None
    price: Decimal | None = Field(None, ge=0, decimal_places=2)
    currency: str | None = Field(None, max_length=3)
    price_range: PriceRange | None = None
    main_image_url: str | None = None
    images: list[str] | None = None
    affiliate_url_raw: str | None = None
    affiliate_redirect_slug: str | None = Field(None, max_length=150)
    platform_product_id: str | None = None
    categories: list[str] | None = None
    tags: list[str] | None = None
    availability: ProductAvailability | None = None
    rating: Decimal | None = Field(None, ge=0, le=5, decimal_places=2)
    review_count: int | None = Field(None, ge=0)

    # Metadados Instagram (pre-configuracao para posts futuros)
    instagram_headline: str | None = Field(None, max_length=40)
    instagram_title: str | None = Field(None, max_length=100)
    instagram_badge: str | None = Field(None, max_length=20)
    instagram_caption: str | None = None
    instagram_hashtags: list[str] | None = None

    @field_validator("affiliate_redirect_slug")
    @classmethod
    def validate_redirect_slug(cls, v: str | None) -> str | None:
        """
        Valida slug de redirecionamento.
        Nao permite caractere / pois quebra o redirecionamento.
        Apenas letras minusculas, numeros e hifens sao permitidos.
        """
        if v is None:
            return None
        if not re.match(r"^[a-z0-9-]+$", v):
            raise ValueError(
                "Slug de redirecionamento deve conter apenas letras minusculas, "
                "numeros e hifens (caractere '/' nao e permitido)"
            )
        return v

    @field_validator("name")
    @classmethod
    def sanitize_name(cls, v: str | None) -> str | None:
        """Sanitiza nome removendo scripts/HTML malicioso."""
        if v is None:
            return None
        sanitized = sanitize_text(v)
        if not sanitized or len(sanitized) < 5:
            raise ValueError("Nome invalido apos sanitizacao")
        return sanitized

    @field_validator("slug")
    @classmethod
    def validate_and_sanitize_slug(cls, v: str | None) -> str | None:
        """Valida e sanitiza slug."""
        if v is None:
            return None
        sanitized = sanitize_slug(v)
        if not sanitized or len(sanitized) < 5:
            raise ValueError("Slug invalido - deve conter apenas letras minusculas, numeros e hifens")

        if not re.match(r"^[a-z0-9]+(?:-[a-z0-9]+)*$", sanitized):
            raise ValueError("Slug deve conter apenas letras minusculas, numeros e hifens")

        return sanitized

    @field_validator("short_description")
    @classmethod
    def sanitize_short_description(cls, v: str | None) -> str | None:
        """Sanitiza descricao curta removendo scripts/HTML malicioso."""
        if v is None:
            return None
        return sanitize_text(v)


class ProductUpdatePrice(BaseSchema):
    """Schema para atualizacao de preco do produto."""

    price: Decimal = Field(..., ge=0, decimal_places=2)
    price_range: PriceRange | None = None
    availability: ProductAvailability | None = None


class ProductUpdateScore(BaseSchema):
    """Schema para atualizacao do score interno."""

    internal_score: Decimal = Field(..., ge=0, le=100, decimal_places=2)


# -----------------------------------------------------------------------------
# Response
# -----------------------------------------------------------------------------


class ProductResponse(ProductBase, ProductAffiliate, ResponseSchema):
    """Schema de resposta completa de Product."""

    categories: list[str]
    tags: list[str]
    availability: ProductAvailability
    rating: Decimal | None
    review_count: int
    internal_score: Decimal
    last_price_update: datetime | None
    click_count: int
    # Campos de controle de posts em redes sociais
    last_post_date: datetime | None
    post_count: int
    last_post_platform: str | None
    last_post_url: str | None

    # Metadados Instagram (pre-configuracao para posts futuros)
    instagram_headline: str | None
    instagram_title: str | None
    instagram_badge: str | None
    instagram_caption: str | None
    instagram_hashtags: list[str]


class ProductBrief(BaseSchema):
    """Schema resumido de Product (para listagens)."""

    id: UUID
    name: str
    slug: str
    price: Decimal | None
    price_range: PriceRange | None
    main_image_url: str | None
    platform: ProductPlatform
    availability: ProductAvailability
    rating: Decimal | None
    click_count: int


class ProductPublic(BaseSchema):
    """Schema de produto para exibicao publica (frontend)."""

    id: UUID
    name: str
    slug: str
    short_description: str | None
    long_description: str | None
    price: Decimal | None
    currency: str
    price_range: PriceRange | None
    main_image_url: str | None
    images: list[str]
    affiliate_redirect_slug: str  # Usado para construir URL de redirect
    platform: ProductPlatform
    availability: ProductAvailability
    rating: Decimal | None
    review_count: int


class ProductCard(BaseSchema):
    """Schema de produto para cards (listagens publicas)."""

    id: UUID
    name: str
    slug: str
    short_description: str | None
    price: Decimal | None
    price_range: PriceRange | None
    main_image_url: str | None
    affiliate_redirect_slug: str
    platform: ProductPlatform
    rating: Decimal | None


# -----------------------------------------------------------------------------
# Atualização por Plataforma (Bulk Update via API externa)
# -----------------------------------------------------------------------------


class ProductPlatformUpdate(BaseSchema):
    """
    Schema para atualizacao de produto via plataforma + ID.

    Permite atualizar atributos de um produto identificado pela combinacao
    de plataforma (amazon, mercadolivre, shopee) e ID do produto na plataforma.

    Todos os campos sao opcionais, permitindo atualizacao parcial.
    Se o preco for alterado, o historico de precos sera automaticamente registrado.

    Atributos:
        price: Novo preco do produto
        availability: Status de disponibilidade
        rating: Avaliacao do produto (0-5)
        review_count: Numero de avaliacoes
        name: Nome do produto (caso tenha mudado)
        main_image_url: URL da imagem principal
        affiliate_url_raw: URL de afiliado atualizada

    Exemplo de uso (n8n workflow):
        PATCH /api/v1/products/platform/amazon/B08N5WRWNW
        {
            "price": 129.90,
            "availability": "available",
            "rating": 4.5,
            "review_count": 1250
        }
    """

    # Campos de preco e disponibilidade (mais comuns em atualizacoes)
    price: Decimal | None = Field(None, ge=0, decimal_places=2, description="Preco atual")
    price_range: PriceRange | None = Field(None, description="Faixa de preco")
    availability: ProductAvailability | None = Field(None, description="Disponibilidade")

    # Campos de avaliacao
    rating: Decimal | None = Field(
        None, ge=0, le=5, decimal_places=2, description="Rating 0-5"
    )
    review_count: int | None = Field(None, ge=0, description="Numero de reviews")

    # Campos opcionais que podem mudar
    name: str | None = Field(None, min_length=5, max_length=300, description="Nome do produto")
    short_description: str | None = Field(None, max_length=500, description="Descricao curta")
    main_image_url: str | None = Field(None, max_length=500, description="URL imagem principal")
    affiliate_url_raw: str | None = Field(None, description="URL do afiliado")

    # Fonte da atualizacao (para historico de precos)
    source: str = Field(
        default="api",
        max_length=50,
        description="Fonte da atualizacao (api, api_amazon, api_ml, scraper, manual)",
    )
    notes: str | None = Field(None, description="Observacoes sobre a atualizacao")

    @field_validator("name")
    @classmethod
    def sanitize_name(cls, v: str | None) -> str | None:
        """Sanitiza nome removendo scripts/HTML malicioso."""
        if v is None:
            return None
        sanitized = sanitize_text(v)
        if not sanitized or len(sanitized) < 5:
            raise ValueError("Nome invalido apos sanitizacao")
        return sanitized

    @field_validator("short_description")
    @classmethod
    def sanitize_short_description(cls, v: str | None) -> str | None:
        """Sanitiza descricao curta removendo scripts/HTML malicioso."""
        if v is None:
            return None
        return sanitize_text(v)


class ProductPlatformUpdateResponse(BaseSchema):
    """
    Resposta de atualizacao de produto via plataforma.

    Atributos:
        success: Se a atualizacao foi bem sucedida
        product_id: UUID do produto atualizado
        platform: Plataforma do produto
        platform_product_id: ID do produto na plataforma
        updated_fields: Lista de campos que foram atualizados
        price_history_created: Se foi criado registro no historico de precos
        previous_price: Preco anterior (se houve alteracao de preco)
        new_price: Novo preco (se houve alteracao de preco)
        availability: Status atual do produto (available, unavailable, unknown)
    """

    success: bool
    product_id: UUID
    platform: ProductPlatform
    platform_product_id: str
    updated_fields: list[str]
    price_history_created: bool = False
    previous_price: Decimal | None = None
    new_price: Decimal | None = None
    availability: ProductAvailability | None = None
