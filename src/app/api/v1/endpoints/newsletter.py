"""
Endpoints REST para gerenciamento de Newsletter.

Este módulo implementa a gestão de inscrições na newsletter,
incluindo endpoints públicos para inscrição/desinscrição e
endpoints administrativos para listagem e estatísticas.

Endpoints públicos (sem autenticação):
    POST   /newsletter/subscribe        - Inscrever email (envia verificacao)
    GET    /newsletter/verify/{token}   - Confirmar email (double opt-in)
    POST   /newsletter/unsubscribe      - Desinscrever email

Endpoints administrativos (requer autenticação - TODO):
    GET    /newsletter/subscribers - Lista inscritos
    GET    /newsletter/stats       - Estatísticas

Funcionalidades:
    - Double opt-in: email de verificacao obrigatório
    - Inscrição com detecção de origem (referer)
    - Reinscrição automática de emails inativos
    - Soft delete (is_active=false) ao desinscrever
    - Estatísticas de crescimento da lista

Campos capturados:
    - email: Email do inscrito (obrigatório)
    - name: Nome do inscrito (opcional)
    - source: Origem da inscrição (capturado automaticamente via referer)
"""

import logging

from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import RedirectResponse

from app.api.deps import NewsletterRepo, Pagination
from app.config import settings
from app.schemas import (
    MessageResponse,
    NewsletterPublicResponse,
    NewsletterResponse,
    NewsletterStats,
    NewsletterSubscribe,
    NewsletterVerifyResponse,
    PaginatedResponse,
)
from app.services.antispam import validate_newsletter_submission
from app.services.email import email_service

logger = logging.getLogger(__name__)

# Router com prefixo /newsletter e tag para documentação OpenAPI
router = APIRouter(prefix="/newsletter", tags=["newsletter"])


def get_client_ip(request: Request) -> str:
    """
    Extrai o IP real do cliente considerando proxies reversos.

    Ordem de prioridade:
    1. X-Forwarded-For (primeiro IP da lista)
    2. X-Real-IP
    3. request.client.host

    Args:
        request: Request do FastAPI

    Returns:
        IP do cliente como string
    """
    # X-Forwarded-For pode ter multiplos IPs separados por virgula
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        # Pega o primeiro IP (cliente original)
        return forwarded_for.split(",")[0].strip()

    # X-Real-IP é mais simples
    real_ip = request.headers.get("x-real-ip")
    if real_ip:
        return real_ip.strip()

    # Fallback para o host do cliente direto
    if request.client:
        return request.client.host

    return "unknown"


# =============================================================================
# Endpoints Públicos (Subscribe/Unsubscribe)
# =============================================================================


