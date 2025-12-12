"""
Rotas SSR para paginas publicas de produtos.

Renderiza templates HTML para:
- Listagem de produtos
- Produto individual
"""

from pathlib import Path

from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import HTMLResponse

from app.api.deps import ProductRepo
from app.config import settings
from app.core.templates import setup_templates
from app.models.product import ProductAvailability

# Router para rotas publicas de produtos
router = APIRouter(tags=["products-ssr"])

# Templates com filtros customizados
BASE_DIR = Path(__file__).resolve().parent.parent
templates = setup_templates(BASE_DIR / "templates")


def get_base_url() -> str:
    """Retorna a URL base do site."""
    return settings.app_url.rstrip("/")


# -----------------------------------------------------------------------------
# Listagem de Produtos
# -----------------------------------------------------------------------------


@router.get("/produtos", response_class=HTMLResponse)
async def list_products(
    request: Request,
    repo: ProductRepo,
    page: int = 1,
    per_page: int = 12,
):
    """
    Pagina de listagem de produtos disponiveis.

    Exibe produtos disponiveis ordenados por score interno.
    """
    # Calcula offset para paginacao
    skip = (page - 1) * per_page

    # Busca produtos disponiveis
    products = await repo.get_available(skip=skip, limit=per_page)
    total = await repo.count()

    # Calcula total de paginas
    pages = (total + per_page - 1) // per_page if total > 0 else 1

    base_url = get_base_url()
    canonical_url = f"{base_url}/produtos" if page == 1 else f"{base_url}/produtos?page={page}"

    return templates.TemplateResponse(
        request=request,
        name="products/list.html",
        context={
            "title": "Produtos - geek.bidu.guru",
            "description": "Descubra os melhores produtos geek selecionados para voce",
            "products": products,
            "page": page,
            "per_page": per_page,
            "total": total,
            "pages": pages,
            "has_prev": page > 1,
            "has_next": page < pages,
            # SEO
            "base_url": base_url,
            "canonical_url": canonical_url,
            "og_type": "website",
            "breadcrumbs": [
                {"name": "Home", "url": base_url},
                {"name": "Produtos", "url": f"{base_url}/produtos"},
            ],
        },
    )


# -----------------------------------------------------------------------------
# Produto Individual
# -----------------------------------------------------------------------------


@router.get("/produto/{slug}", response_class=HTMLResponse)
async def get_product(
    request: Request,
    slug: str,
    repo: ProductRepo,
):
    """
    Pagina de produto individual.

    Exibe detalhes do produto e link de afiliado.
    """
    # Busca produto por slug
    product = await repo.get_by_slug(slug)

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produto nao encontrado",
        )

    base_url = get_base_url()
    canonical_url = f"{base_url}/produto/{product.slug}"

    # Breadcrumbs para SEO
    breadcrumbs = [
        {"name": "Home", "url": base_url},
        {"name": "Produtos", "url": f"{base_url}/produtos"},
        {"name": product.name, "url": canonical_url},
    ]

    return templates.TemplateResponse(
        request=request,
        name="products/detail.html",
        context={
            "title": f"{product.name} - geek.bidu.guru",
            "description": product.short_description or f"Confira {product.name} na loja",
            "product": product,
            # SEO
            "base_url": base_url,
            "canonical_url": canonical_url,
            "og_type": "product",
            "og_image": product.main_image_url,
            "breadcrumbs": breadcrumbs,
        },
    )
