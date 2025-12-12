# Deploy Cookbook - geek.bidu.guru

> Guia passo a passo para deploy em produção na VPS Hostinger KVM8 usando **Easypanel + Docker Compose** (abordagem híbrida).

## Índice

1. [Visão Geral da Arquitetura](#visão-geral-da-arquitetura)
2. [Pré-requisitos](#pré-requisitos)
3. [Etapa 1: Configuração do Banco de Dados](#etapa-1-configuração-do-banco-de-dados)
4. [Etapa 2: Clonar Repositório na VPS](#etapa-2-clonar-repositório-na-vps)
5. [Etapa 3: Configurar Projeto no Easypanel](#etapa-3-configurar-projeto-no-easypanel)
6. [Etapa 4: Executar Migrations](#etapa-4-executar-migrations)
7. [Etapa 5: Verificação Pós-Deploy](#etapa-5-verificação-pós-deploy)
8. [Etapa 6: Configurar Webhook para Deploy Automático](#etapa-6-configurar-webhook-para-deploy-automático)
9. [Manutenção e Updates](#manutenção-e-updates)
10. [Troubleshooting](#troubleshooting)

---

## Visão Geral da Arquitetura

Usamos uma **abordagem híbrida**:
- **Easypanel**: Interface web para gerenciar o serviço docker-compose
- **Docker Compose**: Controle total sobre redes e containers
- **Webhook Script**: Deploy automático via script Python (não usa Easypanel)

```
┌─────────────────────────────────────────────────────────────┐
│                    VPS Hostinger KVM8                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐     ┌─────────────────────────────────┐   │
│  │   Traefik   │────▶│  Rede: interna                  │   │
│  │  (SSL/Proxy)│     │  ┌───────────────┐              │   │
│  └─────────────┘     │  │  PostgreSQL   │              │   │
│         │            │  │ alias:postgres│              │   │
│         │            │  └───────────────┘              │   │
│         │            │         ▲                       │   │
│         ▼            │         │                       │   │
│  ┌─────────────────────────────┼───────────────────┐   │   │
│  │  Projeto: geek-bidu-guru    │                   │   │   │
│  │  (gerenciado via Easypanel) │                   │   │   │
│  │  ┌───────────────┐  ┌───────┴─────┐            │   │   │
│  │  │  geek_bidu_app│──│   Redis     │            │   │   │
│  │  │  (FastAPI)    │  │             │            │   │   │
│  │  └───────────────┘  └─────────────┘            │   │   │
│  │  Redes: geek_bidu_network + interna            │   │   │
│  └─────────────────────────────────────────────────┘   │   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Webhook Server (porta 9000) - Deploy Automático    │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Pré-requisitos

### Na VPS (já configurado)
- [x] Docker e Docker Compose instalados
- [x] Easypanel instalado e acessível
- [x] PostgreSQL rodando em container com rede `interna`
- [x] Traefik configurado para SSL automático
- [x] Rede Docker `interna` criada e compartilhada

### Verificar pré-requisitos

Execute estes comandos na VPS para verificar se tudo está pronto:

```bash
# 1. Verificar Docker
docker --version
docker compose version

# 2. Verificar rede interna existe
docker network ls | grep interna

# 3. Verificar PostgreSQL está rodando
docker ps | grep postgres

# 4. Verificar PostgreSQL está na rede interna
docker inspect kvm8_postgre-postgres-1 --format='{{range $k, $v := .NetworkSettings.Networks}}{{$k}} {{end}}'
# Deve mostrar: interna (entre outras)

# 5. Verificar alias do PostgreSQL na rede interna (IMPORTANTE!)
docker inspect kvm8_postgre-postgres-1 --format='{{json .NetworkSettings.Networks.interna.Aliases}}'
# Deve mostrar: ["postgres","db"] ou similar
```

### Se o alias "postgres" não existir:

```bash
# Desconectar e reconectar com aliases
docker network disconnect interna kvm8_postgre-postgres-1
docker network connect --alias postgres --alias db interna kvm8_postgre-postgres-1

# Verificar novamente
docker inspect kvm8_postgre-postgres-1 --format='{{json .NetworkSettings.Networks.interna.Aliases}}'
```

---

## Etapa 1: Configuração do Banco de Dados

### 1.1 Acessar PostgreSQL

```bash
docker exec -it kvm8_postgre-postgres-1 psql -U postgres
```

### 1.2 Criar Database e Usuário de Produção

```sql
-- Criar usuário de produção (troque a senha!)
CREATE USER geek_app_prod WITH PASSWORD 'SUA_SENHA_SEGURA_AQUI';

-- Criar database
CREATE DATABASE geek_bidu_prod OWNER geek_app_prod;

-- Conceder privilégios
GRANT ALL PRIVILEGES ON DATABASE geek_bidu_prod TO geek_app_prod;

-- Conectar ao database e configurar schema
\c geek_bidu_prod

-- Garantir que o usuário pode criar objetos
GRANT ALL ON SCHEMA public TO geek_app_prod;

-- Sair
\q
```

### 1.3 Verificar Conexão

```bash
docker exec -it kvm8_postgre-postgres-1 psql -U geek_app_prod -d geek_bidu_prod -c "SELECT 1;"
```

Se retornar `1`, a conexão está funcionando!

---

## Etapa 2: Clonar Repositório na VPS

### 2.1 Criar diretório e clonar

```bash
# Criar diretório do projeto
mkdir -p /opt/geek-bidu-guru
cd /opt/geek-bidu-guru

# Clonar repositório (troque pelo seu usuário/repo)
git clone https://github.com/victorbvieira/geek.bidu.guru.git .

# Verificar se clonou corretamente
ls -la
# Deve mostrar: docker/, src/, docs/, requirements.txt, etc.
```

### 2.2 Verificar arquivo docker-compose.prod.yml existe

```bash
cat docker/docker-compose.prod.yml
```

Deve mostrar o arquivo de compose com os serviços `app` e `redis`.

---

## Etapa 3: Configurar Projeto no Easypanel

### 3.1 Acessar Easypanel

Acesse o Easypanel via browser: `https://seu-ip-ou-dominio:3000`

### 3.2 Criar Novo Projeto

1. Clique em **"+ Create Project"**
2. Nome do projeto: `geek-bidu-guru`
3. Clique em **"Create"**

### 3.3 Adicionar Serviço Docker Compose

1. Dentro do projeto, clique em **"+ Create Service"**
2. Selecione **"Docker Compose"**
3. Em **"Compose Path"**, digite: `/opt/geek-bidu-guru/docker/docker-compose.prod.yml`
   - Ou copie/cole o conteúdo do arquivo docker-compose.prod.yml

### 3.4 Configurar Variáveis de Ambiente

No Easypanel, vá em **"Environment"** e adicione:

```env
# Banco de Dados
DB_PASSWORD=SUA_SENHA_DO_POSTGRES_AQUI

# Segurança (gere com: python -c "import secrets; print(secrets.token_urlsafe(64))")
SECRET_KEY=SUA_CHAVE_SECRETA_AQUI

# JWT
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# Aplicação
APP_NAME=geek.bidu.guru
APP_URL=https://geek.bidu.guru
ALLOWED_HOSTS=geek.bidu.guru,www.geek.bidu.guru

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json

# APIs de Afiliados (opcional - preencha conforme necessário)
AMAZON_ACCESS_KEY=
AMAZON_SECRET_KEY=
AMAZON_PARTNER_TAG=
AMAZON_REGION=BR

MELI_CLIENT_ID=
MELI_CLIENT_SECRET=

SHOPEE_APP_ID=
SHOPEE_SECRET_KEY=

# IA (opcional)
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4o-mini

# Analytics (opcional)
GA4_MEASUREMENT_ID=
GA4_API_SECRET=
```

**Ou** crie o arquivo `.env` manualmente na VPS:

```bash
cd /opt/geek-bidu-guru

# Criar arquivo .env (será lido pelo docker-compose)
cat > .env << 'EOF'
# Banco de Dados
DB_PASSWORD=SUA_SENHA_DO_POSTGRES_AQUI

# Segurança
SECRET_KEY=SUA_CHAVE_SECRETA_AQUI

# JWT
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# Aplicação
APP_NAME=geek.bidu.guru
APP_URL=https://geek.bidu.guru
ALLOWED_HOSTS=geek.bidu.guru,www.geek.bidu.guru

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
EOF

# Editar e preencher valores reais
nano .env
```

### 3.5 Gerar SECRET_KEY segura

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(64))"
```

Copie o resultado e cole no campo `SECRET_KEY`.

### 3.6 Iniciar o Serviço

1. Clique em **"Deploy"** ou **"Start"** no Easypanel
2. Aguarde o build e inicialização
3. Verifique os logs para erros

**Ou** inicie via linha de comando:

```bash
cd /opt/geek-bidu-guru
docker compose -f docker/docker-compose.prod.yml up -d --build
```

### 3.7 Verificar se containers estão rodando

```bash
docker ps | grep geek
```

Deve mostrar:
```
geek_bidu_app    ... Up ...
geek_bidu_redis  ... Up ...
```

### 3.8 Verificar logs

```bash
# Ver logs da aplicação
docker logs -f geek_bidu_app

# Ou via docker-compose
docker compose -f docker/docker-compose.prod.yml logs -f app
```

---

## Etapa 4: Executar Migrations

### 4.1 Rodar migrations do Alembic

```bash
docker exec -it geek_bidu_app sh -c "cd /app/src && alembic upgrade head"
```

### 4.2 Verificar status das migrations

```bash
docker exec -it geek_bidu_app sh -c "cd /app/src && alembic current"
```

---

## Etapa 5: Verificação Pós-Deploy

### 5.1 Health Check Local

```bash
curl http://localhost:8000/health
```

Resposta esperada:
```json
{
  "status": "healthy",
  "app": "geek.bidu.guru",
  "environment": "production",
  "database": "connected"
}
```

### 5.2 Configurar DNS (se ainda não configurou)

No seu provedor de DNS (Cloudflare, etc.):

```
# Registro A
geek.bidu.guru    A    167.88.32.240

# WWW (opcional)
www.geek.bidu.guru    CNAME    geek.bidu.guru
```

### 5.3 Testar via Domínio (após DNS propagado)

```bash
# Health check
curl https://geek.bidu.guru/health

# Homepage
curl https://geek.bidu.guru/

# Sitemap
curl https://geek.bidu.guru/sitemap.xml

# Robots
curl https://geek.bidu.guru/robots.txt
```

### 5.4 Verificar SSL

```bash
curl -I https://geek.bidu.guru
```

Deve mostrar: `HTTP/2 200` e headers de segurança.

### 5.5 Testar Admin

1. Acesse: `https://geek.bidu.guru/admin/login`
2. Login com credenciais iniciais
3. **IMPORTANTE**: Altere a senha após primeiro login!

---

## Etapa 6: Configurar Webhook para Deploy Automático

Configure deploy automático a cada push na branch `main` usando GitHub Webhooks com um script Python.

### 6.1 Criar Script de Deploy

```bash
# Criar diretório para scripts
mkdir -p /opt/scripts

# Criar script de deploy
cat > /opt/scripts/deploy-geek.sh << 'EOF'
#!/bin/bash
# =============================================================================
# Script de Deploy Automático - geek.bidu.guru
# =============================================================================

set -e

PROJECT_DIR="/opt/geek-bidu-guru"
LOG_FILE="/var/log/geek-deploy.log"
COMPOSE_FILE="docker/docker-compose.prod.yml"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "========== Iniciando deploy =========="

cd "$PROJECT_DIR"

# Pull das alterações
log "Baixando alterações do repositório..."
git fetch origin main
git reset --hard origin/main

# Build e restart
log "Fazendo build e restart dos containers..."
docker compose -f "$COMPOSE_FILE" up -d --build

# Aguardar container subir
log "Aguardando container iniciar..."
sleep 10

# Executar migrations
log "Executando migrations..."
docker exec geek_bidu_app sh -c "cd /app/src && alembic upgrade head" 2>&1 | tee -a "$LOG_FILE"

# Health check
log "Verificando health check..."
if curl -sf http://localhost:8000/health > /dev/null; then
    log "✓ Deploy concluído com sucesso!"
else
    log "✗ Health check falhou!"
    exit 1
fi

# Limpar imagens antigas
log "Limpando imagens antigas..."
docker image prune -f

log "========== Deploy finalizado =========="
EOF

# Dar permissão de execução
chmod +x /opt/scripts/deploy-geek.sh
```

### 6.2 Criar Servidor de Webhook

```bash
# Criar script do servidor webhook
cat > /opt/scripts/webhook-server.py << 'EOF'
#!/usr/bin/env python3
"""
Servidor de Webhook para Deploy Automático
Escuta webhooks do GitHub e executa deploy quando há push na main
"""

import hashlib
import hmac
import json
import os
import subprocess
from http.server import HTTPServer, BaseHTTPRequestHandler

# Configurações
WEBHOOK_SECRET = os.environ.get('WEBHOOK_SECRET', 'seu-secret-aqui')
DEPLOY_SCRIPT = '/opt/scripts/deploy-geek.sh'
PORT = 9000

class WebhookHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        # Verificar path
        if self.path != '/webhook/deploy':
            self.send_response(404)
            self.end_headers()
            return

        # Ler payload
        content_length = int(self.headers.get('Content-Length', 0))
        payload = self.rfile.read(content_length)

        # Verificar assinatura do GitHub
        signature = self.headers.get('X-Hub-Signature-256', '')
        if not self.verify_signature(payload, signature):
            print(f"[ERRO] Assinatura inválida")
            self.send_response(401)
            self.end_headers()
            self.wfile.write(b'Invalid signature')
            return

        # Parsear payload
        try:
            data = json.loads(payload.decode('utf-8'))
        except json.JSONDecodeError:
            self.send_response(400)
            self.end_headers()
            return

        # Verificar se é push na main
        ref = data.get('ref', '')
        if ref != 'refs/heads/main':
            print(f"[INFO] Ignorando push para {ref}")
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'Ignored (not main branch)')
            return

        # Executar deploy
        print(f"[INFO] Recebido push na main, iniciando deploy...")
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'Deploy started')

        # Executar script de deploy em background
        subprocess.Popen(
            [DEPLOY_SCRIPT],
            stdout=open('/var/log/geek-deploy.log', 'a'),
            stderr=subprocess.STDOUT,
            start_new_session=True
        )

    def verify_signature(self, payload, signature):
        if not signature:
            return False

        expected = 'sha256=' + hmac.new(
            WEBHOOK_SECRET.encode('utf-8'),
            payload,
            hashlib.sha256
        ).hexdigest()

        return hmac.compare_digest(expected, signature)

    def log_message(self, format, *args):
        print(f"[{self.log_date_time_string()}] {args[0]}")

def main():
    server = HTTPServer(('0.0.0.0', PORT), WebhookHandler)
    print(f"Webhook server rodando na porta {PORT}...")
    print(f"Endpoint: http://0.0.0.0:{PORT}/webhook/deploy")
    server.serve_forever()

if __name__ == '__main__':
    main()
EOF

chmod +x /opt/scripts/webhook-server.py
```

### 6.3 Criar Serviço Systemd

```bash
# Gerar secret seguro
WEBHOOK_SECRET=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
echo "============================================"
echo "Seu WEBHOOK_SECRET: $WEBHOOK_SECRET"
echo "============================================"
echo "GUARDE ESTE VALOR! Você vai precisar dele no GitHub."
echo ""

# Criar arquivo de serviço
cat > /etc/systemd/system/geek-webhook.service << EOF
[Unit]
Description=Webhook Server para Deploy do geek.bidu.guru
After=network.target docker.service

[Service]
Type=simple
User=root
Environment=WEBHOOK_SECRET=$WEBHOOK_SECRET
ExecStart=/usr/bin/python3 /opt/scripts/webhook-server.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Habilitar e iniciar serviço
systemctl daemon-reload
systemctl enable geek-webhook
systemctl start geek-webhook

# Verificar status
systemctl status geek-webhook
```

### 6.4 Abrir Porta no Firewall

```bash
# Usando UFW (se instalado)
ufw allow 9000/tcp

# Ou usando iptables
iptables -A INPUT -p tcp --dport 9000 -j ACCEPT
```

### 6.5 Configurar Webhook no GitHub

1. Acesse o repositório: `https://github.com/victorbvieira/geek.bidu.guru`
2. Vá em **Settings** → **Webhooks** → **Add webhook**
3. Configure:
   - **Payload URL**: `http://167.88.32.240:9000/webhook/deploy`
   - **Content type**: `application/json`
   - **Secret**: Cole o `WEBHOOK_SECRET` que foi gerado no passo 6.3
   - **Which events?**: Selecione "Just the push event"
   - **Active**: ✓ Marcado
4. Clique em **Add webhook**

### 6.6 Testar o Webhook

```bash
# Ver logs do servidor webhook
journalctl -u geek-webhook -f
```

Em outro terminal ou no seu computador local:

```bash
# Fazer um commit de teste
git commit --allow-empty -m "test: trigger webhook deploy"
git push origin main
```

Verifique os logs:

```bash
# Logs de deploy
tail -f /var/log/geek-deploy.log
```

### 6.7 Verificar no GitHub

Vá em **Settings** → **Webhooks** → Clique no webhook → **Recent Deliveries**

- ✓ Verde: Webhook entregue com sucesso
- ✗ Vermelho: Erro na entrega

---

## Manutenção e Updates

### Atualização Manual

```bash
cd /opt/geek-bidu-guru

# Baixar alterações
git pull origin main

# Rebuild e restart
docker compose -f docker/docker-compose.prod.yml up -d --build

# Executar novas migrations (se houver)
docker exec -it geek_bidu_app sh -c "cd /app/src && alembic upgrade head"

# Verificar logs
docker compose -f docker/docker-compose.prod.yml logs -f app
```

### Reiniciar Serviços

```bash
# Reiniciar tudo
docker compose -f docker/docker-compose.prod.yml restart

# Reiniciar apenas a aplicação
docker restart geek_bidu_app
```

### Parar Serviços

```bash
docker compose -f docker/docker-compose.prod.yml down
```

### Backup do Banco

```bash
# Criar backup
docker exec kvm8_postgre-postgres-1 pg_dump -U geek_app_prod geek_bidu_prod > backup_$(date +%Y%m%d_%H%M%S).sql

# Restaurar backup
cat backup.sql | docker exec -i kvm8_postgre-postgres-1 psql -U geek_app_prod geek_bidu_prod
```

---

## Troubleshooting

### Erro: "Name or service not known"

O container não consegue resolver o hostname `postgres`.

```bash
# Ver redes do container
docker inspect geek_bidu_app --format='{{range $k, $v := .NetworkSettings.Networks}}{{$k}} {{end}}'
# Deve mostrar: geek_bidu_network interna

# Se não mostrar "interna", rebuild:
docker compose -f docker/docker-compose.prod.yml down
docker compose -f docker/docker-compose.prod.yml up -d --build
```

### Erro: "Connection refused" ou "Timeout"

```bash
# Verificar se PostgreSQL está rodando
docker ps | grep postgres

# Verificar alias existe
docker inspect kvm8_postgre-postgres-1 --format='{{json .NetworkSettings.Networks.interna.Aliases}}'

# Testar conexão de dentro do container app
docker exec -it geek_bidu_app python -c "
import asyncio
import asyncpg

async def test():
    conn = await asyncpg.connect('postgresql://geek_app_prod:SENHA@postgres:5432/geek_bidu_prod')
    print('Conexão OK!')
    await conn.close()

asyncio.run(test())
"
```

### Container não sobe / Reiniciando

```bash
# Ver logs detalhados
docker logs geek_bidu_app --tail 100

# Verificar .env
cat /opt/geek-bidu-guru/.env
```

### Webhook não funciona

```bash
# Ver status do serviço
systemctl status geek-webhook

# Ver logs
journalctl -u geek-webhook -n 50

# Reiniciar serviço
systemctl restart geek-webhook

# Testar script manualmente
/opt/scripts/deploy-geek.sh
```

### Erro: "502 Bad Gateway"

```bash
# Verificar se app está rodando
docker ps | grep geek_bidu_app

# Verificar porta 8000
docker exec -it geek_bidu_app curl http://localhost:8000/health
```

---

## Checklist de Deploy

```
[ ] 1. Verificar pré-requisitos (Docker, rede interna, PostgreSQL, aliases)
[ ] 2. Criar database e usuário PostgreSQL
[ ] 3. Clonar repositório na VPS (/opt/geek-bidu-guru)
[ ] 4. Configurar projeto no Easypanel (ou criar .env manual)
[ ] 5. Definir variáveis de ambiente (DB_PASSWORD, SECRET_KEY, etc.)
[ ] 6. Iniciar serviço (via Easypanel ou docker-compose)
[ ] 7. Verificar containers rodando (docker ps)
[ ] 8. Verificar logs (sem erros)
[ ] 9. Executar migrations (alembic upgrade head)
[ ] 10. Testar health check local (curl localhost:8000/health)
[ ] 11. Configurar DNS (se necessário)
[ ] 12. Testar via domínio (curl https://geek.bidu.guru/health)
[ ] 13. Verificar SSL/HTTPS
[ ] 14. Testar login no admin
[ ] 15. Configurar webhook (script + systemd + GitHub)
[ ] 16. Testar deploy automático
```

---

## Comandos Úteis

```bash
# Ver logs em tempo real
docker compose -f docker/docker-compose.prod.yml logs -f

# Ver logs apenas da app
docker logs -f geek_bidu_app

# Entrar no container
docker exec -it geek_bidu_app bash

# Ver uso de recursos
docker stats geek_bidu_app geek_bidu_redis

# Rebuild completo
docker compose -f docker/docker-compose.prod.yml down
docker compose -f docker/docker-compose.prod.yml up -d --build --force-recreate

# Limpar imagens antigas
docker image prune -f

# Ver logs do webhook
journalctl -u geek-webhook -f

# Ver logs de deploy
tail -f /var/log/geek-deploy.log
```

---

**Versão**: 2.1
**Última atualização**: 2025-12-12
**Método**: Easypanel + Docker Compose (híbrido)