@router.post("/subscribe", response_model=NewsletterPublicResponse)
async def subscribe(
    data: NewsletterSubscribe,
    repo: NewsletterRepo,
    request: Request,
):
    """
    Inscreve um email na newsletter (endpoint público).

    Implementa double opt-in: após inscrição, um email de verificação
    é enviado e o usuário só é considerado inscrito após confirmar.

    Comportamento:
    - Se email é novo: cria inscrição pendente + envia email de verificação
    - Se email existe, verificado e ativo: retorna mensagem informativa
    - Se email existe mas não verificado: reenvia email de verificação
    - Se email existe e está inativo: reativa + reenvia verificação

    Args:
        data: Dados da inscrição (email obrigatório, nome opcional)
        repo: Repositório de newsletter (injetado automaticamente)
        request: Request do FastAPI (para capturar referer)

    Returns:
        NewsletterPublicResponse com mensagem e email

    Body (JSON):
        {
            "email": "usuario@exemplo.com",
            "name": "João Silva"  // opcional
        }

    Segurança:
        - Endpoint público, não requer autenticação
        - Pode ser usado em formulários do frontend
        - Protecao anti-spam: honeypot, rate limiting, blocklist

    Anti-spam:
        - Honeypot: campo 'website' deve estar vazio
        - Rate limit: max 10 requisicoes/hora por IP
        - Rate limit: max 3 tentativas por email/hora
        - Tempo minimo de preenchimento: 2 segundos
        - Blocklist de dominios de email temporario
    """
    # =========================================================================
    # Validacao Anti-Spam
    # =========================================================================
    await validate_newsletter_submission(
        request=request,
        email=data.email,
        honeypot=data.website,  # Campo invisivel (honeypot)
        timestamp=data.ts,  # Timestamp do formulario
    )

    # =========================================================================
    # Logica de Inscricao
    # =========================================================================
    # Verifica se email já está inscrito
    existing = await repo.get_by_email(data.email)

    if existing:
        if existing.is_active and existing.email_verified:
            # Já inscrito, verificado e ativo - apenas informa
            return NewsletterPublicResponse(
                message="Email ja esta inscrito!",
                email=data.email,
                needs_verification=False,
            )
        elif existing.is_active and not existing.email_verified:
            # Inscrito mas não verificou - reenvia email
            token = existing.generate_verification_token()
            await repo.db.commit()
            await repo.db.refresh(existing)

            # Envia email de verificação
            verification_url = f"{settings.app_url}/api/v1/newsletter/verify/{token}"
            await email_service.send_verification_email(
                to_email=data.email,
                verification_url=verification_url,
            )

            return NewsletterPublicResponse(
                message="Email de verificacao reenviado! Verifique sua caixa de entrada.",
                email=data.email,
                needs_verification=True,
            )
        else:
            # Estava inscrito mas desativou - reativa e reenvia verificação
            await repo.resubscribe(data.email)

            # Gera novo token se não estava verificado
            if not existing.email_verified:
                token = existing.generate_verification_token()
                await repo.db.commit()
                await repo.db.refresh(existing)

                verification_url = f"{settings.app_url}/api/v1/newsletter/verify/{token}"
                await email_service.send_verification_email(
                    to_email=data.email,
                    verification_url=verification_url,
                )

            return NewsletterPublicResponse(
                message="Inscricao reativada! Verifique seu email para confirmar.",
                email=data.email,
                needs_verification=not existing.email_verified,
            )

    # Nova inscrição - captura origem da inscrição e IP (LGPD)
    client_ip = get_client_ip(request)
    signup_data = {
        "email": data.email,
        "name": data.name,
        "source": request.headers.get("referer", "direct"),
        "signup_ip": client_ip,  # LGPD: IP da inscricao
        "email_verified": False,  # Aguardando verificação
    }

    signup = await repo.create(signup_data)

    # Gera token de verificação
    token = signup.generate_verification_token()
    await repo.db.commit()
    await repo.db.refresh(signup)

    # Envia email de verificação
    verification_url = f"{settings.app_url}/api/v1/newsletter/verify/{token}"
    email_sent = await email_service.send_verification_email(
        to_email=data.email,
        verification_url=verification_url,
    )

    if email_sent:
        logger.info("Email de verificacao enviado para %s", data.email)
        return NewsletterPublicResponse(
            message="Inscricao realizada! Verifique seu email para confirmar.",
            email=data.email,
            needs_verification=True,
        )
    else:
        # Email não foi enviado (provavelmente SES não configurado)
        # Em dev, permite inscrição direta para facilitar testes
        logger.warning(
            "Falha ao enviar email de verificacao para %s. "
            "Verifique as credenciais AWS SES.",
            data.email,
        )
        return NewsletterPublicResponse(
            message="Inscricao realizada! Verifique seu email para confirmar.",
            email=data.email,
            needs_verification=True,
        )


@router.get("/verify/{token}")
async def verify_email(token: str, repo: NewsletterRepo, request: Request):
    """
    Verifica email via token (double opt-in).

    Este endpoint é acessado quando o usuário clica no link do email
    de verificação. Redireciona para uma página de confirmação ou erro.

    Args:
        token: Token de verificação enviado por email
        repo: Repositório de newsletter (injetado automaticamente)
        request: Request do FastAPI

    Returns:
        Redirect para página de confirmação ou erro
    """
    signup = await repo.get_by_token(token)

    if not signup:
        # Token inválido ou já usado - redireciona para página de erro
        logger.warning("Tentativa de verificacao com token invalido: %s", token[:20])
        return RedirectResponse(
            url=f"{settings.app_url}/newsletter/erro?tipo=invalid",
            status_code=status.HTTP_303_SEE_OTHER,
        )

    # Verifica se já foi verificado (token limpo após verificação)
    if signup.email_verified:
        logger.info("Email ja verificado anteriormente: %s", signup.email)
        return RedirectResponse(
            url=f"{settings.app_url}/newsletter/erro?tipo=already_verified",
            status_code=status.HTTP_303_SEE_OTHER,
        )

    # Verifica se token expirou
    if signup.is_token_expired(settings.email_verification_expire_hours):
        logger.warning("Token expirado para email: %s", signup.email)
        return RedirectResponse(
            url=f"{settings.app_url}/newsletter/erro?tipo=expired",
            status_code=status.HTTP_303_SEE_OTHER,
        )

    # Marca email como verificado e registra IP do consentimento (LGPD)
    consent_ip = get_client_ip(request)
    signup.verify_email(consent_ip=consent_ip)
    await repo.db.commit()
    await repo.db.refresh(signup)

    logger.info(
        "Email verificado com sucesso: %s (IP consentimento: %s)",
        signup.email,
        consent_ip,
    )

    # Redireciona para página de confirmação
    return RedirectResponse(
        url=f"{settings.app_url}/newsletter/confirmado",
        status_code=status.HTTP_303_SEE_OTHER,
    )


