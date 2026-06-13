"""
Registry e runner dos jobs agendados.

Arquitetura (um unico "tick"):
- O Dokploy Schedule chama POST /api/v1/cron/tick de hora em hora.
- Esse endpoint chama `run_due_jobs`, que percorre o REGISTRY de jobs,
  carrega/cria a config de cada um (tabela scheduled_jobs) e executa os
  que estiverem habilitados e vencidos (respeitando interval_minutes).
- Assim nao e preciso criar um Schedule no Dokploy por job: liga/desliga
  e cadencia ficam no admin/banco.

Para adicionar um job novo: escreva um handler async (db) -> dict e
registre um JobDefinition em JOB_REGISTRY. A config aparece sozinha no
admin no primeiro tick (get-or-create).
"""

import time
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Awaitable, Callable

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.models.scheduled_job import ScheduledJob
from app.repositories.post import PostRepository

logger = get_logger(__name__)


# -----------------------------------------------------------------------------
# Definicao de job
# -----------------------------------------------------------------------------


@dataclass(frozen=True)
class JobDefinition:
    """Metadados + handler de um job. O handler recebe a sessao e retorna
    um dict serializavel com o resumo da execucao."""

    key: str
    name: str
    description: str
    default_interval_minutes: int
    handler: Callable[[AsyncSession], Awaitable[dict]]


# -----------------------------------------------------------------------------
# Handlers
# -----------------------------------------------------------------------------


async def _publish_scheduled_posts(db: AsyncSession) -> dict:
    """Promove posts SCHEDULED com publish_at vencido para PUBLISHED."""
    repo = PostRepository(db)
    published = await repo.publish_due_scheduled()
    return {
        "published_count": len(published),
        "published_slugs": [p.slug for p in published],
    }


# -----------------------------------------------------------------------------
# Registry
# -----------------------------------------------------------------------------


JOB_REGISTRY: dict[str, JobDefinition] = {
    "publish_scheduled_posts": JobDefinition(
        key="publish_scheduled_posts",
        name="Publicar posts agendados",
        description=(
            "Publica posts com status 'agendado' cuja data de publicacao ja chegou."
        ),
        default_interval_minutes=60,
        handler=_publish_scheduled_posts,
    ),
}


# -----------------------------------------------------------------------------
# Config (get-or-create) e listagem
# -----------------------------------------------------------------------------


async def _get_or_create_config(db: AsyncSession, definition: JobDefinition) -> ScheduledJob:
    """Retorna a config do job, criando-a com os defaults na primeira vez."""
    result = await db.execute(
        select(ScheduledJob).where(ScheduledJob.key == definition.key)
    )
    job = result.scalar_one_or_none()
    if job is None:
        job = ScheduledJob(
            key=definition.key,
            name=definition.name,
            description=definition.description,
            enabled=True,
            interval_minutes=definition.default_interval_minutes,
        )
        db.add(job)
        await db.commit()
        await db.refresh(job)
    return job


async def list_jobs(db: AsyncSession) -> list[ScheduledJob]:
    """Garante que todos os jobs do registry tenham config e retorna a lista."""
    jobs = []
    for definition in JOB_REGISTRY.values():
        jobs.append(await _get_or_create_config(db, definition))
    jobs.sort(key=lambda j: j.name)
    return jobs


# -----------------------------------------------------------------------------
# Execucao
# -----------------------------------------------------------------------------


async def _execute(db: AsyncSession, definition: JobDefinition, job: ScheduledJob) -> dict:
    """Roda um job, registrando duracao/status/resultado na config."""
    started = time.perf_counter()
    entry: dict = {"key": definition.key, "ran": True}
    try:
        result = await definition.handler(db)
        job.last_status = "ok"
        job.last_result = str(result)
        entry["status"] = "ok"
        entry["result"] = result
    except Exception as exc:  # nao deixa um job derrubar o tick inteiro
        logger.exception(f"Job '{definition.key}' falhou: {exc}")
        job.last_status = "error"
        job.last_result = str(exc)
        entry["status"] = "error"
        entry["result"] = str(exc)
    finally:
        job.last_duration_ms = int((time.perf_counter() - started) * 1000)
        job.last_run_at = datetime.now(UTC)
        await db.commit()
    return entry


def _is_due(job: ScheduledJob, now: datetime) -> bool:
    """Vencido se nunca rodou ou se passou o intervalo desde a ultima execucao."""
    if job.last_run_at is None:
        return True
    last = job.last_run_at
    if last.tzinfo is None:
        last = last.replace(tzinfo=UTC)
    return now - last >= timedelta(minutes=job.interval_minutes)


async def run_due_jobs(db: AsyncSession) -> list[dict]:
    """
    Executa todos os jobs habilitados e vencidos. Chamado pelo tick do cron.

    Retorna uma lista de entradas (uma por job do registry) com o que
    aconteceu: ran/skipped, status e resultado.
    """
    now = datetime.now(UTC)
    summary: list[dict] = []
    for definition in JOB_REGISTRY.values():
        job = await _get_or_create_config(db, definition)
        if not job.enabled:
            summary.append({"key": definition.key, "ran": False, "status": "disabled"})
            continue
        if not _is_due(job, now):
            summary.append({"key": definition.key, "ran": False, "status": "not_due"})
            continue
        summary.append(await _execute(db, definition, job))
    return summary


async def run_job_now(db: AsyncSession, key: str) -> dict:
    """
    Executa um job especifico imediatamente, ignorando enabled/intervalo.
    Usado pelo botao "Executar agora" do admin. Retorna a entrada de resumo
    ou None se a key nao existir no registry.
    """
    definition = JOB_REGISTRY.get(key)
    if definition is None:
        return None
    job = await _get_or_create_config(db, definition)
    return await _execute(db, definition, job)
