#!/bin/bash
# =============================================================================
# Deploy Automatico - geek.bidu.guru
#
# Verifica novos commits e faz deploy se necessario.
# Use -f ou --force para forcar deploy sem verificar commits.
#
# Cron (a cada 10 min):
#   */10 * * * * /opt/scripts/update-geek-bidu.sh >> /var/log/geek-deploy.log 2>&1
#
# Deploy manual forcado:
#   /opt/scripts/update-geek-bidu.sh --force
# =============================================================================

set -euo pipefail

# Configuracoes
SITE_NAME="geek.bidu.guru"
SITE_DIR="/opt/geek-bidu-guru"
DOCKER_IMAGE="geek-bidu-app:latest"
CONTAINER_NAME="geek_bidu_app"
STATE_FILE="/tmp/geek-bidu-last-commit.txt"
FORCE_DEPLOY=false

# Verificar parametro --force
if [[ "${1:-}" == "-f" || "${1:-}" == "--force" ]]; then
    FORCE_DEPLOY=true
fi

# Funcao de log
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [$SITE_NAME] $1"
}

# Funcao de deploy
do_deploy() {
    log "1/4 Rebuild da imagem Docker..."
    docker build -t "$DOCKER_IMAGE" -f "$SITE_DIR/docker/Dockerfile" "$SITE_DIR" --quiet

    log "2/4 Recriando container com nova imagem..."
    # Para e remove o container antigo, depois recria com a nova imagem
    # Usa docker-compose para garantir que todas as configs (shm_size, etc) sejam aplicadas
    cd "$SITE_DIR"
    docker compose -f docker/docker-compose.easypanel.yml up -d --force-recreate app

    log "3/4 Aguardando health check..."
    sleep 10

    local attempt=1
    while [ $attempt -le 6 ]; do
        if curl -sf http://localhost:8000/health > /dev/null 2>&1; then
            log "4/4 Health check OK!"
            docker image prune -f > /dev/null 2>&1
            return 0
        fi
        log "    Tentativa $attempt/6 - aguardando..."
        sleep 5
        attempt=$((attempt + 1))
    done

    log "ERRO: Health check falhou!"
    return 1
}

# Main
log "=========================================="
if [ "$FORCE_DEPLOY" = true ]; then
    log "Deploy FORCADO iniciado"
else
    log "Verificando atualizacoes..."
fi
log "=========================================="

# Verificar diretorio
if [ ! -d "$SITE_DIR/.git" ]; then
    log "ERRO: Repositorio nao encontrado em $SITE_DIR"
    exit 1
fi

cd "$SITE_DIR"

# Buscar atualizacoes
git fetch origin main --quiet

LOCAL_COMMIT=$(git rev-parse HEAD)
REMOTE_COMMIT=$(git rev-parse origin/main)
DEPLOYED_COMMIT=$(cat "$STATE_FILE" 2>/dev/null || echo "")

log "Commit local:    ${LOCAL_COMMIT:0:7}"
log "Commit remoto:   ${REMOTE_COMMIT:0:7}"
log "Ultimo deploy:   ${DEPLOYED_COMMIT:0:7}"

# Verificar se precisa atualizar codigo
if [ "$REMOTE_COMMIT" != "$LOCAL_COMMIT" ]; then
    log "Atualizando codigo..."
    git reset --hard origin/main
    LOCAL_COMMIT=$(git rev-parse HEAD)
fi

# Verificar se precisa fazer deploy
if [ "$FORCE_DEPLOY" = true ] || [ "$LOCAL_COMMIT" != "$DEPLOYED_COMMIT" ]; then
    log "Iniciando deploy..."

    if do_deploy; then
        echo "$LOCAL_COMMIT" > "$STATE_FILE"
        log "=========================================="
        log "Deploy concluido! Commit: ${LOCAL_COMMIT:0:7}"
        log "=========================================="
    else
        log "=========================================="
        log "ERRO: Deploy falhou!"
        log "=========================================="
        exit 1
    fi
else
    log "Nenhuma atualizacao necessaria."
    log "=========================================="
fi
