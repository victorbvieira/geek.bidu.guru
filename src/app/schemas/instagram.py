"""
Schemas Pydantic para API de Instagram.

Define os schemas de request/response para:
- Selecao de produtos para posting
- Controle de produtos postados
- Conversao HTML para imagem
- Redimensionamento de imagens
"""

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


# =============================================================================
# Request Schemas
# =============================================================================


class MarkPostedRequest(BaseModel):
    """
    Request para marcar produto como postado.

    Chamado apos o post ser publicado com sucesso no Instagram.
    """

    platform: str = Field(
        default="instagram",
        max_length=50,
        description="Plataforma onde foi postado",
    )
    post_url: str | None = Field(
        None,
        max_length=500,
        description="URL do post publicado",
    )
    caption: str | None = Field(
        None,
        description="Caption utilizada no post (para historico)",
    )
    ig_media_id: str | None = Field(
        None,
        max_length=100,
        description="IG Media ID retornado pela Graph API do Instagram",
    )


class HtmlToImageRequest(BaseModel):
    """
    Request para converter HTML em imagem.

    O HTML sera renderizado com Playwright e convertido para PNG/JPEG.
    """

    html: str = Field(
        ...,
        min_length=10,
        description="Conteudo HTML completo para renderizar",
    )
    width: int = Field(
        default=1080,
        ge=100,
        le=4096,
        description="Largura da imagem em pixels",
    )
    height: int = Field(
        default=1080,
        ge=100,
        le=4096,
        description="Altura da imagem em pixels",
    )
    format: Literal["png", "jpeg"] = Field(
        default="png",
        description="Formato de saida da imagem",
    )


class ResizeImageRequest(BaseModel):
    """
    Request para redimensionar imagem via base64.

    Alternativa ao endpoint com upload de arquivo.
    """

    image_base64: str = Field(
        ...,
        description="Imagem em base64",
    )
    width: int = Field(
        default=1080,
        ge=100,
        le=4096,
        description="Largura desejada em pixels",
    )
    height: int = Field(
        default=1080,
        ge=100,
        le=4096,
        description="Altura desejada em pixels",
    )
    quality: int = Field(
        default=85,
        ge=1,
        le=100,
        description="Qualidade de compressao JPEG",
    )
    maintain_aspect: bool = Field(
        default=True,
        description="Manter proporcao original",
    )


# =============================================================================
# Response Schemas
# =============================================================================


class MarkPostedResponse(BaseModel):
    """Response do endpoint mark-posted."""

    success: bool = Field(..., description="Se a operacao foi bem sucedida")
    product_id: UUID = Field(..., description="UUID do produto atualizado")
    last_post_date: datetime = Field(..., description="Data/hora do post")
    post_count: int = Field(..., description="Total de posts do produto")
    ig_media_id: str | None = Field(None, description="IG Media ID registrado")
    history_id: UUID | None = Field(None, description="UUID do registro de historico criado")


class ProductForPostingResponse(BaseModel):
    """
    Produto selecionado para posting.

    Retorna dados essenciais do produto para geracao de conteudo,
    incluindo metadados Instagram pre-configurados.
    """

    id: UUID
    name: str
    slug: str
    short_description: str | None
    price: float | None
    currency: str
    main_image_url: str | None
    platform: str
    affiliate_redirect_slug: str
    categories: list[str]
    tags: list[str]
    post_count: int
    last_post_date: datetime | None

    # Metadados Instagram pre-configurados
    instagram_headline: str | None = Field(
        None,
        description="Headline de impacto pre-configurada",
    )
    instagram_title: str | None = Field(
        None,
        description="Titulo curto pre-configurado",
    )
    instagram_badge: str | None = Field(
        None,
        description="Texto do badge pre-configurado",
    )
    instagram_caption: str | None = Field(
        None,
        description="Caption pre-definida para o post",
    )
    instagram_hashtags: list[str] = Field(
        default_factory=list,
        description="Hashtags pre-configuradas",
    )

    class Config:
        """Configuracao do schema."""

        from_attributes = True


