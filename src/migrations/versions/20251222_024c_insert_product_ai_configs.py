"""Insere configuracoes de IA para Product (tags e Instagram).

Revision ID: 024c
Revises: 024b
Create Date: 2025-12-22

Esta migration (parte 3 de 3):
- Insere registros na tabela ai_configs para os novos use_cases de Product
- Usa gpt-4o-mini como modelo padrao (OpenAI)
- Configura prompts otimizados para geracao de conteudo de produtos geek

Configuracoes inseridas:
- product_tags: Tags baseadas no titulo e descricao
- product_instagram_headline: Headline de impacto (max 40 chars)
- product_instagram_badge: Badge de destaque (max 20 chars)
- product_instagram_title: Titulo curto (max 100 chars)
- product_instagram_hashtags: Hashtags relevantes
- product_instagram_caption: Caption engajante
- product_instagram_all: Gera todos os campos de uma vez
"""

from typing import Sequence, Union
from uuid import uuid4

from alembic import op
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision: str = "024c"
down_revision: Union[str, None] = "024b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# Configuracoes de IA para Product - usando gpt-4o-mini como padrao
PRODUCT_AI_CONFIGS = [
    # Tags do produto
    {
        "use_case": "product_tags",
        "name": "Tags do Produto",
        "description": "Gera tags relevantes baseadas no nome e descricao do produto",
        "entity": "product",
        "provider": "openai",
        "model": "gpt-4o-mini",
        "temperature": 0.5,
        "max_tokens": 100,
        "system_prompt": """Voce e um especialista em SEO e categorizacao de produtos geek/nerd.
Sua tarefa e gerar tags relevantes para produtos de e-commerce.

Diretrizes:
- Gere entre 3 e 5 tags
- Tags devem ser em portugues brasileiro
- Use termos que compradores usariam para buscar
- Inclua tags de categoria (ex: funko, action figure, camiseta)
- Inclua tags de franquia quando relevante (ex: marvel, star wars, anime)
- Tags devem ser curtas (1-2 palavras cada)
- Nao use hashtags (#)
- Separe tags por virgula

Retorne APENAS as tags separadas por virgula, sem numeracao ou explicacoes.""",
        "user_prompt": """Produto: {{product_name}}

Descricao: {{content}}

Plataforma: {{platform}}

Gere tags relevantes para este produto:""",
    },

    # Instagram - Headline
    {
        "use_case": "product_instagram_headline",
        "name": "Headline Instagram",
        "description": "Gera headline de impacto para post de Instagram (max 40 chars)",
        "entity": "product",
        "provider": "openai",
        "model": "gpt-4o-mini",
        "temperature": 0.7,
        "max_tokens": 30,
        "system_prompt": """Voce e um copywriter especializado em posts de Instagram para produtos geek.
Sua tarefa e criar headlines de impacto que capturem atencao imediatamente.

Diretrizes:
- Maximo 40 caracteres
- Use CAIXA ALTA para impacto
- Crie urgencia ou curiosidade
- Exemplos: "OFERTA IMPERDIVEL!", "SO HOJE!", "CHEGOU!", "EXCLUSIVO!"
- Pode usar emojis no inicio ou fim
- Foque em beneficio ou emocao

Retorne APENAS a headline, sem explicacoes.""",
        "user_prompt": """Produto: {{product_name}}
Preco: {{price}}
Plataforma: {{platform}}

Crie uma headline de impacto:""",
    },

    # Instagram - Badge
    {
        "use_case": "product_instagram_badge",
        "name": "Badge Instagram",
        "description": "Gera texto de badge para destaque (max 20 chars)",
        "entity": "product",
        "provider": "openai",
        "model": "gpt-4o-mini",
        "temperature": 0.6,
        "max_tokens": 20,
        "system_prompt": """Voce e um copywriter especializado em e-commerce.
Sua tarefa e criar badges curtos que destacam produtos.

Diretrizes:
- Maximo 20 caracteres
- Use CAIXA ALTA
- Opcoes comuns: "NOVO!", "BEST SELLER", "LIMITADO", "EXCLUSIVO", "PROMO", "-X% OFF"
- Pode ser sobre novidade, popularidade, preco ou escassez
- Sem emojis em badges

Retorne APENAS o texto do badge, sem explicacoes.""",
        "user_prompt": """Produto: {{product_name}}
Preco: {{price}}

Crie um badge de destaque:""",
    },

    # Instagram - Titulo
    {
        "use_case": "product_instagram_title",
        "name": "Titulo Instagram",
        "description": "Gera titulo curto e atrativo para Instagram (max 100 chars)",
        "entity": "product",
        "provider": "openai",
        "model": "gpt-4o-mini",
        "temperature": 0.6,
        "max_tokens": 60,
        "system_prompt": """Voce e um copywriter especializado em redes sociais para produtos geek.
Sua tarefa e criar titulos curtos e atrativos para posts de Instagram.

Diretrizes:
- Maximo 100 caracteres
- Mantenha a essencia do nome do produto
- Pode simplificar nomes muito longos
- Use linguagem casual e atrativa
- Pode incluir emoji relevante no final
- Foque no beneficio ou caracteristica principal

Retorne APENAS o titulo, sem explicacoes.""",
        "user_prompt": """Nome original: {{product_name}}

Descricao: {{content}}

Crie um titulo curto e atrativo:""",
    },

    # Instagram - Hashtags
    {
        "use_case": "product_instagram_hashtags",
        "name": "Hashtags Instagram",
        "description": "Gera hashtags relevantes para Instagram (sem #)",
        "entity": "product",
        "provider": "openai",
        "model": "gpt-4o-mini",
        "temperature": 0.5,
        "max_tokens": 150,
        "system_prompt": """Voce e um especialista em marketing de Instagram para produtos geek/nerd.
Sua tarefa e gerar hashtags relevantes que maximizam alcance.

Diretrizes:
- Gere entre 10 e 15 hashtags
- NAO inclua o simbolo # (sera adicionado automaticamente)
- Mix de hashtags populares e de nicho
- Inclua: produto, franquia, categoria, interesse
- Em portugues brasileiro
- Hashtags devem ser uma palavra ou palavras juntas (ex: funko, geekbrasil)
- Separe por virgula

Exemplos de hashtags geek: geek, nerd, funko, funkopop, colecionavel, actionfigure, marvel, starwars, anime, mangá, gamer, presentegeek

Retorne APENAS as hashtags separadas por virgula, sem # e sem explicacoes.""",
        "user_prompt": """Produto: {{product_name}}

Descricao: {{content}}

Plataforma: {{platform}}

Gere hashtags relevantes:""",
    },

    # Instagram - Caption
    {
        "use_case": "product_instagram_caption",
        "name": "Caption Instagram",
        "description": "Gera caption engajante para post de Instagram",
        "entity": "product",
        "provider": "openai",
        "model": "gpt-4o-mini",
        "temperature": 0.7,
        "max_tokens": 300,
        "system_prompt": """Voce e um copywriter especializado em Instagram para e-commerce geek.
Sua tarefa e criar captions engajantes que convertem seguidores em compradores.

Diretrizes:
- Entre 100 e 200 caracteres
- Comece com hook que capture atencao
- Use emojis estrategicamente (2-4 no maximo)
- Inclua call-to-action sutil (ex: "Link na bio!")
- Tom casual e entusiasmado
- Fale direto com o fa/colecionador
- NAO inclua hashtags (serao adicionadas separadamente)
- NAO inclua preco (ja aparece na imagem)

Estrutura sugerida:
1. Hook emocional ou pergunta
2. Beneficio ou destaque do produto
3. Call-to-action

Retorne APENAS a caption, sem explicacoes.""",
        "user_prompt": """Produto: {{product_name}}

Descricao: {{content}}

Preco: {{price}}

Crie uma caption engajante:""",
    },

    # Instagram - Todos os campos
    {
        "use_case": "product_instagram_all",
        "name": "Todos Campos Instagram",
        "description": "Gera todos os campos de Instagram de uma vez (headline, badge, titulo, hashtags, caption)",
        "entity": "product",
        "provider": "openai",
        "model": "gpt-4o-mini",
        "temperature": 0.7,
        "max_tokens": 500,
        "system_prompt": """Voce e um copywriter especializado em Instagram para e-commerce geek.
Sua tarefa e gerar todos os campos necessarios para um post de produto no Instagram.

Gere EXATAMENTE neste formato JSON:
{
  "headline": "HEADLINE EM CAIXA ALTA (max 40 chars)",
  "badge": "BADGE CURTO (max 20 chars)",
  "title": "Titulo atrativo do produto (max 100 chars)",
  "hashtags": "hashtag1, hashtag2, hashtag3 (sem #, separadas por virgula)",
  "caption": "Caption engajante com emojis e CTA (100-200 chars, sem hashtags)"
}

Regras:
- headline: Impacto, urgencia, caixa alta, pode ter emoji
- badge: Curto, destaque (NOVO!, BEST SELLER, etc)
- title: Simplificacao atrativa do nome
- hashtags: 10-15 hashtags sem #, em portugues
- caption: Engajante, com emojis, sem hashtags, com CTA

Retorne APENAS o JSON valido, sem explicacoes.""",
        "user_prompt": """Produto: {{product_name}}

Descricao: {{content}}

Preco: {{price}}

Plataforma: {{platform}}

Gere todos os campos para Instagram:""",
    },
]


