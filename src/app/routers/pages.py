"""
Rotas SSR para paginas institucionais estaticas.

Renderiza templates HTML para:
- Sobre
- Contato
- Politica de Privacidade
- Termos de Uso
- Newsletter (confirmacao, erro, descadastro)
"""

import logging
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Form, Query, Request
from fastapi.responses import HTMLResponse

from app.api.deps import DBSession, NewsletterRepo
from app.config import settings
from app.core.templates import setup_templates
from app.core.context import get_footer_context

logger = logging.getLogger(__name__)

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


# -----------------------------------------------------------------------------
# Newsletter - Confirmacao de Email
# -----------------------------------------------------------------------------


@router.get("/newsletter/confirmado", response_class=HTMLResponse)
async def newsletter_confirmed_page(request: Request, db: DBSession):
    """Pagina de confirmacao de inscricao na newsletter."""
    base_url = get_base_url()
    footer_context = await get_footer_context(db)

    return templates.TemplateResponse(
        request=request,
        name="pages/newsletter_confirmado.html",
        context={
            "title": "Inscricao Confirmada! - geek.bidu.guru",
            "description": "Sua inscricao na newsletter foi confirmada com sucesso.",
            "base_url": base_url,
            "canonical_url": f"{base_url}/newsletter/confirmado",
            "og_type": "website",
            "noindex": True,  # Nao indexar pagina de confirmacao
            **footer_context,
        },
    )


# -----------------------------------------------------------------------------
# Newsletter - Erro de Verificacao
# -----------------------------------------------------------------------------


@router.get("/newsletter/erro", response_class=HTMLResponse)
async def newsletter_error_page(
    request: Request,
    db: DBSession,
    tipo: Optional[str] = Query(None, description="Tipo do erro: expired, invalid, already_verified"),
):
    """
    Pagina de erro para verificacao de newsletter.

    Args:
        tipo: Tipo do erro para exibir mensagem apropriada
    """
    base_url = get_base_url()
    footer_context = await get_footer_context(db)

    # Configuracoes baseadas no tipo de erro
    error_config = {
        "expired": {
            "title": "Link Expirado",
            "message": "O link de verificacao expirou. Por favor, inscreva-se novamente.",
        },
        "invalid": {
            "title": "Link Invalido",
            "message": "Este link de verificacao e invalido ou ja foi utilizado.",
        },
        "already_verified": {
            "title": "Email Ja Verificado",
            "message": "Este email ja foi verificado anteriormente.",
        },
    }

    config = error_config.get(tipo, error_config["invalid"])

    return templates.TemplateResponse(
        request=request,
        name="pages/newsletter_erro.html",
        context={
            "title": f"{config['title']} - geek.bidu.guru",
            "description": config["message"],
            "base_url": base_url,
            "canonical_url": f"{base_url}/newsletter/erro",
            "og_type": "website",
            "noindex": True,
            "error_type": tipo or "invalid",
            "error_title": config["title"],
            "error_message": config["message"],
            "expire_hours": settings.email_verification_expire_hours,
            **footer_context,
        },
    )


# -----------------------------------------------------------------------------
# Newsletter - Descadastro
# -----------------------------------------------------------------------------


@router.get("/newsletter/descadastro", response_class=HTMLResponse)
async def newsletter_unsubscribe_page(
    request: Request,
    db: DBSession,
    email: Optional[str] = Query(None, description="Email para descadastrar"),
):
    """
    Pagina de descadastro da newsletter (GET - formulario).

    Se email for fornecido via query param, pre-preenche o formulario.
    """
    base_url = get_base_url()
    footer_context = await get_footer_context(db)

    return templates.TemplateResponse(
        request=request,
        name="pages/newsletter_descadastro.html",
        context={
            "title": "Cancelar Inscricao - geek.bidu.guru",
            "description": "Cancele sua inscricao na newsletter do geek.bidu.guru",
            "base_url": base_url,
            "canonical_url": f"{base_url}/newsletter/descadastro",
            "og_type": "website",
            "noindex": True,
            "email": email,
            "success": False,
            "already_unsubscribed": False,
            "not_found": False,
            **footer_context,
        },
    )


@router.post("/newsletter/descadastro", response_class=HTMLResponse)
async def newsletter_unsubscribe_submit(
    request: Request,
    db: DBSession,
    repo: NewsletterRepo,
    email: str = Form(..., description="Email para descadastrar"),
    reason: Optional[str] = Form(None, description="Motivo do descadastro"),
):
    """
    Processa o descadastro da newsletter (POST).

    Realiza soft delete do email e exibe pagina de confirmacao.
    """
    base_url = get_base_url()
    footer_context = await get_footer_context(db)

    # Busca o inscrito
    signup = await repo.get_by_email(email)

    # Configura estado da pagina
    success = False
    already_unsubscribed = False
    not_found = False

    if not signup:
        not_found = True
        logger.info("Tentativa de descadastro para email nao encontrado: %s", email)
    elif not signup.is_active:
        already_unsubscribed = True
        logger.info("Email ja estava descadastrado: %s", email)
    else:
        # Realiza o descadastro
        await repo.unsubscribe(email)
        success = True
        logger.info(
            "Email descadastrado com sucesso: %s, motivo: %s",
            email,
            reason or "nao informado",
        )

    return templates.TemplateResponse(
        request=request,
        name="pages/newsletter_descadastro.html",
        context={
            "title": "Cancelar Inscricao - geek.bidu.guru",
            "description": "Cancele sua inscricao na newsletter do geek.bidu.guru",
            "base_url": base_url,
            "canonical_url": f"{base_url}/newsletter/descadastro",
            "og_type": "website",
            "noindex": True,
            "email": email,
            "success": success,
            "already_unsubscribed": already_unsubscribed,
            "not_found": not_found,
            **footer_context,
        },
    )
