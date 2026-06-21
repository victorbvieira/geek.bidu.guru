"""
Acesso somente-leitura ao banco do Paperclip (control plane de agentes de IA).

O Paperclip e um projeto open-source instalado na mesma VPS, na mesma rede
Docker (`dokploy-network`). Em vez de modificar o projeto upstream — o que daria
trabalho de manutencao — lemos os dados direto do Postgres dele com queries
read-only e expomos pela nossa propria API de dashboard.

Conectividade: o container do Geek alcanca o Postgres do Paperclip pelo DNS
interno da rede `dokploy-network` (ex.: `databases-postgres-cypdtq:5432`).
Configure a connection string em `PAPERCLIP_DATABASE_URL`.

Tabelas consumidas (schema do Paperclip, snake_case):
- companies   -> resolve company_id pelo issue_prefix (ex.: "GEEAA")
- agents      -> status + nome/titulo do agente
- issues      -> status (in_review, blocked, ...), title, identifier, assignee
- cost_events -> input/output tokens e custo (cost_cents) por occurred_at

Tudo aqui e SELECT. Nenhuma escrita e feita no banco do Paperclip.
"""

from datetime import UTC, datetime, timedelta

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine

from app.config import settings

# -----------------------------------------------------------------------------
# Engine dedicada (lazy) para o banco do Paperclip
# -----------------------------------------------------------------------------
# Mantemos uma engine separada da do Geek: bancos, credenciais e ciclo de vida
# sao independentes. Criada sob demanda para nao abrir conexoes se a integracao
# nao estiver configurada.

_engine: AsyncEngine | None = None
_session_maker: async_sessionmaker | None = None


def _normalize_async_url(url: str) -> str:
    """Garante o driver asyncpg na connection string.

    O Paperclip usa `postgres://...`; o SQLAlchemy async precisa de
    `postgresql+asyncpg://...`.
    """
    if url.startswith("postgresql+asyncpg://"):
        return url
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+asyncpg://", 1)
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql+asyncpg://", 1)
    return url


def _get_session_maker() -> async_sessionmaker:
    """Retorna (criando se necessario) o session maker do banco do Paperclip."""
    global _engine, _session_maker
    if _session_maker is None:
        if not settings.paperclip_database_url:
            raise RuntimeError("PAPERCLIP_DATABASE_URL nao configurado")
        _engine = create_async_engine(
            _normalize_async_url(settings.paperclip_database_url),
            echo=False,
            pool_pre_ping=True,
            pool_size=2,
            max_overflow=3,
        )
        _session_maker = async_sessionmaker(_engine, expire_on_commit=False)
    return _session_maker


def is_configured() -> bool:
    """Indica se a integracao com o Paperclip esta habilitada."""
    return bool(settings.paperclip_database_url)


# -----------------------------------------------------------------------------
# Helpers de apresentacao
# -----------------------------------------------------------------------------

# Status de issue considerados "abertos" (mesma regra do dashboard do Paperclip:
# tudo que nao esta concluido nem cancelado).
_CLOSED_ISSUE_STATUSES = {"done", "cancelled"}

# Issues que indicam que um agente esta "ocupado" com um trabalho, em ordem de
# prioridade para escolher a issue "atual" de um agente.
_ACTIVE_ISSUE_PRIORITY = {"in_progress": 0, "blocked": 1, "in_review": 2}


def _trend(current: float, previous: float) -> dict:
    """Bloco de tendencia entre o periodo atual e o anterior (mesmo formato do
    dashboard do Geek)."""
    if previous == 0:
        trend_pct = None
    else:
        trend_pct = round((current - previous) / previous * 100, 1)

    if current > previous:
        direction = "up"
    elif current < previous:
        direction = "down"
    else:
        direction = "flat"

    return {
        "current": current,
        "previous": previous,
        "trend_pct": trend_pct,
        "direction": direction,
    }


