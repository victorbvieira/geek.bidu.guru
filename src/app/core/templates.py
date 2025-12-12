"""
Configuracao centralizada de templates Jinja2.

Inclui filtros customizados para Markdown, formatacao, etc.
"""

from pathlib import Path
from fastapi.templating import Jinja2Templates
from markupsafe import Markup

from app.utils.markdown import markdown_to_html


def setup_templates(directory: Path) -> Jinja2Templates:
    """
    Configura templates Jinja2 com filtros customizados.

    Args:
        directory: Caminho para a pasta de templates

    Returns:
        Instancia de Jinja2Templates configurada
    """
    templates = Jinja2Templates(directory=directory)

    # Adiciona filtros customizados
    templates.env.filters["markdown"] = _markdown_filter
    templates.env.filters["format_price"] = _format_price_filter

    return templates


def _markdown_filter(content: str) -> Markup:
    """
    Filtro Jinja2 para converter Markdown para HTML.

    Uso no template:
        {{ post.content | markdown }}
    """
    if not content:
        return Markup("")

    html = markdown_to_html(content, sanitize=True)
    return Markup(html)


def _format_price_filter(value: float, currency: str = "R$") -> str:
    """
    Filtro Jinja2 para formatar precos.

    Uso no template:
        {{ product.price | format_price }}
    """
    if value is None:
        return ""

    return f"{currency} {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
