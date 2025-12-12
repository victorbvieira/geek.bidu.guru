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
mkdir -p /opt/geek-bidu-guru
cd /opt/geek-bidu-guru
git clone https://github.com/victorbvieira/geek.bidu.guru.git .
```

---

## 3. Build da Imagem Docker

```bash
cd /opt/geek-bidu-guru
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
cd /opt/geek-bidu-guru

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

## Deploy Automático (Cron)

Configure deploy automático via cron que verifica novos commits periodicamente.

### 1. Copiar Script para a VPS

```bash
mkdir -p /opt/scripts
cp /opt/geek-bidu-guru/scripts/update-geek-bidu.sh /opt/scripts/update-geek-bidu.sh
chmod +x /opt/scripts/update-geek-bidu.sh
```

### 2. Configurar Cron

```bash
crontab -e

# Adicionar linha para verificar a cada 10 minutos:
*/10 * * * * /opt/scripts/update-geek-bidu.sh >> /var/log/geek-deploy.log 2>&1
```

### 3. Testar

```bash
# Verificar atualizacoes (deploy apenas se houver commits novos)
/opt/scripts/update-geek-bidu.sh

# Forcar deploy (ignora verificacao de commits)
/opt/scripts/update-geek-bidu.sh --force

# Ver logs
tail -f /var/log/geek-deploy.log
```

---

**Última atualização**: 2025-12-12
