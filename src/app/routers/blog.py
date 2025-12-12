"""
Rotas SSR para paginas publicas do blog.

Renderiza templates HTML para:
- Listagem de posts
- Post individual
- Listagem por categoria
"""

from pathlib import Path

from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.api.deps import CategoryRepo, PostRepo
from app.models.post import PostStatus
from urllib.parse import unquote_plus

# Router para rotas publicas do blog
router = APIRouter(tags=["blog"])

# Templates (caminho absoluto)
BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=BASE_DIR / "templates")


# -----------------------------------------------------------------------------
# Listagem de Posts
# -----------------------------------------------------------------------------


@router.get("/blog", response_class=HTMLResponse)
async def list_posts(
    request: Request,
    repo: PostRepo,
    page: int = 1,
    per_page: int = 12,
):
    """
    Pagina de listagem de posts publicados.

    Exibe posts ordenados por data de publicacao (mais recentes primeiro).
    """
    # Calcula offset para paginacao
    skip = (page - 1) * per_page

    # Busca posts publicados
    posts = await repo.get_published(skip=skip, limit=per_page)
    total = await repo.count_published()

    # Calcula total de paginas
    pages = (total + per_page - 1) // per_page if total > 0 else 1

    return templates.TemplateResponse(
        request=request,
        name="blog/list.html",
        context={
            "title": "Blog - geek.bidu.guru",
            "description": "Artigos, listas e guias de presentes geek",
            "posts": posts,
            "page": page,
            "per_page": per_page,
            "total": total,
            "pages": pages,
            "has_prev": page > 1,
            "has_next": page < pages,
        },
    )


# -----------------------------------------------------------------------------
# Post Individual
# -----------------------------------------------------------------------------


@router.get("/blog/{slug}", response_class=HTMLResponse)
async def get_post(
    request: Request,
    slug: str,
    repo: PostRepo,
):
    """
    Pagina de post individual.

    Exibe o conteudo completo do post com produtos relacionados.
    Incrementa o contador de views.
    """
    # Busca post por slug
    post = await repo.get_by_slug(slug)

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post nao encontrado",
        )

    # Verifica se esta publicado (ou draft em modo preview - a implementar)
    if post.status != PostStatus.PUBLISHED:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post nao encontrado",
        )

    # Incrementa views (fire and forget - nao espera)
    await repo.increment_view_count(post.id)

    # SEO: usa seo_title/seo_description se definidos, senao usa title/subtitle
    seo_title = post.seo_title or post.title
    seo_description = post.seo_description or (post.subtitle or post.title)

    return templates.TemplateResponse(
        request=request,
        name="blog/post.html",
        context={
            "title": f"{seo_title} - geek.bidu.guru",
            "description": seo_description,
            "post": post,
            "seo_title": seo_title,
            "seo_description": seo_description,
        },
    )


# -----------------------------------------------------------------------------
# Listagem por Categoria
# -----------------------------------------------------------------------------


@router.get("/categoria/{slug}", response_class=HTMLResponse)
async def list_by_category(
    request: Request,
    slug: str,
    category_repo: CategoryRepo,
    post_repo: PostRepo,
    page: int = 1,
    per_page: int = 12,
):
    """
    Pagina de listagem de posts por categoria.

    Exibe posts publicados de uma categoria especifica.
    """
    # Busca categoria por slug
    category = await category_repo.get_by_slug(slug)

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Categoria nao encontrada",
        )

    # Calcula offset para paginacao
    skip = (page - 1) * per_page

    # Busca posts publicados da categoria
    posts = await post_repo.get_published(
        skip=skip,
        limit=per_page,
        category_id=category.id,
    )
    total = await post_repo.count_published(category_id=category.id)

    # Calcula total de paginas
    pages = (total + per_page - 1) // per_page if total > 0 else 1

    return templates.TemplateResponse(
        request=request,
        name="blog/category.html",
        context={
            "title": f"{category.name} - geek.bidu.guru",
            "description": category.description or f"Posts sobre {category.name}",
            "category": category,
            "posts": posts,
            "page": page,
            "per_page": per_page,
            "total": total,
            "pages": pages,
            "has_prev": page > 1,
            "has_next": page < pages,
        },
    )


# -----------------------------------------------------------------------------
# Categorias
# -----------------------------------------------------------------------------


@router.get("/categorias", response_class=HTMLResponse)
async def list_categories(
    request: Request,
    repo: CategoryRepo,
):
    """
    Pagina de listagem de todas as categorias.
    """
    # Busca categorias raiz (sem parent)
    categories = await repo.get_root_categories()

    return templates.TemplateResponse(
        request=request,
        name="blog/categories.html",
        context={
            "title": "Categorias - geek.bidu.guru",
            "description": "Navegue por categoria e encontre o presente geek perfeito",
            "categories": categories,
        },
    )


# -----------------------------------------------------------------------------
# Busca
# -----------------------------------------------------------------------------


@router.get("/busca", response_class=HTMLResponse)
async def search_posts(
    request: Request,
    repo: PostRepo,
    q: str = "",
    page: int = 1,
    per_page: int = 12,
):
    """
    Pagina de busca de posts.

    Busca em titulo, subtitulo, conteudo e keywords.
    """
    # Decode query string
    query = unquote_plus(q).strip()

    # Se nao tem query, mostra pagina de busca vazia
    if not query:
        return templates.TemplateResponse(
            request=request,
            name="blog/search.html",
            context={
                "title": "Busca - geek.bidu.guru",
                "description": "Busque posts e produtos geek",
                "query": "",
                "posts": [],
                "total": 0,
                "page": 1,
                "pages": 1,
                "has_prev": False,
                "has_next": False,
            },
        )

    # Calcula offset para paginacao
    skip = (page - 1) * per_page

    # Busca posts
    posts = await repo.search(query, skip=skip, limit=per_page)
    total = await repo.count_search(query)

    # Calcula total de paginas
    pages = (total + per_page - 1) // per_page if total > 0 else 1

    return templates.TemplateResponse(
        request=request,
        name="blog/search.html",
        context={
            "title": f"Busca: {query} - geek.bidu.guru",
            "description": f"Resultados de busca para {query}",
            "query": query,
            "posts": posts,
            "total": total,
            "page": page,
            "per_page": per_page,
            "pages": pages,
            "has_prev": page > 1,
            "has_next": page < pages,
        },
    )
