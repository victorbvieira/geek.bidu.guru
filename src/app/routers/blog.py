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
from urllib.parse import unquote_plus

from app.api.deps import CategoryRepo, OccasionRepo, PostRepo, ProductRepo, DBSession
from app.config import settings
from app.models.post import PostStatus, PostType
from app.core.templates import setup_templates
from app.core.context import get_footer_context
from app.utils.markdown import (
    extract_product_refs,
    markdown_to_html,
    replace_product_shortcodes,
)

# Router para rotas publicas do blog
router = APIRouter(tags=["blog"])

# Templates com filtros customizados (markdown, format_price)
BASE_DIR = Path(__file__).resolve().parent.parent
templates = setup_templates(BASE_DIR / "templates")


def get_base_url() -> str:
    """Retorna a URL base do site."""
    return settings.app_url.rstrip("/")


# -----------------------------------------------------------------------------
# Listagem de Posts
# -----------------------------------------------------------------------------


@router.get("/blog", response_class=HTMLResponse)
async def list_posts(
    request: Request,
    repo: PostRepo,
    db: DBSession,
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

    # Footer dinamico
    footer_context = await get_footer_context(db)

    base_url = get_base_url()
    canonical_url = f"{base_url}/blog" if page == 1 else f"{base_url}/blog?page={page}"

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
            # SEO
            "base_url": base_url,
            "canonical_url": canonical_url,
            "og_type": "website",
            "breadcrumbs": [
                {"name": "Home", "url": base_url},
                {"name": "Blog", "url": f"{base_url}/blog"},
            ],
            # Footer
            **footer_context,
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
    product_repo: ProductRepo,
    db: DBSession,
):
    """
    Pagina de post individual.

    Exibe o conteudo completo do post com produtos relacionados.
    Incrementa o contador de views.

    Suporta shortcodes de produto: [product:slug]
    Os shortcodes sao substituidos por cards de produto renderizados.
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

    # Processa shortcodes de produtos no conteudo
    # Fluxo: Markdown -> HTML -> Substitui shortcodes por cards HTML
    content_html = ""
    embedded_products = []

    if post.content:
        # Primeiro converte Markdown para HTML
        content_html = markdown_to_html(post.content, sanitize=True)

        # Depois extrai e substitui shortcodes de produtos
        product_refs = extract_product_refs(post.content)
        if product_refs:
            products_dict = {}
            for ref in product_refs:
                product = await product_repo.get_by_slug(ref)
                if product:
                    embedded_products.append(product)
                    products_dict[ref] = {
                        "name": product.name,
                        "slug": product.slug,
                        "price": float(product.price) if product.price else None,
                        "main_image_url": product.main_image_url,
                        "platform": product.platform.value if product.platform else "amazon",
                        "affiliate_redirect_slug": product.affiliate_redirect_slug or product.slug,
                    }
            # Substitui shortcodes no HTML (os shortcodes ficam como texto apos conversao)
            content_html = replace_product_shortcodes(content_html, products_dict)

    # SEO: usa seo_title/seo_description se definidos, senao usa title/subtitle
    seo_title = post.seo_title or post.title
    seo_description = post.seo_description or (post.subtitle or post.title)

    # Footer dinamico
    footer_context = await get_footer_context(db)

    base_url = get_base_url()
    canonical_url = f"{base_url}/blog/{post.slug}"

    # Breadcrumbs para SEO
    breadcrumbs = [
        {"name": "Home", "url": base_url},
        {"name": "Blog", "url": f"{base_url}/blog"},
    ]
    if post.category:
        breadcrumbs.append({
            "name": post.category.name,
            "url": f"{base_url}/categoria/{post.category.slug}"
        })
    breadcrumbs.append({"name": post.title, "url": canonical_url})

    return templates.TemplateResponse(
        request=request,
        name="blog/post.html",
        context={
            "title": f"{seo_title} - geek.bidu.guru",
            "description": seo_description,
            "post": post,
            "content_html": content_html,  # HTML completo com produtos renderizados
            "embedded_products": embedded_products,  # Lista de produtos embedados para Schema.org
            "seo_title": seo_title,
            "seo_description": seo_description,
            # SEO
            "base_url": base_url,
            "canonical_url": canonical_url,
            "og_type": "article",
            "og_image": post.featured_image_url,
            "article_published": post.publish_at.isoformat() if post.publish_at else None,
            "article_modified": post.updated_at.isoformat() if post.updated_at else None,
            "article_author": post.author.name if post.author else None,
            "article_section": post.category.name if post.category else None,
            "article_tags": post.tags or [],
            "schema_type": "BlogPosting",
            "breadcrumbs": breadcrumbs,
            "seo_keywords": post.seo_focus_keyword,
            # Footer
            **footer_context,
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
    product_repo: ProductRepo,
    db: DBSession,
    page: int = 1,
    per_page: int = 12,
):
    """
    Pagina de listagem de posts por categoria.

    Exibe posts publicados, subcategorias e produtos de uma categoria especifica.
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
    total_posts = await post_repo.count_published(category_id=category.id)

    # Busca subcategorias (se houver)
    subcategories = await category_repo.get_children(category.id)

    # Busca produtos da categoria
    products = await product_repo.get_by_category(category.slug, skip=0, limit=12)
    total_products = await product_repo.count_by_category(category.slug)

    # Calcula total de paginas (baseado em posts)
    pages = (total_posts + per_page - 1) // per_page if total_posts > 0 else 1

    # Footer dinamico
    footer_context = await get_footer_context(db)

    base_url = get_base_url()
    canonical_url = f"{base_url}/categoria/{category.slug}"
    if page > 1:
        canonical_url = f"{canonical_url}?page={page}"

    # SEO: usa campos SEO se disponiveis
    seo_title = getattr(category, 'seo_title', None) or category.name
    seo_description = getattr(category, 'seo_description', None) or category.description or f"Posts sobre {category.name}"
    og_image = getattr(category, 'image_url', None)

    return templates.TemplateResponse(
        request=request,
        name="blog/category.html",
        context={
            "title": f"{seo_title} - geek.bidu.guru",
            "description": seo_description,
            "category": category,
            "posts": posts,
            "subcategories": subcategories,
            "products": products,
            "total_products": total_products,
            "page": page,
            "per_page": per_page,
            "total": total_posts,
            "pages": pages,
            "has_prev": page > 1,
            "has_next": page < pages,
            # SEO
            "base_url": base_url,
            "canonical_url": canonical_url,
            "og_type": "website",
            "og_image": og_image,
            "breadcrumbs": [
                {"name": "Home", "url": base_url},
                {"name": "Categorias", "url": f"{base_url}/categorias"},
                {"name": category.name, "url": f"{base_url}/categoria/{category.slug}"},
            ],
            # Footer
            **footer_context,
        },
    )


