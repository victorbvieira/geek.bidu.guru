"""Corrige placeholders nos prompts de ocasiao.

Revision ID: 016
Revises: 015
Create Date: 2025-12-14

Esta migration corrige os placeholders nos prompts de ocasiao:
- Remove {% raw %} e {% endraw %} (sintaxe Jinja2 nao necessaria)
- Substitui {{name}} por {{title}} (placeholder suportado pelo servico)

O servico ai_seo.py substitui:
- {{title}} -> valor do campo title
- {{content}} -> valor do campo content
"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "016"
down_revision: Union[str, None] = "015"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Corrige placeholders nos prompts de ocasiao."""

    # Atualiza system_prompt de todos os prompts de ocasiao
    # Remove {% raw %} e {% endraw %}, substitui {{name}} por {{title}}
    op.execute("""
        UPDATE ai_configs
        SET system_prompt = REPLACE(
            REPLACE(
                REPLACE(system_prompt, '{% raw %}', ''),
                '{% endraw %}', ''
            ),
            '{{name}}', '{{title}}'
        )
        WHERE use_case::text LIKE 'occasion_%'
    """)

    # Atualiza user_prompt de todos os prompts de ocasiao
    op.execute("""
        UPDATE ai_configs
        SET user_prompt = REPLACE(
            REPLACE(
                REPLACE(user_prompt, '{% raw %}', ''),
                '{% endraw %}', ''
            ),
            '{{name}}', '{{title}}'
        )
        WHERE use_case::text LIKE 'occasion_%'
          AND user_prompt IS NOT NULL
    """)


def downgrade() -> None:
    """Reverte para placeholders originais (com {% raw %})."""

    # Reverte system_prompt
    op.execute("""
        UPDATE ai_configs
        SET system_prompt = REPLACE(system_prompt, '{{title}}', '{% raw %}{{name}}{% endraw %}')
        WHERE use_case::text LIKE 'occasion_%'
    """)

    # Reverte user_prompt
    op.execute("""
        UPDATE ai_configs
        SET user_prompt = REPLACE(user_prompt, '{{title}}', '{% raw %}{{name}}{% endraw %}')
        WHERE use_case::text LIKE 'occasion_%'
          AND user_prompt IS NOT NULL
    """)
