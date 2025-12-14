"""
Modelo de Log de chamadas LLM.

Registra todas as chamadas ao LLM para debug, auditoria e analise de custos.
"""

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.database import Base


class AILog(Base):
    """
    Log de chamadas ao LLM.

    Atributos:
        id: UUID primary key
        created_at: Timestamp da chamada
        use_case: Caso de uso (post_tags, seo_title, etc)
        entity_type: Tipo da entidade (post, category, etc)
        entity_id: ID da entidade relacionada
        provider: Provider (openai, openrouter, etc)
        model: Modelo usado
        temperature: Temperature configurado
        max_tokens: Max tokens configurado
        system_prompt: System prompt enviado
        user_prompt: User prompt enviado
        response_content: Conteudo da resposta
        finish_reason: Razao de finalizacao
        prompt_tokens: Tokens de entrada
        completion_tokens: Tokens de saida
        total_tokens: Total de tokens
        cost_usd: Custo em USD
        latency_ms: Latencia em milissegundos
        success: Se a chamada foi bem sucedida
        error_message: Mensagem de erro se falhou
        user_id: ID do usuario admin que disparou
    """

    __tablename__ = "ai_logs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    # Contexto da chamada
    use_case: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Caso de uso (post_tags, seo_title, etc)",
    )
    entity_type: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="Tipo da entidade (post, category, etc)",
    )
    entity_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
        comment="ID da entidade relacionada",
    )

    # Modelo e configuracao
    provider: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Provider (openai, openrouter, etc)",
    )
    model: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Modelo usado",
    )
    temperature: Mapped[Optional[float]] = mapped_column(
        Float(),
        nullable=True,
        comment="Temperature configurado",
    )
    max_tokens: Mapped[Optional[int]] = mapped_column(
        Integer(),
        nullable=True,
        comment="Max tokens configurado",
    )

    # Prompts
    system_prompt: Mapped[Optional[str]] = mapped_column(
        Text(),
        nullable=True,
        comment="System prompt enviado",
    )
    user_prompt: Mapped[str] = mapped_column(
        Text(),
        nullable=False,
        comment="User prompt enviado",
    )

    # Resposta
    response_content: Mapped[Optional[str]] = mapped_column(
        Text(),
        nullable=True,
        comment="Conteudo da resposta",
    )
    finish_reason: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="Razao de finalizacao",
    )

    # Metricas
    prompt_tokens: Mapped[Optional[int]] = mapped_column(
        Integer(),
        nullable=True,
        comment="Tokens de entrada",
    )
    completion_tokens: Mapped[Optional[int]] = mapped_column(
        Integer(),
        nullable=True,
        comment="Tokens de saida",
    )
    total_tokens: Mapped[Optional[int]] = mapped_column(
        Integer(),
        nullable=True,
        comment="Total de tokens",
    )
    cost_usd: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(precision=10, scale=6),
        nullable=True,
        comment="Custo em USD",
    )
    latency_ms: Mapped[Optional[int]] = mapped_column(
        Integer(),
        nullable=True,
        comment="Latencia em milissegundos",
    )

    # Status
    success: Mapped[bool] = mapped_column(
        Boolean(),
        nullable=False,
        default=True,
        comment="Se a chamada foi bem sucedida",
    )
    error_message: Mapped[Optional[str]] = mapped_column(
        Text(),
        nullable=True,
        comment="Mensagem de erro se falhou",
    )

    # Usuario que disparou
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
        comment="ID do usuario admin",
    )

    def __repr__(self) -> str:
        status = "OK" if self.success else "ERRO"
        return f"<AILog {self.use_case} [{status}] {self.model}>"
