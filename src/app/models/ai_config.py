"""
Modelo para configuracao de IA/LLM.

Este modelo permite configurar diferentes providers, modelos e prompts
para cada tipo de uso de IA no sistema. Isso permite:
- Trocar modelos sem alterar codigo
- Ajustar prompts via admin
- Usar diferentes modelos para diferentes tarefas (custo vs qualidade)
"""

import enum

from sqlalchemy import Boolean, Enum, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.models.base import TimestampMixin, UUIDMixin


class AIProvider(str, enum.Enum):
    """Provedores de IA suportados via LiteLLM/OpenRouter."""

    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    OPENROUTER = "openrouter"


class AIEntity(str, enum.Enum):
    """Entidades que podem usar configuracoes de IA."""

    POST = "post"
    CATEGORY = "category"
    OCCASION = "occasion"
    PRODUCT = "product"
    GENERAL = "general"


class AIUseCase(str, enum.Enum):
    """Casos de uso para configuracao de IA.

    Cada caso de uso pode ter seu proprio provider, modelo e prompts.
    """

    # Geracao de SEO (generico - retrocompatibilidade)
    SEO_TITLE = "seo_title"
    SEO_DESCRIPTION = "seo_description"
    SEO_KEYWORDS = "seo_keywords"

    # SEO especifico para Post
    POST_SEO_ALL = "post_seo_all"
    POST_SEO_KEYWORD = "post_seo_keyword"
    POST_SEO_TITLE = "post_seo_title"
    POST_SEO_DESCRIPTION = "post_seo_description"
    POST_TAGS = "post_tags"

    # SEO especifico para Occasion
    OCCASION_SEO_ALL = "occasion_seo_all"
    OCCASION_SEO_KEYWORD = "occasion_seo_keyword"
    OCCASION_SEO_TITLE = "occasion_seo_title"
    OCCASION_SEO_DESCRIPTION = "occasion_seo_description"
    OCCASION_CONTENT = "occasion_content"
    OCCASION_TAGS = "occasion_tags"

    # SEO especifico para Category
    CATEGORY_SEO_KEYWORD = "category_seo_keyword"
    CATEGORY_SEO_TITLE = "category_seo_title"
    CATEGORY_SEO_DESCRIPTION = "category_seo_description"
    CATEGORY_TAGS = "category_tags"

    # Geracao de conteudo
    POST_CONTENT = "post_content"
    PRODUCT_DESCRIPTION = "product_description"

    # Social media
    SOCIAL_SHARE = "social_share"

    # Traducao (futuro)
    TRANSLATION = "translation"


class AIConfig(Base, UUIDMixin, TimestampMixin):
    """
    Configuracao de IA para cada caso de uso.

    Permite configurar via admin:
    - Provider (OpenAI, Anthropic, Google, OpenRouter)
    - Modelo especifico (gpt-4o-mini, gemini-2.0-flash, etc.)
    - System prompt customizado
    - Parametros de geracao (temperatura, max_tokens)
    """

    __tablename__ = "ai_configs"

    # Identificador do caso de uso (unico)
    # Nota: create_constraint=False porque o tipo ja existe no banco
    # values_callable retorna os valores do enum (lowercase) em vez dos nomes
    use_case: Mapped[AIUseCase] = mapped_column(
        Enum(
            AIUseCase,
            name="ai_use_case",
            create_constraint=False,
            values_callable=lambda obj: [e.value for e in obj],
        ),
        unique=True,
        nullable=False,
        index=True,
    )

    # Nome amigavel para exibicao no admin
    name: Mapped[str] = mapped_column(String(100), nullable=False)

    # Descricao do uso (ajuda o admin a entender)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Entidade associada (post, category, occasion, product, general)
    entity: Mapped[AIEntity] = mapped_column(
        Enum(
            AIEntity,
            name="ai_entity",
            create_constraint=False,
            values_callable=lambda obj: [e.value for e in obj],
        ),
        nullable=False,
        default=AIEntity.GENERAL,
    )

    # Provider de IA
    provider: Mapped[AIProvider] = mapped_column(
        Enum(
            AIProvider,
            name="ai_provider",
            create_constraint=False,
            values_callable=lambda obj: [e.value for e in obj],
        ),
        nullable=False,
        default=AIProvider.OPENROUTER,
    )

    # Modelo especifico (ex: google/gemini-2.0-flash-exp:free)
    model: Mapped[str] = mapped_column(String(100), nullable=False)

    # System prompt (instrucoes para o modelo)
    system_prompt: Mapped[str] = mapped_column(Text, nullable=False)

    # User prompt template (com placeholders como {{title}}, {{content}}, etc.)
    # Se preenchido, sera usado para montar o user_prompt com os dados
    user_prompt: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Parametros de geracao
    temperature: Mapped[float] = mapped_column(Float, nullable=False, default=0.7)
    max_tokens: Mapped[int] = mapped_column(Integer, nullable=False, default=500)

    # Ativo/inativo
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    def __repr__(self) -> str:
        return f"<AIConfig {self.use_case.value}: {self.model}>"

    @property
    def full_model_name(self) -> str:
        """
        Retorna nome completo do modelo para LiteLLM.

        Para OpenRouter, adiciona prefixo 'openrouter/'.
        Para outros providers, usa o nome direto.
        """
        if self.provider == AIProvider.OPENROUTER:
            # OpenRouter ja usa formato completo (ex: google/gemini-2.0-flash-exp:free)
            if not self.model.startswith("openrouter/"):
                return f"openrouter/{self.model}"
            return self.model
        elif self.provider == AIProvider.GOOGLE:
            # Google Gemini usa prefixo gemini/
            if not self.model.startswith("gemini/"):
                return f"gemini/{self.model}"
            return self.model
        else:
            # OpenAI e Anthropic usam nome direto
            return self.model
