"""Adiciona tabela ai_configs para configuracao de IA.

Revision ID: 006
Revises: 20251213_7d02c38a81cd_add_content_and_next_review_to_occasions
Create Date: 2025-12-13

Esta migration cria:
- Tabela ai_configs com configuracoes de provider, modelo e prompts
- Seed inicial com prompts otimizados para SEO usando Google Gemini 2.0 Flash
"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "006"
down_revision: Union[str, None] = "7d02c38a81cd"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# Prompts iniciais para geracao de SEO
SEO_PROMPTS = {
    "seo_title": {
        "name": "Titulo SEO",
        "description": "Gera titulo otimizado para SEO (max 60 caracteres) a partir do titulo original.",
        "system_prompt": """Voce e um especialista em SEO para blogs de presentes geek.

Sua tarefa e criar um titulo SEO otimizado a partir do conteudo fornecido.

REGRAS:
1. Maximo de 60 caracteres
2. Inclua a palavra-chave principal no inicio quando possivel
3. Use numeros quando relevante (ex: "10 Melhores", "Top 5")
4. Crie senso de urgencia ou curiosidade
5. Seja especifico e descritivo
6. Evite clickbait exagerado
7. Use linguagem natural em portugues brasileiro

FORMATO DE RESPOSTA:
Retorne APENAS o titulo, sem explicacoes ou formatacao adicional.""",
        "temperature": 0.7,
        "max_tokens": 100,
    },
    "seo_description": {
        "name": "Descricao SEO (Meta Description)",
        "description": "Gera meta description otimizada para SEO (max 160 caracteres).",
        "system_prompt": """Voce e um especialista em SEO para blogs de presentes geek.

Sua tarefa e criar uma meta description otimizada para SEO.

REGRAS:
1. Entre 120-160 caracteres (ideal: 155)
2. Inclua a palavra-chave principal naturalmente
3. Crie um resumo atrativo que incentive o clique
4. Use call-to-action sutil (Descubra, Confira, Veja)
5. Destaque beneficios ou diferenciais
6. Evite promessas vazias
7. Use linguagem natural em portugues brasileiro

FORMATO DE RESPOSTA:
Retorne APENAS a meta description, sem explicacoes ou formatacao adicional.""",
        "temperature": 0.7,
        "max_tokens": 200,
    },
    "seo_keywords": {
        "name": "Palavras-chave SEO",
        "description": "Sugere palavras-chave relevantes para o conteudo.",
        "system_prompt": """Voce e um especialista em SEO para blogs de presentes geek.

Sua tarefa e sugerir palavras-chave relevantes para o conteudo fornecido.

REGRAS:
1. Sugira entre 5-8 palavras-chave
2. Inclua variacoes long-tail (mais especificas)
3. Considere intencao de busca (compra, pesquisa, comparacao)
4. Priorize termos com potencial de busca real
5. Inclua sinonimos e variacoes
6. Pense em como pessoas buscam presentes geek no Brasil

FORMATO DE RESPOSTA:
Retorne as palavras-chave separadas por virgula, sem explicacoes.""",
        "temperature": 0.5,
        "max_tokens": 200,
    },
    "post_content": {
        "name": "Conteudo de Post",
        "description": "Gera conteudo completo para posts do blog.",
        "system_prompt": """Voce e um redator especialista em presentes geek para o blog geek.bidu.guru.

Seu tom e amigavel, informativo e entusiasta, mas sem exageros.
Voce escreve como um amigo geek dando dicas sinceras.

REGRAS:
- Use linguagem acessivel (nem todos sao experts)
- Inclua referencias geek contextualizadas quando apropriado
- Foque nos beneficios para quem vai dar/receber o presente
- Seja honesto sobre pontos negativos quando houver
- Use emojis com moderacao (maximo 2-3 por secao)
- Escreva em portugues brasileiro
- Evite cliches e frases feitas
- Nao use "voce" demais - varie as construcoes

SEO:
- Use a palavra-chave principal no titulo, primeiro paragrafo e subtitulos
- Crie subtitulos (H2, H3) descritivos e com palavras-chave
- Mantenha paragrafos curtos (3-4 linhas)
- Use listas quando apropriado
- Inclua variacoes naturais da palavra-chave""",
        "temperature": 0.7,
        "max_tokens": 3000,
    },
    "product_description": {
        "name": "Descricao de Produto",
        "description": "Gera descricao curta e longa para produtos.",
        "system_prompt": """Voce e um redator especialista em presentes geek para o blog geek.bidu.guru.

