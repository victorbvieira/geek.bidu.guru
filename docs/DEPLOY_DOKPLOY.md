# 🚀 Guia de Deploy no Dokploy - geek.bidu.guru

Este guia explica como fazer o deploy da aplicação **geek.bidu.guru** no **Dokploy**.

---

## 📋 Pré-requisitos

### 1. PostgreSQL Remoto Configurado
- Database `geek_bidu_prod` criado
- Usuário `geek_app_prod` com permissões adequadas
- Acessível via rede (IP da VPS)

### 2. Variáveis de Ambiente Necessárias

Crie as seguintes variáveis no painel do Dokploy:

```bash
# Ambiente
ENVIRONMENT=production
DEBUG=false

# Banco de Dados (PostgreSQL remoto)
DATABASE_URL=postgresql+asyncpg://geek_app_prod:SENHA@IP_VPS:5432/geek_bidu_prod

# Redis (service name no docker-compose)
REDIS_URL=redis://redis:6379/0

# Segurança (GERE UMA CHAVE NOVA!)
# python -c "import secrets; print(secrets.token_urlsafe(32))"
SECRET_KEY=sua-chave-secreta-aqui

# JWT
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=120
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# Aplicação
APP_NAME=geek.bidu.guru
APP_URL=https://geek.bidu.guru
ALLOWED_HOSTS=geek.bidu.guru,www.geek.bidu.guru

# Uploads (volume externo)
UPLOAD_DIR=/app/uploads

# APIs de Afiliados
AMAZON_ACCESS_KEY=...
AMAZON_SECRET_KEY=...
AMAZON_PARTNER_TAG=...
AMAZON_REGION=BR

MELI_CLIENT_ID=...
MELI_CLIENT_SECRET=...
MELI_REDIRECT_URI=...

SHOPEE_APP_ID=...
SHOPEE_SECRET_KEY=...

# IA / LLM
OPENAI_API_KEY=...
OPENAI_MODEL=gpt-4o-mini
OPENROUTER_API_KEY=...

# Google Analytics 4
GA4_MEASUREMENT_ID=G-XXXXXXXXXX
GA4_API_SECRET=...
GOOGLE_SITE_VERIFICATION=...

# Amazon SES (Email)
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_REGION=us-west-2
EMAIL_FROM_ADDRESS=contato-geek@bidu.guru
EMAIL_FROM_NAME=geek.bidu.guru
EMAIL_VERIFICATION_EXPIRE_HOURS=48

# n8n (se aplicável)
N8N_WEBHOOK_URL=...
N8N_API_KEY=...

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
```

---

## 🐳 Passo a Passo do Deploy

### 1. Preparar o Repositório

No Dokploy, configure:
- **Repositório Git**: `https://github.com/victorbvieira/geek.bidu.guru`
- **Branch**: `main`
- **Dockerfile Path**: `docker/Dockerfile`
- **Docker Compose Path**: `docker/docker-compose.yml`

### 2. Configurar Rede Externa

No servidor onde o Dokploy está instalado, verifique se a rede `dokploy-network` existe:

```bash
docker network ls | grep dokploy-network
```

Se não existir, crie:

```bash
docker network create dokploy-network
```

### 3. Criar Aplicação no Dokploy

1. **Novo Projeto** → `geek-bidu-guru`
2. **Tipo**: Docker Compose
3. **Arquivo Compose**: `docker/docker-compose.dokploy.yml`
4. **Variáveis de Ambiente**: Adicione todas as variáveis acima

### 4. Configurar Volumes Persistentes

No Dokploy, mapeie os volumes:

- `uploads_data` → `/app/uploads` (persistência de imagens)
- `redis_data` → `/data` (cache Redis)

### 5. Configurar Reverse Proxy

Configure o Traefik ou Nginx no Dokploy:

```yaml
# Exemplo de labels para Traefik
labels:
  - "traefik.enable=true"
  - "traefik.http.routers.geek-bidu.rule=Host(`geek.bidu.guru`)"
  - "traefik.http.routers.geek-bidu.entrypoints=websecure"
  - "traefik.http.routers.geek-bidu.tls=true"
  - "traefik.http.routers.geek-bidu.tls.certresolver=letsencrypt"
  - "traefik.http.services.geek-bidu.loadbalancer.server.port=8000"
```

### 6. Executar Migrations

**ANTES do primeiro deploy**, execute as migrations:

```bash
# Acesse o container da aplicação
docker exec -it geek_app bash

# Execute as migrations
cd /app/src
alembic upgrade head
```

**Nota**: O Dockerfile já executa migrations automaticamente no CMD, mas é bom verificar.

### 7. Criar Usuário Admin

Após o primeiro deploy, crie o usuário administrador:

```bash
# Acesse o container
docker exec -it geek_app bash

# Acesse o shell Python
python

# Execute:
from app.database import AsyncSessionLocal
from app.models.admin import Admin
from app.core.security import hash_password
import asyncio

async def create_admin():
    async with AsyncSessionLocal() as db:
        admin = Admin(
            username="admin",
            email="seu-email@exemplo.com",
            hashed_password=hash_password("SuaSenhaSuperSegura123!"),
            is_active=True,
        )
        db.add(admin)
        await db.commit()
        print("Admin criado com sucesso!")

asyncio.run(create_admin())
```

### 8. Verificar Saúde da Aplicação

