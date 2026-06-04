"""Add internal_notes column to products.

Revision ID: 003
Revises: 002
Create Date: 2026-06-04

Adiciona o campo `internal_notes` (TEXT, nullable) na tabela `products`.

Campo de notas para uso interno da equipe e comunicacao entre usuarios.
Nao e exibido publicamente no site; e acessivel pelas APIs de consulta,
gravacao e atualizacao de produtos (POST/PATCH /api/v1/products).

Idempotente via `ADD COLUMN IF NOT EXISTS` para bancos que ja tenham
a coluna (ex: criada por `metadata.create_all` em fresh install).
"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "ALTER TABLE products ADD COLUMN IF NOT EXISTS internal_notes TEXT"
    )
    op.execute(
        "COMMENT ON COLUMN products.internal_notes IS "
        "'Notas internas para uso da equipe e comunicacao entre usuarios'"
    )


def downgrade() -> None:
    op.execute("ALTER TABLE products DROP COLUMN IF EXISTS internal_notes")
