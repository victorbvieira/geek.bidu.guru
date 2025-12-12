"""
Entry point da aplicacao FastAPI - geek.bidu.guru
Blog de Presentes Geek com Automacao e IA
"""

import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.config import settings
from app.database import check_database_connection

# -----------------------------------------------------------------------------
# Logging
# -----------------------------------------------------------------------------

logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


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

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_hosts_list if settings.is_production else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -----------------------------------------------------------------------------
# Static Files e Templates
# -----------------------------------------------------------------------------

# Diretório base da aplicação (onde está este arquivo main.py)
BASE_DIR = Path(__file__).resolve().parent

# Montar arquivos estaticos (caminho absoluto para funcionar em qualquer contexto)
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

# Templates Jinja2 (caminho absoluto)
templates = Jinja2Templates(directory=BASE_DIR / "templates")


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
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors(), "body": exc.body},
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
    return templates.TemplateResponse(
        request=request,
        name="home.html",
        context={
            "title": "geek.bidu.guru - Presentes Geek",
            "description": "Encontre o presente geek perfeito para quem voce ama",
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
# Affiliate Redirect Routes (/goto/{slug})
# -----------------------------------------------------------------------------

from app.routers.affiliates import router as affiliates_router

app.include_router(affiliates_router)


# -----------------------------------------------------------------------------
# SEO Routes (sitemap.xml, robots.txt)
# -----------------------------------------------------------------------------

from app.routers.seo import router as seo_router

app.include_router(seo_router)
