#!/bin/bash
# =============================================================================
# Auto Deploy Script - geek.bidu.guru
# Verifica novos commits no GitHub e faz deploy automatico via Easypanel CLI
#
# Uso: Adicionar ao cron para rodar a cada X minutos
# Exemplo: */5 * * * * /path/to/auto-deploy.sh >> /var/log/geek-deploy.log 2>&1
# =============================================================================

set -e

# Configuracoes
REPO_URL="https://api.github.com/repos/SEU_USUARIO/geek.bidu.guru/commits/main"
GITHUB_TOKEN="SEU_GITHUB_TOKEN"  # Token com permissao de leitura
PROJECT_NAME="geek-bidu-guru"
SERVICE_NAME="app"
STATE_FILE="/tmp/geek-last-commit.txt"

# Funcao de log
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# Buscar ultimo commit do GitHub
get_remote_commit() {
    curl -s -H "Authorization: token $GITHUB_TOKEN" \
         -H "Accept: application/vnd.github.v3+json" \
         "$REPO_URL" | grep -o '"sha": "[^"]*"' | head -1 | cut -d'"' -f4
}

# Buscar commit atual (ultimo deploy)
get_local_commit() {
    if [ -f "$STATE_FILE" ]; then
        cat "$STATE_FILE"
    else
        echo ""
    fi
}

# Salvar commit atual
save_commit() {
    echo "$1" > "$STATE_FILE"
}

# Fazer deploy via Easypanel CLI
do_deploy() {
    log "Iniciando deploy..."

    # Opcao 1: Via Easypanel CLI (se instalado)
    if command -v easypanel &> /dev/null; then
        easypanel deploy --project "$PROJECT_NAME" --service "$SERVICE_NAME"
        return $?
    fi

    # Opcao 2: Via Docker Compose (rebuild do container)
    # Descomentar se preferir este metodo
    # cd /path/to/easypanel/projects/$PROJECT_NAME
    # docker compose pull
    # docker compose up -d --build

    # Opcao 3: Via API do Easypanel (HTTP request)
    # Descomentar e configurar se Easypanel expor API
    # curl -X POST "http://localhost:3000/api/projects/$PROJECT_NAME/services/$SERVICE_NAME/deploy" \
    #      -H "Authorization: Bearer $EASYPANEL_TOKEN"

    log "AVISO: Nenhum metodo de deploy configurado. Configure uma das opcoes acima."
    return 1
}

# Main
main() {
    log "Verificando atualizacoes..."

    REMOTE_COMMIT=$(get_remote_commit)
    LOCAL_COMMIT=$(get_local_commit)

    if [ -z "$REMOTE_COMMIT" ]; then
        log "ERRO: Nao foi possivel obter commit remoto"
        exit 1
    fi

    log "Commit remoto: ${REMOTE_COMMIT:0:7}"
    log "Commit local:  ${LOCAL_COMMIT:0:7:-"(nenhum)"}"

    if [ "$REMOTE_COMMIT" != "$LOCAL_COMMIT" ]; then
        log "Novo commit detectado! Iniciando deploy..."

        if do_deploy; then
            save_commit "$REMOTE_COMMIT"
            log "Deploy concluido com sucesso!"
        else
            log "ERRO: Falha no deploy"
            exit 1
        fi
    else
        log "Nenhuma atualizacao necessaria"
    fi
}

main "$@"
