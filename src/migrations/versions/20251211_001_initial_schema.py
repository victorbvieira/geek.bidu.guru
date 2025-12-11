"""Initial schema - criacao de todas as tabelas base.

Revision ID: 001
Revises:
Create Date: 2025-12-11

Tabelas criadas:
- users: Usuarios admin/editor/author
- categories: Categorias de posts (hierarquicas)
- posts: Artigos/listicles/guides
- products: Produtos de afiliados
- post_products: Relacionamento N:N posts-products
- affiliate_clicks: Tracking de cliques
- sessions: Tracking de visitantes
- newsletter_signups: Inscricoes em newsletter
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade database schema."""

    # Criar ENUMs
    user_role = postgresql.ENUM(
        "admin", "editor", "author", "automation",
        name="user_role",
        create_type=True,
    )
    user_role.create(op.get_bind(), checkfirst=True)

    post_type = postgresql.ENUM(
        "product_single", "listicle", "guide",
        name="post_type",
        create_type=True,
    )
    post_type.create(op.get_bind(), checkfirst=True)

    post_status = postgresql.ENUM(
        "draft", "review", "scheduled", "published", "archived",
        name="post_status",
        create_type=True,
    )
    post_status.create(op.get_bind(), checkfirst=True)

    product_platform = postgresql.ENUM(
        "amazon", "mercadolivre", "shopee",
        name="product_platform",
        create_type=True,
    )
    product_platform.create(op.get_bind(), checkfirst=True)

    product_availability = postgresql.ENUM(
        "available", "unavailable", "unknown",
        name="product_availability",
        create_type=True,
    )
    product_availability.create(op.get_bind(), checkfirst=True)

    price_range = postgresql.ENUM(
        "0-50", "50-100", "100-200", "200+",
        name="price_range",
        create_type=True,
    )
    price_range.create(op.get_bind(), checkfirst=True)

    device_type = postgresql.ENUM(
        "mobile", "desktop", "tablet", "unknown",
        name="device_type",
        create_type=True,
    )
    device_type.create(op.get_bind(), checkfirst=True)

    # ==========================================================================
    # Tabela: users
    # ==========================================================================
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("role", sa.Enum("admin", "editor", "author", "automation", name="user_role"), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=True, default=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )
    op.create_index("idx_users_email", "users", ["email"])
    op.create_index("idx_users_role", "users", ["role"])
    op.create_index("idx_users_active", "users", ["is_active"])

    # ==========================================================================
    # Tabela: categories
    # ==========================================================================
    op.create_table(
        "categories",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("slug", sa.String(120), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("parent_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["parent_id"], ["categories.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
        sa.UniqueConstraint("slug"),
    )
    op.create_index("idx_categories_slug", "categories", ["slug"])
    op.create_index("idx_categories_parent", "categories", ["parent_id"])

    # ==========================================================================
    # Tabela: posts
    # ==========================================================================
    op.create_table(
        "posts",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("type", sa.Enum("product_single", "listicle", "guide", name="post_type"), nullable=False),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("slug", sa.String(250), nullable=False),
        sa.Column("subtitle", sa.String(300), nullable=True),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("featured_image_url", sa.String(500), nullable=True),
        sa.Column("seo_focus_keyword", sa.String(100), nullable=True),
        sa.Column("seo_title", sa.String(60), nullable=True),
        sa.Column("seo_description", sa.String(160), nullable=True),
        sa.Column("category_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("author_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("tags", postgresql.JSONB(astext_type=sa.Text()), server_default="[]", nullable=True),
        sa.Column("status", sa.Enum("draft", "review", "scheduled", "published", "archived", name="post_status"), nullable=True),
        sa.Column("publish_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("shared", sa.Boolean(), nullable=True, default=False),
        sa.Column("view_count", sa.Integer(), server_default="0", nullable=True),
        sa.Column("click_count", sa.Integer(), server_default="0", nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["category_id"], ["categories.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["author_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug"),
    )
    op.create_index("idx_posts_slug", "posts", ["slug"])
    op.create_index("idx_posts_status", "posts", ["status"])
    op.create_index("idx_posts_type", "posts", ["type"])
    op.create_index("idx_posts_category", "posts", ["category_id"])
    op.create_index("idx_posts_author", "posts", ["author_id"])
    op.create_index("idx_posts_publish_at", "posts", ["publish_at"])
    op.create_index("idx_posts_tags", "posts", ["tags"], postgresql_using="gin")
    op.create_index("idx_posts_status_publish", "posts", ["status", "publish_at"])

    # ==========================================================================
    # Tabela: products
    # ==========================================================================
    op.create_table(
        "products",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("name", sa.String(300), nullable=False),
        sa.Column("slug", sa.String(350), nullable=False),
        sa.Column("short_description", sa.String(500), nullable=True),
        sa.Column("long_description", sa.Text(), nullable=True),
        sa.Column("price", sa.Numeric(10, 2), nullable=True),
        sa.Column("currency", sa.String(3), server_default="BRL", nullable=True),
        sa.Column("price_range", sa.Enum("0-50", "50-100", "100-200", "200+", name="price_range"), nullable=True),
        sa.Column("main_image_url", sa.String(500), nullable=True),
        sa.Column("images", postgresql.JSONB(astext_type=sa.Text()), server_default="[]", nullable=True),
        sa.Column("affiliate_url_raw", sa.Text(), nullable=False),
        sa.Column("affiliate_redirect_slug", sa.String(150), nullable=False),
        sa.Column("platform", sa.Enum("amazon", "mercadolivre", "shopee", name="product_platform"), nullable=False),
        sa.Column("platform_product_id", sa.String(200), nullable=True),
        sa.Column("categories", postgresql.JSONB(astext_type=sa.Text()), server_default="[]", nullable=True),
        sa.Column("tags", postgresql.JSONB(astext_type=sa.Text()), server_default="[]", nullable=True),
        sa.Column("availability", sa.Enum("available", "unavailable", "unknown", name="product_availability"), nullable=True),
        sa.Column("rating", sa.Numeric(3, 2), nullable=True),
        sa.Column("review_count", sa.Integer(), server_default="0", nullable=True),
        sa.Column("internal_score", sa.Numeric(5, 2), server_default="0", nullable=True),
        sa.Column("last_price_update", sa.DateTime(timezone=True), nullable=True),
        sa.Column("click_count", sa.Integer(), server_default="0", nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug"),
        sa.UniqueConstraint("affiliate_redirect_slug"),
    )
    op.create_index("idx_products_slug", "products", ["slug"])
    op.create_index("idx_products_platform", "products", ["platform"])
    op.create_index("idx_products_availability", "products", ["availability"])
    op.create_index("idx_products_price_range", "products", ["price_range"])
    op.create_index("idx_products_internal_score", "products", ["internal_score"])
    op.create_index("idx_products_redirect_slug", "products", ["affiliate_redirect_slug"])
    op.create_index("idx_products_platform_id", "products", ["platform", "platform_product_id"])
    op.create_index("idx_products_categories", "products", ["categories"], postgresql_using="gin")
    op.create_index("idx_products_tags", "products", ["tags"], postgresql_using="gin")

    # ==========================================================================
    # Tabela: post_products (N:N)
    # ==========================================================================
    op.create_table(
        "post_products",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("post_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("product_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("position", sa.Integer(), server_default="0", nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["post_id"], ["posts.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("post_id", "product_id", name="uq_post_product"),
    )
    op.create_index("idx_post_products_post", "post_products", ["post_id"])
    op.create_index("idx_post_products_product", "post_products", ["product_id"])
    op.create_index("idx_post_products_position", "post_products", ["post_id", "position"])

    # ==========================================================================
    # Tabela: affiliate_clicks
    # ==========================================================================
    op.create_table(
        "affiliate_clicks",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("product_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("post_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("session_id", sa.String(100), nullable=True),
        sa.Column("user_agent", sa.Text(), nullable=True),
        sa.Column("referer", sa.Text(), nullable=True),
        sa.Column("ip_address", sa.String(45), nullable=True),
        sa.Column("clicked_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["post_id"], ["posts.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_clicks_product", "affiliate_clicks", ["product_id"])
    op.create_index("idx_clicks_post", "affiliate_clicks", ["post_id"])
    op.create_index("idx_clicks_clicked_at", "affiliate_clicks", ["clicked_at"])
    op.create_index("idx_clicks_session", "affiliate_clicks", ["session_id"])
    op.create_index("idx_clicks_analytics", "affiliate_clicks", ["product_id", "clicked_at"])

    # ==========================================================================
    # Tabela: sessions
    # ==========================================================================
    op.create_table(
        "sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("session_id", sa.String(100), nullable=False),
        sa.Column("post_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("user_agent", sa.Text(), nullable=True),
        sa.Column("referer", sa.Text(), nullable=True),
        sa.Column("ip_address", sa.String(45), nullable=True),
        sa.Column("country", sa.String(2), nullable=True),
        sa.Column("device_type", sa.Enum("mobile", "desktop", "tablet", "unknown", name="device_type"), nullable=True),
        sa.Column("time_on_page", sa.Integer(), nullable=True),
        sa.Column("scroll_depth", sa.Integer(), nullable=True),
        sa.Column("is_new_user", sa.Boolean(), server_default="true", nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["post_id"], ["posts.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_sessions_session_id", "sessions", ["session_id"])
    op.create_index("idx_sessions_post", "sessions", ["post_id"])
    op.create_index("idx_sessions_created_at", "sessions", ["created_at"])
    op.create_index("idx_sessions_new_user", "sessions", ["is_new_user"])
    op.create_index("idx_sessions_device", "sessions", ["device_type"])

    # ==========================================================================
    # Tabela: newsletter_signups
    # ==========================================================================
    op.create_table(
        "newsletter_signups",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("name", sa.String(200), nullable=True),
        sa.Column("session_id", sa.String(100), nullable=True),
        sa.Column("source", sa.String(100), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=True),
        sa.Column("subscribed_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("unsubscribed_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )
    op.create_index("idx_newsletter_email", "newsletter_signups", ["email"])
    op.create_index("idx_newsletter_active", "newsletter_signups", ["is_active"])
    op.create_index("idx_newsletter_subscribed_at", "newsletter_signups", ["subscribed_at"])


def downgrade() -> None:
    """Downgrade database schema."""
    # Dropar tabelas na ordem inversa (respeitando FKs)
    op.drop_table("newsletter_signups")
    op.drop_table("sessions")
    op.drop_table("affiliate_clicks")
    op.drop_table("post_products")
    op.drop_table("products")
    op.drop_table("posts")
    op.drop_table("categories")
    op.drop_table("users")

    # Dropar ENUMs
    op.execute("DROP TYPE IF EXISTS device_type")
    op.execute("DROP TYPE IF EXISTS price_range")
    op.execute("DROP TYPE IF EXISTS product_availability")
    op.execute("DROP TYPE IF EXISTS product_platform")
    op.execute("DROP TYPE IF EXISTS post_status")
    op.execute("DROP TYPE IF EXISTS post_type")
    op.execute("DROP TYPE IF EXISTS user_role")
