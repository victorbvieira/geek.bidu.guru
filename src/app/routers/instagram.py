"""
Rotas SSR para pagina publica do Instagram.

Renderiza template HTML com:
- Destaque para o ultimo post do Instagram
- Listagem de produtos postados com paginacao
- Ferramenta de busca de produtos
"""

from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from app.api.deps import ProductRepo
from app.config import settings
from app.core.templates import setup_templates

# Router para rotas publicas do Instagram
router = APIRouter(tags=["instagram-ssr"])

# Templates com filtros customizados
BASE_DIR = Path(__file__).resolve().parent.parent
templates = setup_templates(BASE_DIR / "templates")


def get_base_url() -> str:
    """Retorna a URL base do site."""
    return settings.app_url.rstrip("/")


# -----------------------------------------------------------------------------
# Pagina Principal do Instagram
# -----------------------------------------------------------------------------


@router.get("/insta", response_class=HTMLResponse)
async def instagram_page(
    request: Request,
    repo: ProductRepo,
    page: int = 1,
    per_page: int = 12,
):
    """
    Pagina publica do Instagram.

    Exibe:
    - Chamada para o ultimo post do Instagram
    - Listagem de produtos postados com paginacao
    - Ferramenta de busca de produtos

    Args:
        request: Request do FastAPI
        repo: Repositorio de produtos (injetado)
        page: Numero da pagina atual (default: 1)
        per_page: Itens por pagina (default: 12)

    Returns:
        Template HTML renderizado
    """
    # Calcula offset para paginacao
    skip = (page - 1) * per_page

    # Busca o ultimo produto postado no Instagram (destaque)
    last_posted = await repo.get_last_posted_on_instagram()

    # Busca produtos postados no Instagram (com paginacao)
    # Exclui o produto de destaque da listagem se estiver na primeira pagina
    products = await repo.get_posted_on_instagram(skip=skip, limit=per_page)
    total = await repo.count_posted_on_instagram()

    # Remove o produto de destaque da listagem na primeira pagina
    # para evitar duplicacao visual
    if page == 1 and last_posted and products:
        products = [p for p in products if p.id != last_posted.id]

    # Calcula total de paginas
    pages = (total + per_page - 1) // per_page if total > 0 else 1

    base_url = get_base_url()
    canonical_url = f"{base_url}/insta" if page == 1 else f"{base_url}/insta?page={page}"

    return templates.TemplateResponse(
        request=request,
        name="instagram/page.html",
        context={
            "title": "Instagram - geek.bidu.guru",
            "description": "Confira os produtos geek que compartilhamos no Instagram. Ofertas incriveis selecionadas para voce!",
            "last_posted": last_posted,
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
                {"name": "Instagram", "url": f"{base_url}/insta"},
            ],
        },
    )
