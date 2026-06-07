"""Add preferences (JSONB) column to users.

Revision ID: 007
Revises: 006
Create Date: 2026-06-07

Adiciona o campo `preferences` (JSONB) na tabela `users`. Guarda preferencias
por usuario — atualmente o filtro de status pre-carregado nas listagens do
admin de posts e produtos. Ex:

    {"posts_default_status": "draft", "products_default_status": "draft"}

Default '{}' (sem preferencias). Idempotente via ADD COLUMN IF NOT EXISTS.
"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "007"
down_revision: Union[str, None] = "006"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS preferences JSONB "
        "NOT NULL DEFAULT '{}'::jsonb"
    )
    op.execute(
        "COMMENT ON COLUMN users.preferences IS "
        "'Preferencias do usuario (ex: filtro de status pre-carregado no admin)'"
    )


def downgrade() -> None:
    op.execute("ALTER TABLE users DROP COLUMN IF EXISTS preferences")
