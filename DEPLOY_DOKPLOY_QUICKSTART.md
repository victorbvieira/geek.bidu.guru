# ⚡ Deploy Rápido no Dokploy - geek.bidu.guru

Guia resumido para deploy em **5 minutos**. Documentação completa: `docs/DEPLOY_DOKPLOY.md`

---

## 🚀 5 Minutos para Deploy

### 1️⃣ Preparar Rede Docker (30 seg)

```bash
# No servidor Dokploy, criar rede (se não existir)
docker network ls | grep dokploy-network || docker network create dokploy-network
```

### 2️⃣ Preparar PostgreSQL (2 min)

**Opção A: PostgreSQL já existe no Dokploy**
```bash
# Apenas criar database e usuário
docker exec -it postgres psql -U postgres

CREATE DATABASE geek_bidu_prod;
CREATE USER geek_app_prod WITH PASSWORD 'SuaSenhaSegura123!';
GRANT ALL PRIVILEGES ON DATABASE geek_bidu_prod TO geek_app_prod;
\q
```

**Opção B: PostgreSQL remoto/externo**
```bash
# Testar conexão do servidor Dokploy ao PostgreSQL
psql "postgresql://geek_app_prod:SuaSenhaSegura123!@IP_POSTGRES:5432/geek_bidu_prod"
```

### 3️⃣ Configurar Projeto no Dokploy (1 min)

**No painel do Dokploy:**

1. **Novo Projeto** → `geek-bidu-guru`
2. **Tipo**: Docker Compose
3. **Git**:
   - Repositório: `https://github.com/seu-usuario/geek.bidu.guru`
   - Branch: `main`
4. **Build**:
   - Compose File: `docker/docker-compose.yml`
   - Dockerfile: `docker/Dockerfile`

### 4️⃣ Configurar Variáveis de Ambiente (1 min)

**Mínimo essencial** (configure no painel do Dokploy):

```bash
# Database (OBRIGATÓRIO - URL COMPLETA!)
# Opção A: Container PostgreSQL no Dokploy
DATABASE_URL=postgresql+asyncpg://geek_app_prod:SUA_SENHA@NOME_CONTAINER_POSTGRES:5432/geek_bidu_prod

# Opção B: PostgreSQL externo/VPS
DATABASE_URL=postgresql+asyncpg://geek_app_prod:SUA_SENHA@IP_OU_HOST:5432/geek_bidu_prod

# Segurança (OBRIGATÓRIO - gere uma chave nova!)
SECRET_KEY=<execute: python -c "import secrets; print(secrets.token_urlsafe(32))">

# App (OBRIGATÓRIO)
APP_URL=https://geek.bidu.guru
ALLOWED_HOSTS=geek.bidu.guru,www.geek.bidu.guru
```

**Como descobrir o nome do container PostgreSQL:**
```bash
docker ps | grep postgres
# Ou
docker network inspect dokploy-network | grep postgres
```

**Opcionais** (configure depois se precisar):
```bash
# APIs de afiliados
AMAZON_ACCESS_KEY=...
AMAZON_SECRET_KEY=...
AMAZON_PARTNER_TAG=...
MELI_CLIENT_ID=...
MELI_CLIENT_SECRET=...

# IA
OPENAI_API_KEY=sk-...

# Analytics
GA4_MEASUREMENT_ID=G-...

# Email
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
```

**Lista completa**: `.env.production.example`

### 5️⃣ Deploy! (5-10 min primeiro build)

1. **Deploy** no painel do Dokploy
2. Aguardar build completar (pode levar 5-10 min na primeira vez)
3. Verificar logs: `docker logs -f geek_bidu_app`

---

## ✅ Pós-Deploy Essencial (2 min)

### Teste 1: Health Check (10 seg)

```bash
# No servidor
curl http://localhost:8000/health

# Ou de fora (se HTTPS configurado)
curl https://geek.bidu.guru/health
```

**Resposta esperada:**
```json
{
  "status": "healthy",
  "app": "geek.bidu.guru",
  "environment": "production",
  "database": "connected"
}
```

### Teste 2: Criar Admin (1 min)

```bash
# Acessar container
docker exec -it geek_bidu_app bash

# Executar script interativo
python /app/scripts/create_admin.py

# Seguir as instruções:
# - Username: admin
# - Email: seu@email.com
# - Senha: (mínimo 8 caracteres)
```

### Teste 3: Fazer Login (30 seg)

1. Acesse: `https://geek.bidu.guru/admin/login`
2. Login com credenciais criadas
3. ✅ Deve aparecer o painel admin

---

## 🔧 Troubleshooting Rápido

### ❌ "Database not connected"

```bash
# Testar conexão
docker exec geek_bidu_app python /app/scripts/test_database.py
```

**Causas comuns:**
- `DB_PASSWORD` incorreto → Corrigir no painel do Dokploy
- PostgreSQL não acessível → Verificar se está na rede `dokploy-network`
- Firewall bloqueando → Verificar `pg_hba.conf`

**Solução rápida:**
```bash
# Verificar DATABASE_URL
docker exec geek_bidu_app env | grep DATABASE_URL

# Testar ping ao PostgreSQL
docker exec geek_bidu_app ping postgres
```

