# Deploy - geek.bidu.guru

> Guia para deploy em produção na VPS Hostinger KVM8 com Easypanel.

## Pré-requisitos

- Docker e Docker Compose instalados
- Easypanel configurado
- Rede `interna` criada (compartilhada com PostgreSQL)
- PostgreSQL rodando com alias `postgres` na rede `interna`

### Verificar pré-requisitos

```bash
# Docker
docker --version
docker compose version

# Rede interna
docker network ls | grep interna

# PostgreSQL rodando e com alias
docker ps | grep postgres
docker inspect kvm8_postgre-postgres-1 --format='{{json .NetworkSettings.Networks.interna.Aliases}}'
# Deve mostrar: ["postgres","db"]
```

---

## 1. Configurar Banco de Dados

```bash
# Acessar PostgreSQL
docker exec -it kvm8_postgre-postgres-1 psql -U postgres
```

```sql
-- Criar usuário e database
CREATE USER geek_app_prod WITH PASSWORD 'SUA_SENHA_SEGURA';
CREATE DATABASE geek_bidu_prod OWNER geek_app_prod;
GRANT ALL PRIVILEGES ON DATABASE geek_bidu_prod TO geek_app_prod;

\c geek_bidu_prod
GRANT ALL ON SCHEMA public TO geek_app_prod;
\q
```

---

## 2. Clonar Repositório

```bash
mkdir -p /opt/sites/geek-bidu-guru
cd /opt/sites/geek-bidu-guru
git clone https://github.com/victorbvieira/geek.bidu.guru.git .
```

---

## 3. Build da Imagem Docker

```bash
cd /opt/sites/geek-bidu-guru
docker build -t geek-bidu-app:latest -f docker/Dockerfile .

# Verificar
docker images | grep geek-bidu-app
```

---

## 4. Configurar no Easypanel

### 4.1 Criar Projeto

1. Acesse o Easypanel
2. Clique em **"+ Create Project"**
3. Nome: `geek-bidu-guru`

### 4.2 Criar Serviço Docker Compose

1. Dentro do projeto, clique em **"+ Create Service"**
2. Selecione **"Docker Compose"**
3. Cole o conteúdo abaixo:

```yaml
services:
  app:
    image: geek-bidu-app:latest
    container_name: geek_bidu_app
    restart: unless-stopped
    environment:
      - DATABASE_URL=postgresql+asyncpg://geek_app_prod:${DB_PASSWORD}@postgres:5432/geek_bidu_prod
      - REDIS_URL=redis://redis:6379/0
      - ENVIRONMENT=production
      - DEBUG=false
      - SECRET_KEY=${SECRET_KEY}
      - JWT_ALGORITHM=${JWT_ALGORITHM:-HS256}
      - JWT_ACCESS_TOKEN_EXPIRE_MINUTES=${JWT_ACCESS_TOKEN_EXPIRE_MINUTES:-30}
      - JWT_REFRESH_TOKEN_EXPIRE_DAYS=${JWT_REFRESH_TOKEN_EXPIRE_DAYS:-7}
      - APP_NAME=${APP_NAME:-geek.bidu.guru}
      - APP_URL=${APP_URL:-https://geek.bidu.guru}
      - ALLOWED_HOSTS=${ALLOWED_HOSTS:-geek.bidu.guru,www.geek.bidu.guru}
      - LOG_LEVEL=${LOG_LEVEL:-INFO}
      - LOG_FORMAT=${LOG_FORMAT:-json}
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      start_period: 10s
      retries: 3
    ports:
      - "127.0.0.1:8000:8000"
    volumes:
      - geek_bidu_uploads:/app/uploads
    depends_on:
      redis:
        condition: service_healthy
    networks:
      - interna
      - easypanel-kvm8
      - geek_network

  redis:
    image: redis:7-alpine
    container_name: geek_bidu_redis
    restart: unless-stopped
    command: redis-server --appendonly yes
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
    volumes:
      - geek_bidu_redis:/data
    networks:
      - geek_network

volumes:
  geek_bidu_uploads:
  geek_bidu_redis:

networks:
  interna:
    external: true
  easypanel-kvm8:
    external: true
  geek_network:
    driver: bridge
```

### 4.3 Configurar Variáveis de Ambiente

No Easypanel, vá em **"Environment"** e adicione:

```
DB_PASSWORD=sua_senha_do_postgres
SECRET_KEY=sua_chave_secreta
```

