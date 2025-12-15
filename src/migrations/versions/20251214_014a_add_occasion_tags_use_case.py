"""Adiciona use_case occasion_tags ao ENUM.

Revision ID: 014a
Revises: 013
Create Date: 2025-12-14

Esta migration (parte 1 de 2):
- Adiciona novo valor ao ENUM ai_use_case: occasion_tags

NOTA: O INSERT do prompt esta na migration 014b para evitar
erro do PostgreSQL com valores ENUM novos na mesma transacao.
"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "014a"
down_revision: Union[str, None] = "013"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Adiciona novo valor ao ENUM ai_use_case."""

    # IMPORTANTE: ALTER TYPE ADD VALUE nao pode estar dentro de uma transacao
    # Commitamos a transacao atual antes de adicionar o valor
    op.execute("COMMIT")

    op.execute("ALTER TYPE ai_use_case ADD VALUE IF NOT EXISTS 'occasion_tags'")

    # Iniciamos nova transacao para manter consistencia com o Alembic
    op.execute("BEGIN")


def downgrade() -> None:
    """Remove valor do ENUM.

    Nota: PostgreSQL nao permite remover valores de ENUM facilmente.
    """
    pass
