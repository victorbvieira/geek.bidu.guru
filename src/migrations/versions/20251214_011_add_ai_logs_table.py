"""Adiciona tabela de logs de chamadas LLM.

Revision ID: 011
Revises: 010
Create Date: 2025-12-14

Cria tabela ai_logs para registrar todas as chamadas ao LLM,
incluindo prompt enviado, resposta recebida, tokens e custos.
Util para debug e auditoria.
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision: str = "011"
down_revision: Union[str, None] = "010"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Cria tabela de logs de LLM."""
    op.create_table(
        "ai_logs",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),

        # Contexto da chamada
        sa.Column("use_case", sa.String(50), nullable=False, comment="Caso de uso (post_tags, seo_title, etc)"),
        sa.Column("entity_type", sa.String(50), nullable=True, comment="Tipo da entidade (post, category, etc)"),
        sa.Column("entity_id", UUID(as_uuid=True), nullable=True, comment="ID da entidade relacionada"),

        # Modelo e configuracao
        sa.Column("provider", sa.String(50), nullable=False, comment="Provider (openai, openrouter, etc)"),
        sa.Column("model", sa.String(100), nullable=False, comment="Modelo usado"),
        sa.Column("temperature", sa.Float(), nullable=True, comment="Temperature configurado"),
        sa.Column("max_tokens", sa.Integer(), nullable=True, comment="Max tokens configurado"),

        # Prompts
        sa.Column("system_prompt", sa.Text(), nullable=True, comment="System prompt enviado"),
        sa.Column("user_prompt", sa.Text(), nullable=False, comment="User prompt enviado"),

        # Resposta
        sa.Column("response_content", sa.Text(), nullable=True, comment="Conteudo da resposta"),
        sa.Column("finish_reason", sa.String(50), nullable=True, comment="Razao de finalizacao"),

        # Metricas
        sa.Column("prompt_tokens", sa.Integer(), nullable=True, comment="Tokens de entrada"),
        sa.Column("completion_tokens", sa.Integer(), nullable=True, comment="Tokens de saida"),
        sa.Column("total_tokens", sa.Integer(), nullable=True, comment="Total de tokens"),
        sa.Column("cost_usd", sa.Numeric(precision=10, scale=6), nullable=True, comment="Custo em USD"),
        sa.Column("latency_ms", sa.Integer(), nullable=True, comment="Latencia em milissegundos"),

        # Status
        sa.Column("success", sa.Boolean(), nullable=False, default=True, comment="Se a chamada foi bem sucedida"),
        sa.Column("error_message", sa.Text(), nullable=True, comment="Mensagem de erro se falhou"),

        # Usuario que disparou
        sa.Column("user_id", UUID(as_uuid=True), nullable=True, comment="ID do usuario admin"),
    )

    # Indices para consultas comuns
    op.create_index("idx_ai_logs_created_at", "ai_logs", ["created_at"])
    op.create_index("idx_ai_logs_use_case", "ai_logs", ["use_case"])
    op.create_index("idx_ai_logs_entity", "ai_logs", ["entity_type", "entity_id"])
    op.create_index("idx_ai_logs_success", "ai_logs", ["success"])


def downgrade() -> None:
    """Remove tabela de logs."""
    op.drop_index("idx_ai_logs_success")
    op.drop_index("idx_ai_logs_entity")
    op.drop_index("idx_ai_logs_use_case")
    op.drop_index("idx_ai_logs_created_at")
    op.drop_table("ai_logs")
