"""
Configuracao de logging estruturado (JSON).

Usa pythonjsonlogger para output em JSON,
facilitando integracao com sistemas de log (ELK, CloudWatch, etc).
"""

import logging
import sys
from datetime import UTC, datetime

from pythonjsonlogger import jsonlogger

from app.config import settings


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """Formatter customizado para logs JSON."""

    def add_fields(self, log_record, record, message_dict):
        super().add_fields(log_record, record, message_dict)

        # Adiciona campos padrao
        log_record["timestamp"] = datetime.now(UTC).isoformat()
        log_record["level"] = record.levelname
        log_record["logger"] = record.name
        log_record["environment"] = settings.environment
        log_record["app"] = settings.app_name

        # Remove campos duplicados
        if "message" not in log_record and "msg" in log_record:
            log_record["message"] = log_record.pop("msg")


def setup_logging() -> logging.Logger:
    """
    Configura logging estruturado para a aplicacao.

    Em producao: JSON para stdout
    Em desenvolvimento: Formato legivel para humanos
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, settings.log_level.upper()))

    # Remove handlers existentes
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Handler para stdout
    handler = logging.StreamHandler(sys.stdout)

    if settings.is_production:
        # JSON em producao
        formatter = CustomJsonFormatter(
            "%(timestamp)s %(level)s %(name)s %(message)s"
        )
    else:
        # Formato legivel em desenvolvimento
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

    handler.setFormatter(formatter)
    root_logger.addHandler(handler)

    # Silencia loggers verbosos
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

    return root_logger


def get_logger(name: str) -> logging.Logger:
    """Retorna logger com nome especifico."""
    return logging.getLogger(name)


# Logger principal da aplicacao
logger = get_logger("app")
