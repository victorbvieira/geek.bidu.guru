"""Create scheduled_jobs table.

Revision ID: 008
Revises: 007
Create Date: 2026-06-07

Cria a tabela `scheduled_jobs`, que guarda a configuracao e o estado dos
jobs executados pelo dispatcher de cron (POST /api/v1/cron/tick). O
comportamento de cada job vive no codigo (registry); esta tabela permite
ligar/desligar e ver o resultado da ultima execucao pelo admin.

Idempotente via CREATE TABLE IF NOT EXISTS. As linhas (uma por job) sao
criadas sob demanda pela aplicacao (get-or-create no registry), entao a
migration nao faz seed.
"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "008"
down_revision: Union[str, None] = "007"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS scheduled_jobs (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            key VARCHAR(100) NOT NULL UNIQUE,
            name VARCHAR(200) NOT NULL,
            description TEXT,
            enabled BOOLEAN NOT NULL DEFAULT true,
            interval_minutes INTEGER NOT NULL DEFAULT 60,
            last_run_at TIMESTAMPTZ,
            last_status VARCHAR(20),
            last_result TEXT,
            last_duration_ms INTEGER,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
        """
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_scheduled_jobs_key ON scheduled_jobs (key)"
    )


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS scheduled_jobs")