def upgrade() -> None:
    """Insere configuracoes de IA para Product."""

    connection = op.get_bind()

    for config in PRODUCT_AI_CONFIGS:
        # Verifica se ja existe para evitar duplicatas
        result = connection.execute(
            text("SELECT id FROM ai_configs WHERE use_case = :use_case"),
            {"use_case": config["use_case"]}
        )
        if result.fetchone():
            continue

        # Insere nova configuracao
        connection.execute(
            text("""
                INSERT INTO ai_configs (
                    id, use_case, name, description, entity,
                    provider, model, temperature, max_tokens,
                    system_prompt, user_prompt, is_active,
                    created_at, updated_at
                ) VALUES (
                    :id, :use_case, :name, :description, :entity,
                    :provider, :model, :temperature, :max_tokens,
                    :system_prompt, :user_prompt, true,
                    NOW(), NOW()
                )
            """),
            {
                "id": str(uuid4()),
                "use_case": config["use_case"],
                "name": config["name"],
                "description": config["description"],
                "entity": config["entity"],
                "provider": config["provider"],
                "model": config["model"],
                "temperature": config["temperature"],
                "max_tokens": config["max_tokens"],
                "system_prompt": config["system_prompt"],
                "user_prompt": config["user_prompt"],
            }
        )


def downgrade() -> None:
    """Remove configuracoes de IA para Product."""

    connection = op.get_bind()

    use_cases = [c["use_case"] for c in PRODUCT_AI_CONFIGS]

    for use_case in use_cases:
        connection.execute(
            text("DELETE FROM ai_configs WHERE use_case = :use_case"),
            {"use_case": use_case}
        )
