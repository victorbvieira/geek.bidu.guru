"""
Sistema de Prompts para Geracao de Conteudo.

Define prompts otimizados para diferentes tipos de conteudo:
- Posts de produto unico
- Listicles (Top 10)
- Guias completos
- Posts de ofertas/deals
- Descricoes de produto

Tambem define personas para variacao de tom.
"""

from enum import Enum
from typing import Any

from pydantic import BaseModel


# =============================================================================
# Personas
# =============================================================================


class Persona(str, Enum):
    """Personas para variacao de tom."""

    ANA_COMPRADORA = "ana_compradora"
    LUCAS_GEEK_RAIZ = "lucas_geek_raiz"
    MARINA_DEV = "marina_dev"
    PADRAO = "padrao"


PERSONA_MODIFIERS = {
    Persona.ANA_COMPRADORA: {
        "description": "Compradora de presentes, nao-geek",
        "tone_modifier": "Use linguagem simples, explique referencias geek, foque em 'como vai impressionar quem receber', destaque facilidade de compra",
        "cta_style": "Ver Presente",
        "price_focus": "custo-beneficio",
    },
    Persona.LUCAS_GEEK_RAIZ: {
        "description": "Geek entusiasta, compra para si",
        "tone_modifier": "Use referencias geek avancadas, foque em qualidade e autenticidade, compare com alternativas, seja tecnico quando relevante",
        "cta_style": "Garantir o Meu",
        "price_focus": "qualidade",
    },
    Persona.MARINA_DEV: {
        "description": "Desenvolvedora, foco em produtividade",
        "tone_modifier": "Destaque funcionalidade e durabilidade, mencione casos de uso no trabalho, seja objetivo e pratico",
        "cta_style": "Ver Especificacoes",
        "price_focus": "investimento",
    },
    Persona.PADRAO: {
        "description": "Publico geral geek",
        "tone_modifier": "",
        "cta_style": "Ver Oferta",
        "price_focus": "valor",
    },
}


# =============================================================================
# System Prompts Base
# =============================================================================


SYSTEM_PROMPT_BASE = """Voce e um redator especializado em presentes geek para o blog geek.bidu.guru.

Seu tom e amigavel, informativo e entusiasta, mas sem exageros.
Voce escreve como um amigo geek dando dicas sinceras.

Regras:
- Use linguagem acessivel (nem todos sao experts)
- Inclua referencias geek contextualizadas quando apropriado
- Foque nos beneficios para quem vai dar/receber o presente
- Seja honesto sobre pontos negativos quando houver
- Use emojis com moderacao (maximo 2-3 por secao)
- Escreva em portugues brasileiro
- Evite cliches e frases feitas
- Nao use "voce" demais - varie as construcoes"""


SYSTEM_PROMPT_SEO = """Alem das regras acima, otimize para SEO:
- Use a palavra-chave principal no titulo, primeiro paragrafo e subtitulos
- Crie subtitulos (H2, H3) descritivos e com palavras-chave
- Mantenha paragrafos curtos (3-4 linhas)
- Use listas quando apropriado
- Inclua variações naturais da palavra-chave"""


# =============================================================================
# Prompts por Tipo de Conteudo
# =============================================================================


class PostPrompt(BaseModel):
    """Configuracao de prompt para geracao de post."""

    name: str
    system_prompt: str
    user_prompt_template: str
    max_tokens: int = 2000
    temperature: float = 0.7


# Post de Produto Unico
SINGLE_PRODUCT_POST = PostPrompt(
    name="single_product_post",
    system_prompt=f"""{SYSTEM_PROMPT_BASE}

{SYSTEM_PROMPT_SEO}

Voce esta criando um post focado em um unico produto.""",
    user_prompt_template="""Crie um post completo sobre o produto: {product_name}

Informacoes do produto:
- Preco: R$ {price}
- Plataforma: {platform}
- Descricao: {description}
- Avaliacao: {rating} estrelas
- Categoria: {category}

O post deve conter:
1. Titulo atrativo (max 60 caracteres, inclua a palavra-chave)
2. Introducao envolvente (2-3 paragrafos, mencione o produto logo no inicio)
3. Secao "Para quem e ideal" (bullet points)
4. Secao "O que voce vai amar" (3-5 pontos positivos)
5. Secao "Bom saber" (1-2 pontos de atencao, se houver)
6. Conclusao com call-to-action

Palavra-chave principal: {keyword}

Formato de saida: JSON com campos:
- title: string (max 60 chars)
- meta_description: string (max 155 chars)
- content: string (HTML)
- keywords: array de strings (5-8 keywords)""",
    max_tokens=1500,
    temperature=0.7,
)


# Listicle Top 10
LISTICLE_TOP10 = PostPrompt(
    name="listicle_top10",
    system_prompt=f"""{SYSTEM_PROMPT_BASE}

{SYSTEM_PROMPT_SEO}

Voce esta criando um listicle (lista) comparativo de produtos.
Apresente os produtos de forma organizada e util.""",
    user_prompt_template="""Crie um listicle "Top 10" sobre: {theme}

Produtos disponiveis:
{products_list}

O post deve conter:
1. Titulo no formato "10 Melhores {theme} para {occasion_or_persona}"
2. Introducao explicando os criterios de selecao (2 paragrafos)
3. Para cada produto:
   - Numero e nome do produto (H3)
   - Por que esta na lista (1 paragrafo)
   - Para quem e ideal (1 frase)
   - Preco aproximado
   - Link para mais detalhes
4. Conclusao com dicas finais
5. FAQ (3-5 perguntas frequentes com respostas curtas)

Palavras-chave: {keywords}

Formato de saida: JSON com campos:
- title: string (max 60 chars)
- meta_description: string (max 155 chars)
- content: string (HTML)
- keywords: array de strings""",
    max_tokens=3000,
    temperature=0.7,
)


