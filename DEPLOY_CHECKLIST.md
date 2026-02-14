# ✅ Checklist de Deploy - geek.bidu.guru no Dokploy

Use este checklist para garantir que tudo está configurado corretamente antes do deploy.

---

## 📋 Pré-Deploy

### 1. Preparação do Ambiente

- [ ] PostgreSQL remoto criado e acessível
  - [ ] Database: `geek_bidu_prod`
  - [ ] Usuário: `geek_app_prod` com permissões adequadas
  - [ ] Testar conexão: `psql "postgresql://geek_app_prod:SENHA@IP:5432/geek_bidu_prod"`

- [ ] Rede Docker do Dokploy configurada
  - [ ] Verificar: `docker network ls | grep dokploy-network`
  - [ ] Se não existir, criar: `docker network create dokploy-network`

### 2. Variáveis de Ambiente

Configurar no painel do Dokploy (baseado em `.env.production.example`):

**Essenciais (aplicação não inicia sem estas):**
- [ ] `ENVIRONMENT=production`
- [ ] `DEBUG=false`
- [ ] `DATABASE_URL=postgresql+asyncpg://...`
- [ ] `SECRET_KEY=...` (gerado com `secrets.token_urlsafe(32)`)
- [ ] `APP_URL=https://geek.bidu.guru`
- [ ] `ALLOWED_HOSTS=geek.bidu.guru,www.geek.bidu.guru`

**Redis:**
- [ ] `REDIS_URL=redis://redis:6379/0`

**JWT:**
- [ ] `JWT_ALGORITHM=HS256`
- [ ] `JWT_ACCESS_TOKEN_EXPIRE_MINUTES=120`
- [ ] `JWT_REFRESH_TOKEN_EXPIRE_DAYS=7`

**APIs de Afiliados (se aplicável):**
- [ ] `AMAZON_ACCESS_KEY`, `AMAZON_SECRET_KEY`, `AMAZON_PARTNER_TAG`
- [ ] `MELI_CLIENT_ID`, `MELI_CLIENT_SECRET`
- [ ] `SHOPEE_APP_ID`, `SHOPEE_SECRET_KEY`

**IA/LLM (se aplicável):**
- [ ] `OPENAI_API_KEY`, `OPENAI_MODEL`
- [ ] `OPENROUTER_API_KEY` (opcional)

**Google Analytics:**
- [ ] `GA4_MEASUREMENT_ID`
- [ ] `GOOGLE_SITE_VERIFICATION`

**Email (Amazon SES):**
- [ ] `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`
- [ ] `EMAIL_FROM_ADDRESS`, `EMAIL_FROM_NAME`

**Logs:**
- [ ] `LOG_LEVEL=INFO`
- [ ] `LOG_FORMAT=json`

### 3. Configuração do Projeto no Dokploy

- [ ] Criar novo projeto: `geek-bidu-guru`
- [ ] Tipo: **Docker Compose**
- [ ] Repositório Git configurado:
  - [ ] URL: `https://github.com/seu-usuario/geek.bidu.guru`
  - [ ] Branch: `main`
  - [ ] Arquivo Compose: `docker/docker-compose.dokploy.yml`
  - [ ] Dockerfile: `docker/Dockerfile` (se necessário)

### 4. Volumes

- [ ] Volume `uploads_data` mapeado para `/app/uploads`
- [ ] Volume `redis_data` mapeado para `/data`
- [ ] Variável `UPLOAD_DIR=/app/uploads` configurada

### 5. Reverse Proxy (Traefik/Nginx)

