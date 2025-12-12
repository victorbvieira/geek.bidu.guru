"""
Rotas de SEO - Sitemap e Robots.txt.

Gera dinamicamente:
- /sitemap.xml - Mapa do site para motores de busca
- /robots.txt - Instrucoes para crawlers
"""

from datetime import datetime, UTC

from fastapi import APIRouter, Request
from fastapi.responses import PlainTextResponse, Response

from app.api.deps import CategoryRepo, PostRepo
from app.config import settings

router = APIRouter(tags=["seo"])


# -----------------------------------------------------------------------------
# Robots.txt
# -----------------------------------------------------------------------------


@router.get("/robots.txt", response_class=PlainTextResponse)
async def robots_txt(request: Request):
    """
    Gera robots.txt dinamicamente.

    Em producao: Permite indexacao de paginas publicas
    Em desenvolvimento: Bloqueia todos os crawlers
    """
    base_url = str(request.base_url).rstrip("/")

    if settings.is_production:
        content = f"""# robots.txt - geek.bidu.guru
# Gerado dinamicamente

User-agent: *
Allow: /
Allow: /blog/
Allow: /categoria/
Allow: /categorias
Allow: /busca

# Bloquear areas administrativas e API
Disallow: /admin/
Disallow: /api/
Disallow: /static/

# Sitemap
Sitemap: {base_url}/sitemap.xml

# Crawl-delay para ser gentil com o servidor
Crawl-delay: 1
"""
    else:
        # Em dev, bloqueia tudo
        content = """# robots.txt - AMBIENTE DE DESENVOLVIMENTO
# Nao indexar este ambiente

User-agent: *
Disallow: /
"""

    return PlainTextResponse(content=content, media_type="text/plain")


# -----------------------------------------------------------------------------
# Sitemap.xml
# -----------------------------------------------------------------------------


@router.get("/sitemap.xml")
async def sitemap_xml(
    request: Request,
    post_repo: PostRepo,
    category_repo: CategoryRepo,
):
    """
    Gera sitemap.xml dinamicamente.

    Inclui:
    - Homepage
    - Paginas estaticas (categorias, busca)
    - Todos os posts publicados
    - Todas as categorias com posts
    """
    base_url = str(request.base_url).rstrip("/")
    now = datetime.now(UTC).strftime("%Y-%m-%d")

    # Inicio do XML
    xml_parts = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]

    # Homepage (prioridade maxima)
    xml_parts.append(_url_entry(base_url, now, "daily", "1.0"))

    # Paginas estaticas
    static_pages = [
        ("/blog", "daily", "0.9"),
        ("/categorias", "weekly", "0.8"),
        ("/busca", "weekly", "0.5"),
    ]

    for path, changefreq, priority in static_pages:
        xml_parts.append(_url_entry(f"{base_url}{path}", now, changefreq, priority))

    # Posts publicados
    posts = await post_repo.get_published(skip=0, limit=1000)
    for post in posts:
        lastmod = post.updated_at.strftime("%Y-%m-%d") if post.updated_at else now
        xml_parts.append(
            _url_entry(
                f"{base_url}/blog/{post.slug}",
                lastmod,
                "weekly",
                "0.8",
            )
        )

    # Categorias
    categories = await category_repo.get_root_categories()
    for category in categories:
        xml_parts.append(
            _url_entry(
                f"{base_url}/categoria/{category.slug}",
                now,
                "weekly",
                "0.7",
            )
        )

    # Fecha XML
    xml_parts.append("</urlset>")

    xml_content = "\n".join(xml_parts)

    return Response(
        content=xml_content,
        media_type="application/xml",
        headers={"Content-Type": "application/xml; charset=utf-8"},
    )


def _url_entry(loc: str, lastmod: str, changefreq: str, priority: str) -> str:
    """Gera entrada de URL para sitemap."""
    return f"""  <url>
    <loc>{loc}</loc>
    <lastmod>{lastmod}</lastmod>
    <changefreq>{changefreq}</changefreq>
    <priority>{priority}</priority>
  </url>"""


# -----------------------------------------------------------------------------
# Sitemap Index (para sites grandes)
# -----------------------------------------------------------------------------


@router.get("/sitemap-index.xml")
async def sitemap_index(request: Request):
    """
    Sitemap index para sites com muitas paginas.

    Por enquanto aponta para o sitemap principal.
    Pode ser expandido para multiplos sitemaps quando necessario.
    """
    base_url = str(request.base_url).rstrip("/")
    now = datetime.now(UTC).strftime("%Y-%m-%d")

    xml_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <sitemap>
    <loc>{base_url}/sitemap.xml</loc>
    <lastmod>{now}</lastmod>
  </sitemap>
</sitemapindex>"""

    return Response(
        content=xml_content,
        media_type="application/xml",
        headers={"Content-Type": "application/xml; charset=utf-8"},
    )
