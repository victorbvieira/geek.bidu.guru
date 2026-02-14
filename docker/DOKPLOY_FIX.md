# 🔧 Fix: Configuração Docker Compose para Dokploy

## Problema Original

Ao fazer deploy no Dokploy, ocorria o erro:
```
env file /etc/dokploy/compose/geekbiduguru-app-pioca2/code/.env not found
```

## Solução Implementada

### 1. **Build Automático da Imagem**

**Antes:**
```yaml
app:
  image: geek-bidu-app:latest  # Imagem pré-buildada (não existe)
```

**Depois:**
```yaml
app:
  build:
    context: ..
    dockerfile: docker/Dockerfile  # Build automático do Dockerfile
```

**Resultado:** O Dokploy agora faz o build da imagem automaticamente a cada deploy, usando o Dockerfile do repositório.

---

### 2. **Arquivo .env.docker**

Criado o arquivo `.env.docker` com valores padrão (sem secrets):

```bash
# .env.docker
DB_PASSWORD=change-me
SECRET_KEY=change-me
APP_URL=http://localhost:8000
ALLOWED_HOSTS=localhost
```

**Por quê?**
- Docker Compose procura por um arquivo `.env` por padrão
- Sem ele, o comando `docker compose up` falha no Dokploy
- Os valores aqui são apenas placeholders

---

### 3. **Referência no docker-compose.yml**

```yaml
app:
  env_file:
    - ../.env.docker  # Valores padrão (sobrescritos pelo Dokploy)
  environment:
    - DATABASE_URL=...  # Variáveis específicas
```

**Como funciona:**
1. Docker Compose lê `.env.docker` (valores padrão)
2. Dokploy injeta variáveis configuradas no painel (sobrescreve os padrão)
3. Seção `environment` sobrescreve ambos (precedência final)

---

### 4. **Atualização do .gitignore**

```gitignore
# Antes
.env.*
!.env.example
!.env.*.example

# Depois
.env.*
!.env.example
!.env.*.example
!.env.docker  # Permite commitar .env.docker (sem secrets)
```

**Segurança mantida:**
- ✅ `.env` continua ignorado (nunca commitado)
- ✅ `.env.local`, `.env.prod`, etc. continuam ignorados
- ✅ Apenas `.env.docker` (sem secrets) é commitado
- ✅ Variáveis reais ficam no painel do Dokploy

---

## Como Usar no Dokploy

### 1. Configurar Variáveis no Painel

No painel do Dokploy, configure as variáveis de produção:

```bash
DB_PASSWORD=sua_senha_real_aqui
SECRET_KEY=sua_secret_key_real_aqui
APP_URL=https://geek.bidu.guru
ALLOWED_HOSTS=geek.bidu.guru,www.geek.bidu.guru

# Outras variáveis conforme necessário
AMAZON_ACCESS_KEY=...
OPENAI_API_KEY=...
```

### 2. Deploy

O Dokploy agora:
1. ✅ Clona o repositório
2. ✅ Lê `.env.docker` (valores padrão)
3. ✅ Injeta variáveis do painel (sobrescreve padrão)
4. ✅ Faz build da imagem usando o Dockerfile
5. ✅ Sobe os containers

---

## Precedência de Variáveis

```
Prioridade (do menor para o maior):
1. .env.docker (valores padrão commitados)
2. Variáveis do painel Dokploy (injetadas automaticamente)
3. Seção environment no compose (explícitas)
```

**Exemplo:**

```yaml
# .env.docker
APP_URL=http://localhost:8000

# Painel Dokploy
APP_URL=https://geek.bidu.guru  # Esta sobrescreve!

# docker-compose.yml (se existisse)
environment:
  - APP_URL=https://override.com  # Esta teria precedência final
```

---

## Arquivos Envolvidos

### Commitados no Git (seguros)

- ✅ `.env.docker` - Valores padrão sem secrets
- ✅ `.env.example` - Template para desenvolvimento
- ✅ `.env.production.example` - Template para produção
- ✅ `docker/docker-compose.yml` - Configuração do compose
- ✅ `docker/Dockerfile` - Imagem da aplicação

### NUNCA Commitados (secrets)

- ❌ `.env` - Valores locais de desenvolvimento
- ❌ `.env.local` - Valores locais
- ❌ `.env.prod` - Valores de produção
- ❌ Qualquer arquivo com valores sensíveis reais

---

## Checklist de Deploy

- [ ] Variáveis configuradas no painel Dokploy
- [ ] Rede `dokploy-network` criada
- [ ] PostgreSQL acessível via rede
- [ ] Projeto configurado para usar `docker/docker-compose.yml`
- [ ] Build configurado para usar `docker/Dockerfile`

---

## Troubleshooting

### Erro: "env file not found"

**Causa:** Arquivo `.env.docker` não foi commitado ou não está sendo encontrado.

**Solução:**
```bash
# Verificar se arquivo existe no repositório
git ls-files | grep .env.docker

# Deve retornar: .env.docker
```

### Erro: "image not found"

**Causa:** Compose está tentando usar imagem pré-buildada ao invés de fazer build.

**Solução:** Verificar que o `docker-compose.yml` tem a seção `build`:
```yaml
app:
  build:
    context: ..
    dockerfile: docker/Dockerfile
```

### Build muito lento

**Causa:** Dockerfile rebuilda tudo a cada deploy.

**Solução:** O Dockerfile já usa multi-stage build e cache. Para melhorar:
- Dokploy mantém cache de layers entre builds
- Apenas mudanças no código causam rebuild das camadas finais
- Dependências Python são cacheadas (layer anterior)

---

## Referências

- Documentação completa: `docs/DEPLOY_DOKPLOY.md`
- Quickstart: `DEPLOY_DOKPLOY_QUICKSTART.md`
- Checklist: `DEPLOY_CHECKLIST.md`
- Template de variáveis: `.env.production.example`

---

**Versão**: 1.0
**Data**: 2026-02-14
**Status**: ✅ Testado e funcionando
