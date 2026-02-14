# 🐳 Docker - geek.bidu.guru

Configuração Docker otimizada para produção no Dokploy.

---

## 📁 Arquivos

### `Dockerfile`
Imagem multi-stage otimizada para FastAPI com Playwright/Chromium.

**Características:**
- Python 3.12 slim
- Multi-stage build (builder + runtime)
- Playwright + Chromium pré-instalados
- Usuário não-root (`appuser`)
- Health check configurado
- Migrations automáticas no CMD
- Otimizado para produção

### `docker-compose.yml`
Arquivo único para **PRODUÇÃO no Dokploy**.

**Serviços:**
- `app` (FastAPI + Uvicorn)
- `redis` (cache persistente)

**Características:**
- PostgreSQL **remoto** (conecta via `dokploy-network`)
- Rede `dokploy-network` (externa - gerenciada pelo Dokploy)
- Volumes persistentes:
  - `geek_bidu_uploads` → `/app/uploads`
  - `geek_bidu_redis` → `/data`
- Health checks configurados
- Restart policy: `unless-stopped`
- SHM size 2GB para Playwright
- Seccomp unconfined para Chromium
- Porta exposta apenas em localhost (`127.0.0.1:8000`)

### `.dockerignore`
Arquivos ignorados no build da imagem.

---

## 🚀 Deploy no Dokploy

### Pré-requisitos

1. **Rede Dokploy** criada no servidor:
   ```bash
   docker network create dokploy-network
   ```

2. **PostgreSQL remoto** acessível via rede `dokploy-network`
   - Database: `geek_bidu_prod`
   - Usuário: `geek_app_prod`

### Configuração no Dokploy

1. **Criar novo projeto**: `geek-bidu-guru`
2. **Tipo**: Docker Compose
3. **Repositório Git**:
   - URL: `https://github.com/seu-usuario/geek.bidu.guru`
   - Branch: `main`
   - Compose file: `docker/docker-compose.yml`
   - Dockerfile: `docker/Dockerfile`

4. **Variáveis de Ambiente** (configurar no Dokploy):

```bash
# Essenciais
DB_PASSWORD=sua_senha_postgres
SECRET_KEY=sua_secret_key_segura
APP_URL=https://geek.bidu.guru
ALLOWED_HOSTS=geek.bidu.guru,www.geek.bidu.guru

# Opcionais (APIs de afiliados, IA, Analytics, Email)
AMAZON_ACCESS_KEY=...
AMAZON_SECRET_KEY=...
AMAZON_PARTNER_TAG=...
MELI_CLIENT_ID=...
MELI_CLIENT_SECRET=...
OPENAI_API_KEY=...
GA4_MEASUREMENT_ID=...
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
```

**Lista completa**: veja `.env.production.example`

### Build e Deploy

O Dokploy fará o build automaticamente usando:
1. `docker/Dockerfile` para criar a imagem `geek-bidu-app:latest`
2. `docker/docker-compose.yml` para orquestrar os containers

**No primeiro deploy**, após os containers subirem:

```bash
# 1. Criar usuário admin
docker exec -it geek_bidu_app python /app/scripts/create_admin.py

# 2. Verificar health
curl http://localhost:8000/health
```

---

## 🔍 Estrutura de Redes

```
┌─────────────────────────────────────────────────┐
│              dokploy-network (externa)           │
├─────────────────────────────────────────────────┤
│                                                  │
│  ┌──────────────┐      ┌──────────────┐         │
│  │  PostgreSQL  │◄─────┤ geek_bidu_app│         │
│  │   (remoto)   │      └───────┬──────┘         │
│  └──────────────┘              │                │
│                                 │                │
│                          geek_network            │
│                                 │                │
│                        ┌────────▼──────┐         │
│                        │geek_bidu_redis│         │
│                        └───────────────┘         │
└─────────────────────────────────────────────────┘
```

**Redes:**
- `dokploy-network` (externa): Comunicação com PostgreSQL e outros serviços do Dokploy
- `geek_network` (interna): Comunicação app ↔ Redis

---

## 🛠️ Comandos Úteis

### Logs

```bash
# Ver logs do app
docker logs -f geek_bidu_app

# Ver logs do Redis
docker logs -f geek_bidu_redis

# Ver apenas erros (logs JSON)
docker logs geek_bidu_app 2>&1 | grep '"level":"ERROR"'
```

### Acesso ao Container

```bash
# Shell no container do app
docker exec -it geek_bidu_app bash

# Executar comando Python
docker exec -it geek_bidu_app python -c "print('Hello')"
```

### Health Check

```bash
# Verificar saúde da aplicação
curl http://localhost:8000/health

# Ou de fora do servidor (se HTTPS configurado)
curl https://geek.bidu.guru/health
```

### Migrations

```bash
# Ver migration atual
docker exec geek_bidu_app bash -c "cd /app/src && alembic current"

# Executar migrations pendentes
docker exec geek_bidu_app bash -c "cd /app/src && alembic upgrade head"

# Ver histórico de migrations
docker exec geek_bidu_app bash -c "cd /app/src && alembic history"
```

### Volumes

```bash
# Ver volumes
docker volume ls | grep geek_bidu

# Inspecionar volume de uploads
docker volume inspect geek_bidu_uploads

# Backup do volume de uploads
docker run --rm \
  -v geek_bidu_uploads:/data \
  -v $(pwd):/backup \
  alpine tar czf /backup/uploads_backup_$(date +%Y%m%d).tar.gz /data
```

### Restart

```bash
# Restart do app
docker restart geek_bidu_app

# Restart completo
docker compose -f docker/docker-compose.yml restart

# Restart forçado (down + up)
docker compose -f docker/docker-compose.yml down
docker compose -f docker/docker-compose.yml up -d
```

