# =============================================================================
# Makefile - geek.bidu.guru
# Comandos uteis para desenvolvimento local
# =============================================================================

.PHONY: help up down logs shell db-shell migrate test lint format clean

# Variaveis
DOCKER_COMPOSE = docker compose -f docker/docker-compose.yml
APP_CONTAINER = geek_app
# Nota: PostgreSQL e remoto (VPS), nao ha container local

# -----------------------------------------------------------------------------
# Help
# -----------------------------------------------------------------------------
help: ## Mostra esta ajuda
	@echo "geek.bidu.guru - Comandos disponiveis:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# -----------------------------------------------------------------------------
# Docker Compose
# -----------------------------------------------------------------------------
up: ## Inicia todos os containers (dev)
	$(DOCKER_COMPOSE) up -d
	@echo "Aplicacao rodando em http://localhost:8001"
	@echo "Redis local na porta 6380"

up-build: ## Rebuilda e inicia os containers
	$(DOCKER_COMPOSE) up -d --build

down: ## Para todos os containers
	$(DOCKER_COMPOSE) down

down-v: ## Para containers e remove volumes
	$(DOCKER_COMPOSE) down -v

restart: ## Reinicia os containers
	$(DOCKER_COMPOSE) restart

logs: ## Mostra logs de todos os containers
	$(DOCKER_COMPOSE) logs -f

logs-app: ## Mostra logs apenas da aplicacao
	$(DOCKER_COMPOSE) logs -f app

ps: ## Lista containers em execucao
	$(DOCKER_COMPOSE) ps

# -----------------------------------------------------------------------------
# Shell e Debug
# -----------------------------------------------------------------------------
shell: ## Acessa o shell do container da aplicacao
	$(DOCKER_COMPOSE) exec app /bin/bash

shell-root: ## Acessa o shell como root
	$(DOCKER_COMPOSE) exec -u root app /bin/bash

db-shell: ## Acessa o psql do PostgreSQL REMOTO (requer psql instalado)
	@echo "Conectando ao PostgreSQL remoto..."
	@echo "Certifique-se de que DATABASE_URL esta configurado no .env"
	psql "$${DATABASE_URL}"

redis-cli: ## Acessa o Redis CLI
	$(DOCKER_COMPOSE) exec redis redis-cli

# -----------------------------------------------------------------------------
# Database / Migrations
# -----------------------------------------------------------------------------
migrate: ## Executa todas as migrations pendentes
	$(DOCKER_COMPOSE) exec -w /app/src app alembic upgrade head

migrate-down: ## Reverte ultima migration
	$(DOCKER_COMPOSE) exec -w /app/src app alembic downgrade -1

migrate-new: ## Cria nova migration (usar: make migrate-new MSG="descricao")
	$(DOCKER_COMPOSE) exec -w /app/src app alembic revision --autogenerate -m "$(MSG)"

migrate-history: ## Mostra historico de migrations
	$(DOCKER_COMPOSE) exec -w /app/src app alembic history

migrate-current: ## Mostra migration atual
	$(DOCKER_COMPOSE) exec -w /app/src app alembic current

# -----------------------------------------------------------------------------
# Testes
# -----------------------------------------------------------------------------
test: ## Executa todos os testes
	$(DOCKER_COMPOSE) exec app pytest src/tests/ -v

test-cov: ## Executa testes com cobertura
	$(DOCKER_COMPOSE) exec app pytest src/tests/ -v --cov=src/app --cov-report=html

test-unit: ## Executa apenas testes unitarios
	$(DOCKER_COMPOSE) exec app pytest src/tests/unit/ -v

test-integration: ## Executa apenas testes de integracao
	$(DOCKER_COMPOSE) exec app pytest src/tests/integration/ -v

# -----------------------------------------------------------------------------
# Qualidade de Codigo
# -----------------------------------------------------------------------------
lint: ## Executa linter (ruff)
	$(DOCKER_COMPOSE) exec app ruff check src/

lint-fix: ## Corrige problemas do linter automaticamente
	$(DOCKER_COMPOSE) exec app ruff check src/ --fix

format: ## Formata codigo (black)
	$(DOCKER_COMPOSE) exec app black src/

type-check: ## Verifica tipos (mypy)
	$(DOCKER_COMPOSE) exec app mypy src/app/

# -----------------------------------------------------------------------------
# Seed de Dados
# -----------------------------------------------------------------------------
seed: ## Popula banco com dados de exemplo (categorias e produtos)
	cd src && python -m scripts.seed_data

seed-clear: ## Limpa dados e popula novamente
	cd src && python -m scripts.seed_data --clear

seed-force: ## Popula sem confirmacao (uso em CI/CD)
	cd src && python -m scripts.seed_data --force

# -----------------------------------------------------------------------------
# Utilitarios
# -----------------------------------------------------------------------------
clean: ## Remove arquivos temporarios e cache
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true

env: ## Copia .env.example para .env (se nao existir)
	@if [ ! -f .env ]; then cp .env.example .env && echo ".env criado"; else echo ".env ja existe"; fi

secret-key: ## Gera uma SECRET_KEY segura
	@python -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(32))"

# -----------------------------------------------------------------------------
# Producao (Easypanel)
# -----------------------------------------------------------------------------
build-prod: ## Build da imagem para producao
	docker build -f docker/Dockerfile -t geek-bidu-guru:latest .

# -----------------------------------------------------------------------------
# Inicializacao rapida
# -----------------------------------------------------------------------------
init: env up migrate ## Inicializa o projeto (cria .env, sobe containers, roda migrations)
	@echo ""
	@echo "Projeto inicializado com sucesso!"
	@echo "Acesse: http://localhost:8000"
