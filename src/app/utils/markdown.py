"""
Utilitarios para processamento de Markdown.

Converte Markdown para HTML com sanitizacao de seguranca.
Suporta shortcodes para produtos: [product:slug]
"""

import re
import markdown
import bleach
from typing import Optional
from uuid import UUID

# Tags HTML permitidas apos conversao do Markdown
ALLOWED_TAGS = [
    # Estrutura
    "h1", "h2", "h3", "h4", "h5", "h6",
    "p", "br", "hr",
    "div", "span",
    # Texto
    "strong", "b", "em", "i", "u", "s", "del",
    "mark", "code", "pre", "kbd", "var",
    "sup", "sup",
    # Listas
    "ul", "ol", "li",
    # Links e midia
    "a", "img",
    # Tabelas
    "table", "thead", "tbody", "tr", "th", "td",
    # Citacoes
    "blockquote", "q", "cite",
    # Outras
    "figure", "figcaption",
    "details", "summary",
]

# Atributos permitidos por tag
ALLOWED_ATTRIBUTES = {
    "a": ["href", "title", "target", "rel"],
    "img": ["src", "alt", "title", "width", "height", "loading"],
    "code": ["class"],  # Para syntax highlighting
    "pre": ["class"],
    "div": ["class", "id", "data-product-slug"],  # data-product-slug para embeds
    "span": ["class", "id"],
    "th": ["colspan", "rowspan"],
    "td": ["colspan", "rowspan"],
    "table": ["class"],
    "h4": ["class"],  # Para product-embed-name
}

# Extensoes do Markdown
MARKDOWN_EXTENSIONS = [
    "markdown.extensions.extra",      # Tables, fenced_code, etc
    "markdown.extensions.codehilite", # Syntax highlighting
    "markdown.extensions.toc",        # Table of contents
    "markdown.extensions.sane_lists", # Listas mais previsiveis
    "markdown.extensions.smarty",     # Quotes inteligentes
]

MARKDOWN_EXTENSION_CONFIGS = {
    "markdown.extensions.codehilite": {
        "css_class": "highlight",
        "guess_lang": False,
    },
    "markdown.extensions.toc": {
        "permalink": True,
        "permalink_class": "toc-link",
    },
}


def markdown_to_html(content: str, sanitize: bool = True) -> str:
    """
    Converte Markdown para HTML.

    Args:
        content: Texto em Markdown
        sanitize: Se True, sanitiza HTML para prevenir XSS

    Returns:
        HTML convertido e (opcionalmente) sanitizado
    """
    if not content:
        return ""

    # Converte Markdown para HTML
    md = markdown.Markdown(
        extensions=MARKDOWN_EXTENSIONS,
        extension_configs=MARKDOWN_EXTENSION_CONFIGS,
    )
    html = md.convert(content)

    # Sanitiza se necessario
    if sanitize:
        html = bleach.clean(
            html,
            tags=ALLOWED_TAGS,
            attributes=ALLOWED_ATTRIBUTES,
            strip=True,
        )

    return html


def is_markdown(content: str) -> bool:
    """
    Detecta se o conteudo parece ser Markdown.

    Verifica presenca de padroes comuns de Markdown.
    """
    if not content:
        return False

    markdown_patterns = [
        "# ",      # Headers
        "## ",
        "### ",
        "**",      # Bold
        "__",
        "*",       # Italic/lists
        "- ",      # Lists
        "1. ",     # Ordered lists
        "```",     # Code blocks
        "[",       # Links
        "![",      # Images
        "> ",      # Blockquotes
    ]

    return any(pattern in content for pattern in markdown_patterns)


def extract_toc(content: str) -> Optional[str]:
    """
    Extrai table of contents do Markdown.

    Returns:
        HTML do TOC ou None se nao houver headers
    """
    if not content:
        return None

    md = markdown.Markdown(extensions=["markdown.extensions.toc"])
    md.convert(content)

    # TOC esta disponivel apos conversao
    toc = getattr(md, "toc", "")

    return toc if toc.strip() else None


# -----------------------------------------------------------------------------
# Shortcodes de Produto
# -----------------------------------------------------------------------------

# Pattern para shortcode: [product:identificador]
# Suporta slug ou UUID
PRODUCT_SHORTCODE_PATTERN = re.compile(
    r'\[product:([a-zA-Z0-9_-]+)\]',
    re.IGNORECASE
)


def is_uuid(value: str) -> bool:
    """Verifica se string e um UUID valido."""
    try:
        UUID(value)
        return True
    except ValueError:
        return False


def extract_product_refs(content: str) -> list[str]:
    """
    Extrai referencias de produtos do conteudo.

    Args:
        content: Texto com shortcodes [product:slug]

    Returns:
        Lista de slugs/UUIDs de produtos referenciados
    """
    if not content:
        return []

    matches = PRODUCT_SHORTCODE_PATTERN.findall(content)
    return list(set(matches))  # Remove duplicatas


def render_product_card(product: dict) -> str:
    """
    Renderiza HTML de um card de produto.

    Args:
        product: Dict com dados do produto (name, slug, price, etc)

    Returns:
        HTML do card de produto
    """
    image_html = ""
    if product.get("main_image_url"):
        image_html = f'''
        <a href="/produto/{product['slug']}" class="product-embed-image">
            <img src="{product['main_image_url']}" alt="{product['name']}" loading="lazy">
        </a>'''
    else:
        image_html = '''
        <div class="product-embed-image product-embed-no-image">
            <span>Sem imagem</span>
        </div>'''

    price_html = ""
    if product.get("price"):
        price_html = f'<span class="product-embed-price">R$ {product["price"]:.2f}</span>'

    platform = product.get("platform", "amazon")
    platform_display = platform.title() if isinstance(platform, str) else platform

    return f'''
<div class="product-embed" data-product-slug="{product['slug']}">
    {image_html}
    <div class="product-embed-content">
        <span class="product-embed-platform platform-{platform}">{platform_display}</span>
        <h4 class="product-embed-name">
            <a href="/produto/{product['slug']}">{product['name']}</a>
        </h4>
        {price_html}
        <a href="/goto/{product.get('affiliate_redirect_slug', product['slug'])}"
           class="product-embed-cta"
           target="_blank"
           rel="noopener sponsored">
            Ver oferta
        </a>
    </div>
</div>
'''


def render_product_placeholder(identifier: str) -> str:
    """
    Renderiza placeholder para produto nao encontrado.

    Args:
        identifier: Slug ou UUID do produto

    Returns:
        HTML do placeholder
    """
    return f'''
<div class="product-embed product-embed-not-found">
    <p>Produto nao encontrado: <code>{identifier}</code></p>
</div>
'''


def replace_product_shortcodes(content: str, products: dict[str, dict]) -> str:
    """
    Substitui shortcodes de produto por HTML dos cards.

    Args:
        content: Texto com shortcodes [product:slug]
        products: Dict mapeando slug/uuid para dados do produto

    Returns:
        Texto com shortcodes substituidos por HTML
    """
    if not content:
        return ""

    def replace_match(match: re.Match) -> str:
        identifier = match.group(1)
        product = products.get(identifier)

        if product:
            return render_product_card(product)
        return render_product_placeholder(identifier)

    return PRODUCT_SHORTCODE_PATTERN.sub(replace_match, content)
