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
    Request para marcar produto como postado no Instagram.

    Chamado apos o post ser publicado com sucesso no Instagram.
    ig_media_id e platform sao obrigatorios - a data e registrada automaticamente.
    """

    ig_media_id: str = Field(
        ...,
        max_length=100,
        description="IG Media ID retornado pela Graph API do Instagram (obrigatorio)",
    )
    platform: str = Field(
        ...,
        max_length=50,
        description="Plataforma onde foi postado (obrigatorio)",
    )
    post_url: str | None = Field(
        None,
        max_length=500,
        description="URL do post publicado (opcional, pode ser construida a partir do ig_media_id)",
    )
    caption: str | None = Field(
        None,
        description="Caption utilizada no post (opcional, para historico)",
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
    long_description: str | None = Field(
        None,
        description="Descricao completa do produto",
    )
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


class LLMCostInfo(BaseModel):
    """
    Informacoes de custo de uma chamada LLM.

    Usado para rastrear custos de geracao de conteudo por IA.
    """

    provider: str = Field(
        ...,
        max_length=50,
        description="Provedor do LLM (openai, anthropic, etc)",
    )
    model: str = Field(
        ...,
        max_length=100,
        description="Modelo usado (gpt-4o-mini, claude-3, etc)",
    )
    input_tokens: int = Field(
        ...,
        ge=0,
        description="Tokens de entrada (prompt)",
    )
    output_tokens: int = Field(
        ...,
        ge=0,
        description="Tokens de saida (completion)",
    )
    cost_usd: float = Field(
        ...,
        ge=0,
        description="Custo em USD da chamada",
    )


class InstagramMetadataUpdate(BaseModel):
    """
    Schema para atualizar metadados Instagram de um produto.

    Usado no cadastro/edicao de produtos para pre-configurar
    o conteudo de posts futuros. Opcionalmente registra custo de LLM
    quando o conteudo foi gerado por IA.
    """

    instagram_headline: str | None = Field(
        None,
        max_length=40,
        description="Headline de impacto (ex: OFERTA IMPERDIVEL!) - max 40 chars",
    )
    instagram_title: str | None = Field(
        None,
        max_length=100,
        description="Titulo curto para Instagram (se diferente do nome)",
    )
    instagram_badge: str | None = Field(
        None,
        max_length=20,
        description="Texto do badge (ex: NOVO!, BEST SELLER) - max 20 chars",
    )
    instagram_caption: str | None = Field(
        None,
        max_length=2200,
        description="Caption pre-definida para posts Instagram - max 2200 chars",
    )
    instagram_hashtags: list[str] | None = Field(
        None,
        max_length=30,
        description="Lista de hashtags (sem #) - 5 a 10 recomendado",
    )
    llm_cost: LLMCostInfo | None = Field(
        None,
        description="Informacoes de custo do LLM (quando gerado por IA)",
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


class InstagramMetadataUpdateResponse(BaseModel):
    """
    Resposta da atualizacao de metadados Instagram.

    Confirma quais campos foram atualizados e se o custo LLM foi registrado.
    """

    success: bool = Field(..., description="Se a operacao foi bem sucedida")
    product_id: UUID = Field(..., description="UUID do produto atualizado")
    updated_fields: list[str] = Field(
        ...,
        description="Lista de campos que foram atualizados",
    )
    llm_cost_registered: bool = Field(
        False,
        description="Se informacoes de custo LLM foram registradas",
    )
    total_llm_cost_usd: float | None = Field(
        None,
        description="Custo total acumulado de LLM do produto (USD)",
    )


class GenerateImageRequest(BaseModel):
    """
    Request para gerar imagem de post Instagram.

    Recebe os dados do produto e conteudo para gerar a imagem.
    Se os campos de conteudo nao forem passados, usa os pre-cadastrados do produto.

    Por padrao, a imagem e salva no servidor e a URL publica e retornada.
    Para obter tambem o base64, passe include_base64=true.
    """

    product_id: UUID = Field(
        ...,
        description="UUID do produto para gerar imagem",
    )
    headline: str | None = Field(
        None,
        max_length=40,
        description="Override da headline (usa instagram_headline do produto se None)",
    )
    title: str | None = Field(
        None,
        max_length=100,
        description="Override do titulo (usa instagram_title ou name se None)",
    )
    badge: str | None = Field(
        None,
        max_length=20,
        description="Override do badge (usa instagram_badge do produto se None)",
    )
    hashtags: list[str] | None = Field(
        None,
        description="Override das hashtags (usa instagram_hashtags do produto se None)",
    )
    include_base64: bool = Field(
        default=False,
        description="Se True, inclui a imagem em base64 na resposta (alem da URL)",
    )


class GenerateImageResponse(BaseModel):
    """
    Resposta da geracao de imagem Instagram.

    Sempre retorna a URL publica da imagem salva no servidor.
    Opcionalmente inclui a imagem em base64 se solicitado no request.
    """

    success: bool = Field(..., description="Se a geracao foi bem sucedida")
    image_url: str = Field(
        ...,
        description="URL publica da imagem (para uso na Graph API do Instagram)",
    )
    image_base64: str | None = Field(
        None,
        description="Imagem em base64 (apenas se include_base64=true no request)",
    )
    format: str = Field(default="png", description="Formato da imagem")
    width: int = Field(default=1080, description="Largura da imagem")
    height: int = Field(default=1080, description="Altura da imagem")
    file_size_kb: int = Field(..., description="Tamanho do arquivo em KB")
