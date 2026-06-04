"""Add status (publicacao) column to products.

Revision ID: 004
Revises: 003
Create Date: 2026-06-04

Adiciona o campo `status` na tabela `products` para controlar a publicacao
no portal, independente de `availability` (estoque):

- draft       -> Rascunho (produto recem-criado, nao aparece no portal)
- published   -> Publicado (visivel nas paginas publicas)
- unpublished -> Despublicado (retirado do portal, mantido no cadastro)

Novos produtos nascem como `draft` (server_default). Produtos JA existentes
sao migrados para `published` no backfill, pois estavam visiveis no portal
antes deste campo existir — assim a migration nao "esconde" o catalogo atual.

Idempotente:
- CREATE TYPE protegido por bloco DO/EXCEPTION (duplicate_object).
- ADD COLUMN IF NOT EXISTS.
- Backfill so afeta linhas que ainda estao em 'draft' no momento da migration.

Em fresh install a coluna ja e criada via `metadata.create_all` (migration
001) e a tabela esta vazia, entao o backfill e no-op.
"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "004"
down_revision: Union[str, None] = "003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1) Tipo enum no Postgres (idempotente)
    op.execute(
        """
        DO $$ BEGIN
            CREATE TYPE product_status AS ENUM ('draft', 'published', 'unpublished');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
        """
    )

    # 2) Coluna status (default draft para novos registros)
    op.execute(
        "ALTER TABLE products ADD COLUMN IF NOT EXISTS status product_status "
        "NOT NULL DEFAULT 'draft'"
    )

    # 3) Backfill: produtos pre-existentes estavam ativos no portal -> published
    op.execute("UPDATE products SET status = 'published' WHERE status = 'draft'")

    # 4) Indice para filtros por status
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_products_status ON products (status)"
    )

    op.execute(
        "COMMENT ON COLUMN products.status IS "
        "'Status de publicacao: draft (rascunho), published (publicado), "
        "unpublished (despublicado)'"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_products_status")
    op.execute("ALTER TABLE products DROP COLUMN IF EXISTS status")
    op.execute("DROP TYPE IF EXISTS product_status")
