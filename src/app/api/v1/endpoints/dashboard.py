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
from app.services.dashboard import get_dashboard_metrics

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
    - `accesses_24h`: acessos nas ultimas 24h + trend vs as 24h anteriores
      (fonte: cliques de afiliado).
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