Para gerar a SECRET_KEY:

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(64))"
```

### 4.4 Configurar Domínio

1. Vá em **"Domains"**
2. Adicione: `geek.bidu.guru`
3. **Compose Service**: `app`
4. **Port**: `8000`
5. Habilite HTTPS

### 4.5 Deploy

Clique em **"Deploy"** e aguarde os containers subirem.

---

## 5. Verificação

```bash
# Health check local
curl http://localhost:8000/health

# Containers rodando
docker ps | grep geek

# Logs
docker logs -f geek_bidu_app
```

Acesse: `https://geek.bidu.guru/health`

---

## Atualização (Deploy Manual)

```bash
cd /opt/sites/geek-bidu-guru

# Atualizar código
git pull origin main

# Rebuild da imagem
docker build -t geek-bidu-app:latest -f docker/Dockerfile .

# Restart containers (via Easypanel ou comando)
docker restart geek_bidu_app
```

---

## Comandos Úteis

```bash
# Logs
docker logs -f geek_bidu_app

# Entrar no container
docker exec -it geek_bidu_app bash

# Status dos containers
docker ps | grep geek

# Rebuild completo
docker rm -f geek_bidu_app geek_bidu_redis
# Depois faça Deploy no Easypanel

# Backup do banco
docker exec kvm8_postgre-postgres-1 pg_dump -U geek_app_prod geek_bidu_prod > backup_$(date +%Y%m%d).sql
```

---

## Troubleshooting

### Container não conecta ao PostgreSQL

```bash
# Verificar redes do container
docker inspect geek_bidu_app --format='{{range $k, $v := .NetworkSettings.Networks}}{{$k}} {{end}}'
# Deve incluir: interna

# Verificar alias do PostgreSQL
docker inspect kvm8_postgre-postgres-1 --format='{{json .NetworkSettings.Networks.interna.Aliases}}'
```

### Domínio não funciona (página padrão Easypanel)

```bash
# Conectar à rede do Easypanel
docker network connect easypanel-kvm8 geek_bidu_app
```

### Container reiniciando

```bash
docker logs geek_bidu_app --tail 50
```

---

## Deploy Automático (Webhook)

Configure deploy automático a cada push na branch `main`.

### 1. Copiar Scripts para a VPS

```bash
# Criar diretório
mkdir -p /opt/scripts

# Copiar script de deploy
cp /opt/sites/geek-bidu-guru/scripts/auto-deploy.sh /opt/scripts/deploy-geek.sh
chmod +x /opt/scripts/deploy-geek.sh

# Copiar servidor webhook
cp /opt/sites/geek-bidu-guru/scripts/webhook-server.py /opt/scripts/webhook-server.py
chmod +x /opt/scripts/webhook-server.py
```

### 2. Criar Serviço Systemd

```bash
# Gerar secret seguro
WEBHOOK_SECRET=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
echo "============================================"
echo "WEBHOOK_SECRET: $WEBHOOK_SECRET"
echo "============================================"
echo "GUARDE ESTE VALOR para configurar no GitHub!"

# Criar serviço
cat > /etc/systemd/system/geek-webhook.service << EOF
[Unit]
Description=Webhook Deploy geek.bidu.guru
After=network.target docker.service

[Service]
Type=simple
Environment=WEBHOOK_SECRET=$WEBHOOK_SECRET
ExecStart=/usr/bin/python3 /opt/scripts/webhook-server.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Ativar e iniciar
systemctl daemon-reload
systemctl enable geek-webhook
systemctl start geek-webhook

# Verificar status
systemctl status geek-webhook
```

### 3. Abrir Porta no Firewall

```bash
ufw allow 9000/tcp
```

### 4. Configurar Webhook no GitHub

1. Acesse: `https://github.com/victorbvieira/geek.bidu.guru/settings/hooks`
2. Clique **Add webhook**
3. Configure:
   - **Payload URL**: `http://167.88.32.240:9000/webhook/geek-bidu`
   - **Content type**: `application/json`
   - **Secret**: Cole o `WEBHOOK_SECRET` gerado no passo 2
   - **Which events?**: Just the push event
   - **Active**: Marcado
4. Clique **Add webhook**

### 5. Testar

```bash
# Ver logs do webhook server
journalctl -u geek-webhook -f
```

Em outro terminal, faça um push:

```bash
git commit --allow-empty -m "test: webhook deploy"
git push origin main
```

Verifique os logs:

```bash
# Logs do deploy
tail -f /var/log/geek-deploy.log
```

### Comandos do Webhook

```bash
# Status do serviço
systemctl status geek-webhook

# Reiniciar serviço
systemctl restart geek-webhook

# Ver logs
journalctl -u geek-webhook -n 50

# Executar deploy manual
/opt/scripts/deploy-geek.sh
```

---

**Última atualização**: 2025-12-12
