"""
API de Dashboard — indicadores para painel externo.

Autenticacao por token fixo: o consumidor envia `X-Dashboard-Token`
(ou `Authorization: Bearer <token>`), comparado em tempo constante com
settings.dashboard_token. Sem token configurado -> 503 (fail-safe).

Somente leitura.
"""

import secrets

from fastapi import APIRouter, Header, HTTPException, status

from app.api.deps import DBSession
from app.config import settings
from app.services import paperclip
from app.services.dashboard import get_dashboard_metrics
from app.services.paperclip import get_paperclip_metrics

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


def _authorize(x_dashboard_token: str | None, authorization: str | None) -> None:
    """Valida o token fixo do dashboard (header X-Dashboard-Token ou Bearer)."""
    expected = settings.dashboard_token
    if not expected:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Dashboard desabilitado: DASHBOARD_TOKEN nao configurado",
        )

    provided = x_dashboard_token
    if not provided and authorization and authorization.lower().startswith("bearer "):
        provided = authorization[7:]

    if not provided or not secrets.compare_digest(provided, expected):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de dashboard invalido",
        )


@router.get("/metrics", summary="Indicadores para o dashboard")
async def dashboard_metrics(
    db: DBSession,
    x_dashboard_token: str | None = Header(default=None, alias="X-Dashboard-Token"),
    authorization: str | None = Header(default=None),
):
    """
    Retorna os indicadores do dashboard.

    **Autenticação**: header `X-Dashboard-Token: <DASHBOARD_TOKEN>` (ou
    `Authorization: Bearer <DASHBOARD_TOKEN>`).

    Indicadores:
    - `product_clicks_24h`: cliques em produtos nas ultimas 24h + trend vs as
      24h anteriores.
    - `new_products_7d`: produtos cadastrados nos ultimos 7 dias + trend vs
      os 7 dias anteriores.
    - `last_product`: nome do ultimo produto cadastrado e ha quanto tempo
      (min/horas/dias).

    Exemplo:
        curl "https://geek.bidu.guru/api/v1/dashboard/metrics" \\
            -H "X-Dashboard-Token: $DASHBOARD_TOKEN"
    """
    _authorize(x_dashboard_token, authorization)
    return await get_dashboard_metrics(db)


@router.get("/paperclip", summary="Estado dos agentes do Paperclip")
async def paperclip_metrics(
    x_dashboard_token: str | None = Header(default=None, alias="X-Dashboard-Token"),
    authorization: str | None = Header(default=None),
):
    """
    Retorna o estado dos agentes do Paperclip (control plane de IA) lendo direto
    o banco do Paperclip — que roda na mesma VPS, na rede `dokploy-network`.

    **Autenticação**: header `X-Dashboard-Token: <DASHBOARD_TOKEN>` (ou
    `Authorization: Bearer <DASHBOARD_TOKEN>`), o mesmo token de `/metrics`.

    Indicadores:
    - `agents`: total, contagem por status (cru) e por estado derivado
      (`summary`: active/idle/blocked/...) + lista com a issue que cada agente
      está atuando.
    - `issues`: contagem por status, abertas, e a lista (em texto) das issues em
      review e bloqueadas.
    - `tokens_30d`: tokens (input/cached/output) e custo em USD nos últimos 30
      dias, com tendência vs os 30 dias anteriores.

    Requer `PAPERCLIP_DATABASE_URL` configurado; caso contrário retorna 503.

    Exemplo:
        curl "https://geek.bidu.guru/api/v1/dashboard/paperclip" \\
            -H "X-Dashboard-Token: $DASHBOARD_TOKEN"
    """
    _authorize(x_dashboard_token, authorization)

    if not paperclip.is_configured():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Integracao com Paperclip desabilitada: PAPERCLIP_DATABASE_URL nao configurado",
        )

    try:
        return await get_paperclip_metrics()
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