Sua tarefa e criar descricoes de produto atrativas e informativas.

REGRAS:
- Destaque caracteristicas unicas e diferenciais
- Mencione para quem o produto e ideal
- Use linguagem persuasiva mas honesta
- Inclua detalhes praticos (tamanho, material, uso)
- Conecte com o universo geek quando relevante
- Escreva em portugues brasileiro

Para DESCRICAO CURTA (max 150 caracteres):
- Seja direto e impactante
- Foque no principal diferencial

Para DESCRICAO LONGA (2-3 paragrafos):
- Seja mais detalhado
- Inclua beneficios e casos de uso""",
        "temperature": 0.6,
        "max_tokens": 800,
    },
    "social_share": {
        "name": "Texto para Redes Sociais",
        "description": "Gera textos para compartilhamento em redes sociais.",
        "system_prompt": """Voce e um social media manager especialista em conteudo geek.

Sua tarefa e criar textos para compartilhamento em diferentes redes sociais.

REGRAS GERAIS:
- Adapte o tom para cada rede
- Use emojis estrategicamente
- Inclua call-to-action
- Escreva em portugues brasileiro

WHATSAPP/TELEGRAM:
- Informal e pessoal
- 2-3 linhas
- Emojis moderados

TWITTER/X:
- Max 280 caracteres
- Hashtags relevantes (2-3)
- Direto ao ponto

LINKEDIN:
- Profissional mas acessivel
- 3-4 linhas
- Foco em valor/aprendizado

FORMATO DE RESPOSTA:
Retorne em JSON com as chaves: whatsapp, twitter, linkedin""",
        "temperature": 0.8,
        "max_tokens": 500,
    },
}


def upgrade() -> None:
    """Cria tabela ai_configs e insere configuracoes iniciais."""

    # Criar ENUMs separadamente (asyncpg nao suporta multiplos comandos)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE ai_provider AS ENUM ('openai', 'anthropic', 'google', 'openrouter');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$
    """)

    op.execute("""
        DO $$ BEGIN
            CREATE TYPE ai_use_case AS ENUM (
                'seo_title',
                'seo_description',
                'seo_keywords',
                'post_content',
                'product_description',
                'social_share',
                'translation'
            );
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$
    """)

    # Criar tabela
    op.execute("""
        CREATE TABLE ai_configs (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            use_case ai_use_case NOT NULL UNIQUE,
            name VARCHAR(100) NOT NULL,
            description VARCHAR(500),
            provider ai_provider NOT NULL DEFAULT 'openrouter',
            model VARCHAR(100) NOT NULL,
            system_prompt TEXT NOT NULL,
            temperature FLOAT NOT NULL DEFAULT 0.7,
            max_tokens INTEGER NOT NULL DEFAULT 500,
            is_active BOOLEAN NOT NULL DEFAULT TRUE,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
    """)

    # Criar indice
    op.execute("CREATE INDEX idx_ai_configs_use_case ON ai_configs(use_case)")

    # Inserir configuracoes iniciais usando Google Gemini 2.0 Flash via OpenRouter
    # Modelo gratuito: google/gemini-2.0-flash-exp:free
    for use_case, config in SEO_PROMPTS.items():
        # Escape aspas simples no system_prompt
        prompt_escaped = config["system_prompt"].replace("'", "''")
        desc_escaped = config["description"].replace("'", "''") if config["description"] else ""

        op.execute(f"""
            INSERT INTO ai_configs (
                id, use_case, name, description, provider, model,
                system_prompt, temperature, max_tokens, is_active
            ) VALUES (
                gen_random_uuid(),
                '{use_case}'::ai_use_case,
                '{config["name"]}',
                '{desc_escaped}',
                'openrouter'::ai_provider,
                'google/gemini-2.0-flash-exp:free',
                '{prompt_escaped}',
                {config["temperature"]},
                {config["max_tokens"]},
                true
            )
        """)


def downgrade() -> None:
    """Remove tabela ai_configs e ENUMs."""

    op.drop_table("ai_configs")

    # Remove ENUMs
    op.execute("DROP TYPE IF EXISTS ai_use_case CASCADE")
    op.execute("DROP TYPE IF EXISTS ai_provider CASCADE")
