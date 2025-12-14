"""Adiciona campos de custo de IA na tabela posts.

Revision ID: 009
Revises: 008b
Create Date: 2025-12-14

Esta migration adiciona campos para rastrear custos de geracao de IA:
- ai_tokens_used: Total de tokens consumidos
- ai_cost_usd: Custo total em dolares
- ai_generations_count: Numero de geracoes realizadas

Isso permite calcular o ROI do investimento em IA para geracao de conteudo.
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "009"
down_revision: Union[str, None] = "008b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Adiciona campos de custo de IA."""
    # Tokens totais usados para este post
    op.add_column(
        "posts",
        sa.Column(
            "ai_tokens_used",
            sa.Integer(),
            nullable=False,
            server_default="0",
            comment="Total de tokens consumidos em geracoes de IA",
        ),
    )

    # Custo total em USD
    op.add_column(
        "posts",
        sa.Column(
            "ai_cost_usd",
            sa.Numeric(precision=10, scale=6),
            nullable=False,
            server_default="0",
            comment="Custo total em USD das geracoes de IA",
        ),
    )

    # Contador de geracoes (para media de custo por geracao)
    op.add_column(
        "posts",
        sa.Column(
            "ai_generations_count",
            sa.Integer(),
            nullable=False,
            server_default="0",
            comment="Numero de vezes que IA foi usada para gerar conteudo",
        ),
    )


def downgrade() -> None:
    """Remove campos de custo de IA."""
    op.drop_column("posts", "ai_generations_count")
    op.drop_column("posts", "ai_cost_usd")
    op.drop_column("posts", "ai_tokens_used")