def _effective_agent_status(agent_status: str, current_issue: dict | None) -> str:
    """Deriva o estado "util" do agente combinando status do agente + issue atual.

    Regras (do mais especifico para o mais geral):
    - issue atual bloqueada            -> "blocked"
    - agente pausado / em erro         -> mantem o status
    - trabalhando (running/in_progress)-> "active"
    - ocioso                           -> "idle"
    - demais                           -> status cru do agente
    """
    if current_issue and current_issue["status"] == "blocked":
        return "blocked"
    if agent_status in ("paused", "error", "terminated", "pending_approval"):
        return agent_status
    if agent_status == "running" or (current_issue and current_issue["status"] == "in_progress"):
        return "active"
    if agent_status == "idle":
        return "idle"
    if agent_status == "active":
        return "active"
    return agent_status


# -----------------------------------------------------------------------------
# Metricas
# -----------------------------------------------------------------------------


async def get_paperclip_metrics() -> dict:
    """Le o banco do Paperclip e monta as metricas dos agentes para o dashboard.

    Retorna um dict com agentes (status + issue atual), issues em review/blocked
    e consumo de tokens/custo dos ultimos 30 dias com tendencia. Tudo escopado a
    company identificada por `PAPERCLIP_ISSUE_PREFIX`.
    """
    now = datetime.now(UTC)
    prefix = settings.paperclip_issue_prefix
    session_maker = _get_session_maker()

    async with session_maker() as session:
        # --- Resolve a company pelo issue_prefix (ex.: "GEEAA") ---
        company_row = (
            await session.execute(
                text(
                    "SELECT id, name, budget_monthly_cents, spent_monthly_cents "
                    "FROM companies WHERE issue_prefix = :prefix LIMIT 1"
                ),
                {"prefix": prefix},
            )
        ).first()

        if company_row is None:
            raise LookupError(f"Company com issue_prefix '{prefix}' nao encontrada no Paperclip")

        company_id = str(company_row.id)

        # --- Agentes (id, nome, titulo, status) ---
        agent_rows = (
            await session.execute(
                text(
                    "SELECT id, name, title, role, status "
                    "FROM agents WHERE company_id = :cid ORDER BY name"
                ),
                {"cid": company_id},
            )
        ).all()

        # --- Issues "ativas" atribuidas a agentes (para descobrir o que cada um
        # esta tocando) ---
        assigned_rows = (
            await session.execute(
                text(
                    "SELECT assignee_agent_id, identifier, title, status, priority, "
                    "started_at, updated_at "
                    "FROM issues "
                    "WHERE company_id = :cid "
                    "AND assignee_agent_id IS NOT NULL "
                    "AND status IN ('in_progress', 'blocked', 'in_review')"
                ),
                {"cid": company_id},
            )
        ).all()

        # --- Contagem de issues por status ---
        issue_status_rows = (
            await session.execute(
                text(
                    "SELECT status, COUNT(*) AS count "
                    "FROM issues WHERE company_id = :cid GROUP BY status"
                ),
                {"cid": company_id},
            )
        ).all()

        # --- Lista de issues em review e bloqueadas ---
        review_blocked_rows = (
            await session.execute(
                text(
                    "SELECT identifier, title, status, priority, updated_at "
                    "FROM issues "
                    "WHERE company_id = :cid AND status IN ('in_review', 'blocked') "
                    "ORDER BY status, priority, updated_at DESC"
                ),
                {"cid": company_id},
            )
        ).all()

        # --- Tokens/custo: ultimos 30 dias vs os 30 dias anteriores ---
        d30 = now - timedelta(days=30)
        d60 = now - timedelta(days=60)
        tokens_current = await _sum_cost_window(session, company_id, d30, now)
        tokens_previous = await _sum_cost_window(session, company_id, d60, d30)

    # --- Monta "issue atual" por agente (prioriza in_progress > blocked > in_review) ---
    current_issue_by_agent: dict[str, dict] = {}
    for row in assigned_rows:
        agent_id = str(row.assignee_agent_id)
        candidate = {
            "identifier": row.identifier,
            "title": row.title,
            "status": row.status,
            "priority": row.priority,
        }
        existing = current_issue_by_agent.get(agent_id)
        if existing is None or (
            _ACTIVE_ISSUE_PRIORITY.get(candidate["status"], 9)
            < _ACTIVE_ISSUE_PRIORITY.get(existing["status"], 9)
        ):
            current_issue_by_agent[agent_id] = candidate

    # --- Agentes: lista + contagens (cru e derivado) ---
    agents_list: list[dict] = []
    by_status: dict[str, int] = {}
    summary: dict[str, int] = {}
    for row in agent_rows:
        current_issue = current_issue_by_agent.get(str(row.id))
        effective = _effective_agent_status(row.status, current_issue)
        by_status[row.status] = by_status.get(row.status, 0) + 1
        summary[effective] = summary.get(effective, 0) + 1
        agents_list.append(
            {
                "name": row.name,
                "title": row.title,
                "role": row.role,
                "status": row.status,
                "effective_status": effective,
                "current_issue": current_issue,
            }
        )

    # --- Issues por status + buckets de interesse ---
    issue_by_status: dict[str, int] = {row.status: row.count for row in issue_status_rows}
    open_count = sum(
        count for status, count in issue_by_status.items() if status not in _CLOSED_ISSUE_STATUSES
    )

    in_review_items: list[dict] = []
    blocked_items: list[dict] = []
    for row in review_blocked_rows:
        item = {
            "identifier": row.identifier,
            "title": row.title,
            "priority": row.priority,
        }
        if row.status == "in_review":
            in_review_items.append(item)
        else:
            blocked_items.append(item)

    # --- Tokens/custo ---
    cost_usd_current = round(tokens_current["cost_cents"] / 100, 2)
    cost_usd_previous = round(tokens_previous["cost_cents"] / 100, 2)

    return {
        "generated_at": now.isoformat(),
        "company": {
            "name": company_row.name,
            "issue_prefix": prefix,
            "budget_monthly_usd": round((company_row.budget_monthly_cents or 0) / 100, 2),
            "spent_monthly_usd": round((company_row.spent_monthly_cents or 0) / 100, 2),
        },
        "agents": {
            "total": len(agents_list),
            "by_status": by_status,
            "summary": summary,
            "list": agents_list,
        },
        "issues": {
            "open": open_count,
            "by_status": issue_by_status,
            "in_review": {"count": len(in_review_items), "items": in_review_items},
            "blocked": {"count": len(blocked_items), "items": blocked_items},
        },
        "tokens_30d": {
            "label": "Consumo de tokens (30 dias)",
            "input_tokens": tokens_current["input_tokens"],
            "cached_input_tokens": tokens_current["cached_input_tokens"],
            "output_tokens": tokens_current["output_tokens"],
            "total_tokens": (
                tokens_current["input_tokens"]
                + tokens_current["cached_input_tokens"]
                + tokens_current["output_tokens"]
            ),
            "cost_usd": cost_usd_current,
            "trend": _trend(cost_usd_current, cost_usd_previous),
        },
    }


async def _sum_cost_window(session, company_id: str, start: datetime, end: datetime) -> dict:
    """Soma tokens e custo (cost_cents) de cost_events na janela [start, end)."""
    row = (
        await session.execute(
            text(
                "SELECT "
                "COALESCE(SUM(input_tokens), 0) AS input_tokens, "
                "COALESCE(SUM(cached_input_tokens), 0) AS cached_input_tokens, "
                "COALESCE(SUM(output_tokens), 0) AS output_tokens, "
                "COALESCE(SUM(cost_cents), 0) AS cost_cents "
                "FROM cost_events "
                "WHERE company_id = :cid AND occurred_at >= :start AND occurred_at < :end"
            ),
            {"cid": company_id, "start": start, "end": end},
        )
    ).first()

    return {
        "input_tokens": int(row.input_tokens),
        "cached_input_tokens": int(row.cached_input_tokens),
        "output_tokens": int(row.output_tokens),
        "cost_cents": int(row.cost_cents),
    }
