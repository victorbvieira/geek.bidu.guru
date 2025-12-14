"""Insere configuracoes de IA para Posts.

Revision ID: 008b
Revises: 008a
Create Date: 2025-12-14

Esta migration (parte 2 de 2):
- Insere os 5 novos prompts para Post:
  - post_seo_all: Gera todos os campos SEO em JSON
  - post_seo_keyword: Gera palavra-chave foco
  - post_seo_title: Gera titulo SEO
  - post_seo_description: Gera meta description
  - post_tags: Gera tags

NOTA: Esta migration depende de 008a que cria os ENUMs necessarios.
A separacao em duas migrations evita o erro do PostgreSQL de usar
valores ENUM novos na mesma transacao em que foram criados.
"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "008b"
down_revision: Union[str, None] = "008a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# Prompts com placeholders para Post
POST_PROMPTS = {
    "post_seo_all": {
        "name": "SEO Completo (Post)",
        "description": "Gera todos os campos SEO para posts: palavra-chave foco, titulo, descricao e tags.",
        "entity": "post",
        "system_prompt": """Voce e um especialista em SEO para blogs de presentes geek e produtos de afiliados.

TAREFA: Gerar TODOS os campos SEO para o post fornecido.

CONTEXTO DO POST:
- Titulo: {{title}}
- Subtitulo: {{subtitle}}
- Conteudo: {{content}}

VOCE DEVE RETORNAR UM JSON com exatamente estas chaves:
{
    "seo_focus_keyword": "palavra-chave principal (cauda longa, 2-4 palavras)",
    "seo_title": "titulo otimizado (max 60 caracteres)",
    "seo_description": "meta description (120-160 caracteres)",
    "tags": ["tag1", "tag2", "tag3", "tag4", "tag5"]
}

REGRAS:
- seo_focus_keyword: Uma unica keyword de cauda longa relevante para o conteudo
- seo_title: Maximo 60 caracteres, keyword no inicio, atrativo
- seo_description: Entre 120-160 caracteres, resumo atrativo com call-to-action
- tags: 3 a 5 tags relevantes, em minusculo, sem acentos

IMPORTANTE: Retorne APENAS o JSON, sem explicacoes ou texto adicional.""",
        "temperature": 0.6,
        "max_tokens": 500,
    },
    "post_seo_keyword": {
        "name": "Palavra-chave Foco (Post)",
        "description": "Gera a palavra-chave foco para posts.",
        "entity": "post",
        "system_prompt": """Voce e um especialista em SEO para blogs de presentes geek e produtos de afiliados.

TAREFA: Identificar a MELHOR palavra-chave foco para o post.

CONTEXTO DO POST:
- Titulo: {{title}}
- Subtitulo: {{subtitle}}
- Conteudo: {{content}}

REGRAS:
- Retornar apenas UMA palavra-chave (pode ser composta, ex: "funko pop marvel")
- A keyword deve ser especifica e relevante
- Priorizar keywords de cauda longa (2-4 palavras)
- Considerar termos que usuarios realmente buscam
- NAO usar aspas
- NAO adicionar prefixos ou explicacoes

RESPONDA APENAS COM A PALAVRA-CHAVE, sem nenhum texto adicional.""",
        "temperature": 0.5,
        "max_tokens": 50,
    },
    "post_seo_title": {
        "name": "Titulo SEO (Post)",
        "description": "Gera titulo otimizado para SEO de posts.",
        "entity": "post",
        "system_prompt": """Voce e um especialista em SEO para blogs de presentes geek e produtos de afiliados.

TAREFA: Criar um titulo SEO otimizado para o post.

CONTEXTO DO POST:
- Titulo: {{title}}
- Subtitulo: {{subtitle}}
- Conteudo: {{content}}

REGRAS:
- Maximo 60 caracteres (ideal: 50-60)
- Incluir palavra-chave principal no inicio
- Ser atrativo e gerar cliques
- Usar linguagem adequada para publico geek brasileiro
- NAO usar aspas no titulo
- NAO adicionar prefixos como "Titulo:" ou explicacoes

RESPONDA APENAS COM O TITULO, sem nenhum texto adicional.""",
        "temperature": 0.7,
        "max_tokens": 80,
    },
    "post_seo_description": {
        "name": "Descricao SEO (Post)",
        "description": "Gera meta description otimizada para posts.",
        "entity": "post",
        "system_prompt": """Voce e um especialista em SEO para blogs de presentes geek e produtos de afiliados.

TAREFA: Criar uma meta description SEO para o post.

CONTEXTO DO POST:
- Titulo: {{title}}
- Subtitulo: {{subtitle}}
- Conteudo: {{content}}

REGRAS:
- Entre 120 e 160 caracteres (ideal: 150-160)
- Resumir o conteudo de forma atrativa
- Incluir call-to-action quando possivel
- Usar linguagem adequada para publico geek brasileiro
- NAO usar aspas
- NAO adicionar prefixos como "Descricao:" ou explicacoes

RESPONDA APENAS COM A META DESCRIPTION, sem nenhum texto adicional.""",
        "temperature": 0.7,
        "max_tokens": 200,
    },
    "post_tags": {
        "name": "Tags (Post)",
        "description": "Gera tags relevantes para posts.",
        "entity": "post",
        "system_prompt": """Voce e um especialista em SEO para blogs de presentes geek e produtos de afiliados.

TAREFA: Sugerir tags relevantes para o post.

CONTEXTO DO POST:
- Titulo: {{title}}
- Subtitulo: {{subtitle}}
- Conteudo: {{content}}

REGRAS:
- Retornar entre 3 e 5 tags
- Tags em minusculo, sem acentos
- Separadas por virgula
- Relevantes para o conteudo geek/presente
- NAO usar hashtags (#)
- NAO adicionar prefixos ou explicacoes

RESPONDA APENAS COM AS TAGS SEPARADAS POR VIRGULA, sem nenhum texto adicional.
Exemplo: funko pop, marvel, presente geek, colecao""",
        "temperature": 0.5,
        "max_tokens": 100,
    },
}


def upgrade() -> None:
    """Insere novos prompts para Post."""

    for use_case, config in POST_PROMPTS.items():
        prompt_escaped = config["system_prompt"].replace("'", "''")
        desc_escaped = config["description"].replace("'", "''") if config["description"] else ""

        op.execute(f"""
            INSERT INTO ai_configs (
                id, use_case, name, description, entity, provider, model,
                system_prompt, temperature, max_tokens, is_active
            ) VALUES (
                gen_random_uuid(),
                '{use_case}'::ai_use_case,
                '{config["name"]}',
                '{desc_escaped}',
                '{config["entity"]}'::ai_entity,
                'openai'::ai_provider,
                'gpt-5-nano',
                '{prompt_escaped}',
                {config["temperature"]},
                {config["max_tokens"]},
                true
            )
            ON CONFLICT (use_case) DO NOTHING
        """)


def downgrade() -> None:
    """Remove os prompts de Post."""

    op.execute("""
        DELETE FROM ai_configs
        WHERE use_case IN (
            'post_seo_all', 'post_seo_keyword', 'post_seo_title',
            'post_seo_description', 'post_tags'
        )
    """)
