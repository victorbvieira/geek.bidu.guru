"""
Endpoints REST para gerenciamento de Newsletter.

Este módulo implementa a gestão de inscrições na newsletter,
incluindo endpoints públicos para inscrição/desinscrição e
endpoints administrativos para listagem e estatísticas.

Endpoints públicos (sem autenticação):
    POST   /newsletter/subscribe   - Inscrever email
    POST   /newsletter/unsubscribe - Desinscrever email

Endpoints administrativos (requer autenticação - TODO):
    GET    /newsletter/subscribers - Lista inscritos
    GET    /newsletter/stats       - Estatísticas

Funcionalidades:
    - Inscrição com detecção de origem (referer)
    - Reinscrição automática de emails inativos
    - Soft delete (is_active=false) ao desinscrever
    - Estatísticas de crescimento da lista

Campos capturados:
    - email: Email do inscrito (obrigatório)
    - name: Nome do inscrito (opcional)
    - source: Origem da inscrição (capturado automaticamente via referer)
"""

from fastapi import APIRouter, HTTPException, Request, status

from app.api.deps import NewsletterRepo, Pagination
from app.schemas import (
    MessageResponse,
    NewsletterPublicResponse,
    NewsletterResponse,
    NewsletterStats,
    NewsletterSubscribe,
    PaginatedResponse,
)

# Router com prefixo /newsletter e tag para documentação OpenAPI
router = APIRouter(prefix="/newsletter", tags=["newsletter"])


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

    Comportamento:
    - Se email é novo: cria inscrição
    - Se email existe e está ativo: retorna mensagem informativa
    - Se email existe e está inativo: reativa inscrição

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
        - Recomendado adicionar rate limiting em produção
    """
    # Verifica se email já está inscrito
    existing = await repo.get_by_email(data.email)

    if existing:
        if existing.is_active:
            # Já inscrito e ativo - apenas informa
            return NewsletterPublicResponse(
                message="Email ja esta inscrito!",
                email=data.email,
            )
        else:
            # Estava inscrito mas desativou - reativa
            await repo.resubscribe(data.email)
            return NewsletterPublicResponse(
                message="Inscricao reativada com sucesso!",
                email=data.email,
            )

    # Nova inscrição - captura origem da inscrição
    signup_data = {
        "email": data.email,
        "name": data.name,
        "source": request.headers.get("referer", "direct"),  # Captura referer ou "direct"
    }

    await repo.create(signup_data)
    return NewsletterPublicResponse(
        message="Inscricao realizada com sucesso!",
        email=data.email,
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
