"""
Entry point da aplicacao FastAPI - geek.bidu.guru
Blog de Presentes Geek com Automacao e IA
"""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.core.logging import setup_logging, get_logger
from app.core.middleware import SecurityHeadersMiddleware
from app.core.rate_limit import limiter
from app.database import check_database_connection

# -----------------------------------------------------------------------------
# Logging Estruturado (JSON em producao)
# -----------------------------------------------------------------------------

setup_logging()
logger = get_logger(__name__)


# -----------------------------------------------------------------------------
# Lifespan (startup/shutdown)
# -----------------------------------------------------------------------------


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerencia startup e shutdown da aplicacao."""
    # Startup
    logger.info(f"Iniciando {settings.app_name}...")
    logger.info(f"Ambiente: {settings.environment}")
    logger.info(f"Debug: {settings.debug}")

    # Verificar conexao com banco
    if await check_database_connection():
        logger.info("Conexao com banco de dados OK")
    else:
        logger.error("Falha na conexao com banco de dados!")

    yield

    # Shutdown
    logger.info(f"Encerrando {settings.app_name}...")


# -----------------------------------------------------------------------------
# Aplicacao FastAPI
# -----------------------------------------------------------------------------

app = FastAPI(
    title=settings.app_name,
    description="Blog de Presentes Geek com Automacao e IA",
    version="0.1.0",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    lifespan=lifespan,
)


# -----------------------------------------------------------------------------
# Middlewares
# -----------------------------------------------------------------------------

# Security Headers (deve ser o primeiro para aplicar a todas as respostas)
app.add_middleware(SecurityHeadersMiddleware)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_hosts_list if settings.is_production else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate Limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


# -----------------------------------------------------------------------------
# Static Files e Templates
# -----------------------------------------------------------------------------

# Diretório base da aplicação (onde está este arquivo main.py)
BASE_DIR = Path(__file__).resolve().parent

# Montar arquivos estaticos (caminho absoluto para funcionar em qualquer contexto)
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

# Templates Jinja2 com filtros customizados (markdown, format_price)
from app.core.templates import setup_templates
templates = setup_templates(BASE_DIR / "templates")


# -----------------------------------------------------------------------------
# Exception Handlers
# -----------------------------------------------------------------------------


def _is_api_request(request: Request) -> bool:
    """Verifica se e uma requisicao de API (retorna JSON)."""
    accept = request.headers.get("accept", "")
    return (
        request.url.path.startswith("/api/")
        or "application/json" in accept
        or request.url.path == "/health"
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handler para HTTPException (404, 403, etc)."""
    # API requests retornam JSON
    if _is_api_request(request):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
        )

    # SSR requests retornam HTML
    if exc.status_code == status.HTTP_404_NOT_FOUND:
        return templates.TemplateResponse(
            request=request,
            name="errors/404.html",
            context={
                "title": "Pagina nao encontrada - geek.bidu.guru",
                "description": "A pagina que voce procura nao existe",
            },
            status_code=404,
        )

    # Outros erros HTTP retornam JSON por enquanto
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handler para erros de validacao Pydantic."""
    # Converte body para string se nao for serializavel (ex: FormData)
    body = exc.body
    if body is not None:
        try:
            import json
            json.dumps(body)
        except (TypeError, ValueError):
            body = str(body) if body else None

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors(), "body": body},
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handler global para excecoes nao tratadas."""
    logger.exception(f"Erro nao tratado: {exc}")

    # API requests retornam JSON
    if _is_api_request(request):
        if settings.debug:
            return JSONResponse(
                status_code=500,
                content={"detail": str(exc), "type": type(exc).__name__},
            )
        return JSONResponse(
            status_code=500,
            content={"detail": "Erro interno do servidor"},
        )

    # SSR requests retornam HTML
    return templates.TemplateResponse(
        request=request,
        name="errors/500.html",
        context={
            "title": "Erro interno - geek.bidu.guru",
            "description": "Ocorreu um erro interno",
        },
        status_code=500,
    )