# -----------------------------------------------------------------------------
# Categorias
# -----------------------------------------------------------------------------


@router.get("/categorias", response_class=HTMLResponse)
async def list_categories(
    request: Request,
    repo: CategoryRepo,
    db: DBSession,
):
    """
    Pagina de listagem de todas as categorias.
    """
    # Busca categorias raiz (sem parent)
    categories = await repo.get_root_categories()

    # Footer dinamico
    footer_context = await get_footer_context(db)

    base_url = get_base_url()

    return templates.TemplateResponse(
        request=request,
        name="blog/categories.html",
        context={
            "title": "Categorias - geek.bidu.guru",
            "description": "Navegue por categoria e encontre o presente geek perfeito",
            "categories": categories,
            # SEO
            "base_url": base_url,
            "canonical_url": f"{base_url}/categorias",
            "og_type": "website",
            "breadcrumbs": [
                {"name": "Home", "url": base_url},
                {"name": "Categorias", "url": f"{base_url}/categorias"},
            ],
            # Footer
            **footer_context,
        },
    )


# -----------------------------------------------------------------------------
# Busca
# -----------------------------------------------------------------------------


@router.get("/busca", response_class=HTMLResponse)
async def search_posts(
    request: Request,
    repo: PostRepo,
    product_repo: ProductRepo,
    db: DBSession,
    q: str = "",
    page: int = 1,
    per_page: int = 12,
):
    """
    Pagina de busca de posts e produtos.

    Busca posts em: titulo, subtitulo, conteudo e keywords.
    Busca produtos em: nome e descricao curta.
    """
    # Decode query string
    query = unquote_plus(q).strip()

    base_url = get_base_url()

    # Footer dinamico
    footer_context = await get_footer_context(db)

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
                "products": [],
                "total": 0,
                "total_products": 0,
                "page": 1,
                "pages": 1,
                "has_prev": False,
                "has_next": False,
                # SEO - noindex para paginas de busca
                "base_url": base_url,
                "canonical_url": f"{base_url}/busca",
                "noindex": True,
                # Footer
                **footer_context,
            },
        )

    # Calcula offset para paginacao
    skip = (page - 1) * per_page

    # Busca posts
    posts = await repo.search(query, skip=skip, limit=per_page)
    total = await repo.count_search(query)

    # Busca produtos (exibe apenas na primeira pagina, limite de 8)
    products = []
    total_products = 0
    if page == 1:
        products = await product_repo.search(query, skip=0, limit=8)
        total_products = await product_repo.count_search(query)

    # Calcula total de paginas (baseado em posts)
    pages = (total + per_page - 1) // per_page if total > 0 else 1

    return templates.TemplateResponse(
        request=request,
        name="blog/search.html",
        context={
            "title": f"Busca: {query} - geek.bidu.guru",
            "description": f"Resultados de busca para {query}",
            "query": query,
            "posts": posts,
            "products": products,
            "total": total,
            "total_products": total_products,
            "page": page,
            "per_page": per_page,
            "pages": pages,
            "has_prev": page > 1,
            "has_next": page < pages,
            # SEO - noindex para paginas de busca
            "base_url": base_url,
            "canonical_url": f"{base_url}/busca?q={query}",
            "noindex": True,
            # Footer
            **footer_context,
        },
    )


