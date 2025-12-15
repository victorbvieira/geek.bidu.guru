"""Adiciona campos de custo IA e tags ao modelo Category.

Revision ID: 020
Revises: 019b
Create Date: 2025-12-14

Esta migration adiciona ao modelo Category:
- ai_tokens_used: Total de tokens consumidos
- ai_prompt_tokens: Tokens de entrada (prompt)
- ai_completion_tokens: Tokens de saida (completion)
- ai_cost_usd: Custo total em USD
- ai_generations_count: Numero de geracoes
- tags: Lista de tags (JSONB)
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

# revision identifiers, used by Alembic.
revision: str = "020"
down_revision: Union[str, None] = "019b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Adiciona campos de custo IA e tags ao modelo Category."""

    # Campos de custo IA
    op.add_column(
        "categories",
        sa.Column(
            "ai_tokens_used",
            sa.Integer(),
            nullable=False,
            server_default="0",
            comment="Total de tokens consumidos em geracoes de IA",
        ),
    )
    op.add_column(
        "categories",
        sa.Column(
            "ai_prompt_tokens",
            sa.Integer(),
            nullable=False,
            server_default="0",
            comment="Tokens de entrada (prompt) consumidos em geracoes de IA",
        ),
    )
    op.add_column(
        "categories",
        sa.Column(
            "ai_completion_tokens",
            sa.Integer(),
            nullable=False,
            server_default="0",
            comment="Tokens de saida (completion) consumidos em geracoes de IA",
        ),
    )
    op.add_column(
        "categories",
        sa.Column(
            "ai_cost_usd",
            sa.Numeric(precision=10, scale=6),
            nullable=False,
            server_default="0",
            comment="Custo total em USD das geracoes de IA",
        ),
    )
    op.add_column(
        "categories",
        sa.Column(
            "ai_generations_count",
            sa.Integer(),
            nullable=False,
            server_default="0",
            comment="Numero de vezes que IA foi usada para gerar conteudo",
        ),
    )

    # Campo de tags (JSONB array)
    op.add_column(
        "categories",
        sa.Column(
            "tags",
            JSONB,
            nullable=False,
            server_default="[]",
            comment="Lista de tags da categoria",
        ),
    )

    # Indice GIN para tags
    op.create_index(
        "idx_categories_tags",
        "categories",
        ["tags"],
        postgresql_using="gin",
    )


def downgrade() -> None:
    """Remove campos de custo IA e tags."""

    op.drop_index("idx_categories_tags", table_name="categories")
    op.drop_column("categories", "tags")
    op.drop_column("categories", "ai_generations_count")
    op.drop_column("categories", "ai_cost_usd")
    op.drop_column("categories", "ai_completion_tokens")
    op.drop_column("categories", "ai_prompt_tokens")
    op.drop_column("categories", "ai_tokens_used")
