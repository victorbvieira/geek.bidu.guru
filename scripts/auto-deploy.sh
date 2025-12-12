#!/bin/bash
# =============================================================================
# Auto Deploy Script - geek.bidu.guru
# Recebe webhook do GitHub e faz deploy automatico
#
# Instalacao:
#   1. Copie este script para /opt/scripts/deploy-geek.sh na VPS
#   2. Siga o passo a passo em docs/DEPLOY.md secao "Deploy Automatico"
# =============================================================================

set -e

# Configuracoes
PROJECT_DIR="/opt/sites/geek-bidu-guru"
LOG_FILE="/var/log/geek-deploy.log"
DOCKER_IMAGE="geek-bidu-app:latest"
CONTAINER_NAME="geek_bidu_app"

# Funcao de log
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Verificar se diretorio existe
if [ ! -d "$PROJECT_DIR" ]; then
    log "ERRO: Diretorio $PROJECT_DIR nao encontrado"
    exit 1
fi

log "=========================================="
log "Iniciando deploy automatico"
log "=========================================="

cd "$PROJECT_DIR"

# 1. Baixar alteracoes do repositorio
log "1/5 Baixando alteracoes do GitHub..."
git fetch origin main
git reset --hard origin/main
log "    Commit: $(git rev-parse --short HEAD)"

# 2. Rebuild da imagem Docker
log "2/5 Rebuild da imagem Docker..."
docker build -t "$DOCKER_IMAGE" -f docker/Dockerfile . 2>&1 | tee -a "$LOG_FILE"

# 3. Restart do container
log "3/5 Reiniciando container..."
docker restart "$CONTAINER_NAME" 2>&1 | tee -a "$LOG_FILE"

# 4. Aguardar health check
log "4/5 Aguardando health check..."
sleep 10

MAX_ATTEMPTS=6
ATTEMPT=1
while [ $ATTEMPT -le $MAX_ATTEMPTS ]; do
    if curl -sf http://localhost:8000/health > /dev/null 2>&1; then
        log "    Health check OK!"
        break
    fi
    log "    Tentativa $ATTEMPT/$MAX_ATTEMPTS - aguardando..."
    sleep 5
    ATTEMPT=$((ATTEMPT + 1))
done

if [ $ATTEMPT -gt $MAX_ATTEMPTS ]; then
    log "ERRO: Health check falhou apos $MAX_ATTEMPTS tentativas"
    exit 1
fi

# 5. Limpeza
log "5/5 Limpando imagens antigas..."
docker image prune -f > /dev/null 2>&1

log "=========================================="
log "Deploy concluido com sucesso!"
log "=========================================="
