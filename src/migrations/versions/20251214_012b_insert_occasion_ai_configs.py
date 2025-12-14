"""Insere configuracoes de IA para Occasion.

Revision ID: 012b
Revises: 012a
Create Date: 2025-12-14

Esta migration (parte 2 de 2):
- Insere os 5 novos prompts para Occasion:
  - occasion_seo_all: Gera todos os campos SEO em JSON
  - occasion_seo_keyword: Gera palavra-chave foco
  - occasion_seo_title: Gera titulo SEO
  - occasion_seo_description: Gera meta description
  - occasion_content: Gera conteudo em Markdown

NOTA: Esta migration depende de 012a que cria os ENUMs necessarios.
A separacao em duas migrations evita o erro do PostgreSQL de usar
valores ENUM novos na mesma transacao em que foram criados.
"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "012b"
down_revision: Union[str, None] = "012a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# Prompts com placeholders para Occasion
OCCASION_PROMPTS = {
    "occasion_seo_all": {
        "name": "SEO Completo (Ocasiao)",
        "description": "Gera todos os campos SEO para ocasioes: palavra-chave foco, titulo e descricao.",
        "entity": "occasion",
        "system_prompt": """Voce e um especialista em SEO para blogs de presentes geek e produtos de afiliados.

TAREFA: Gerar TODOS os campos SEO para a ocasiao fornecida.

CONTEXTO DA OCASIAO:
- Nome da Ocasiao: {% raw %}{{name}}{% endraw %}
- Conteudo: {% raw %}{{content}}{% endraw %}

VOCE DEVE RETORNAR UM JSON com exatamente estas chaves:
{
    "seo_focus_keyword": "palavra-chave principal (cauda longa, 2-4 palavras)",
    "seo_title": "titulo otimizado (max 60 caracteres)",
    "seo_description": "meta description (120-160 caracteres)"
}

REGRAS:
- seo_focus_keyword: Uma unica keyword de cauda longa relevante para presentear nesta ocasiao
- seo_title: Maximo 60 caracteres, keyword no inicio, atrativo para quem busca presentes
- seo_description: Entre 120-160 caracteres, resumo atrativo com call-to-action para presentes

IMPORTANTE: Retorne APENAS o JSON, sem explicacoes ou texto adicional.""",
        "user_prompt": """Gere SEO completo para a ocasiao "{% raw %}{{name}}{% endraw %}".

{% if content %}Conteudo atual:
{% raw %}{{content}}{% endraw %}{% endif %}""",
        "temperature": 0.6,
        "max_tokens": 500,
    },
    "occasion_seo_keyword": {
        "name": "Palavra-chave Foco (Ocasiao)",
        "description": "Gera a palavra-chave foco para ocasioes.",
        "entity": "occasion",
        "system_prompt": """Voce e um especialista em SEO para blogs de presentes geek e produtos de afiliados.

TAREFA: Identificar a MELHOR palavra-chave foco para a ocasiao.

CONTEXTO DA OCASIAO:
- Nome da Ocasiao: {% raw %}{{name}}{% endraw %}
- Conteudo: {% raw %}{{content}}{% endraw %}

REGRAS:
- Retornar apenas UMA palavra-chave (pode ser composta, ex: "presentes de natal geek")
- A keyword deve ser especifica para presentes nesta ocasiao
- Priorizar keywords de cauda longa (2-4 palavras)
- Considerar termos que usuarios realmente buscam ao procurar presentes
- NAO usar aspas
- NAO adicionar prefixos ou explicacoes

RESPONDA APENAS COM A PALAVRA-CHAVE, sem nenhum texto adicional.""",
        "user_prompt": """Gere a palavra-chave foco para a ocasiao "{% raw %}{{name}}{% endraw %}".

{% if content %}Conteudo atual:
{% raw %}{{content}}{% endraw %}{% endif %}""",
        "temperature": 0.5,
        "max_tokens": 50,
    },
    "occasion_seo_title": {
        "name": "Titulo SEO (Ocasiao)",
        "description": "Gera titulo otimizado para SEO de ocasioes.",
        "entity": "occasion",
        "system_prompt": """Voce e um especialista em SEO para blogs de presentes geek e produtos de afiliados.

TAREFA: Criar um titulo SEO otimizado para a ocasiao.

CONTEXTO DA OCASIAO:
- Nome da Ocasiao: {% raw %}{{name}}{% endraw %}
- Conteudo: {% raw %}{{content}}{% endraw %}

REGRAS:
- Maximo 60 caracteres (ideal: 50-60)
- Incluir palavra-chave principal no inicio
- Ser atrativo e gerar cliques de pessoas buscando presentes
- Usar linguagem adequada para publico geek brasileiro
- NAO usar aspas no titulo
- NAO adicionar prefixos como "Titulo:" ou explicacoes

