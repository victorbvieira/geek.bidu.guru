"""Insere configuracoes de IA para Category.

Revision ID: 019b
Revises: 019a
Create Date: 2025-12-14

Esta migration (parte 2 de 2):
- Insere os 4 novos prompts para Category
- Usa mesmo provider/modelo/temp/max_tokens dos posts

NOTA: Esta migration usa psycopg2 para os INSERTs porque asyncpg
mantem cache da sessao e nao reconhece novos valores de ENUM.
"""

from typing import Sequence, Union

from alembic import op
from sqlalchemy import create_engine, text

# revision identifiers, used by Alembic.
revision: str = "019b"
down_revision: Union[str, None] = "019a"
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


# Prompts para Category (variaveis apenas no user_prompt)
CATEGORY_PROMPTS = {
    "category_seo_keyword": {
        "name": "Palavra-chave Foco (Categoria)",
        "description": "Gera a palavra-chave foco para categorias.",
        "entity": "category",
        "system_prompt": """Voce e um especialista em SEO para blogs de presentes geek e produtos de afiliados.

TAREFA: Identificar a MELHOR palavra-chave foco para uma categoria de produtos/presentes geek.

REGRAS:
- Retornar apenas UMA palavra-chave (pode ser composta, ex: "presentes geek marvel")
- A keyword deve ser especifica para a categoria
- Priorizar keywords de cauda longa (2-4 palavras)
- Considerar termos que usuarios realmente buscam
- NAO usar aspas
- NAO adicionar prefixos ou explicacoes

RESPONDA APENAS COM A PALAVRA-CHAVE, sem nenhum texto adicional.""",
        "user_prompt": """Gere a palavra-chave foco para a categoria: {{title}}

Descricao da categoria:
{{content}}""",
    },
    "category_seo_title": {
        "name": "Titulo SEO (Categoria)",
        "description": "Gera titulo otimizado para SEO de categorias.",
        "entity": "category",
        "system_prompt": """Voce e um especialista em SEO para blogs de presentes geek e produtos de afiliados.

TAREFA: Criar um titulo SEO otimizado para uma pagina de categoria de produtos/presentes geek.

REGRAS:
- Maximo 60 caracteres (ideal: 50-60)
- Incluir palavra-chave principal no inicio
- Ser atrativo e gerar cliques
- Usar linguagem adequada para publico geek brasileiro
- NAO usar aspas no titulo
- NAO adicionar prefixos como "Titulo:" ou explicacoes

RESPONDA APENAS COM O TITULO, sem nenhum texto adicional.""",
        "user_prompt": """Gere o titulo SEO para a categoria: {{title}}

Descricao da categoria:
{{content}}""",
    },
    "category_seo_description": {
        "name": "Descricao SEO (Categoria)",
        "description": "Gera meta description otimizada para categorias.",
        "entity": "category",
        "system_prompt": """Voce e um especialista em SEO para blogs de presentes geek e produtos de afiliados.

TAREFA: Criar uma meta description SEO para uma pagina de categoria de produtos/presentes geek.

REGRAS:
- Entre 120 e 160 caracteres (ideal: 150-160)
- Resumir a categoria de forma atrativa
- Incluir call-to-action quando possivel
- Usar linguagem adequada para publico geek brasileiro
- NAO usar aspas
- NAO adicionar prefixos como "Descricao:" ou explicacoes

RESPONDA APENAS COM A META DESCRIPTION, sem nenhum texto adicional.""",
        "user_prompt": """Gere a meta description para a categoria: {{title}}

Descricao da categoria:
{{content}}""",
    },
    "category_tags": {
        "name": "Tags (Categoria)",
        "description": "Gera tags relevantes para categorias.",
        "entity": "category",
        "system_prompt": """Voce e um especialista em SEO para blogs de presentes geek e produtos de afiliados.

TAREFA: Sugerir tags relevantes para uma categoria de produtos/presentes geek.

REGRAS:
- Retornar entre 3 e 5 tags
- Tags em minusculo, sem acentos
- Separadas por virgula
- Relevantes para a categoria geek
- NAO usar hashtags (#)
- NAO adicionar prefixos ou explicacoes

RESPONDA APENAS COM AS TAGS SEPARADAS POR VIRGULA, sem nenhum texto adicional.
Exemplo: presentes geek, funko pop, colecao, marvel, decoracao""",
        "user_prompt": """Gere tags para a categoria: {{title}}

Descricao da categoria:
{{content}}""",
    },
}


def upgrade() -> None:
    """Insere novos prompts para Category usando psycopg2."""

    sync_engine = _get_sync_engine()

    with sync_engine.connect() as conn:
        for use_case, config in CATEGORY_PROMPTS.items():
            system_escaped = config["system_prompt"].replace("'", "''")
            user_escaped = config["user_prompt"].replace("'", "''")
            desc_escaped = config["description"].replace("'", "''")

            conn.execute(text(f"""
                INSERT INTO ai_configs (
                    id, use_case, name, description, entity, provider, model,
                    system_prompt, user_prompt, temperature, max_tokens, is_active
                ) VALUES (
                    gen_random_uuid(),
                    '{use_case}'::ai_use_case,
                    '{config["name"]}',
                    '{desc_escaped}',
                    '{config["entity"]}'::ai_entity,
                    'openai'::ai_provider,
                    'gpt-5-nano',
                    '{system_escaped}',
                    '{user_escaped}',
                    1.0,
                    4000,
                    true
                )
                ON CONFLICT (use_case) DO NOTHING
            """))
        conn.commit()

    sync_engine.dispose()


def downgrade() -> None:
    """Remove os prompts de Category."""

    op.execute("""
        DELETE FROM ai_configs
        WHERE use_case IN (
            'category_seo_keyword', 'category_seo_title',
            'category_seo_description', 'category_tags'
        )
    """)
