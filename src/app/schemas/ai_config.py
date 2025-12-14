"""
Schemas Pydantic para configuracao de IA.

Inclui schemas para:
- CRUD de configuracoes de IA
- Requisicao de geracao de conteudo
- Resposta de conteudo gerado
"""

from uuid import UUID

from pydantic import BaseModel, Field

from app.models.ai_config import AIProvider, AIUseCase
from app.schemas.base import BaseSchema, TimestampSchema


# =============================================================================
# Schemas de Configuracao
# =============================================================================


class AIConfigBase(BaseModel):
    """Campos base para configuracao de IA."""

    use_case: AIUseCase = Field(..., description="Caso de uso da configuracao")
    name: str = Field(..., min_length=1, max_length=100, description="Nome amigavel")
    description: str | None = Field(None, max_length=500, description="Descricao do uso")
    provider: AIProvider = Field(default=AIProvider.OPENROUTER, description="Provedor de IA")
    model: str = Field(..., min_length=1, max_length=100, description="Modelo a usar")
    system_prompt: str = Field(..., min_length=10, description="System prompt para o modelo")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="Temperatura de geracao")
    max_tokens: int = Field(default=500, ge=50, le=8000, description="Max tokens na resposta")
    is_active: bool = Field(default=True, description="Se a configuracao esta ativa")


class AIConfigCreate(AIConfigBase):
    """Schema para criacao de configuracao de IA."""

    pass


class AIConfigUpdate(BaseModel):
    """Schema para atualizacao de configuracao de IA."""

    name: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = None
    provider: AIProvider | None = None
    model: str | None = Field(None, min_length=1, max_length=100)
    system_prompt: str | None = Field(None, min_length=10)
    temperature: float | None = Field(None, ge=0.0, le=2.0)
    max_tokens: int | None = Field(None, ge=50, le=8000)
    is_active: bool | None = None


class AIConfigResponse(AIConfigBase, TimestampSchema):
    """Schema de resposta com configuracao completa."""

    id: UUID

    class Config:
        from_attributes = True


class AIConfigBrief(BaseModel):
    """Schema resumido para listagem."""

    id: UUID
    use_case: AIUseCase
    name: str
    provider: AIProvider
    model: str
    is_active: bool

    class Config:
        from_attributes = True


# =============================================================================
# Schemas de Geracao de Conteudo
# =============================================================================


class SEOGenerateRequest(BaseModel):
    """Requisicao para geracao de SEO com IA."""

    # Tipo de SEO a gerar
    use_case: AIUseCase = Field(
        ...,
        description="Tipo de conteudo SEO: seo_title, seo_description, seo_keywords",
    )

    # Conteudo de entrada
    title: str | None = Field(None, description="Titulo original do conteudo")
    content: str | None = Field(None, description="Conteudo para analise")
    keywords: list[str] | None = Field(None, description="Palavras-chave existentes")

    # Contexto adicional
    category: str | None = Field(None, description="Categoria do conteudo")
    product_name: str | None = Field(None, description="Nome do produto (se aplicavel)")
    target_audience: str | None = Field(None, description="Publico-alvo")


class SEOGenerateResponse(BaseModel):
    """Resposta da geracao de SEO."""

    use_case: AIUseCase
    generated_content: str = Field(..., description="Conteudo gerado pela IA")
    model_used: str = Field(..., description="Modelo que gerou o conteudo")
    tokens_used: int | None = Field(None, description="Tokens consumidos")


class ProductDescriptionRequest(BaseModel):
    """Requisicao para geracao de descricao de produto."""

    product_name: str = Field(..., description="Nome do produto")
    category: str | None = Field(None, description="Categoria do produto")
    price: float | None = Field(None, description="Preco do produto")
    platform: str | None = Field(None, description="Plataforma (Amazon, ML, Shopee)")
    raw_info: str | None = Field(None, description="Informacoes brutas do produto")
    generate_short: bool = Field(True, description="Gerar descricao curta")
    generate_long: bool = Field(True, description="Gerar descricao longa")


class ProductDescriptionResponse(BaseModel):
    """Resposta da geracao de descricao de produto."""

    short_description: str | None = Field(None, description="Descricao curta (max 150 chars)")
    long_description: str | None = Field(None, description="Descricao completa")
    model_used: str
    tokens_used: int | None = None