# Guia Completo
COMPREHENSIVE_GUIDE = PostPrompt(
    name="comprehensive_guide",
    system_prompt=f"""{SYSTEM_PROMPT_BASE}

{SYSTEM_PROMPT_SEO}

Voce esta criando um guia educativo e completo.
O conteudo deve ser aprofundado e util.""",
    user_prompt_template="""Crie um guia completo sobre: {topic}

Contexto: {context}

Produtos relacionados para mencionar:
{products_list}

Estrutura esperada:
1. Titulo no formato "Como {result} - Guia Completo 2025"
2. Introducao (problema + promessa de solucao)
3. 5-7 secoes principais (H2) cobrindo o tema
4. Produtos recomendados intercalados naturalmente
5. Dicas praticas em cada secao
6. Conclusao com proximos passos
7. FAQ (5+ perguntas frequentes)

Palavras-chave alvo: {keywords}

Formato de saida: JSON com campos:
- title: string (max 60 chars)
- meta_description: string (max 155 chars)
- content: string (HTML)
- keywords: array de strings""",
    max_tokens=4000,
    temperature=0.6,
)


# Post de Oferta/Deal
DEAL_POST = PostPrompt(
    name="deal_post",
    system_prompt=f"""{SYSTEM_PROMPT_BASE}

Voce esta criando um post URGENTE sobre uma oferta.
O tom deve criar senso de urgencia sem ser apelativo.""",
    user_prompt_template="""Crie um post de oferta para o produto:

{product_name}
Preco anterior: R$ {previous_price}
Preco atual: R$ {current_price}
Desconto: {discount_percent}%
Economia: R$ {savings}
Plataforma: {platform}

O post deve:
- Ter titulo com urgencia (use "Oferta", "Preco Baixou" ou similar)
- Destacar a economia de forma clara
- Criar senso de urgencia (mas sem mentir sobre prazos)
- Ser curto e direto (max 300 palavras)
- Ter CTA forte

Formato de saida: JSON com campos:
- title: string (max 60 chars)
- meta_description: string (max 155 chars)
- content: string (HTML)
- keywords: array de strings""",
    max_tokens=800,
    temperature=0.8,
)


# =============================================================================
# Prompts para Descricoes de Produto
# =============================================================================


PRODUCT_DESCRIPTION = PostPrompt(
    name="product_description",
    system_prompt=f"""{SYSTEM_PROMPT_BASE}

Voce esta criando descricoes de produto para o catalogo.
Seja conciso mas informativo.""",
    user_prompt_template="""Crie descricoes para o produto:

Nome: {product_name}
Categoria: {category}
Preco: R$ {price}
Plataforma: {platform}
Informacoes disponiveis: {raw_info}

Crie:
1. Descricao curta (max 150 caracteres) - para cards e listagens
2. Descricao longa (2-3 paragrafos) - para pagina do produto
3. Highlights (3-5 pontos principais em bullet points)
4. Publico alvo (1 frase)

Formato de saida: JSON com campos:
- short_description: string
- long_description: string
- highlights: array de strings
- target_audience: string""",
    max_tokens=600,
    temperature=0.6,
)


# =============================================================================
# Funcoes de Formatacao
# =============================================================================


def format_products_list(products: list[dict[str, Any]]) -> str:
    """Formata lista de produtos para o prompt."""
    lines = []
    for i, p in enumerate(products, 1):
        price = f"R$ {p.get('price', 'N/A')}"
        platform = p.get("platform", "N/A")
        lines.append(f"{i}. {p['name']} - {price} ({platform})")
    return "\n".join(lines)


def get_persona_modifier(persona: Persona) -> str:
    """Retorna modificador de tom para a persona."""
    modifier = PERSONA_MODIFIERS.get(persona, {}).get("tone_modifier", "")
    if modifier:
        return f"\n\nModificador de tom: {modifier}"
    return ""


def build_prompt(
    template: PostPrompt,
    persona: Persona = Persona.PADRAO,
    **kwargs,
) -> tuple[str, str]:
    """
    Constroi system e user prompts a partir do template.

    Args:
        template: PostPrompt com template
        persona: Persona para modificar o tom
        **kwargs: Variaveis para substituir no template

    Returns:
        Tupla (system_prompt, user_prompt)
    """
    system = template.system_prompt + get_persona_modifier(persona)
    user = template.user_prompt_template.format(**kwargs)
    return system, user


# =============================================================================
# Exporta templates
# =============================================================================


POST_TEMPLATES = {
    "single_product": SINGLE_PRODUCT_POST,
    "listicle_top10": LISTICLE_TOP10,
    "comprehensive_guide": COMPREHENSIVE_GUIDE,
    "deal_post": DEAL_POST,
    "product_description": PRODUCT_DESCRIPTION,
}


def get_template(name: str) -> PostPrompt | None:
    """Retorna template por nome."""
    return POST_TEMPLATES.get(name)
