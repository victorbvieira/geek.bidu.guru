"""Consolidated seed data — admin user + AI configs essenciais.

Revision ID: 002
Revises: 001
Create Date: 2026-01-01

Insere os dados de seed necessários para que o sistema seja utilizável
imediatamente após `alembic upgrade head` num banco vazio:

1. Admin user padrão (admin@geek.bidu.guru / Admin@123) — TROCAR senha
   após primeiro login.
2. Automation user (automation@geek.bidu.guru) — sem senha válida
   (autentica via API tokens, não senha).
3. AI configs essenciais por use_case (post, occasion, category, product)
   — apontam para openai/gpt-5-nano e gpt-4o-mini por padrão. Ajuste
   provider/model/prompt via admin UI conforme necessário.

Todos os INSERTs usam `ON CONFLICT DO NOTHING` para serem idempotentes:
rodar 2x não duplica.

Em bancos legados que já têm esses dados (vide stamping em 001), basta
fazer `INSERT INTO alembic_version VALUES ('002')` sem rodar a migration.
"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# Password hash para "Admin@123" — bcrypt cost 12.
# CHANGE AFTER FIRST LOGIN!
ADMIN_PASSWORD_HASH = "$2b$12$HMeTFJrvoD/HmG6YjCjtlekrFAyn0oUG/R.7Kml95FS9/y4E/WOgy"

# Hash inválido deliberado — automation user autentica via API token,
# não via senha. Login com senha sempre falha para esse user.
AUTOMATION_INVALID_PASSWORD_HASH = "$2b$12$INVALID_HASH_NO_LOGIN_ALLOWED_VIA_PASSWORD"


def _insert_user(name: str, email: str, password_hash: str, role: str) -> str:
    return f"""
INSERT INTO users (id, name, email, password_hash, role, is_active, created_at, updated_at)
VALUES (
    gen_random_uuid(),
    '{name}',
    '{email}',
    '{password_hash}',
    '{role}',
    true,
    NOW(),
    NOW()
)
ON CONFLICT (email) DO NOTHING;
"""


def _insert_ai_config(
    name: str,
    entity: str,
    use_case: str,
    provider: str,
    model: str,
    system_prompt: str,
    user_prompt: str,
    temperature: float,
    max_tokens: int,
    is_active: bool = True,
) -> str:
    sp = system_prompt.replace("'", "''")
    up = user_prompt.replace("'", "''")
    return f"""
INSERT INTO ai_configs (
    id, name, entity, use_case, provider, model,
    system_prompt, user_prompt, temperature, max_tokens,
    is_active, created_at, updated_at
)
VALUES (
    gen_random_uuid(),
    '{name}',
    '{entity}'::ai_entity,
    '{use_case}'::ai_use_case,
    '{provider}'::ai_provider,
    '{model}',
    '{sp}',
    '{up}',
    {temperature},
    {max_tokens},
    {'true' if is_active else 'false'},
    NOW(),
    NOW()
)
ON CONFLICT DO NOTHING;
"""


def upgrade() -> None:
    # ---------------------------------------------------------------- users
    op.execute(_insert_user(
        name="Administrador",
        email="admin@geek.bidu.guru",
        password_hash=ADMIN_PASSWORD_HASH,
        role="admin",
    ))
    op.execute(_insert_user(
        name="n8n Automation",
        email="automation@geek.bidu.guru",
        password_hash=AUTOMATION_INVALID_PASSWORD_HASH,
        role="automation",
    ))

    # ---------------------------------------------------------- ai_configs
    # Configs essenciais — apontam para modelos baratos por default
    # (openai/gpt-5-nano e gpt-4o-mini). Ajuste via admin UI.

    # Post SEO
    for use_case, temp, tokens, label in [
        ("post_seo_all",         0.6, 500, "Post SEO completo"),
        ("post_seo_keyword",     0.5,  50, "Post keyword"),
        ("post_seo_title",       0.7,  80, "Post título SEO"),
        ("post_seo_description", 0.7, 200, "Post meta description"),
        ("post_tags",            0.5, 100, "Post tags"),
    ]:
        op.execute(_insert_ai_config(
            name=label,
            entity="post",
            use_case=use_case,
            provider="openai",
            model="gpt-5-nano",
            system_prompt="Você é um especialista em SEO para blogs.",
            user_prompt="Título: {{title}}\nSubtítulo: {{subtitle}}\nConteúdo: {{content}}",
            temperature=temp,
            max_tokens=tokens,
        ))

    # Occasion (estado final após fixes 015-018 nas migrations antigas)
    for use_case, temp, label in [
        ("occasion_seo_all",         0.6, "Ocasião SEO completo"),
        ("occasion_seo_keyword",     0.5, "Ocasião keyword"),
        ("occasion_seo_title",       0.7, "Ocasião título"),
        ("occasion_seo_description", 0.7, "Ocasião meta description"),
        ("occasion_content",         0.8, "Ocasião conteúdo introdutório"),
        ("occasion_tags",            0.5, "Ocasião tags"),
    ]:
        op.execute(_insert_ai_config(
            name=label,
            entity="occasion",
            use_case=use_case,
            provider="openai",
            model="gpt-5-nano",
            system_prompt="Você é um especialista em SEO para páginas de ocasiões temáticas.",
            user_prompt="Título: {{title}}\nConteúdo: {{content}}",
            temperature=temp,
            max_tokens=4000,
            is_active=(use_case != "occasion_content"),
        ))

    # Category
    for use_case, label in [
        ("category_seo_keyword",     "Categoria keyword"),
        ("category_seo_title",       "Categoria título"),
        ("category_seo_description", "Categoria meta description"),
        ("category_tags",            "Categoria tags"),
    ]:
        op.execute(_insert_ai_config(
            name=label,
            entity="category",
            use_case=use_case,
            provider="openai",
            model="gpt-5-nano",
            system_prompt="Você é um especialista em SEO para categorias de blog.",
            user_prompt="Título: {{title}}\nConteúdo: {{content}}",
            temperature=1.0,
            max_tokens=4000,
        ))

    # Product (Instagram + tags)
    product_configs = [
        ("product_tags",                0.5, 100, "Produto tags"),
        ("product_instagram_headline",  0.7,  30, "Produto IG headline"),
        ("product_instagram_badge",     0.6,  20, "Produto IG badge"),
        ("product_instagram_title",     0.6,  60, "Produto IG título"),
        ("product_instagram_hashtags",  0.5, 150, "Produto IG hashtags"),
        ("product_instagram_caption",   0.7, 300, "Produto IG caption"),
        ("product_instagram_all",       0.7, 500, "Produto IG completo"),
    ]
    for use_case, temp, tokens, label in product_configs:
        op.execute(_insert_ai_config(
            name=label,
            entity="product",
            use_case=use_case,
            provider="openai",
            model="gpt-4o-mini",
            system_prompt="Você é um especialista em copy para Instagram de e-commerce afiliado.",
            user_prompt="Produto: {{product_name}}\nDescrição: {{content}}\nPreço: {{price}}\nPlataforma: {{platform}}",
            temperature=temp,
            max_tokens=tokens,
        ))


def downgrade() -> None:
    # Remove apenas os seeds que esta migration inseriu.
    # Não remove users criados depois manualmente.
    op.execute(
        "DELETE FROM users WHERE email IN ('admin@geek.bidu.guru', 'automation@geek.bidu.guru')"
    )
    op.execute(
        "DELETE FROM ai_configs WHERE entity IN ('post', 'occasion', 'category', 'product')"
    )
