"""Move variaveis dos system prompts para user prompts nas ocasioes.

Revision ID: 017
Revises: 016
Create Date: 2025-12-14

Esta migration reorganiza os prompts de ocasiao para que:
- system_prompt: contenha apenas instrucoes (sem variaveis)
- user_prompt: contenha o contexto com as variaveis {{title}} e {{content}}

Isso segue o padrao do GPT onde system_prompt e instrucoes fixas
e user_prompt e o conteudo variavel.
"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "017"
down_revision: Union[str, None] = "016"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# Novos prompts limpos (sem variaveis no system_prompt)
OCCASION_PROMPTS_CLEAN = {
    "occasion_seo_keyword": {
        "system_prompt": """Voce e um especialista em SEO para blogs de presentes geek e produtos de afiliados.

TAREFA: Identificar a MELHOR palavra-chave foco para uma ocasiao de presentes.

REGRAS:
- Retornar apenas UMA palavra-chave (pode ser composta, ex: "presentes de natal geek")
- A keyword deve ser especifica para presentes nesta ocasiao
- Priorizar keywords de cauda longa (2-4 palavras)
- Considerar termos que usuarios realmente buscam ao procurar presentes
- NAO usar aspas
- NAO adicionar prefixos ou explicacoes

RESPONDA APENAS COM A PALAVRA-CHAVE, sem nenhum texto adicional.""",
        "user_prompt": """Gere a palavra-chave foco para a ocasiao: {{title}}

Conteudo da pagina:
{{content}}""",
    },
    "occasion_seo_title": {
        "system_prompt": """Voce e um especialista em SEO para blogs de presentes geek e produtos de afiliados.

TAREFA: Criar um titulo SEO otimizado para uma pagina de ocasiao de presentes.

REGRAS:
- Maximo 60 caracteres (ideal: 50-60)
- Incluir palavra-chave principal no inicio
- Ser atrativo e gerar cliques de pessoas buscando presentes
- Usar linguagem adequada para publico geek brasileiro
- NAO usar aspas no titulo
- NAO adicionar prefixos como "Titulo:" ou explicacoes

RESPONDA APENAS COM O TITULO, sem nenhum texto adicional.""",
        "user_prompt": """Gere o titulo SEO para a ocasiao: {{title}}

Conteudo da pagina:
{{content}}""",
    },
    "occasion_seo_description": {
        "system_prompt": """Voce e um especialista em SEO para blogs de presentes geek e produtos de afiliados.

TAREFA: Criar uma meta description SEO para uma pagina de ocasiao de presentes.

REGRAS:
- Entre 120 e 160 caracteres (ideal: 150-160)
- Resumir o conteudo de forma atrativa para quem busca presentes
- Incluir call-to-action quando possivel
- Usar linguagem adequada para publico geek brasileiro
- NAO usar aspas
- NAO adicionar prefixos como "Descricao:" ou explicacoes

RESPONDA APENAS COM A META DESCRIPTION, sem nenhum texto adicional.""",
        "user_prompt": """Gere a meta description para a ocasiao: {{title}}

Conteudo da pagina:
{{content}}""",
    },
    "occasion_seo_all": {
        "system_prompt": """Voce e um especialista em SEO para blogs de presentes geek e produtos de afiliados.

TAREFA: Gerar TODOS os campos SEO para uma pagina de ocasiao de presentes.

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
        "user_prompt": """Gere SEO completo para a ocasiao: {{title}}

Conteudo da pagina:
{{content}}""",
    },
    "occasion_tags": {
        "system_prompt": """Voce e um especialista em SEO para blogs de presentes geek e produtos de afiliados.

TAREFA: Sugerir tags relevantes para uma pagina de ocasiao de presentes.

REGRAS:
- Retornar entre 3 e 5 tags
- Tags em minusculo, sem acentos
- Separadas por virgula
- Relevantes para presentes geek nesta ocasiao
- NAO usar hashtags (#)
- NAO adicionar prefixos ou explicacoes

RESPONDA APENAS COM AS TAGS SEPARADAS POR VIRGULA, sem nenhum texto adicional.
Exemplo: presentes natal, geek, nerd, colecao, decoracao""",
        "user_prompt": """Gere tags para a ocasiao: {{title}}

Conteudo da pagina:
{{content}}""",
    },
}


def upgrade() -> None:
    """Atualiza prompts de ocasiao para ter variaveis apenas no user_prompt."""

    for use_case, prompts in OCCASION_PROMPTS_CLEAN.items():
        system_escaped = prompts["system_prompt"].replace("'", "''")
        user_escaped = prompts["user_prompt"].replace("'", "''")

        op.execute(f"""
            UPDATE ai_configs
            SET system_prompt = '{system_escaped}',
                user_prompt = '{user_escaped}'
            WHERE use_case = '{use_case}'::ai_use_case
        """)


def downgrade() -> None:
    """Reverte para prompts anteriores (com variaveis no system_prompt)."""
    # Nao implementado - seria muito complexo reverter
    pass
