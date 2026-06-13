"""
Modelo de Job Agendado (configuracao dos jobs do "tick" do cron).

Cada linha representa um job que o dispatcher (POST /api/v1/cron/tick)
pode executar. O comportamento (a funcao) vive no codigo (registry em
app/services/jobs.py); esta tabela guarda apenas a configuracao e o
estado da ultima execucao, permitindo ligar/desligar pelo admin.
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.models.base import TimestampMixin, UUIDMixin


class ScheduledJob(Base, UUIDMixin, TimestampMixin):
    """
    Configuracao e estado de um job agendado.

    Atributos:
        key: Identificador unico do job (casa com o registry no codigo)
        name: Nome amigavel exibido no admin
        description: Descricao do que o job faz
        enabled: Se o job deve ser executado pelo dispatcher
        interval_minutes: Intervalo minimo entre execucoes (em minutos)
        last_run_at: Quando rodou pela ultima vez (UTC)
        last_status: Resultado da ultima execucao (ok, error, skipped)
        last_result: Resumo textual da ultima execucao
        last_duration_ms: Duracao da ultima execucao em milissegundos
    """

    __tablename__ = "scheduled_jobs"

    key: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    enabled: Mapped[bool] = mapped_column(
        Boolean, default=True, server_default="true", nullable=False
    )
    interval_minutes: Mapped[int] = mapped_column(
        Integer, default=60, server_default="60", nullable=False,
        comment="Intervalo minimo entre execucoes, em minutos",
    )
    last_run_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    last_status: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    last_result: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    last_duration_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    def __repr__(self) -> str:
        return f"<ScheduledJob {self.key} enabled={self.enabled}>"
