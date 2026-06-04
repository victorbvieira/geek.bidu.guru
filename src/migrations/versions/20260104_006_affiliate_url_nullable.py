"""Make products.affiliate_url_raw nullable.

Revision ID: 006
Revises: 005
Create Date: 2026-06-04

Torna `affiliate_url_raw` opcional no cadastro. No fluxo atual um agente de IA
cadastra o produto (como rascunho) antes de termos o link de afiliado — o link
e gerado manualmente depois, a partir do `amazon_clean_url`.

A obrigatoriedade passa a ser uma regra de negocio na aplicacao: um produto so
pode ser PUBLICADO se tiver `affiliate_url_raw` preenchido. O banco apenas
deixa de exigir NOT NULL.

Idempotente: DROP NOT NULL e no-op se a coluna ja for nullable.
"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "006"
down_revision: Union[str, None] = "005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TABLE products ALTER COLUMN affiliate_url_raw DROP NOT NULL")


def downgrade() -> None:
    # Preenche eventuais nulos antes de restaurar a constraint NOT NULL
    op.execute(
        "UPDATE products SET affiliate_url_raw = '' WHERE affiliate_url_raw IS NULL"
    )
    op.execute("ALTER TABLE products ALTER COLUMN affiliate_url_raw SET NOT NULL")
