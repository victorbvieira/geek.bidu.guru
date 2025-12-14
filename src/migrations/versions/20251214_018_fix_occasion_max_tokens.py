"""Corrige max_tokens das configs de ocasiao para 4000.

Revision ID: 018
Revises: 017
Create Date: 2025-12-14

Esta migration atualiza max_tokens de todas as configs de ocasiao
para 4000, seguindo o padrao das configs de post.
"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "018"
down_revision: Union[str, None] = "017"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Atualiza max_tokens para 4000 em todas as configs de ocasiao."""

    op.execute("""
        UPDATE ai_configs
        SET max_tokens = 4000
        WHERE use_case::text LIKE 'occasion_%'
    """)


def downgrade() -> None:
    """Reverte max_tokens para valores anteriores."""

    op.execute("UPDATE ai_configs SET max_tokens = 500 WHERE use_case = 'occasion_seo_all'::ai_use_case")
    op.execute("UPDATE ai_configs SET max_tokens = 50 WHERE use_case = 'occasion_seo_keyword'::ai_use_case")
    op.execute("UPDATE ai_configs SET max_tokens = 80 WHERE use_case = 'occasion_seo_title'::ai_use_case")
    op.execute("UPDATE ai_configs SET max_tokens = 200 WHERE use_case = 'occasion_seo_description'::ai_use_case")
    op.execute("UPDATE ai_configs SET max_tokens = 100 WHERE use_case = 'occasion_tags'::ai_use_case")
    op.execute("UPDATE ai_configs SET max_tokens = 2000 WHERE use_case = 'occasion_content'::ai_use_case")