- [ ] Domínio apontando para o servidor (DNS)
- [ ] Configuração de HTTPS/SSL (Let's Encrypt)
- [ ] Labels do Traefik configuradas (se aplicável):
  ```yaml
  labels:
    - "traefik.enable=true"
    - "traefik.http.routers.geek-bidu.rule=Host(`geek.bidu.guru`)"
    - "traefik.http.routers.geek-bidu.entrypoints=websecure"
    - "traefik.http.routers.geek-bidu.tls=true"
    - "traefik.http.services.geek-bidu.loadbalancer.server.port=8000"
  ```

---

## 🚀 Deploy

### 1. Build e Deploy

- [ ] Fazer push para o branch `main`
- [ ] No Dokploy, clicar em **Deploy**
- [ ] Aguardar build completar (pode levar 5-10 min na primeira vez)
- [ ] Verificar logs para erros:
  ```bash
  docker logs -f geek_app
  ```

### 2. Executar Migrations (Primeira vez)

**O Dockerfile executa migrations automaticamente no CMD**, mas verifique:

```bash
# Acessar container
docker exec -it geek_app bash

# Verificar migrations
cd /app/src
alembic current

# Se necessário, executar manualmente
alembic upgrade head
```

- [ ] Migrations executadas com sucesso

### 3. Criar Usuário Admin (Primeira vez)

```bash
# Acessar container
docker exec -it geek_app bash

# Abrir shell Python
python

# Executar:
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

- [ ] Usuário admin criado
- [ ] Testar login em `https://geek.bidu.guru/admin/login`

---

## ✅ Pós-Deploy

### 1. Verificações de Saúde

- [ ] **Health Check OK**:
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

- [ ] **Homepage carrega**: `https://geek.bidu.guru/`
- [ ] **Admin Panel acessível**: `https://geek.bidu.guru/admin/login`
- [ ] **Docs desabilitadas em prod**: `https://geek.bidu.guru/docs` → 404 (OK!)

### 2. Testes Funcionais

- [ ] Login no admin funciona
- [ ] Criar categoria de teste
- [ ] Upload de imagem funciona
- [ ] Criar produto de teste
- [ ] Criar post de teste
- [ ] Acessar página do produto no frontend
- [ ] Acessar página do post no frontend
- [ ] Testar link de afiliado (`/goto/{slug}`)
- [ ] Verificar sitemap.xml: `https://geek.bidu.guru/sitemap.xml`
- [ ] Verificar robots.txt: `https://geek.bidu.guru/robots.txt`

### 3. Performance

- [ ] Tempo de carregamento da homepage < 2s
- [ ] Lighthouse Score > 80 (Performance, SEO, Accessibility)
- [ ] Imagens sendo servidas corretamente do volume `/app/uploads`

### 4. Segurança

- [ ] HTTPS funcionando (certificado válido)
- [ ] Headers de segurança presentes:
  ```bash
  curl -I https://geek.bidu.guru/ | grep -E '(Strict-Transport|Content-Security|X-Frame|X-Content)'
  ```
- [ ] DEBUG=false em produção (verificar logs)
- [ ] `/docs` e `/redoc` desabilitados (404)

### 5. Monitoramento

- [ ] Logs estruturados (JSON) funcionando:
  ```bash
  docker logs geek_app | tail -20
  ```
- [ ] Google Analytics tracking instalado (verificar no navegador)
- [ ] Alertas configurados (opcional - Uptime Robot, etc.)

### 6. Backup

- [ ] Backup do PostgreSQL configurado:
  ```bash
  pg_dump -U geek_app_prod -d geek_bidu_prod -F c -f backup_$(date +%Y%m%d).dump
  ```
- [ ] Backup do volume `uploads_data`:
  ```bash
  docker run --rm -v uploads_data:/data -v $(pwd):/backup alpine tar czf /backup/uploads_backup_$(date +%Y%m%d).tar.gz /data
  ```

---

## 🔄 Rollback (Se algo der errado)

- [ ] Identificar problema nos logs
- [ ] Se necessário, fazer rollback:
  ```bash
  # Via Dokploy UI: selecionar versão anterior e redeploy

  # Ou manualmente:
  docker-compose -f docker/docker-compose.dokploy.yml down
  git checkout <commit-anterior>
  docker-compose -f docker/docker-compose.dokploy.yml up -d --build
  ```
- [ ] Restaurar backup do banco (se necessário)

---

## 📊 Monitoramento Contínuo

### Diariamente:
- [ ] Verificar logs para erros
- [ ] Verificar uso de disco (volumes)
- [ ] Verificar health check

### Semanalmente:
- [ ] Revisar métricas do Google Analytics
- [ ] Verificar links de afiliados (cliques, conversões)
- [ ] Backup completo (PostgreSQL + volumes)

### Mensalmente:
- [ ] Atualizar dependências Python (se necessário)
- [ ] Revisar e otimizar queries lentas
- [ ] Revisar logs de erros acumulados

---

## 🐛 Troubleshooting Rápido

### App não inicia
```bash
# Ver logs
docker logs geek_app --tail 100

# Verificar variáveis de ambiente
docker exec geek_app env | grep -E '(DATABASE|SECRET|APP_URL)'

# Testar conexão com PostgreSQL
docker exec geek_app python -c "
from app.database import check_database_connection
import asyncio
print(asyncio.run(check_database_connection()))
"
```

### 502 Bad Gateway
```bash
# Verificar se app está respondendo
docker exec geek_app curl http://localhost:8000/health

# Verificar se está na porta correta
docker port geek_app

# Restart container
docker restart geek_app
```

### Uploads não aparecem
```bash
# Verificar volume montado
docker exec geek_app ls -la /app/uploads

# Verificar permissões
docker exec geek_app stat /app/uploads

# Verificar variável UPLOAD_DIR
docker exec geek_app env | grep UPLOAD_DIR
```

### Redis connection error
```bash
# Verificar se Redis está rodando
docker ps | grep geek_redis

# Testar conexão
docker exec geek_redis redis-cli ping

# Verificar redes
docker inspect geek_app | grep -A 10 Networks
docker inspect geek_redis | grep -A 10 Networks
```

---

## 📞 Suporte

- **Documentação completa**: `docs/DEPLOY_DOKPLOY.md`
- **PRD do projeto**: `PRD.md`
- **Configuração**: `CLAUDE.md`
- **Docker**: `docker/README.md`

---

**Versão**: 1.0
**Última atualização**: 2026-02-14
**Projeto**: geek.bidu.guru
**Deploy Platform**: Dokploy

---

## ✨ Deploy Concluído!

Se todos os itens acima estão ✅, parabéns! Sua aplicação está rodando em produção no Dokploy. 🎉

Próximos passos:
1. Configurar backups automáticos
2. Configurar alertas de uptime
3. Começar a criar conteúdo (posts, produtos)
4. Monitorar métricas e otimizar
