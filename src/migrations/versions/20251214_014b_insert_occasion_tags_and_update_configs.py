"""Insere prompt de tags e atualiza configs de ocasiao.

Revision ID: 014b
Revises: 014a
Create Date: 2025-12-14

Esta migration:
- Insere o prompt occasion_tags
- Atualiza temperatura para 1 em todos os prompts de ocasiao
- Ajusta max_tokens para alinhar com os prompts de post:
  - occasion_seo_all: 500 (igual post_seo_all)
  - occasion_seo_keyword: 50 (igual post_seo_keyword)
  - occasion_seo_title: 80 (igual post_seo_title)
  - occasion_seo_description: 200 (igual post_seo_description)
  - occasion_tags: 100 (igual post_tags)
  - occasion_content: removido (nao usado por enquanto)
"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "014b"
down_revision: Union[str, None] = "014a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


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
    """Insere prompt de tags e atualiza configs existentes."""

    # 1. Inserir prompt de tags
    system_escaped = OCCASION_TAGS_PROMPT["system_prompt"].replace("'", "''")
    user_escaped = OCCASION_TAGS_PROMPT["user_prompt"].replace("'", "''")
    desc_escaped = OCCASION_TAGS_PROMPT["description"].replace("'", "''")

    op.execute(f"""
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
    """)

    # 2. Atualizar temperatura para 1 em todos os prompts de ocasiao
    op.execute("""
        UPDATE ai_configs
        SET temperature = 1.0
        WHERE use_case::text LIKE 'occasion_%'
    """)

    # 3. Ajustar max_tokens para alinhar com posts
    # occasion_seo_all: 500 (ja esta ok)
    # occasion_seo_keyword: 50 (ja esta ok)
    # occasion_seo_title: 80 (ja esta ok)
    # occasion_seo_description: 200 (ja esta ok)
    # occasion_content: desativar (nao usado)
    op.execute("""
        UPDATE ai_configs
        SET is_active = false
        WHERE use_case = 'occasion_content'::ai_use_case
    """)


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
