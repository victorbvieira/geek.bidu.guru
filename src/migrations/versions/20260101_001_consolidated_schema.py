"""Consolidated schema snapshot — squash de 40 migrations anteriores.

Revision ID: 001
Revises:
Create Date: 2026-01-01

Esta migration substitui as 40 migrations originais que se acumularam
de 2025-12-11 a 2026-06-01 (ver `legacy_migrations_v1.md` no commit que
introduziu este squash). Em vez de aplicar 40 passos, recria o schema
inteiro a partir dos modelos SQLAlchemy via `metadata.create_all`.

## Para fresh install (banco vazio)
Roda normalmente: `alembic upgrade head`. Aplica 001 (DDL completo) e
depois 002 (seeds).

## Para upgrade de bancos legados (que estavam em revision '029' ou
posteriores das migrations antigas)
NÃO RODE `alembic upgrade head` direto — vai tentar recriar tabelas que
já existem. Em vez disso, faça stamping manual:

    -- Conecte no Postgres do ambiente, e em UMA query:
    DELETE FROM alembic_version;
    INSERT INTO alembic_version (version_num) VALUES ('002');

Isso marca o banco como "já em 002" sem rodar nada. A próxima migration
nova encadeará a partir daí.

## Por que squash agora
- 40 migrations acumuladas com IDs em 3 formatos diferentes (3-dígitos,
  3-dígitos+letra, hash de 12 chars), confuso pra contribuidores novos.
- Restore recente de backup antigo trouxe `alembic_version = '0015'`
  fantasma que parou o startup (PR #2 corrigiu deletando a linha).
- Sistema está estável em produção, momento certo pra resetar a base.

## O que NÃO está nesta migration
- Seeds (admin user + ai_configs): vão na 002.
"""

from typing import Sequence, Union

from alembic import op

# Importa todos os modelos para que metadata.create_all veja tudo
from app.database import Base
import app.models  # noqa: F401 — força import de todos os modelos

# revision identifiers, used by Alembic.
revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# DDL extra que não é gerado por metadata.create_all (triggers, GIN
# indexes pra full-text search, função de update_at).
EXTRA_DDL_UP = """
-- Função reusável para auto-update de updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers aplicados às tabelas com TimestampMixin
CREATE TRIGGER trigger_update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trigger_update_categories_updated_at
    BEFORE UPDATE ON categories
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trigger_update_posts_updated_at
    BEFORE UPDATE ON posts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trigger_update_products_updated_at
    BEFORE UPDATE ON products
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trigger_update_affiliate_clicks_updated_at
    BEFORE UPDATE ON affiliate_clicks
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trigger_update_sessions_updated_at
    BEFORE UPDATE ON sessions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trigger_update_newsletter_signups_updated_at
    BEFORE UPDATE ON newsletter_signups
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- GIN indexes para full-text search em pt-BR
CREATE INDEX IF NOT EXISTS ix_posts_fulltext ON posts USING GIN (
    to_tsvector('portuguese',
        COALESCE(title, '') || ' ' ||
        COALESCE(subtitle, '') || ' ' ||
        COALESCE(content, '') || ' ' ||
        COALESCE(seo_focus_keyword, '')
    )
);

CREATE INDEX IF NOT EXISTS ix_products_fulltext ON products USING GIN (
    to_tsvector('portuguese',
        COALESCE(name, '') || ' ' || COALESCE(short_description, '')
    )
);
"""

EXTRA_DDL_DOWN = """
DROP INDEX IF EXISTS ix_products_fulltext;
DROP INDEX IF EXISTS ix_posts_fulltext;

DROP TRIGGER IF EXISTS trigger_update_newsletter_signups_updated_at ON newsletter_signups;
DROP TRIGGER IF EXISTS trigger_update_sessions_updated_at ON sessions;
DROP TRIGGER IF EXISTS trigger_update_affiliate_clicks_updated_at ON affiliate_clicks;
DROP TRIGGER IF EXISTS trigger_update_products_updated_at ON products;
DROP TRIGGER IF EXISTS trigger_update_posts_updated_at ON posts;
DROP TRIGGER IF EXISTS trigger_update_categories_updated_at ON categories;
DROP TRIGGER IF EXISTS trigger_update_users_updated_at ON users;

DROP FUNCTION IF EXISTS update_updated_at_column();
"""


def upgrade() -> None:
    # 1. Cria todas as tabelas a partir dos modelos SQLAlchemy
    bind = op.get_bind()
    Base.metadata.create_all(bind=bind, checkfirst=True)

    # 2. DDL complementar (triggers, GIN indexes, função)
    op.execute(EXTRA_DDL_UP)


def downgrade() -> None:
    # Remove extras primeiro (não dependem das tabelas em CASCADE)
    op.execute(EXTRA_DDL_DOWN)

    # Drop all tables na ordem inversa (respeitando FKs)
    bind = op.get_bind()
    Base.metadata.drop_all(bind=bind, checkfirst=True)
