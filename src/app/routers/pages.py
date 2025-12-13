"""
Rotas SSR para paginas institucionais estaticas.

Renderiza templates HTML para:
- Sobre
- Contato
- Politica de Privacidade
- Termos de Uso
"""

from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from app.api.deps import DBSession
from app.config import settings
from app.core.templates import setup_templates
from app.core.context import get_footer_context

# Router para paginas estaticas
router = APIRouter(tags=["pages"])

# Templates com filtros customizados
BASE_DIR = Path(__file__).resolve().parent.parent
templates = setup_templates(BASE_DIR / "templates")


def get_base_url() -> str:
    """Retorna a URL base do site."""
    return settings.app_url.rstrip("/")


# -----------------------------------------------------------------------------
# Sobre
# -----------------------------------------------------------------------------


@router.get("/sobre", response_class=HTMLResponse)
async def about_page(request: Request, db: DBSession):
    """Pagina Sobre Nos."""
    base_url = get_base_url()
    footer_context = await get_footer_context(db)

    return templates.TemplateResponse(
        request=request,
        name="pages/sobre.html",
        context={
            "title": "Sobre - geek.bidu.guru",
            "description": "Conheça o geek.bidu.guru - seu guia definitivo para presentes geek",
            "base_url": base_url,
            "canonical_url": f"{base_url}/sobre",
            "og_type": "website",
            **footer_context,
        },
    )


# -----------------------------------------------------------------------------
# Contato
# -----------------------------------------------------------------------------


@router.get("/contato", response_class=HTMLResponse)
async def contact_page(request: Request, db: DBSession):
    """Pagina de Contato."""
    base_url = get_base_url()
    footer_context = await get_footer_context(db)

    return templates.TemplateResponse(
        request=request,
        name="pages/contato.html",
        context={
            "title": "Contato - geek.bidu.guru",
            "description": "Entre em contato conosco - geek.bidu.guru",
            "base_url": base_url,
            "canonical_url": f"{base_url}/contato",
            "og_type": "website",
            **footer_context,
        },
    )


# -----------------------------------------------------------------------------
# Politica de Privacidade
# -----------------------------------------------------------------------------


@router.get("/privacidade", response_class=HTMLResponse)
async def privacy_page(request: Request, db: DBSession):
    """Pagina de Politica de Privacidade."""
    base_url = get_base_url()
    footer_context = await get_footer_context(db)

    return templates.TemplateResponse(
        request=request,
        name="pages/privacidade.html",
        context={
            "title": "Politica de Privacidade - geek.bidu.guru",
            "description": "Politica de Privacidade do geek.bidu.guru",
            "base_url": base_url,
            "canonical_url": f"{base_url}/privacidade",
            "og_type": "website",
            "noindex": False,  # Pode ser indexada
            **footer_context,
        },
    )


# -----------------------------------------------------------------------------
# Termos de Uso
# -----------------------------------------------------------------------------


@router.get("/termos", response_class=HTMLResponse)
async def terms_page(request: Request, db: DBSession):
    """Pagina de Termos de Uso."""
    base_url = get_base_url()
    footer_context = await get_footer_context(db)

    return templates.TemplateResponse(
        request=request,
        name="pages/termos.html",
        context={
            "title": "Termos de Uso - geek.bidu.guru",
            "description": "Termos de Uso do geek.bidu.guru",
            "base_url": base_url,
            "canonical_url": f"{base_url}/termos",
            "og_type": "website",
            "noindex": False,  # Pode ser indexada
            **footer_context,
        },
    )
