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


class AIUseCase(str, enum.Enum):
    """Casos de uso para configuracao de IA.

    Cada caso de uso pode ter seu proprio provider, modelo e prompts.
    """

    # Geracao de SEO
    SEO_TITLE = "seo_title"
    SEO_DESCRIPTION = "seo_description"
    SEO_KEYWORDS = "seo_keywords"

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
    use_case: Mapped[AIUseCase] = mapped_column(
        Enum(AIUseCase),
        unique=True,
        nullable=False,
        index=True,
    )

    # Nome amigavel para exibicao no admin
    name: Mapped[str] = mapped_column(String(100), nullable=False)

    # Descricao do uso (ajuda o admin a entender)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Provider de IA
    provider: Mapped[AIProvider] = mapped_column(
        Enum(AIProvider),
        nullable=False,
        default=AIProvider.OPENROUTER,
    )

    # Modelo especifico (ex: google/gemini-2.0-flash-exp:free)
    model: Mapped[str] = mapped_column(String(100), nullable=False)

    # System prompt (instrucoes para o modelo)
    system_prompt: Mapped[str] = mapped_column(Text, nullable=False)

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