@router.get("/verify-status/{token}", response_model=NewsletterVerifyResponse)
async def verify_email_api(token: str, repo: NewsletterRepo, request: Request):
    """
    Verifica email via API (retorna JSON em vez de redirect).

    Útil para aplicações SPA ou testes.

    Args:
        token: Token de verificação enviado por email
        repo: Repositório de newsletter (injetado automaticamente)
        request: Request do FastAPI (para capturar IP LGPD)

    Returns:
        NewsletterVerifyResponse com status da verificação
    """
    signup = await repo.get_by_token(token)

    if not signup:
        return NewsletterVerifyResponse(
            message="Link de verificacao invalido ou expirado.",
            email="",
            verified=False,
        )

    if signup.is_token_expired(settings.email_verification_expire_hours):
        return NewsletterVerifyResponse(
            message="Link de verificacao expirado. Inscreva-se novamente.",
            email=signup.email,
            verified=False,
        )

    # Marca email como verificado e registra IP do consentimento (LGPD)
    consent_ip = get_client_ip(request)
    signup.verify_email(consent_ip=consent_ip)
    await repo.db.commit()
    await repo.db.refresh(signup)

    return NewsletterVerifyResponse(
        message="Email verificado com sucesso! Voce esta inscrito na newsletter.",
        email=signup.email,
        verified=True,
    )


@router.post("/unsubscribe", response_model=MessageResponse)
async def unsubscribe(email: str, repo: NewsletterRepo):
    """
    Desinscreve um email da newsletter.

    Realiza soft delete (is_active=false) para manter histórico
    e permitir reinscrição futura.

    Args:
        email: Email a ser desinscrito
        repo: Repositório de newsletter (injetado automaticamente)

    Returns:
        MessageResponse confirmando a desinscrição

    Raises:
        HTTPException 404: Se o email não estiver cadastrado

    Query Parameters:
        email (str): Email a desinscrever

    Exemplo:
        POST /newsletter/unsubscribe?email=usuario@exemplo.com

    Notas:
        - Não remove o registro, apenas desativa
        - Email pode ser reinscrito posteriormente
        - LGPD: considerar opção de remoção completa
    """
    signup = await repo.get_by_email(email)

    # Email não encontrado
    if not signup:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email nao encontrado",
        )

    # Já estava desinscrito
    if not signup.is_active:
        return MessageResponse(message="Email ja estava desinscrito")

    # Desativa a inscrição (soft delete)
    await repo.unsubscribe(email)
    return MessageResponse(message="Desinscricao realizada com sucesso")


# =============================================================================
# Endpoints Administrativos
# =============================================================================


@router.get("/subscribers", response_model=PaginatedResponse)
async def list_subscribers(
    repo: NewsletterRepo,
    pagination: Pagination,
    active_only: bool = True,
):
    """
    Lista inscritos na newsletter (admin).

    Permite filtrar apenas inscritos ativos ou todos os registros.

    Args:
        repo: Repositório de newsletter (injetado automaticamente)
        pagination: Parâmetros de paginação
        active_only: Se True, retorna apenas inscritos ativos

    Returns:
        PaginatedResponse com lista de inscritos

    Query Parameters:
        page (int): Número da página
        per_page (int): Itens por página
        active_only (bool): Filtrar apenas ativos (default: true)

    Exemplo:
        GET /newsletter/subscribers?active_only=false&page=1

    TODO:
        - Adicionar autenticação (apenas admin)
        - Adicionar filtro por período de inscrição
        - Adicionar exportação para CSV
    """
    if active_only:
        # Apenas inscritos ativos
        subscribers = await repo.get_active_subscribers(
            skip=pagination["skip"],
            limit=pagination["limit"],
        )
        total = await repo.count_active()
    else:
        # Todos os registros (incluindo inativos)
        subscribers = await repo.get_multi(
            skip=pagination["skip"],
            limit=pagination["limit"],
            order_by="subscribed_at",  # Ordenado por data de inscrição
        )
        total = await repo.count()

    return PaginatedResponse.create(
        items=[NewsletterResponse.model_validate(s) for s in subscribers],
        total=total,
        page=pagination["page"],
        per_page=pagination["per_page"],
    )


@router.get("/stats", response_model=NewsletterStats)
async def get_stats(repo: NewsletterRepo):
    """
    Retorna estatísticas da newsletter (admin).

    Fornece métricas agregadas para dashboard administrativo.

    Args:
        repo: Repositório de newsletter (injetado automaticamente)

    Returns:
        NewsletterStats com métricas:
        - total_subscribers: Total de inscritos ativos
        - total_unsubscribed: Total de desinscritos
        - subscriptions_this_month: Inscrições no mês atual
        - unsubscriptions_this_month: Desinscrições no mês atual
        - growth_rate: Taxa de crescimento (%)

    Uso:
        - Dashboard administrativo
        - Relatórios de crescimento
        - Métricas de email marketing

    TODO:
        - Adicionar autenticação (apenas admin)
        - Adicionar breakdown por fonte (source)
        - Adicionar série temporal para gráficos
    """
    stats = await repo.get_stats()
    return NewsletterStats(**stats)