# -----------------------------------------------------------------------------
# Rotas Base
# -----------------------------------------------------------------------------


@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    Usado pelo Docker e Easypanel para verificar se a aplicacao esta saudavel.
    """
    db_ok = await check_database_connection()

    return {
        "status": "healthy" if db_ok else "unhealthy",
        "app": settings.app_name,
        "environment": settings.environment,
        "database": "connected" if db_ok else "disconnected",
    }


@app.get("/")
async def home(request: Request):
    """
    Homepage do blog.
    Renderiza o template home.html com SSR.
    """
    from app.api.deps import get_db
    from app.repositories.product import ProductRepository
    from app.repositories.post import PostRepository
    from app.repositories.category import CategoryRepository

    base_url = settings.app_url.rstrip("/")

    # Busca produtos, posts e categorias em destaque
    featured_products = []
    featured_posts = []
    categories = []

    async for db in get_db():
        product_repo = ProductRepository(db)
        post_repo = PostRepository(db)
        category_repo = CategoryRepository(db)

        # Busca até 6 produtos disponíveis (ordenados por score)
        featured_products = await product_repo.get_available(limit=6)

        # Busca até 3 posts publicados recentes
        featured_posts = await post_repo.get_published(limit=3)

        # Busca categorias raiz (até 6 para exibir na home)
        all_categories = await category_repo.get_root_categories()
        categories = all_categories[:6]

    return templates.TemplateResponse(
        request=request,
        name="home.html",
        context={
            "title": "geek.bidu.guru - Presentes Geek",
            "description": "Encontre o presente geek perfeito para quem voce ama",
            "featured_products": featured_products,
            "featured_posts": featured_posts,
            "categories": categories,
            # SEO
            "base_url": base_url,
            "canonical_url": base_url,
            "og_type": "website",
        },
    )


# -----------------------------------------------------------------------------
# API Routes
# -----------------------------------------------------------------------------

from app.api.v1.router import api_router

app.include_router(api_router, prefix="/api/v1")


# -----------------------------------------------------------------------------
# SSR Routes (paginas publicas do blog)
# -----------------------------------------------------------------------------

from app.routers.blog import router as blog_router

app.include_router(blog_router)


# -----------------------------------------------------------------------------
# SSR Routes (paginas publicas de produtos)
# -----------------------------------------------------------------------------

from app.routers.products import router as products_router

app.include_router(products_router)


# -----------------------------------------------------------------------------
# Affiliate Redirect Routes (/goto/{slug})
# -----------------------------------------------------------------------------

from app.routers.affiliates import router as affiliates_router

app.include_router(affiliates_router)


# -----------------------------------------------------------------------------
# SEO Routes (sitemap.xml, robots.txt)
# -----------------------------------------------------------------------------

from app.routers.seo import router as seo_router

app.include_router(seo_router)


# -----------------------------------------------------------------------------
# Admin Routes (painel administrativo)
# -----------------------------------------------------------------------------

from app.routers.admin import router as admin_router, AdminRedirectException
from app.routers.admin_actions import router as admin_actions_router
from fastapi.responses import RedirectResponse

app.include_router(admin_router)
app.include_router(admin_actions_router)


@app.exception_handler(AdminRedirectException)
async def admin_redirect_exception_handler(request: Request, exc: AdminRedirectException):
    """Handler para redirecionar usuarios nao autenticados no admin para o login."""
    return RedirectResponse(url="/admin/login", status_code=status.HTTP_303_SEE_OTHER)


# -----------------------------------------------------------------------------
# Redirects 301 (URLs antigas)
# -----------------------------------------------------------------------------

from app.routers.redirects import router as redirects_router

app.include_router(redirects_router)


# -----------------------------------------------------------------------------
# OG Images (imagens Open Graph dinamicas)
# -----------------------------------------------------------------------------

from app.routers.og_images import router as og_images_router

app.include_router(og_images_router)