RESPONDA APENAS COM O TITULO, sem nenhum texto adicional.""",
        "user_prompt": """Gere o titulo SEO para a ocasiao "{% raw %}{{name}}{% endraw %}".

{% if content %}Conteudo atual:
{% raw %}{{content}}{% endraw %}{% endif %}""",
        "temperature": 0.7,
        "max_tokens": 80,
    },
    "occasion_seo_description": {
        "name": "Descricao SEO (Ocasiao)",
        "description": "Gera meta description otimizada para ocasioes.",
        "entity": "occasion",
        "system_prompt": """Voce e um especialista em SEO para blogs de presentes geek e produtos de afiliados.

TAREFA: Criar uma meta description SEO para a ocasiao.

CONTEXTO DA OCASIAO:
- Nome da Ocasiao: {% raw %}{{name}}{% endraw %}
- Conteudo: {% raw %}{{content}}{% endraw %}

REGRAS:
- Entre 120 e 160 caracteres (ideal: 150-160)
- Resumir o conteudo de forma atrativa para quem busca presentes
- Incluir call-to-action quando possivel
- Usar linguagem adequada para publico geek brasileiro
- NAO usar aspas
- NAO adicionar prefixos como "Descricao:" ou explicacoes

RESPONDA APENAS COM A META DESCRIPTION, sem nenhum texto adicional.""",
        "user_prompt": """Gere a meta description para a ocasiao "{% raw %}{{name}}{% endraw %}".

{% if content %}Conteudo atual:
{% raw %}{{content}}{% endraw %}{% endif %}""",
        "temperature": 0.7,
        "max_tokens": 200,
    },
    "occasion_content": {
        "name": "Conteudo (Ocasiao)",
        "description": "Gera conteudo em Markdown para ocasioes.",
        "entity": "occasion",
        "system_prompt": """Voce e um especialista em conteudo para blogs de presentes geek e produtos de afiliados.

TAREFA: Criar conteudo otimizado em Markdown para a pagina da ocasiao.

CONTEXTO DA OCASIAO:
- Nome da Ocasiao: {% raw %}{{name}}{% endraw %}

REGRAS DE CONTEUDO:
- Escrever em portugues brasileiro informal mas profissional
- Usar tom amigavel e entusiastico sobre a cultura geek
- Estruturar com subtitulos (## e ###) para facilitar leitura
- Incluir introducao explicando a ocasiao e por que presentes geek sao ideais
- Sugerir categorias de presentes (ex: camisetas geek, action figures, etc.)
- Incluir dicas de como escolher o presente ideal
- Texto entre 300-500 palavras
- Usar negrito (**texto**) para destacar pontos importantes
- Usar listas quando apropriado

NAO INCLUIR:
- Links externos ou produtos especificos
- Precos ou promocoes
- Shortcodes de produto ([product:...])
- Emojis em excesso

RESPONDA APENAS COM O CONTEUDO MARKDOWN, sem explicacoes.""",
        "user_prompt": """Gere conteudo em Markdown para a ocasiao "{% raw %}{{name}}{% endraw %}".

O conteudo deve ser informativo, engajador e otimizado para SEO, focando em presentes geek para esta ocasiao.""",
        "temperature": 0.8,
        "max_tokens": 2000,
    },
}


def upgrade() -> None:
    """Insere novos prompts para Occasion."""

    for use_case, config in OCCASION_PROMPTS.items():
        system_prompt_escaped = config["system_prompt"].replace("'", "''")
        user_prompt_escaped = config.get("user_prompt", "").replace("'", "''") if config.get("user_prompt") else ""
        desc_escaped = config["description"].replace("'", "''") if config["description"] else ""

        op.execute(f"""
            INSERT INTO ai_configs (
                id, use_case, name, description, entity, provider, model,
                system_prompt, user_prompt, temperature, max_tokens, is_active
            ) VALUES (
                gen_random_uuid(),
                '{use_case}'::ai_use_case,
                '{config["name"]}',
                '{desc_escaped}',
                '{config["entity"]}'::ai_entity,
                'openrouter'::ai_provider,
                'google/gemini-2.0-flash-exp:free',
                '{system_prompt_escaped}',
                '{user_prompt_escaped}',
                {config["temperature"]},
                {config["max_tokens"]},
                true
            )
            ON CONFLICT (use_case) DO NOTHING
        """)


def downgrade() -> None:
    """Remove os prompts de Occasion."""

    op.execute("""
        DELETE FROM ai_configs
        WHERE use_case IN (
            'occasion_seo_all', 'occasion_seo_keyword', 'occasion_seo_title',
            'occasion_seo_description', 'occasion_content'
        )
    """)