### Uso de Recursos

```bash
# Ver uso de CPU/RAM/Rede
docker stats geek_bidu_app geek_bidu_redis

# Ver uso de disco
docker system df -v
```

---

## 🔧 Troubleshooting

### ❌ "Database not connected"

**Causa**: PostgreSQL inacessível ou credenciais incorretas.

**Soluções:**
```bash
# 1. Testar conexão
docker exec geek_bidu_app python /app/scripts/test_database.py

# 2. Verificar variável DB_PASSWORD
docker exec geek_bidu_app env | grep DATABASE_URL

# 3. Verificar se container está na rede dokploy-network
docker inspect geek_bidu_app | grep -A 10 Networks

# 4. Testar conexão direta ao PostgreSQL
docker exec geek_bidu_app ping postgres
```

### ❌ "Redis connection failed"

**Causa**: Redis não está rodando ou não está na rede.

**Soluções:**
```bash
# 1. Verificar se Redis está rodando
docker ps | grep geek_bidu_redis

# 2. Testar conexão
docker exec geek_bidu_redis redis-cli ping
# Deve retornar: PONG

# 3. Verificar redes
docker inspect geek_bidu_app | grep -A 5 geek_network
docker inspect geek_bidu_redis | grep -A 5 geek_network
```

### ❌ "Playwright Chromium crash"

**Causa**: shm_size insuficiente.

**Solução**: Verificar `docker-compose.yml`:
```yaml
shm_size: '2gb'
security_opt:
  - seccomp:unconfined
```

Se correto, restart:
```bash
docker restart geek_bidu_app
```

### ❌ "502 Bad Gateway"

**Causa**: App não está respondendo.

**Soluções:**
```bash
# 1. Verificar se app está respondendo
docker exec geek_bidu_app curl http://localhost:8000/health

# 2. Ver logs
docker logs geek_bidu_app --tail 50

# 3. Verificar porta
docker port geek_bidu_app

# 4. Restart
docker restart geek_bidu_app
```

### ❌ "Uploads não aparecem"

**Causa**: Volume não montado ou `UPLOAD_DIR` incorreto.

**Soluções:**
```bash
# 1. Verificar volume montado
docker exec geek_bidu_app ls -la /app/uploads

# 2. Verificar variável UPLOAD_DIR
docker exec geek_bidu_app env | grep UPLOAD_DIR
# Deve retornar: UPLOAD_DIR=/app/uploads

# 3. Verificar permissões
docker exec geek_bidu_app stat /app/uploads
# Owner deve ser: appuser
```

---

## 🔐 Segurança

### Checklist

- [ ] `DEBUG=false` em produção
- [ ] `SECRET_KEY` única e segura (mínimo 32 caracteres)
- [ ] `DB_PASSWORD` forte (mínimo 16 caracteres, alfanumérico + símbolos)
- [ ] Porta exposta apenas em localhost (`127.0.0.1:8000`)
- [ ] HTTPS configurado via Traefik/Nginx
- [ ] Variáveis de ambiente configuradas no Dokploy (não no código)
- [ ] Backups regulares (PostgreSQL + volumes)

### Gerar Chaves Seguras

```bash
# SECRET_KEY (use esta no Dokploy)
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Senha forte aleatória
python -c "import secrets, string; chars = string.ascii_letters + string.digits + string.punctuation; print(''.join(secrets.choice(chars) for _ in range(20)))"
```

---

## 📊 Monitoramento

### Logs Estruturados (JSON)

A aplicação gera logs em JSON para facilitar parsing:

```bash
# Ver apenas erros
docker logs geek_bidu_app 2>&1 | grep '"level":"ERROR"'

# Ver apenas warnings
docker logs geek_bidu_app 2>&1 | grep '"level":"WARNING"'

# Filtrar por path
docker logs geek_bidu_app 2>&1 | grep '/api/v1/products'
```

### Health Checks

```bash
# Via curl
curl http://localhost:8000/health

# Via Docker
docker inspect geek_bidu_app | grep -A 10 Health
```

### Métricas de Uso

```bash
# CPU, RAM, I/O em tempo real
docker stats geek_bidu_app geek_bidu_redis

# Disco usado pelos containers
docker ps --size | grep geek_bidu

# Disco usado pelos volumes
docker system df -v | grep geek_bidu
```

---

## 📚 Documentação Adicional

- **Deploy completo**: `../docs/DEPLOY_DOKPLOY.md`
- **Quickstart**: `../DEPLOY_DOKPLOY_QUICKSTART.md`
- **Checklist**: `../DEPLOY_CHECKLIST.md`
- **PRD**: `../PRD.md`
- **Configuração**: `../CLAUDE.md`

---

## 🎯 Diferenças: Easypanel → Dokploy

| Item | Easypanel | Dokploy |
|---|---|---|
| **Rede externa** | `easypanel-kvm8` + `interna` | `dokploy-network` |
| **Nome dos volumes** | `geek_bidu_uploads` | `geek_bidu_uploads` (mesmo) |
| **Container name** | `geek_bidu_app` | `geek_bidu_app` (mesmo) |
| **Porta** | `127.0.0.1:8000` | `127.0.0.1:8000` (mesmo) |
| **Variáveis** | Inline no compose | Configuradas no painel |

**Principais mudanças:**
- ✅ Rede `easypanel-kvm8` → `dokploy-network`
- ✅ Variáveis de ambiente agora usam `${VAR}` (configuradas no Dokploy)
- ✅ Mantidas todas as configurações que funcionavam (Playwright, volumes, health checks)

---

**Versão**: 2.0 (Dokploy)
**Última atualização**: 2026-02-14
**Projeto**: geek.bidu.guru
