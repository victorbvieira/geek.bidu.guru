"""Adiciona use_cases de IA para Category.

Revision ID: 019a
Revises: 018
Create Date: 2025-12-14

Esta migration (parte 1 de 2):
- Adiciona novos valores ao ENUM ai_use_case para Category:
  - category_seo_keyword: Gera palavra-chave foco
  - category_seo_title: Gera titulo SEO
  - category_seo_description: Gera meta description
  - category_tags: Gera tags

NOTA: Os INSERTs de dados estao na migration 019b.
"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "019a"
down_revision: Union[str, None] = "018"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Adiciona novos valores ao ENUM ai_use_case para Category."""

    # IMPORTANTE: ALTER TYPE ADD VALUE nao pode estar dentro de uma transacao
    # Commitamos a transacao atual antes de adicionar os valores
    op.execute("COMMIT")

    op.execute("ALTER TYPE ai_use_case ADD VALUE IF NOT EXISTS 'category_seo_keyword'")
    op.execute("ALTER TYPE ai_use_case ADD VALUE IF NOT EXISTS 'category_seo_title'")
    op.execute("ALTER TYPE ai_use_case ADD VALUE IF NOT EXISTS 'category_seo_description'")
    op.execute("ALTER TYPE ai_use_case ADD VALUE IF NOT EXISTS 'category_tags'")

    # Iniciamos nova transacao para manter consistencia com o Alembic
    op.execute("BEGIN")


def downgrade() -> None:
    """PostgreSQL nao permite remover valores de ENUM facilmente."""
    pass