# -----------------------------------------------------------------------------
# Listas (Listicles)
# -----------------------------------------------------------------------------


@router.get("/listas", response_class=HTMLResponse)
async def list_listicles(
    request: Request,
    repo: PostRepo,
    db: DBSession,
    page: int = 1,
    per_page: int = 12,
):
    """
    Pagina de listagem de listicles (listas Top 10, etc).

    Exibe posts do tipo LISTICLE ordenados por data de publicacao.
    """
    skip = (page - 1) * per_page

    # Busca posts do tipo listicle
    posts = await repo.get_published(
        skip=skip,
        limit=per_page,
        post_type=PostType.LISTICLE,
    )
    total = await repo.count_published(post_type=PostType.LISTICLE)

    # Calcula total de paginas
    pages = (total + per_page - 1) // per_page if total > 0 else 1

    # Footer dinamico
    footer_context = await get_footer_context(db)

    base_url = get_base_url()
    canonical_url = f"{base_url}/listas" if page == 1 else f"{base_url}/listas?page={page}"

    return templates.TemplateResponse(
        request=request,
        name="blog/type_list.html",
        context={
            "title": "Listas - Melhores Presentes Geek",
            "description": "Listas com os melhores presentes geek: Top 10, comparativos e selecoes especiais para quem ama cultura pop, games e tecnologia.",
            "page_title": "Listas",
            "page_subtitle": "Top 10, comparativos e selecoes especiais de presentes geek",
            "page_icon": "📋",
            "post_type": "listicle",
            "posts": posts,
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
                {"name": "Listas", "url": f"{base_url}/listas"},
            ],
            # Footer
            **footer_context,
        },
    )


# -----------------------------------------------------------------------------
# Guias de Compra
# -----------------------------------------------------------------------------


@router.get("/guias", response_class=HTMLResponse)
async def list_guides(
    request: Request,
    repo: PostRepo,
    db: DBSession,
    page: int = 1,
    per_page: int = 12,
):
    """
    Pagina de listagem de guias de compra.

    Exibe posts do tipo GUIDE ordenados por data de publicacao.
    """
    skip = (page - 1) * per_page

    # Busca posts do tipo guide
    posts = await repo.get_published(
        skip=skip,
        limit=per_page,
        post_type=PostType.GUIDE,
    )
    total = await repo.count_published(post_type=PostType.GUIDE)

    # Calcula total de paginas
    pages = (total + per_page - 1) // per_page if total > 0 else 1

    # Footer dinamico
    footer_context = await get_footer_context(db)

    base_url = get_base_url()
    canonical_url = f"{base_url}/guias" if page == 1 else f"{base_url}/guias?page={page}"

    return templates.TemplateResponse(
        request=request,
        name="blog/type_list.html",
        context={
            "title": "Guias de Compra - Presentes Geek",
            "description": "Guias completos para escolher o presente geek perfeito. Aprenda o que considerar, compare opcoes e faca a melhor escolha.",
            "page_title": "Guias de Compra",
            "page_subtitle": "Tudo que voce precisa saber para escolher o presente perfeito",
            "page_icon": "📖",
            "post_type": "guide",
            "posts": posts,
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
                {"name": "Guias", "url": f"{base_url}/guias"},
            ],
            # Footer
            **footer_context,
        },
    )


