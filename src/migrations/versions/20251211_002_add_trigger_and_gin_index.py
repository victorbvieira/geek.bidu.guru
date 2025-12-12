"""Add trigger updated_at and GIN index for full-text search.

Revision ID: 002
Revises: 001
Create Date: 2025-12-11

Changes:
- Create trigger function to auto-update updated_at timestamp
- Apply trigger to all tables with updated_at column
- Create GIN index on posts for full-text search
- Create GIN index on products for full-text search
"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# Tables that have updated_at column
TABLES_WITH_UPDATED_AT = [
    "users",
    "categories",
    "posts",
    "products",
    "affiliate_clicks",
    "sessions",
    "newsletter_signups",
]


def upgrade() -> None:
    """Upgrade database schema."""

    # ==========================================================================
    # 1. Create trigger function for auto-updating updated_at
    # ==========================================================================
    op.execute("""
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = NOW();
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)

    # ==========================================================================
    # 2. Apply trigger to all tables with updated_at column
    # ==========================================================================
    for table in TABLES_WITH_UPDATED_AT:
        trigger_name = f"trigger_update_{table}_updated_at"
        op.execute(f"""
            DO $$ BEGIN
                CREATE TRIGGER {trigger_name}
                BEFORE UPDATE ON {table}
                FOR EACH ROW
                EXECUTE FUNCTION update_updated_at_column();
            EXCEPTION
                WHEN duplicate_object THEN null;
            END $$;
        """)

    # ==========================================================================
    # 3. Create GIN index on posts for full-text search
    # ==========================================================================
    # Index for searching title, subtitle, content, and tags
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_posts_fulltext
        ON posts
        USING GIN (
            to_tsvector('portuguese',
                COALESCE(title, '') || ' ' ||
                COALESCE(subtitle, '') || ' ' ||
                COALESCE(content, '') || ' ' ||
                COALESCE(seo_focus_keyword, '')
            )
        );
    """)

    # Index for tags array search
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_posts_tags_gin
        ON posts
        USING GIN (tags);
    """)

    # ==========================================================================
    # 4. Create GIN index on products for full-text search
    # ==========================================================================
    # Index for searching name and description
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_products_fulltext
        ON products
        USING GIN (
            to_tsvector('portuguese',
                COALESCE(name, '') || ' ' ||
                COALESCE(short_description, '')
            )
        );
    """)

    # Index for tags and categories array search
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_products_tags_gin
        ON products
        USING GIN (tags);
    """)

    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_products_categories_gin
        ON products
        USING GIN (categories);
    """)


def downgrade() -> None:
    """Downgrade database schema."""

    # Remove GIN indexes
    op.execute("DROP INDEX IF EXISTS ix_products_categories_gin;")
    op.execute("DROP INDEX IF EXISTS ix_products_tags_gin;")
    op.execute("DROP INDEX IF EXISTS ix_products_fulltext;")
    op.execute("DROP INDEX IF EXISTS ix_posts_tags_gin;")
    op.execute("DROP INDEX IF EXISTS ix_posts_fulltext;")

    # Remove triggers
    for table in TABLES_WITH_UPDATED_AT:
        trigger_name = f"trigger_update_{table}_updated_at"
        op.execute(f"DROP TRIGGER IF EXISTS {trigger_name} ON {table};")

    # Remove trigger function
    op.execute("DROP FUNCTION IF EXISTS update_updated_at_column();")
