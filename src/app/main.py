"""
Entry point da aplicacao FastAPI - geek.bidu.guru
Blog de Presentes Geek com Automacao e IA
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
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

# Montar arquivos estaticos
app.mount("/static", StaticFiles(directory="src/app/static"), name="static")

# Templates Jinja2
templates = Jinja2Templates(directory="src/app/templates")


# -----------------------------------------------------------------------------
# Exception Handlers
# -----------------------------------------------------------------------------


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handler global para excecoes nao tratadas."""
    logger.exception(f"Erro nao tratado: {exc}")

    if settings.debug:
        return JSONResponse(
            status_code=500,
            content={"detail": str(exc), "type": type(exc).__name__},
        )

    return JSONResponse(
        status_code=500,
        content={"detail": "Erro interno do servidor"},
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
# Incluir Routers (a implementar)
# -----------------------------------------------------------------------------

# from app.api.v1 import auth, posts, products, affiliates
# app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
# app.include_router(posts.router, prefix="/api/v1/posts", tags=["posts"])
# app.include_router(products.router, prefix="/api/v1/products", tags=["products"])
# app.include_router(affiliates.router, prefix="/api/v1/affiliates", tags=["affiliates"])

# from app.routers import home, post, category, search
# app.include_router(home.router)
# app.include_router(post.router)
# app.include_router(category.router)
# app.include_router(search.router)