# -----------------------------------------------------------------------------
# Ocasiões
# -----------------------------------------------------------------------------


@router.get("/ocasioes", response_class=HTMLResponse)
async def list_occasions(
    request: Request,
    repo: OccasionRepo,
    db: DBSession,
):
    """
    Página de listagem de todas as ocasiões para presentear.

    Exibe ocasiões ativas ordenadas por display_order.
    """
    # Busca ocasiões ativas
    occasions = await repo.get_active()

    # Footer dinâmico
    footer_context = await get_footer_context(db)

    base_url = get_base_url()

    return templates.TemplateResponse(
        request=request,
        name="blog/occasions.html",
        context={
            "title": "Ocasiões para Presentear - geek.bidu.guru",
            "description": "Encontre o presente geek perfeito para cada ocasião: Natal, Aniversário, Dia dos Namorados, Dia das Mães e muito mais.",
            "occasions": occasions,
            # SEO
            "base_url": base_url,
            "canonical_url": f"{base_url}/ocasioes",
            "og_type": "website",
            "breadcrumbs": [
                {"name": "Home", "url": base_url},
                {"name": "Ocasiões", "url": f"{base_url}/ocasioes"},
            ],
            # Footer
            **footer_context,
        },
    )


@router.get("/ocasiao/{slug}", response_class=HTMLResponse)
async def get_occasion(
    request: Request,
    slug: str,
    repo: OccasionRepo,
    product_repo: ProductRepo,
    db: DBSession,
):
    """
    Página de ocasião individual.

    Exibe o conteúdo da ocasião com produtos sugeridos.
    Suporta shortcodes de produto: [product:slug]
    """
    # Busca ocasião por slug
    occasion = await repo.get_by_slug(slug)

    if not occasion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ocasião não encontrada",
        )

    # Verifica se está ativa
    if not occasion.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ocasião não encontrada",
        )

    # Processa shortcodes de produtos no conteúdo
    content_html = ""
    embedded_products = []

    if occasion.content:
        # Primeiro converte Markdown para HTML
        content_html = markdown_to_html(occasion.content, sanitize=True)

        # Depois extrai e substitui shortcodes de produtos
        product_refs = extract_product_refs(occasion.content)
        if product_refs:
            products_dict = {}
            for ref in product_refs:
                product = await product_repo.get_by_slug(ref)
                if product:
                    embedded_products.append(product)
                    products_dict[ref] = {
                        "name": product.name,
                        "slug": product.slug,
                        "price": float(product.price) if product.price else None,
                        "main_image_url": product.main_image_url,
                        "platform": product.platform.value if product.platform else "amazon",
                        "affiliate_redirect_slug": product.affiliate_redirect_slug or product.slug,
                    }
            # Substitui shortcodes no HTML
            content_html = replace_product_shortcodes(content_html, products_dict)

    # SEO: usa seo_title/seo_description se definidos
    seo_title = occasion.seo_title or f"Presentes para {occasion.name}"
    seo_description = occasion.seo_description or occasion.description or f"Descubra os melhores presentes geek para {occasion.name}"

    # Footer dinâmico
    footer_context = await get_footer_context(db)

    base_url = get_base_url()
    canonical_url = f"{base_url}/ocasiao/{occasion.slug}"

    return templates.TemplateResponse(
        request=request,
        name="blog/occasion.html",
        context={
            "title": f"{seo_title} - geek.bidu.guru",
            "description": seo_description,
            "occasion": occasion,
            "content_html": content_html,
            "embedded_products": embedded_products,
            "seo_title": seo_title,
            "seo_description": seo_description,
            # SEO
            "base_url": base_url,
            "canonical_url": canonical_url,
            "og_type": "website",
            "og_image": occasion.image_url,
            "breadcrumbs": [
                {"name": "Home", "url": base_url},
                {"name": "Ocasiões", "url": f"{base_url}/ocasioes"},
                {"name": occasion.name, "url": canonical_url},
            ],
            # Footer
            **footer_context,
        },
    )