### ❌ "Redis connection failed"

```bash
# Verificar se Redis está rodando
docker ps | grep geek_bidu_redis

# Testar conexão
docker exec geek_bidu_redis redis-cli ping
# Deve retornar: PONG
```

**Solução**: Restart do Redis
```bash
docker restart geek_bidu_redis
```

### ❌ "502 Bad Gateway"

```bash
# Ver logs
docker logs geek_bidu_app --tail 50

# Testar se app está respondendo
docker exec geek_bidu_app curl http://localhost:8000/health
```

**Solução**: Restart do app
```bash
docker restart geek_bidu_app
```

### ❌ "Uploads não aparecem"

```bash
# Verificar volume
docker exec geek_bidu_app ls -la /app/uploads

# Verificar variável
docker exec geek_bidu_app env | grep UPLOAD_DIR
# Deve retornar: UPLOAD_DIR=/app/uploads
```

**Solução**: Verificar se volume está montado no `docker-compose.yml`
```yaml
volumes:
  - geek_bidu_uploads:/app/uploads
```

---

## 📊 Comandos Úteis

### Logs

```bash
# Ver logs em tempo real
docker logs -f geek_bidu_app

# Ver apenas erros (logs JSON)
docker logs geek_bidu_app 2>&1 | grep '"level":"ERROR"'
```

### Acesso ao Container

```bash
# Shell interativo
docker exec -it geek_bidu_app bash

# Executar comando direto
docker exec geek_bidu_app python /app/scripts/test_database.py
```

### Restart

```bash
# Restart do app
docker restart geek_bidu_app

# Restart completo (app + redis)
docker compose -f docker/docker-compose.yml restart
```

### Migrations

```bash
# Ver migration atual
docker exec geek_bidu_app bash -c "cd /app/src && alembic current"

# Executar migrations pendentes
docker exec geek_bidu_app bash -c "cd /app/src && alembic upgrade head"
```

### Monitoramento

```bash
# CPU, RAM, I/O
docker stats geek_bidu_app geek_bidu_redis

# Health check
docker inspect geek_bidu_app | grep -A 5 Health
```

---

## 🎯 Estrutura de Redes

```
┌────────────────────────────────────┐
│      dokploy-network (externa)     │
├────────────────────────────────────┤
│                                    │
│  ┌────────┐      ┌─────────────┐  │
│  │Postgres│◄─────┤geek_bidu_app│  │
│  └────────┘      └──────┬──────┘  │
│                         │          │
│                   geek_network     │
│                         │          │
│                  ┌──────▼──────┐   │
│                  │geek_bidu    │   │
│                  │_redis       │   │
│                  └─────────────┘   │
└────────────────────────────────────┘
```

**Explicação:**
- `dokploy-network`: Rede externa (acesso ao PostgreSQL e outros serviços)
- `geek_network`: Rede interna (app ↔ Redis)

---

## 📚 Próximos Passos

Agora que sua aplicação está rodando:

1. ✅ **Configurar HTTPS** (via Traefik no Dokploy)
2. ✅ **Configurar backups** do PostgreSQL e volumes
3. ✅ **Configurar APIs de afiliados** (Amazon, Mercado Livre)
4. ✅ **Configurar Google Analytics**
5. ✅ **Criar conteúdo** (categorias, produtos, posts)

### Documentação Completa

- **Deploy detalhado**: `docs/DEPLOY_DOKPLOY.md`
- **Checklist completo**: `DEPLOY_CHECKLIST.md`
- **Docker**: `docker/README.md`
- **PRD**: `PRD.md`

---

## 🆘 Precisa de Ajuda?

**Scripts úteis:**
- `scripts/test_database.py` - Testar conexão PostgreSQL
- `scripts/create_admin.py` - Criar usuário admin

**Documentação:**
- Troubleshooting completo: `docs/DEPLOY_DOKPLOY.md`
- README do Docker: `docker/README.md`

**Comandos de debug:**
```bash
# Ver todas as variáveis de ambiente
docker exec geek_bidu_app env

# Ver redes do container
docker inspect geek_bidu_app | grep -A 10 Networks

# Ver volumes montados
docker inspect geek_bidu_app | grep -A 10 Mounts

# Ver uso de recursos
docker stats geek_bidu_app geek_bidu_redis
```

---

## 🎯 Diferença Principal: Easypanel vs Dokploy

**Única mudança na rede:**
- ❌ Easypanel: `easypanel-kvm8` + `interna`
- ✅ Dokploy: `dokploy-network`

**Todo o resto é igual:**
- ✅ Mesmos volumes (`geek_bidu_uploads`, `geek_bidu_redis`)
- ✅ Mesmos containers (`geek_bidu_app`, `geek_bidu_redis`)
- ✅ Mesmas configurações (Playwright, health checks, etc.)

---

**Versão**: 2.0 (Dokploy)
**Última atualização**: 2026-02-14
**Projeto**: geek.bidu.guru

🚀 **Deploy concluído!** Acesse: https://geek.bidu.guru
