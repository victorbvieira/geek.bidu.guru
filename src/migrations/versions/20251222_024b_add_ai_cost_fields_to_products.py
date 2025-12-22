"""Adiciona campos de custo IA ao modelo Product.

Revision ID: 024b
Revises: 024a
Create Date: 2025-12-22

Esta migration (parte 2 de 3):
- Adiciona ao modelo Product campos para rastrear custos de IA:
  - ai_tokens_used: Total de tokens consumidos
  - ai_prompt_tokens: Tokens de entrada (prompt)
  - ai_completion_tokens: Tokens de saida (completion)
  - ai_cost_usd: Custo total em USD
  - ai_generations_count: Numero de geracoes

Estes campos permitem calcular o ROI de geracoes automaticas de conteudo
para produtos, como tags, descricoes e campos de Instagram.
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "024b"
down_revision: Union[str, None] = "024a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Adiciona campos de custo IA ao modelo Product."""

    # ai_tokens_used - Total de tokens consumidos
    op.add_column(
        "products",
        sa.Column(
            "ai_tokens_used",
            sa.Integer(),
            nullable=False,
            server_default="0",
            comment="Total de tokens consumidos em geracoes de IA",
        ),
    )

    # ai_prompt_tokens - Tokens de entrada
    op.add_column(
        "products",
        sa.Column(
            "ai_prompt_tokens",
            sa.Integer(),
            nullable=False,
            server_default="0",
            comment="Tokens de entrada (prompt) consumidos em geracoes de IA",
        ),
    )

    # ai_completion_tokens - Tokens de saida
    op.add_column(
        "products",
        sa.Column(
            "ai_completion_tokens",
            sa.Integer(),
            nullable=False,
            server_default="0",
            comment="Tokens de saida (completion) consumidos em geracoes de IA",
        ),
    )

    # ai_cost_usd - Custo em USD com 6 casas decimais
    op.add_column(
        "products",
        sa.Column(
            "ai_cost_usd",
            sa.Numeric(precision=10, scale=6),
            nullable=False,
            server_default="0",
            comment="Custo total em USD das geracoes de IA",
        ),
    )

    # ai_generations_count - Contador de geracoes
    op.add_column(
        "products",
        sa.Column(
            "ai_generations_count",
            sa.Integer(),
            nullable=False,
            server_default="0",
            comment="Numero de vezes que IA foi usada para gerar conteudo",
        ),
    )


def downgrade() -> None:
    """Remove campos de custo IA do modelo Product."""

    op.drop_column("products", "ai_generations_count")
    op.drop_column("products", "ai_cost_usd")
    op.drop_column("products", "ai_completion_tokens")
    op.drop_column("products", "ai_prompt_tokens")
    op.drop_column("products", "ai_tokens_used")
