# =============================================================================
# Dockerfile - geek.bidu.guru
# Multi-stage build otimizado para FastAPI
# Usado por: Easypanel (producao) e Docker Compose (desenvolvimento local)
#
# Python 3.12 - Versao estavel mais recente (3.14 ainda em alpha)
# PostgreSQL 18 - Conexao remota (VPS)
# =============================================================================

# -----------------------------------------------------------------------------
# Stage 1: Builder - Instala dependencias e cria wheels
# -----------------------------------------------------------------------------
FROM python:3.12-slim AS builder

WORKDIR /app

# Instalar dependencias de build
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar e instalar requirements
COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

# -----------------------------------------------------------------------------
# Stage 2: Runtime - Imagem final otimizada
# -----------------------------------------------------------------------------
FROM python:3.12-slim

WORKDIR /app

# Instalar apenas runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar wheels do builder e instalar
COPY --from=builder /app/wheels /wheels
COPY --from=builder /app/requirements.txt .
RUN pip install --no-cache-dir /wheels/*

# Copiar codigo fonte
COPY src/ ./src/

# Criar diretorio para uploads persistentes com subdiretorios
# Em producao, configure UPLOAD_DIR=/app/uploads e monte um volume
RUN mkdir -p /app/uploads/products /app/uploads/categories /app/uploads/posts

# Criar usuario nao-root para seguranca
RUN useradd --create-home --shell /bin/bash appuser \
    && chown -R appuser:appuser /app
USER appuser

# Volume para uploads persistentes
VOLUME ["/app/uploads"]

# Variaveis de ambiente
ENV PYTHONPATH=/app/src
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Porta da aplicacao
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Comando padrao (producao)
# Executa migrations e depois inicia o servidor
CMD ["sh", "-c", "cd /app/src && alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
