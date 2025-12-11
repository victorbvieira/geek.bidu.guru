"""
Endpoints para Newsletter.
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

router = APIRouter(prefix="/newsletter", tags=["newsletter"])


@router.post("/subscribe", response_model=NewsletterPublicResponse)
async def subscribe(
    data: NewsletterSubscribe,
    repo: NewsletterRepo,
    request: Request,
):
    """Inscreve email na newsletter (endpoint publico)."""
    # Verificar se ja esta inscrito
    existing = await repo.get_by_email(data.email)

    if existing:
        if existing.is_active:
            return NewsletterPublicResponse(
                message="Email ja esta inscrito!",
                email=data.email,
            )
        else:
            # Reinscrever
            await repo.resubscribe(data.email)
            return NewsletterPublicResponse(
                message="Inscricao reativada com sucesso!",
                email=data.email,
            )

    # Nova inscricao
    signup_data = {
        "email": data.email,
        "name": data.name,
        "source": request.headers.get("referer", "direct"),
    }

    await repo.create(signup_data)
    return NewsletterPublicResponse(
        message="Inscricao realizada com sucesso!",
        email=data.email,
    )


@router.post("/unsubscribe", response_model=MessageResponse)
async def unsubscribe(email: str, repo: NewsletterRepo):
    """Desinscreve email da newsletter."""
    signup = await repo.get_by_email(email)

    if not signup:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email nao encontrado",
        )

    if not signup.is_active:
        return MessageResponse(message="Email ja estava desinscrito")

    await repo.unsubscribe(email)
    return MessageResponse(message="Desinscricao realizada com sucesso")


# -----------------------------------------------------------------------------
# Endpoints administrativos
# -----------------------------------------------------------------------------


@router.get("/subscribers", response_model=PaginatedResponse)
async def list_subscribers(
    repo: NewsletterRepo,
    pagination: Pagination,
    active_only: bool = True,
):
    """Lista inscritos (admin)."""
    if active_only:
        subscribers = await repo.get_active_subscribers(
            skip=pagination["skip"],
            limit=pagination["limit"],
        )
        total = await repo.count_active()
    else:
        subscribers = await repo.get_multi(
            skip=pagination["skip"],
            limit=pagination["limit"],
            order_by="subscribed_at",
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
    """Retorna estatisticas de newsletter (admin)."""
    stats = await repo.get_stats()
    return NewsletterStats(**stats)
