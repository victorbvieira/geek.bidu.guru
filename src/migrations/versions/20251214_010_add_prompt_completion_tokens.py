"""Adiciona campos de tokens de entrada/saida separados.

Revision ID: 010
Revises: 009
Create Date: 2025-12-14

Separa os tokens em prompt_tokens (entrada) e completion_tokens (saida)
para melhor visibilidade do custo por tipo de token.
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "010"
down_revision: Union[str, None] = "009"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Adiciona campos de tokens separados."""
    # Tokens de entrada (prompt)
    op.add_column(
        "posts",
        sa.Column(
            "ai_prompt_tokens",
            sa.Integer(),
            nullable=False,
            server_default="0",
            comment="Tokens de entrada (prompt) consumidos em geracoes de IA",
        ),
    )

    # Tokens de saida (completion)
    op.add_column(
        "posts",
        sa.Column(
            "ai_completion_tokens",
            sa.Integer(),
            nullable=False,
            server_default="0",
            comment="Tokens de saida (completion) consumidos em geracoes de IA",
        ),
    )


def downgrade() -> None:
    """Remove campos de tokens separados."""
    op.drop_column("posts", "ai_completion_tokens")
    op.drop_column("posts", "ai_prompt_tokens")
