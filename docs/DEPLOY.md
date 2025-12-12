# Deploy Cookbook - geek.bidu.guru

> Guia passo a passo para deploy em produção na VPS Hostinger KVM8 usando Docker Compose.

## Índice

1. [Pré-requisitos](#pré-requisitos)
2. [Configuração do Banco de Dados](#configuração-do-banco-de-dados)
3. [Deploy da Aplicação](#deploy-da-aplicação)
4. [Configuração do Traefik](#configuração-do-traefik)
5. [Executar Migrations](#executar-migrations)
6. [Verificação Pós-Deploy](#verificação-pós-deploy)
7. [Manutenção e Updates](#manutenção-e-updates)
8. [Troubleshooting](#troubleshooting)

---

## Pré-requisitos

### Na VPS (já configurado)
- [x] Docker e Docker Compose instalados
- [x] PostgreSQL rodando em container com rede `interna`
- [x] Traefik configurado para SSL automático
- [x] Rede Docker `interna` criada e compartilhada

### Verificar pré-requisitos

```bash
# Verificar Docker
docker --version
docker compose version

# Verificar rede interna existe
docker network ls | grep interna

# Verificar PostgreSQL está rodando e na rede interna
docker ps | grep postgres
docker inspect kvm8_postgre-postgres-1 --format='{{range $k, $v := .NetworkSettings.Networks}}{{$k}} {{end}}'
# Deve mostrar: interna monitoring

# Verificar alias do PostgreSQL na rede interna
docker inspect kvm8_postgre-postgres-1 --format='{{json .NetworkSettings.Networks.interna.Aliases}}'
# Deve mostrar: ["postgres","db"]
```

### Se o alias não existir, criar:

```bash
docker network disconnect interna kvm8_postgre-postgres-1
docker network connect --alias postgres --alias db interna kvm8_postgre-postgres-1
```

---

## Configuração do Banco de Dados

### 1. Acessar PostgreSQL

```bash
docker exec -it kvm8_postgre-postgres-1 psql -U postgres
```

### 2. Criar Database e Usuário de Produção

```sql
-- Criar usuário de produção
CREATE USER geek_app_prod WITH PASSWORD 'sua-senha-segura-aqui';

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

### 3. Verificar Conexão

```bash
docker exec -it kvm8_postgre-postgres-1 psql -U geek_app_prod -d geek_bidu_prod -c "SELECT 1;"
```

---

## Deploy da Aplicação

### 1. Clonar Repositório na VPS

```bash
# Criar diretório do projeto
mkdir -p /opt/geek-bidu-guru
cd /opt/geek-bidu-guru

# Clonar repositório
git clone https://github.com/victorbvieira/geek.bidu.guru.git .

# Ou se já existe, atualizar
git pull origin main
```

### 2. Criar Arquivo .env

```bash
# Criar .env na raiz do projeto
cat > .env << 'EOF'
# =============================================================================
# Variáveis de Ambiente - Produção
# =============================================================================

# Banco de Dados
DB_PASSWORD=SUA_SENHA_DO_POSTGRES_AQUI

# Segurança (gerar com: python -c "import secrets; print(secrets.token_urlsafe(64))")
SECRET_KEY=GERE_UMA_CHAVE_SEGURA_AQUI

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

# APIs de Afiliados (preencher conforme necessário)
AMAZON_ACCESS_KEY=
AMAZON_SECRET_KEY=
AMAZON_PARTNER_TAG=
AMAZON_REGION=BR

MELI_CLIENT_ID=
MELI_CLIENT_SECRET=

SHOPEE_APP_ID=
SHOPEE_SECRET_KEY=

# IA
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4o-mini

# Analytics
GA4_MEASUREMENT_ID=
GA4_API_SECRET=
EOF

# Editar e preencher as variáveis
nano .env
```

### 3. Build e Deploy

```bash
# Build e subir containers
docker compose -f docker/docker-compose.prod.yml up -d --build

# Verificar se subiu
docker ps | grep geek

# Deve mostrar:
# geek_bidu_app    ... Up ...
# geek_bidu_redis  ... Up ...
```

### 4. Verificar Logs

```bash
# Ver logs da aplicação
docker compose -f docker/docker-compose.prod.yml logs -f app

# Ver logs de todos os serviços
docker compose -f docker/docker-compose.prod.yml logs -f
```

### 5. Verificar Conexão com PostgreSQL

```bash
# Testar se a aplicação consegue conectar ao PostgreSQL
docker exec -it geek_bidu_app python -c "
import asyncio
import asyncpg

async def test():
    try:
        conn = await asyncpg.connect('postgresql://geek_app_prod:SUA_SENHA@postgres:5432/geek_bidu_prod')
        await conn.close()
        print('✓ Conexão com PostgreSQL OK!')
    except Exception as e:
        print(f'✗ Erro: {e}')

asyncio.run(test())
"
```

---

## Configuração do Traefik

O docker-compose.prod.yml já inclui labels para o Traefik. Se o Traefik está rodando, a aplicação será automaticamente exposta.

### Verificar se Traefik detectou o serviço

```bash
# Ver logs do Traefik
docker logs traefik 2>&1 | grep geek
```

### Configuração DNS

No seu provedor de DNS (Cloudflare, etc.):

```
# Registro A
geek.bidu.guru    A    167.88.32.240

# WWW (opcional)
www.geek.bidu.guru    CNAME    geek.bidu.guru
```

---

## Executar Migrations

### Primeiro Deploy (criar tabelas)

```bash
docker exec -it geek_bidu_app sh -c "cd /app/src && alembic upgrade head"
```

### Verificar status das migrations

```bash
docker exec -it geek_bidu_app sh -c "cd /app/src && alembic current"
```

---

## Verificação Pós-Deploy

### 1. Health Check

```bash
# Testar localmente na VPS
curl http://localhost:8000/health

# Testar via domínio (após DNS propagado)
curl https://geek.bidu.guru/health
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

### 2. Testar Admin

1. Acesse: `https://geek.bidu.guru/admin/login`
2. Login com credenciais iniciais
3. **IMPORTANTE**: Altere a senha após primeiro login!

### 3. Verificar SSL

```bash
curl -I https://geek.bidu.guru
```

Deve mostrar:
- `HTTP/2 200`
- Headers de segurança

### 4. Testar Endpoints

```bash
# Homepage
curl https://geek.bidu.guru/

# Sitemap
curl https://geek.bidu.guru/sitemap.xml

# Robots
curl https://geek.bidu.guru/robots.txt
```

---

## Manutenção e Updates

### Atualizar Aplicação

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

**Solução**: Verificar se o container está na rede `interna`:

```bash
# Ver redes do container
docker inspect geek_bidu_app --format='{{range $k, $v := .NetworkSettings.Networks}}{{$k}} {{end}}'

# Deve mostrar: geek_bidu_network interna

# Se não mostrar "interna", verificar docker-compose.prod.yml
# e fazer rebuild:
docker compose -f docker/docker-compose.prod.yml down
docker compose -f docker/docker-compose.prod.yml up -d --build
```

### Erro: "Connection refused" ou "Timeout"

O PostgreSQL não está acessível.

```bash
# Verificar se PostgreSQL está rodando
docker ps | grep postgres

# Verificar se PostgreSQL está na rede interna
docker inspect kvm8_postgre-postgres-1 --format='{{range $k, $v := .NetworkSettings.Networks}}{{$k}} {{end}}'

# Testar conexão de dentro do container app
docker exec -it geek_bidu_app ping postgres
```

### Erro: "Permission denied" no PostgreSQL

```bash
# Verificar se usuário existe e tem permissões
docker exec -it kvm8_postgre-postgres-1 psql -U postgres -c "\du geek_app_prod"

# Recriar permissões se necessário
docker exec -it kvm8_postgre-postgres-1 psql -U postgres -c "
GRANT ALL PRIVILEGES ON DATABASE geek_bidu_prod TO geek_app_prod;
"
```

### Container não sobe / Reiniciando

```bash
# Ver logs detalhados
docker logs geek_bidu_app --tail 100

# Ver status
docker ps -a | grep geek

# Verificar .env está correto
cat .env
```

### Erro: "502 Bad Gateway"

O Traefik não consegue alcançar a aplicação.

```bash
# Verificar se app está rodando
docker ps | grep geek_bidu_app

# Verificar se porta 8000 está respondendo
docker exec -it geek_bidu_app curl http://localhost:8000/health

# Verificar labels do Traefik
docker inspect geek_bidu_app --format='{{json .Config.Labels}}' | jq
```

### Migrations falham

```bash
# Ver erro detalhado
docker exec -it geek_bidu_app sh -c "cd /app/src && alembic upgrade head"

# Ver histórico de migrations
docker exec -it geek_bidu_app sh -c "cd /app/src && alembic history"

# Ver versão atual
docker exec -it geek_bidu_app sh -c "cd /app/src && alembic current"
```

---

## Checklist de Deploy

```
[ ] 1. Verificar pré-requisitos (Docker, rede interna, PostgreSQL)
[ ] 2. Criar database e usuário PostgreSQL
[ ] 3. Clonar repositório na VPS
[ ] 4. Criar arquivo .env com variáveis de produção
[ ] 5. Build e subir containers
[ ] 6. Verificar logs (sem erros)
[ ] 7. Executar migrations
[ ] 8. Testar health check local
[ ] 9. Configurar DNS
[ ] 10. Testar health check via domínio
[ ] 11. Verificar SSL/HTTPS
[ ] 12. Testar login no admin
[ ] 13. Alterar senha do admin
[ ] 14. Testar endpoints principais
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

# Listar containers do projeto
docker compose -f docker/docker-compose.prod.yml ps

# Rebuild completo
docker compose -f docker/docker-compose.prod.yml down
docker compose -f docker/docker-compose.prod.yml up -d --build --force-recreate

# Limpar imagens antigas
docker image prune -f
```

---

## Arquitetura de Produção

```
┌─────────────────────────────────────────────────────────────┐
│                    VPS Hostinger KVM8                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐     ┌─────────────────────────────────┐   │
│  │   Traefik   │────▶│  Rede: interna                  │   │
│  │  (SSL/Proxy)│     │  ┌───────────────┐              │   │
│  └─────────────┘     │  │  PostgreSQL   │              │   │
│         │            │  │  (postgres)   │              │   │
│         │            │  └───────────────┘              │   │
│         │            │         ▲                       │   │
│         ▼            │         │                       │   │
│  ┌─────────────────────────────┼───────────────────┐   │   │
│  │  Projeto: geek-bidu-guru    │                   │   │   │
│  │  ┌───────────────┐  ┌───────┴─────┐            │   │   │
│  │  │  geek_bidu_app│──│   Redis     │            │   │   │
│  │  │  (FastAPI)    │  │             │            │   │   │
│  │  └───────────────┘  └─────────────┘            │   │   │
│  │  Rede: geek_bidu_network + interna             │   │   │
│  └─────────────────────────────────────────────────┘   │   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

**Versão**: 2.0
**Última atualização**: 2025-12-12
**Método**: Docker Compose (sem Easypanel)
