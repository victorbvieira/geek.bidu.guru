"""
Servico de processamento de conteudo.

Processa Markdown e shortcodes para renderizacao de posts.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.product import ProductRepository
from app.utils.markdown import (
    extract_product_refs,
    markdown_to_html,
    replace_product_shortcodes,
)


async def process_post_content(
    content: str,
    db: AsyncSession,
) -> str:
    """
    Processa conteudo de post com Markdown e shortcodes.

    1. Extrai referencias de produtos [product:slug]
    2. Busca dados dos produtos no banco
    3. Substitui shortcodes por HTML dos cards
    4. Converte Markdown para HTML

    Args:
        content: Conteudo em Markdown com shortcodes
        db: Sessao do banco de dados

    Returns:
        HTML processado com cards de produtos
    """
    if not content:
        return ""

    # 1. Extrai referencias de produtos
    product_refs = extract_product_refs(content)

    # 2. Busca dados dos produtos
    products_data: dict[str, dict] = {}
    if product_refs:
        product_repo = ProductRepository(db)

        for ref in product_refs:
            # Tenta buscar por slug
            product = await product_repo.get_by_slug(ref)

            if product:
                # Converte para dict para o template
                platform_value = (
                    product.platform.value
                    if hasattr(product.platform, "value")
                    else str(product.platform)
                )

                products_data[ref] = {
                    "id": str(product.id),
                    "name": product.name,
                    "slug": product.slug,
                    "price": float(product.price) if product.price else None,
                    "main_image_url": product.main_image_url,
                    "platform": platform_value,
                    "affiliate_redirect_slug": product.affiliate_redirect_slug,
                    "short_description": product.short_description,
                }

    # 3. Substitui shortcodes por HTML
    content_with_products = replace_product_shortcodes(content, products_data)

    # 4. Converte Markdown para HTML
    # Nota: sanitize=False pois os shortcodes ja foram processados
    # e queremos manter o HTML dos cards de produto
    html = markdown_to_html(content_with_products, sanitize=True)

    return html


def get_product_shortcode(slug: str) -> str:
    """
    Retorna shortcode formatado para um produto.

    Args:
        slug: Slug do produto

    Returns:
        Shortcode formatado: [product:slug]
    """
    return f"[product:{slug}]"
