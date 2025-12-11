"""
Configuracoes da aplicacao usando Pydantic Settings.
Carrega variaveis de ambiente automaticamente.
"""

from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuracoes globais da aplicacao."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # -------------------------------------------------------------------------
    # Ambiente
    # -------------------------------------------------------------------------
    environment: Literal["development", "staging", "production"] = "development"
    debug: bool = True

    # -------------------------------------------------------------------------
    # Aplicacao
    # -------------------------------------------------------------------------
    app_name: str = "geek.bidu.guru"
    app_url: str = "http://localhost:8000"
    allowed_hosts: str = "localhost,127.0.0.1"

    # -------------------------------------------------------------------------
    # Banco de Dados
    # -------------------------------------------------------------------------
    database_url: str = "postgresql+asyncpg://geek_app_dev:dev_password@db:5432/geek_bidu_dev"

    # -------------------------------------------------------------------------
    # Redis
    # -------------------------------------------------------------------------
    redis_url: str = "redis://redis:6379/0"

    # -------------------------------------------------------------------------
    # Seguranca
    # -------------------------------------------------------------------------
    secret_key: str = "dev-secret-key-change-in-production-INSECURE"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    jwt_refresh_token_expire_days: int = 7

    # -------------------------------------------------------------------------
    # Logging
    # -------------------------------------------------------------------------
    log_level: str = "INFO"
    log_format: Literal["json", "text"] = "json"

    # -------------------------------------------------------------------------
    # APIs Externas (opcionais)
    # -------------------------------------------------------------------------
    openai_api_key: str | None = None
    openai_model: str = "gpt-4o-mini"

    # -------------------------------------------------------------------------
    # Propriedades computadas
    # -------------------------------------------------------------------------
    @property
    def is_development(self) -> bool:
        return self.environment == "development"

    @property
    def is_production(self) -> bool:
        return self.environment == "production"

    @property
    def allowed_hosts_list(self) -> list[str]:
        return [h.strip() for h in self.allowed_hosts.split(",")]


@lru_cache
def get_settings() -> Settings:
    """Retorna instancia cacheada das configuracoes."""
    return Settings()


# Instancia global para imports diretos
settings = get_settings()
