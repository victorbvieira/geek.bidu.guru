# 🔧 Fix: Database Connection no Dokploy

## ❌ Erro

```
socket.gaierror: [Errno -3] Temporary failure in name resolution
```

**Causa:** O hostname `postgres` na `DATABASE_URL` não está sendo resolvido na rede do Dokploy.

---

## ✅ Solução

Configure a `DATABASE_URL` **completa** no painel do Dokploy, com o hostname/IP correto do PostgreSQL.

---

## 📋 Opções de Configuração

### **Opção 1: PostgreSQL em Container no Dokploy**

Se o PostgreSQL está em um container gerenciado pelo Dokploy no mesmo servidor:

#### **1. Descobrir o nome do container PostgreSQL**

```bash
# No servidor Dokploy
docker ps | grep postgres

# Ou
docker network inspect dokploy-network | grep postgres
```

Exemplo de saída:
```
databases-postgres-cypdtq
```

#### **2. Configurar DATABASE_URL no Dokploy**

No painel do Dokploy, adicione:

```bash
DATABASE_URL=postgresql+asyncpg://geek_app_prod:SUA_SENHA@databases-postgres-cypdtq:5432/geek_bidu_prod
```

**Substitua:**
- `geek_app_prod` → seu usuário do PostgreSQL
- `SUA_SENHA` → senha do usuário
- `databases-postgres-cypdtq` → nome real do container PostgreSQL
- `geek_bidu_prod` → nome do database

---

### **Opção 2: PostgreSQL em Servidor Externo/VPS**

Se o PostgreSQL está em outro servidor:

#### **1. Usar IP ou Hostname do Servidor**

No painel do Dokploy, adicione:

```bash
DATABASE_URL=postgresql+asyncpg://geek_app_prod:SUA_SENHA@IP_DO_SERVIDOR:5432/geek_bidu_prod
```

**Exemplo com IP:**
```bash
DATABASE_URL=postgresql+asyncpg://geek_app_prod:minha_senha@192.168.1.100:5432/geek_bidu_prod
```

**Exemplo com hostname:**
```bash
DATABASE_URL=postgresql+asyncpg://geek_app_prod:minha_senha@postgres.meudominio.com:5432/geek_bidu_prod
```

#### **2. Garantir Conectividade**

Se PostgreSQL está em servidor externo, certifique-se que:

- ✅ Firewall permite conexões na porta 5432
- ✅ `postgresql.conf` tem `listen_addresses = '*'` ou o IP do servidor Dokploy
- ✅ `pg_hba.conf` permite conexão do IP do servidor Dokploy:

```conf
# pg_hba.conf
host    geek_bidu_prod    geek_app_prod    IP_SERVIDOR_DOKPLOY/32    md5
```

---

### **Opção 3: PostgreSQL no Localhost (mesmo host do Dokploy)**

Se PostgreSQL está instalado diretamente no servidor (não em container):

```bash
DATABASE_URL=postgresql+asyncpg://geek_app_prod:SUA_SENHA@host.docker.internal:5432/geek_bidu_prod
```

Ou use o IP da interface Docker bridge:
```bash
DATABASE_URL=postgresql+asyncpg://geek_app_prod:SUA_SENHA@172.17.0.1:5432/geek_bidu_prod
```

---

## 🧪 Testar Conexão

### **1. Descobrir o Hostname Correto**

Entre no container da aplicação e teste DNS:

```bash
# Acessar container
docker exec -it geek_bidu_app bash

# Testar resolução DNS (se for container)
ping databases-postgres-cypdtq

# Testar resolução DNS (se for externo)
ping IP_DO_SERVIDOR

# Testar conexão PostgreSQL
apt-get update && apt-get install -y postgresql-client
psql "postgresql://geek_app_prod:SENHA@HOSTNAME:5432/geek_bidu_prod"
```

### **2. Testar com Script Python**

Dentro do container:

```bash
python /app/scripts/test_database.py
```

---

## 📝 Exemplos Completos

### **Exemplo 1: Container PostgreSQL chamado `postgres-main`**

```bash
# No painel Dokploy
DATABASE_URL=postgresql+asyncpg://geek_app_prod:minha_senha_segura@postgres-main:5432/geek_bidu_prod
```

### **Exemplo 2: PostgreSQL em VPS externo**

```bash
# No painel Dokploy
DATABASE_URL=postgresql+asyncpg://geek_app_prod:minha_senha_segura@vps.meuservidor.com:5432/geek_bidu_prod
```

### **Exemplo 3: PostgreSQL local no host**

```bash
# No painel Dokploy
DATABASE_URL=postgresql+asyncpg://geek_app_prod:minha_senha_segura@host.docker.internal:5432/geek_bidu_prod
```

---

## 🔐 Segurança

⚠️ **NUNCA** exponha a `DATABASE_URL` com senha em logs ou código!

✅ **Sempre** configure via painel do Dokploy (variáveis de ambiente)

✅ **Verifique** que o `.env` local não está commitado no Git

---

## 🚀 Após Configurar

1. **Salvar variáveis** no painel Dokploy
2. **Fazer redeploy** da aplicação
3. **Verificar logs**:
   ```bash
   docker logs -f geek_bidu_app
   ```
4. **Testar health**:
   ```bash
   curl http://localhost:8000/health
   ```

Se retornar `"database": "connected"`, está funcionando! ✅

---

## 📚 Referências

- **Teste de database**: `scripts/test_database.py`
- **Config do compose**: `docker/docker-compose.yml`
- **Template de variáveis**: `.env.production.example`

---

**Versão**: 1.0
**Data**: 2026-02-15
**Status**: ✅ Solução testada
