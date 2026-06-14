"""
Utilitarios para montar/ajustar links de afiliado.
"""

from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse


def build_amazon_affiliate_url(url: str | None, tag: str | None) -> str | None:
    """
    Retorna a URL da Amazon com o parametro `tag` definido como `tag`.

    - Substitui qualquer `tag` existente pela informada (enforce da nossa tag).
    - Preserva os demais parametros e o restante da URL.
    - Se url ou tag forem vazios, ou a url nao for valida, retorna a url
      original sem alteracao.

    Exemplos:
        build_amazon_affiliate_url("https://amazon.com.br/dp/B0X", "geek-20")
            -> "https://amazon.com.br/dp/B0X?tag=geek-20"
        build_amazon_affiliate_url("https://amazon.com.br/dp/B0X?tag=old-20", "geek-20")
            -> "https://amazon.com.br/dp/B0X?tag=geek-20"
    """
    if not url or not tag:
        return url

    cleaned_tag = tag.strip()
    if not cleaned_tag:
        return url

    parsed = urlparse(url.strip())
    if not parsed.scheme or not parsed.netloc:
        # Nao parece uma URL absoluta valida; nao mexe.
        return url

    # Remove qualquer tag existente e adiciona a nossa
    query = [
        (k, v)
        for k, v in parse_qsl(parsed.query, keep_blank_values=True)
        if k.lower() != "tag"
    ]
    query.append(("tag", cleaned_tag))

    return urlunparse(parsed._replace(query=urlencode(query)))
