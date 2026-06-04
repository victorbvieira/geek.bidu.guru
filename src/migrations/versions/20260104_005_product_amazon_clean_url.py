"""Add amazon_clean_url column to products.

Revision ID: 005
Revises: 004
Create Date: 2026-06-04

Adiciona o campo `amazon_clean_url` (TEXT, nullable) na tabela `products`.

Link "limpo" do produto na Amazon (sem tag de afiliado). No fluxo atual um
agente de IA cadastra o produto e um humano precisa abrir esse link para
gerar manualmente o link de afiliado, ate termos acesso direto a API de
afiliados da Amazon.

Idempotente via `ADD COLUMN IF NOT EXISTS`.
"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "005"
down_revision: Union[str, None] = "004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "ALTER TABLE products ADD COLUMN IF NOT EXISTS amazon_clean_url TEXT"
    )
    op.execute(
        "COMMENT ON COLUMN products.amazon_clean_url IS "
        "'Link limpo do produto na Amazon (sem tag de afiliado), para gerar o "
        "link de referenciado manualmente'"
    )


def downgrade() -> None:
    op.execute("ALTER TABLE products DROP COLUMN IF EXISTS amazon_clean_url")
