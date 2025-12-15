"""Insere prompt de tags e atualiza configs de ocasiao.

Revision ID: 014b
Revises: 014a
Create Date: 2025-12-14

Esta migration:
- Insere o prompt occasion_tags
- Atualiza temperatura para 1 em todos os prompts de ocasiao
- Ajusta max_tokens para alinhar com os prompts de post

NOTA: Esta migration usa psycopg2 para os INSERTs porque asyncpg
mantem cache da sessao e nao reconhece novos valores de ENUM.
"""

from typing import Sequence, Union

from alembic import op
from sqlalchemy import create_engine, text

# revision identifiers, used by Alembic.
revision: str = "014b"
down_revision: Union[str, None] = "014a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _get_sync_engine():
    """Retorna engine sincrona com psycopg2."""
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from app.config import settings

    sync_url = settings.database_url.replace(
        "postgresql+asyncpg://", "postgresql+psycopg2://"
    )
    return create_engine(sync_url)


# Prompt de tags para Occasion
OCCASION_TAGS_PROMPT = {
    "name": "Tags (Ocasiao)",
    "description": "Gera tags relevantes para ocasioes.",
    "entity": "occasion",
    "system_prompt": """Voce e um especialista em SEO para blogs de presentes geek e produtos de afiliados.

TAREFA: Sugerir tags relevantes para a ocasiao.

CONTEXTO DA OCASIAO:
- Nome da Ocasiao: {% raw %}{{name}}{% endraw %}
- Conteudo: {% raw %}{{content}}{% endraw %}

REGRAS:
- Retornar entre 3 e 5 tags
- Tags em minusculo, sem acentos
- Separadas por virgula
- Relevantes para presentes geek nesta ocasiao
- NAO usar hashtags (#)
- NAO adicionar prefixos ou explicacoes

RESPONDA APENAS COM AS TAGS SEPARADAS POR VIRGULA, sem nenhum texto adicional.
Exemplo: presentes natal, geek, nerd, colecao, decoracao""",
    "user_prompt": """Gere tags para a ocasiao "{% raw %}{{name}}{% endraw %}".

{% if content %}Conteudo atual:
{% raw %}{{content}}{% endraw %}{% endif %}""",
    "temperature": 1.0,
    "max_tokens": 100,
}


def upgrade() -> None:
    """Insere prompt de tags e atualiza configs existentes usando psycopg2."""

    sync_engine = _get_sync_engine()

    with sync_engine.connect() as conn:
        # 1. Inserir prompt de tags
        system_escaped = OCCASION_TAGS_PROMPT["system_prompt"].replace("'", "''")
        user_escaped = OCCASION_TAGS_PROMPT["user_prompt"].replace("'", "''")
        desc_escaped = OCCASION_TAGS_PROMPT["description"].replace("'", "''")

        conn.execute(text(f"""
            INSERT INTO ai_configs (
                id, use_case, name, description, entity, provider, model,
                system_prompt, user_prompt, temperature, max_tokens, is_active
            ) VALUES (
                gen_random_uuid(),
                'occasion_tags'::ai_use_case,
                '{OCCASION_TAGS_PROMPT["name"]}',
                '{desc_escaped}',
                '{OCCASION_TAGS_PROMPT["entity"]}'::ai_entity,
                'openrouter'::ai_provider,
                'google/gemini-2.0-flash-exp:free',
                '{system_escaped}',
                '{user_escaped}',
                {OCCASION_TAGS_PROMPT["temperature"]},
                {OCCASION_TAGS_PROMPT["max_tokens"]},
                true
            )
            ON CONFLICT (use_case) DO NOTHING
        """))

        # 2. Atualizar temperatura para 1 em todos os prompts de ocasiao
        conn.execute(text("""
            UPDATE ai_configs
            SET temperature = 1.0
            WHERE use_case::text LIKE 'occasion_%'
        """))

        # 3. Desativar occasion_content (nao usado)
        conn.execute(text("""
            UPDATE ai_configs
            SET is_active = false
            WHERE use_case = 'occasion_content'::ai_use_case
        """))

        conn.commit()

    sync_engine.dispose()


def downgrade() -> None:
    """Remove prompt de tags e reverte alteracoes."""

    # Remove prompt de tags
    op.execute("""
        DELETE FROM ai_configs
        WHERE use_case = 'occasion_tags'::ai_use_case
    """)

    # Reativa occasion_content
    op.execute("""
        UPDATE ai_configs
        SET is_active = true
        WHERE use_case = 'occasion_content'::ai_use_case
    """)

    # Reverte temperaturas (valores originais variavam)
    op.execute("""
        UPDATE ai_configs SET temperature = 0.6
        WHERE use_case = 'occasion_seo_all'::ai_use_case
    """)
    op.execute("""
        UPDATE ai_configs SET temperature = 0.5
        WHERE use_case = 'occasion_seo_keyword'::ai_use_case
    """)
    op.execute("""
        UPDATE ai_configs SET temperature = 0.7
        WHERE use_case IN ('occasion_seo_title'::ai_use_case, 'occasion_seo_description'::ai_use_case)
    """)
    op.execute("""
        UPDATE ai_configs SET temperature = 0.8
        WHERE use_case = 'occasion_content'::ai_use_case
    """)
