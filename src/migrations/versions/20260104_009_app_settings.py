"""Create app_settings table.

Revision ID: 009
Revises: 008
Create Date: 2026-06-13

Cria a tabela `app_settings` (key/value) para configuracoes editaveis pelo
admin em runtime, comecando pela tag do programa de afiliados da Amazon
(key = 'amazon_affiliate_tag').

Idempotente via CREATE TABLE IF NOT EXISTS. As linhas sao criadas sob
demanda pela aplicacao (get-or-create), entao a migration nao faz seed.
"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "009"
down_revision: Union[str, None] = "008"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS app_settings (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            key VARCHAR(100) NOT NULL UNIQUE,
            value TEXT,
            description TEXT,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
        """
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_app_settings_key ON app_settings (key)"
    )


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS app_settings")