Acesse:
- **Health Check**: `https://geek.bidu.guru/health`
- **Admin Panel**: `https://geek.bidu.guru/admin/login`
- **Homepage**: `https://geek.bidu.guru/`

---

## 🔍 Verificações Pós-Deploy

### 1. Logs da Aplicação

```bash
# Ver logs do app
docker logs -f geek_app

# Ver logs do Redis
docker logs -f geek_redis
```

### 2. Health Check

```bash
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

### 3. Conexão com PostgreSQL

```bash
# No container da aplicação
docker exec -it geek_app bash

# Testar conexão
python -c "
from app.database import check_database_connection
import asyncio
result = asyncio.run(check_database_connection())
print(f'Database OK: {result}')
"
```

### 4. Verificar Uploads

```bash
# Verificar se o diretório de uploads está montado corretamente
docker exec geek_app ls -la /app/uploads

# Deve mostrar os subdiretórios:
# - products/
# - categories/
# - posts/
# - instagram/
```

### 5. Testar Playwright

```bash
# Verificar se o Chromium está instalado
docker exec geek_app python -m playwright install --dry-run chromium
```

---

## 🛠️ Troubleshooting

### Erro: "Database not connected"

**Causa**: DATABASE_URL incorreto ou PostgreSQL inacessível.

**Solução**:
1. Verifique o DATABASE_URL nas variáveis de ambiente
2. Teste a conexão do container ao PostgreSQL:
   ```bash
   docker exec geek_app ping IP_DO_POSTGRESQL
   ```
3. Verifique se o PostgreSQL aceita conexões externas (`postgresql.conf` e `pg_hba.conf`)

### Erro: "Redis connection failed"

**Causa**: Container Redis não está rodando ou não está na mesma rede.

**Solução**:
1. Verifique se o Redis está rodando:
   ```bash
   docker ps | grep geek_redis
   ```
2. Verifique se ambos os containers estão na `dokploy-network`:
   ```bash
   docker inspect geek_app | grep -A 10 Networks
   docker inspect geek_redis | grep -A 10 Networks
   ```

### Erro: "Playwright Chromium crash"

**Causa**: shm_size insuficiente ou seccomp bloqueando.

**Solução**:
1. Verifique se o `docker-compose.dokploy.yml` contém:
   ```yaml
   shm_size: '2gb'
   security_opt:
     - seccomp:unconfined
   ```
2. Restart o container:
   ```bash
   docker restart geek_app
   ```

### Erro: "Uploads não aparecem após restart"

**Causa**: Volume não está montado corretamente.

**Solução**:
1. Verifique os volumes no Dokploy
2. Certifique-se que `UPLOAD_DIR=/app/uploads` está definido nas variáveis de ambiente
3. Verifique permissões do volume:
   ```bash
   docker exec geek_app ls -la /app/uploads
   # Deve estar como appuser:appuser
   ```

### Erro: "502 Bad Gateway"

**Causa**: Aplicação não está respondendo na porta 8000.

**Solução**:
1. Verifique se a aplicação está rodando:
   ```bash
   docker exec geek_app curl http://localhost:8000/health
   ```
2. Verifique os logs:
   ```bash
   docker logs geek_app --tail 100
   ```

---

## 🔄 Atualizações e Rollback

### Atualizar Aplicação

1. **Push** para o branch `main` no GitHub
2. No Dokploy, clique em **Deploy** (rebuild automático)
3. Aguarde o build e restart

### Rollback

Se algo der errado após deploy:

```bash
# Via Dokploy UI: selecione a versão anterior e faça redeploy

# Ou via Docker (manual):
docker-compose -f docker/docker-compose.dokploy.yml down
git checkout <commit-anterior>
docker-compose -f docker/docker-compose.dokploy.yml up -d --build
```

---

## 📊 Monitoramento

### Logs Estruturados (JSON)

A aplicação usa logs em JSON para facilitar parsing:

```bash
# Ver apenas erros
docker logs geek_app 2>&1 | grep '"level":"ERROR"'

# Ver apenas INFO
docker logs geek_app 2>&1 | grep '"level":"INFO"'
```

### Métricas

Endpoints úteis para monitoramento:
- `/health` - Health check básico
- `/api/v1/admin/dashboard/stats` - Estatísticas do admin (requer auth)

---

## 🔐 Segurança

### Checklist de Segurança

- [ ] `DEBUG=false` em produção
- [ ] `SECRET_KEY` gerada de forma segura e única
- [ ] `ALLOWED_HOSTS` configurado corretamente
- [ ] PostgreSQL com senha forte e acesso restrito
- [ ] HTTPS configurado (via Traefik)
- [ ] Variáveis de ambiente não commitadas no Git
- [ ] Backup regular do volume `uploads_data`
- [ ] Backup regular do PostgreSQL

### Backup do PostgreSQL

```bash
# No servidor do PostgreSQL
pg_dump -U geek_app_prod -d geek_bidu_prod -F c -f backup_$(date +%Y%m%d).dump

# Restaurar (se necessário)
pg_restore -U geek_app_prod -d geek_bidu_prod backup_20260214.dump
```

---

## 📞 Suporte

- **Documentação do projeto**: `PRD.md`, `CLAUDE.md`
- **Logs de erro**: `/var/log/dokploy/` (no servidor)
- **Issues GitHub**: `https://github.com/seu-usuario/geek.bidu.guru/issues`

---

**Versão**: 1.0
**Última atualização**: 2026-02-14
**Projeto**: geek.bidu.guru
**Deploy Platform**: Dokploy
