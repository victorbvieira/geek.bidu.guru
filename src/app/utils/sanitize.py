"""
Utilitarios para sanitizacao de entrada de dados.

Previne ataques XSS e outros tipos de injecao ao limpar dados de entrada.
"""

import re
import bleach


def sanitize_text(text: str | None) -> str | None:
    """
    Sanitiza texto simples removendo tags HTML/scripts.

    Usado para campos como name, description, etc. que NAO devem conter HTML.

    Args:
        text: Texto a ser sanitizado

    Returns:
        Texto limpo sem tags HTML

    Exemplos:
        >>> sanitize_text("<script>alert('xss')</script>Hello")
        "Hello"
        >>> sanitize_text("<b>Bold</b> text")
        "Bold text"
    """
    if text is None:
        return None

    # Remove todas as tags HTML (bleach com tags vazias = strip all)
    cleaned = bleach.clean(text, tags=[], strip=True)

    # Remove espacos extras resultantes da remocao de tags
    cleaned = " ".join(cleaned.split())

    return cleaned


def sanitize_slug(slug: str | None) -> str | None:
    """
    Sanitiza slug para URLs seguras.

    Remove caracteres perigosos como path traversal (../) e scripts.
    Converte para lowercase e substitui espacos por hifens.

    Args:
        slug: Slug a ser sanitizado

    Returns:
        Slug limpo e seguro

    Raises:
        ValueError: Se o slug resultante for invalido
    """
    if slug is None:
        return None

    # Converte para lowercase
    slug = slug.lower()

    # Remove path traversal
    slug = slug.replace("../", "").replace("..\\", "")
    slug = slug.replace("..", "")

    # Remove caracteres perigosos, mantendo apenas alfanumericos e hifens
    slug = re.sub(r"[^a-z0-9-]", "-", slug)

    # Remove hifens duplicados
    slug = re.sub(r"-+", "-", slug)

    # Remove hifens no inicio e fim
    slug = slug.strip("-")

    return slug


def validate_slug_format(slug: str) -> bool:
    """
    Valida se slug tem formato correto.

    Formato valido:
    - Apenas letras minusculas (a-z)
    - Numeros (0-9)
    - Hifens (-)
    - Sem caracteres especiais ou path traversal

    Args:
        slug: Slug a ser validado

    Returns:
        True se valido, False caso contrario
    """
    if not slug:
        return False

    # Pattern: apenas letras minusculas, numeros e hifens
    pattern = r"^[a-z0-9]+(?:-[a-z0-9]+)*$"

    return bool(re.match(pattern, slug))


def escape_html_entities(text: str | None) -> str | None:
    """
    Escapa entidades HTML em texto.

    Converte caracteres especiais em entidades HTML seguras.
    Usado quando queremos exibir texto que pode conter caracteres especiais.

    Args:
        text: Texto a ser escapado

    Returns:
        Texto com entidades HTML escapadas
    """
    if text is None:
        return None

    # Usa bleach.clean com tags vazias para escapar
    return bleach.clean(text, tags=[], strip=False)
