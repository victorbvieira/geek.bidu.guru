"""
Utilitarios para processamento de Markdown.

Converte Markdown para HTML com sanitizacao de seguranca.
"""

import markdown
import bleach
from typing import Optional

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
    "div": ["class", "id"],
    "span": ["class", "id"],
    "th": ["colspan", "rowspan"],
    "td": ["colspan", "rowspan"],
    "table": ["class"],
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
