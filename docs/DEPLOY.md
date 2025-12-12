# Deploy Cookbook - geek.bidu.guru

> Guia passo a passo para deploy em produção usando Easypanel na VPS Hostinger KVM8.

## Índice

1. [Pré-requisitos](#pré-requisitos)
2. [Configuração do Easypanel](#configuração-do-easypanel)
3. [Configuração do Banco de Dados](#configuração-do-banco-de-dados)
4. [Deploy da Aplicação](#deploy-da-aplicação)
5. [Configuração do Domínio](#configuração-do-domínio)
6. [Executar Migrations](#executar-migrations)
7. [Verificação Pós-Deploy](#verificação-pós-deploy)
8. [Troubleshooting](#troubleshooting)

---

## Pré-requisitos

### Na VPS (já configurado)
- [x] Easypanel instalado e acessível
- [x] PostgreSQL rodando como serviço compartilhado
- [x] Traefik configurado para SSL automático
- [x] n8n rodando (para automações futuras)

### No repositório
- [x] Dockerfile otimizado para produção
- [x] Migrations do Alembic prontas
- [x] Variáveis de ambiente documentadas

---

## Configuração do Easypanel

### 1. Criar Projeto

1. Acesse o Easypanel: `https://painel.seudominio.com`
2. Clique em **"New Project"**
3. Configure:
   - **Name**: `geek-bidu-guru`
   - **Description**: Blog de Presentes Geek

### 2. Conectar GitHub (repositório privado)

Se o repositório é **privado**, você precisa criar um Personal Access Token:

#### Criar Token no GitHub:
1. Vá em GitHub → **Settings** → **Developer settings** → **Personal access tokens** → **Tokens (classic)**
2. Clique em **"Generate new token (classic)"**
3. Configure:
   - **Note**: `Easypanel - geek.bidu.guru`
   - **Expiration**: `90 days` ou `No expiration` (para produção)
   - **Scopes**: Marque apenas **`repo`** (Full control of private repositories)
4. Clique em **"Generate token"**
5. **Copie o token imediatamente** (só aparece uma vez!)

#### Configurar no Easypanel:
1. No Easypanel, vá em **"Settings"** → **"Git Providers"**
2. Clique em **"Add Provider"** → **"GitHub"**
3. Cole o **Personal Access Token** gerado
4. Salve a configuração

### 3. Criar Serviço da Aplicação

1. Dentro do projeto, clique em **"New Service"** → **"App"**
2. Selecione **"GitHub"** como source
3. Configure o repositório:
   - **Repository**: `seu-usuario/geek.bidu.guru`
   - **Branch**: `main`
4. Configure o Build:
   - **Build Type**: `Dockerfile` (não Buildpack ou Nixpacks)
   - **Dockerfile Path**: `docker/Dockerfile`
   - **Build Path**: `/` ou deixar vazio (raiz do projeto - necessário para copiar `src/` e `requirements.txt`)

### 3. Configurar Variáveis de Ambiente

No serviço criado, vá em **"Environment"** e adicione:

```env
# Aplicação
APP_NAME=geek.bidu.guru
ENVIRONMENT=production
DEBUG=false
SECRET_KEY=<gerar-chave-segura-64-chars>

# Banco de Dados (PostgreSQL compartilhado)
DATABASE_URL=postgresql+asyncpg://geek_app_prod:<senha>@postgres:5432/geek_bidu_prod

# JWT
JWT_SECRET_KEY=<gerar-chave-segura-64-chars>
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS e Hosts permitidos
ALLOWED_HOSTS=geek.bidu.guru,www.geek.bidu.guru

# Redis (se configurado)
REDIS_URL=redis://redis:6379/0
```

#### Gerar chaves seguras:
```bash
# No terminal local
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

### 4. Configurar Domínio

1. Vá em **"Domains"** no serviço
2. Clique em **"Add Domain"**
3. Configure:
   - **Host**: `geek.bidu.guru`
   - **Path**: `/` (raiz - aceita todas as rotas)
   - **Port**: `8000` (porta do uvicorn no container)
   - **HTTPS**: `Ativado` (Let's Encrypt automático via Traefik)
4. Opcionalmente, adicione `www.geek.bidu.guru` com as mesmas configurações

> **Sobre as opções**:
> - **Path**: Use `/` para rotear todo o tráfego. Use paths específicos apenas se quiser dividir entre serviços
> - **Port**: `8000` é a porta definida no Dockerfile (`EXPOSE 8000`)
> - **HTTPS/SSL**: Sempre ativar em produção - Traefik gera certificado Let's Encrypt automaticamente
> - **Middlewares**: Deixar padrão (Traefik já aplica redirecionamento HTTP→HTTPS)

### 5. Configurar Storage para Uploads

O Dockerfile declara `/app/uploads` como volume, mas você **precisa configurar no Easypanel** para que seja persistente.

1. No serviço, vá em **"Storage"** → **"Mounts"**
2. Clique em **"Add Volume Mount"**
3. Configure:
   - **Volume Name**: `geek-uploads` (ou deixar auto-gerado)
   - **Mount Path**: `/app/uploads`
4. Clique em **"Save"**

> **Opções de Mount disponíveis**:
> - **Volume Mount** (recomendado): Volume gerenciado pelo Docker, persistente e portável
> - **Bind Mount**: Monta diretório do host diretamente (útil para debug)
> - **File Mount**: Monta arquivo específico (útil para configs)

> ⚠️ **Importante**: O `VOLUME` no Dockerfile é apenas uma declaração. Sem configurar o mount no Easypanel, uploads serão perdidos em cada redeploy!

### 6. Health Check (já configurado no Dockerfile)

O Dockerfile já define o health check automaticamente:
```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1
```

> **Nota**: Se o Easypanel tiver opção de Health Check na UI, você pode deixar em branco (usa o do Dockerfile) ou configurar manualmente com Path `/health`.

### 7. Configurar Auto Deploy

O Easypanel pode não ter opção nativa de auto deploy. Existem duas alternativas:

#### Opção A: Deploy Manual
Após cada push, clique manualmente em **"Deploy"** → **"Deploy Now"** no Easypanel.

#### Opção B: Script com Cron (recomendado)

Use o script `scripts/auto-deploy.sh` para verificar novos commits automaticamente:

1. **Copiar script para a VPS**:
```bash
scp scripts/auto-deploy.sh user@vps-ip:/opt/scripts/
chmod +x /opt/scripts/auto-deploy.sh
```

2. **Configurar o script** (editar variáveis):
```bash
nano /opt/scripts/auto-deploy.sh

# Alterar:
REPO_URL="https://api.github.com/repos/SEU_USUARIO/geek.bidu.guru/commits/main"
GITHUB_TOKEN="ghp_xxxxx"  # Token com permissão de leitura
```

3. **Adicionar ao cron** (verificar a cada 5 minutos):
```bash
crontab -e

# Adicionar linha:
*/5 * * * * /opt/scripts/auto-deploy.sh >> /var/log/geek-deploy.log 2>&1
```

4. **Verificar logs**:
```bash
tail -f /var/log/geek-deploy.log
```

> **Nota**: O script detecta novos commits comparando o SHA do GitHub com o último deploy realizado.

### 8. Configurar Recursos (opcional)

Em **"Resources"** você pode definir limites ou deixar em branco:
- **Deixar em branco**: Alocação dinâmica (recomendado para começar)
- **Memory**: `512MB` (mínimo sugerido se quiser limitar)
- **CPU**: `0.5` cores (mínimo sugerido se quiser limitar)

> **Dica**: Comece sem limites e monitore o uso. Defina limites depois se necessário para evitar que um serviço consuma todos os recursos da VPS.

---

## Configuração do Banco de Dados

### 1. Acessar PostgreSQL

Se o PostgreSQL está como serviço compartilhado no Easypanel:

```bash
# Via terminal do Easypanel ou SSH na VPS
docker exec -it <container-postgres> psql -U postgres
```

### 2. Criar Database e Usuário de Produção

```sql
-- Criar usuário de produção
CREATE USER geek_app_prod WITH PASSWORD 'senha-segura-aqui';

-- Criar database
CREATE DATABASE geek_bidu_prod OWNER geek_app_prod;

-- Conceder privilégios
GRANT ALL PRIVILEGES ON DATABASE geek_bidu_prod TO geek_app_prod;

-- Conectar ao database e configurar schema
\c geek_bidu_prod

-- Garantir que o usuário pode criar objetos
GRANT ALL ON SCHEMA public TO geek_app_prod;
```

### 3. Verificar Conexão

```bash
# Testar conexão
psql postgresql://geek_app_prod:<senha>@localhost:5432/geek_bidu_prod -c "SELECT 1;"
```

---

## Deploy da Aplicação

### 1. Push para GitHub

```bash
# No repositório local
git add .
git commit -m "feat: prepare for production deploy"
git push origin main
```

### 2. Trigger do Build

O Easypanel detecta automaticamente o push e inicia o build.

Ou manualmente:
1. Vá no serviço no Easypanel
2. Clique em **"Deploy"** → **"Deploy Now"**

### 3. Acompanhar Logs

```bash
# Via Easypanel UI: Logs tab
# Ou via terminal:
docker logs -f <container-app>
```

---

## Executar Migrations

### Opção 1: Via Easypanel Terminal (recomendado para primeiro deploy)

1. No serviço, vá em **"Terminal"**
2. Execute:

```bash
cd /app/src
alembic upgrade head
```

### Opção 2: Via SSH na VPS

```bash
# Conectar na VPS
ssh user@vps-ip

# Entrar no container
docker exec -it <container-app> bash

# Executar migrations
cd /app/src
alembic upgrade head
```

### Opção 3: Modificar Command do Serviço (migrations automáticas)

Para rodar migrations automaticamente em cada deploy, altere o **Command** do serviço no Easypanel:

1. Vá em **"Advanced"** ou **"General"** → **"Command"**
2. Altere de:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```
3. Para:
```bash
sh -c "cd /app/src && alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"
```

> **Nota**: Com essa configuração, migrations rodam automaticamente antes da aplicação iniciar em cada deploy.

---

## Verificação Pós-Deploy

### 1. Health Check

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

### 2. Testar Admin

1. Acesse: `https://geek.bidu.guru/admin/login`
2. Login com:
   - **Email**: `admin@geek.bidu.guru`
   - **Senha**: `Admin@123`
3. **IMPORTANTE**: Altere a senha após primeiro login!

### 3. Verificar SSL

```bash
curl -I https://geek.bidu.guru
```

Deve mostrar:
- `HTTP/2 200`
- Headers de segurança (CSP, X-Frame-Options, etc.)

### 4. Testar Endpoints

```bash
# Homepage
curl https://geek.bidu.guru/

# API
curl https://geek.bidu.guru/api/v1/posts

# Sitemap
curl https://geek.bidu.guru/sitemap.xml

# Robots
curl https://geek.bidu.guru/robots.txt
```

---

## Configuração DNS

### No seu provedor de DNS (Cloudflare, Route53, etc.)

```
# Registro A
geek.bidu.guru    A    <IP-DA-VPS>

# Ou CNAME se usar proxy
geek.bidu.guru    CNAME    vps.seudominio.com

# WWW (opcional)
www.geek.bidu.guru    CNAME    geek.bidu.guru
```

### Tempo de propagação
- DNS pode levar até 48h para propagar
- Use `dig geek.bidu.guru` para verificar

---

## Troubleshooting

### Erro: "Database connection failed"

1. Verificar se PostgreSQL está rodando:
```bash
docker ps | grep postgres
```

2. Verificar DATABASE_URL no Easypanel

3. Testar conexão manualmente:
```bash
docker exec -it <container-app> python -c "
from app.database import check_database_connection
import asyncio
print(asyncio.run(check_database_connection()))
"
```

### Erro: "Migration failed"

1. Verificar logs:
```bash
docker logs <container-app> | grep -i alembic
```

2. Rodar migration manualmente:
```bash
docker exec -it <container-app> alembic upgrade head
```

3. Se houver conflito, verificar versão atual:
```bash
docker exec -it <container-app> alembic current
```

### Erro: "502 Bad Gateway"

1. Verificar se app está rodando:
```bash
docker ps | grep geek
```

2. Verificar logs da aplicação:
```bash
docker logs -f <container-app>
```

3. Verificar health check:
```bash
curl http://localhost:8000/health
```

### Erro: "SSL Certificate"

1. Verificar se domínio aponta para VPS:
```bash
dig geek.bidu.guru
```

2. Forçar renovação do certificado no Traefik:
```bash
# Reiniciar Traefik
docker restart traefik
```

### Performance lenta

1. Verificar recursos:
```bash
docker stats <container-app>
```

2. Aumentar recursos no Easypanel se necessário

3. Verificar queries lentas:
```sql
-- No PostgreSQL
SELECT * FROM pg_stat_activity WHERE state = 'active';
```

---

## Checklist de Deploy

```
[ ] 1. Criar projeto no Easypanel
[ ] 2. Criar database e usuário PostgreSQL
[ ] 3. Configurar variáveis de ambiente
[ ] 4. Configurar domínio no Easypanel
[ ] 5. Configurar DNS no provedor
[ ] 6. Fazer deploy (push para main)
[ ] 7. Executar migrations
[ ] 8. Verificar health check
[ ] 9. Testar login no admin
[ ] 10. Alterar senha do admin
[ ] 11. Verificar SSL/HTTPS
[ ] 12. Testar endpoints principais
```

---

## Comandos Úteis

```bash
# Ver logs em tempo real
docker logs -f <container>

# Entrar no container
docker exec -it <container> bash

# Reiniciar serviço
docker restart <container>

# Ver uso de recursos
docker stats

# Backup do banco
docker exec <postgres> pg_dump -U geek_app_prod geek_bidu_prod > backup.sql

# Restaurar banco
cat backup.sql | docker exec -i <postgres> psql -U geek_app_prod geek_bidu_prod
```

---

## Contatos e Recursos

- **Easypanel Docs**: https://easypanel.io/docs
- **Repositório**: https://github.com/seu-usuario/geek.bidu.guru
- **Issues**: https://github.com/seu-usuario/geek.bidu.guru/issues

---

**Versão**: 1.0
**Última atualização**: 2025-12-12
**Autor**: Claude Code
