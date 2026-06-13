"""
Endpoint de cron/jobs — dispatcher unico ("tick").

Um Schedule do Dokploy chama POST /api/v1/cron/tick periodicamente (ex: de
hora em hora). Este endpoint executa todos os jobs habilitados e vencidos
(ver app/services/jobs.py). Assim nao e preciso um Schedule por job nem um
worker sempre-ligado: liga/desliga e cadencia ficam no admin/banco.

Autenticacao: token fixo compartilhado com o Dokploy, enviado no header
`X-Cron-Token` (ou `Authorization: Bearer <token>`), comparado em tempo
constante com settings.cron_secret. Sem segredo configurado, o endpoint
fica desabilitado (503) para nao ficar aberto por engano.
"""

import secrets

from fastapi import APIRouter, Header, HTTPException, status

from app.api.deps import DBSession
from app.config import settings
from app.services.jobs import run_due_jobs

router = APIRouter(prefix="/cron", tags=["cron"])


def _authorize(x_cron_token: str | None, authorization: str | None) -> None:
    """Valida o token fixo do cron (header X-Cron-Token ou Bearer)."""
    expected = settings.cron_secret
    if not expected:
        # Sem segredo configurado: nao expõe o endpoint.
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Cron desabilitado: CRON_SECRET nao configurado",
        )

    provided = x_cron_token
    if not provided and authorization and authorization.lower().startswith("bearer "):
        provided = authorization[7:]

    if not provided or not secrets.compare_digest(provided, expected):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de cron invalido",
        )


@router.post("/tick", summary="Executa os jobs agendados habilitados e vencidos")
async def cron_tick(
    db: DBSession,
    x_cron_token: str | None = Header(default=None, alias="X-Cron-Token"),
    authorization: str | None = Header(default=None),
):
    """
    Dispatcher do cron. Deve ser chamado por um Schedule do Dokploy.

    **Autenticação**: header `X-Cron-Token: <CRON_SECRET>` (ou
    `Authorization: Bearer <CRON_SECRET>`).

    Returns:
        JSON com o resumo da execucao de cada job (ran/skipped, status,
        resultado).

    Exemplo (Dokploy Schedule / cron):
        curl -X POST "https://geek.bidu.guru/api/v1/cron/tick" \\
            -H "X-Cron-Token: $CRON_SECRET"
    """
    _authorize(x_cron_token, authorization)
    results = await run_due_jobs(db)
    ran = [r for r in results if r.get("ran")]
    return {
        "success": True,
        "jobs_total": len(results),
        "jobs_ran": len(ran),
        "results": results,
    }
