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
    # Tempo de expiracao do token JWT (padrao 24h para admin, evita logout frequente)
    jwt_access_token_expire_minutes: int = 1440  # 24 horas
    jwt_refresh_token_expire_days: int = 7

    # -------------------------------------------------------------------------
    # Logging
    # -------------------------------------------------------------------------
    log_level: str = "INFO"
    log_format: Literal["json", "text"] = "json"

    # -------------------------------------------------------------------------
    # Uploads
    # -------------------------------------------------------------------------
    # Diretorio para uploads persistentes (em producao, monte um volume aqui)
    # Se nao definido, usa o diretorio padrao dentro do projeto
    upload_dir: str | None = None

    # -------------------------------------------------------------------------
    # Google Analytics 4 & Search Console
    # -------------------------------------------------------------------------
    ga4_measurement_id: str | None = None  # Ex: G-XXXXXXXXXX
    google_site_verification: str | None = None  # Meta tag para verificacao GSC

    # -------------------------------------------------------------------------
    # n8n (Automacao)
    # -------------------------------------------------------------------------
    n8n_webhook_url: str | None = None  # URL base do n8n na VPS
    n8n_api_key: str | None = None  # API Key para autenticacao dos webhooks

    # -------------------------------------------------------------------------
    # LLM / IA (LiteLLM - suporta multiplos providers)
    # -------------------------------------------------------------------------
    # Chaves de API (configure apenas as que for usar)
    openai_api_key: str | None = None
    anthropic_api_key: str | None = None
    gemini_api_key: str | None = None       # Google Gemini (gemini/gemini-pro, gemini/gemini-1.5-flash)
    openrouter_api_key: str | None = None   # Para modelos gratuitos/baratos

    # Modelo padrao (ex: gpt-4o-mini, claude-3-haiku-20240307, openrouter/mistralai/mistral-7b-instruct)
    llm_default_model: str = "gpt-4o-mini"

    # Modelos por funcionalidade (permite otimizar custo vs qualidade)
    llm_model_content: str | None = None  # Para geracao de conteudo (posts, listicles)
    llm_model_simple: str | None = None   # Para tarefas simples (slugs, tags, SEO)

    # Configuracoes de geracao
    llm_max_tokens: int = 2000
    llm_temperature: float = 0.7

    # Timeout em segundos
    llm_timeout: int = 60

    # Cache de respostas (em minutos, 0 = desabilitado)
    llm_cache_ttl: int = 60

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
