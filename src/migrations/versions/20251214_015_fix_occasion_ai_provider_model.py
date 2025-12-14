"""Corrige provider e modelo das configs de ocasiao.

Revision ID: 015
Revises: 014b
Create Date: 2025-12-14

Esta migration corrige o provider e modelo dos prompts de ocasiao
para usar o mesmo dos posts: openai / gpt-5-nano
"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "015"
down_revision: Union[str, None] = "014b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Atualiza provider e modelo das configs de ocasiao."""

    op.execute("""
        UPDATE ai_configs
        SET provider = 'openai'::ai_provider,
            model = 'gpt-5-nano'
        WHERE use_case::text LIKE 'occasion_%'
    """)


def downgrade() -> None:
    """Reverte para openrouter/gemini."""

    op.execute("""
        UPDATE ai_configs
        SET provider = 'openrouter'::ai_provider,
            model = 'google/gemini-2.0-flash-exp:free'
        WHERE use_case::text LIKE 'occasion_%'
    """)