class PostingStatsResponse(BaseModel):
    """Estatisticas de posting."""

    available_for_posting: int = Field(
        ...,
        description="Quantidade de produtos elegiveis para posting",
    )
    total_products: int = Field(
        ...,
        description="Total de produtos disponiveis",
    )
    days_since_last_post: int = Field(
        ...,
        description="Dias considerados para elegibilidade",
    )


class HtmlToImageResponse(BaseModel):
    """Response da conversao HTML para imagem."""

    success: bool = Field(..., description="Se a conversao foi bem sucedida")
    image_base64: str = Field(..., description="Imagem em base64")
    format: str = Field(..., description="Formato da imagem (png/jpeg)")
    width: int = Field(..., description="Largura da imagem gerada")
    height: int = Field(..., description="Altura da imagem gerada")
    file_size_kb: int = Field(..., description="Tamanho do arquivo em KB")


class ResizeImageResponse(BaseModel):
    """Response do redimensionamento de imagem."""

    success: bool = Field(..., description="Se o redimensionamento foi bem sucedido")
    image_base64: str = Field(..., description="Imagem redimensionada em base64")
    format: str = Field(..., description="Formato da imagem (jpeg)")
    width: int = Field(..., description="Largura final da imagem")
    height: int = Field(..., description="Altura final da imagem")
    file_size_kb: int = Field(..., description="Tamanho final em KB")
    original_size_kb: int = Field(..., description="Tamanho original em KB")


# =============================================================================
# Schemas para Metadados Instagram (usados no cadastro de produtos)
# =============================================================================


class InstagramMetadataUpdate(BaseModel):
    """
    Schema para atualizar metadados Instagram de um produto.

    Usado no cadastro/edicao de produtos para pre-configurar
    o conteudo de posts futuros.
    """

    instagram_headline: str | None = Field(
        None,
        max_length=50,
        description="Headline de impacto (ex: OFERTA IMPERDIVEL!)",
    )
    instagram_title: str | None = Field(
        None,
        max_length=100,
        description="Titulo curto para Instagram (se diferente do nome)",
    )
    instagram_badge: str | None = Field(
        None,
        max_length=30,
        description="Texto do badge (ex: NOVO!, BEST SELLER)",
    )
    instagram_caption: str | None = Field(
        None,
        description="Caption pre-definida para posts Instagram",
    )
    instagram_hashtags: list[str] | None = Field(
        None,
        max_length=30,
        description="Lista de hashtags (sem #)",
    )


# =============================================================================
# Schemas para Histórico de Publicações Instagram
# =============================================================================


class InstagramPostHistoryResponse(BaseModel):
    """
    Resposta com dados de um registro de histórico de publicação.

    Representa uma publicação individual de produto no Instagram.
    """

    id: UUID = Field(..., description="UUID do registro de histórico")
    product_id: UUID = Field(..., description="UUID do produto publicado")
    ig_media_id: str | None = Field(None, description="IG Media ID do Instagram")
    post_url: str | None = Field(None, description="URL do post no Instagram")
    caption: str | None = Field(None, description="Caption utilizada")
    posted_at: datetime = Field(..., description="Data/hora da publicação")
    created_at: datetime = Field(..., description="Data de criação do registro")

    class Config:
        """Configuração do schema."""

        from_attributes = True


class InstagramPostHistoryListResponse(BaseModel):
    """
    Lista de registros de histórico de publicações.

    Usada para exibir o histórico completo de publicações de um produto.
    """

    items: list[InstagramPostHistoryResponse] = Field(
        ..., description="Lista de publicações"
    )
    total: int = Field(..., description="Total de publicações")


class ProductInstagramInfoResponse(BaseModel):
    """
    Informações resumidas de Instagram de um produto.

    Usado no admin para exibir campos somente leitura com as
    informações de publicação do produto.
    """

    product_id: UUID = Field(..., description="UUID do produto")
    last_ig_media_id: str | None = Field(
        None, description="IG Media ID da última publicação"
    )
    last_post_date: datetime | None = Field(
        None, description="Data/hora da última publicação"
    )
    post_count: int = Field(..., description="Total de publicações")
    last_post_url: str | None = Field(
        None, description="URL da última publicação"
    )
    history: list[InstagramPostHistoryResponse] = Field(
        default_factory=list,
        description="Histórico de publicações (últimas 5)"
    )
