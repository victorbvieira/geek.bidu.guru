# Guia Rápido - geek.bidu.guru

## Pré-requisitos

1. Docker e Docker Compose instalados
2. Arquivo `.env` configurado na raiz do projeto

```bash
# Criar .env a partir do exemplo
cp .env.example .env

# Editar com suas credenciais
# IMPORTANTE: Configure DATABASE_URL com IP e senha da VPS
```

---

## Comandos do Dia a Dia

### Iniciar o Sistema

```bash
make up
```

Acesse: http://localhost:8001

### Parar o Sistema

```bash
make down
```

### Parar e Remover Volumes (reset completo)

```bash
make down-v
```

---

## Logs e Debug

```bash
# Ver logs de todos os containers
make logs

# Ver logs só da aplicação
make logs-app

# Ver status dos containers
make ps

# Acessar shell do container
make shell
```

---

## Banco de Dados

```bash
# Rodar migrations pendentes
make migrate

# Criar nova migration
make migrate-new MSG="descricao_da_mudanca"

# Reverter última migration
make migrate-down

# Ver histórico de migrations
make migrate-history

# Conectar no PostgreSQL remoto (requer psql)
make db-shell
```

---

## Desenvolvimento

```bash
# Rebuild e reiniciar (após mudar Dockerfile ou requirements)
make up-build

# Reiniciar containers
make restart

# Verificar código (linter)
make lint

# Corrigir problemas do linter
make lint-fix

# Formatar código
make format

# Rodar testes
make test
```

---

## Fluxo Típico de Trabalho

```bash
# 1. Iniciar ambiente
make up

# 2. Desenvolver... (código atualiza automaticamente com --reload)

# 3. Se criar/alterar modelos, gerar migration
make migrate-new MSG="add_campo_x_to_tabela_y"

# 4. Aplicar migration
make migrate

# 5. Ao finalizar, parar ambiente
make down
```

---

## Troubleshooting

### Container não sobe

```bash
# Ver logs detalhados
make logs

# Verificar se .env existe e está correto
cat .env | grep DATABASE_URL
```

### Erro de conexão com banco

```bash
# Testar conexão manual (requer psql)
make db-shell

# Verificar se DATABASE_URL está correto no .env
```

### Rebuild forçado

```bash
make down
make up-build
```

---

## Portas Utilizadas

| Serviço | Porta Local | Porta Interna |
|---------|-------------|---------------|
| App     | 8001        | 8000          |
| Redis   | 6380        | 6379          |

---

## Referência Rápida

| Comando | Descrição |
|---------|-----------|
| `make up` | Iniciar |
| `make down` | Parar |
| `make logs` | Ver logs |
| `make migrate` | Rodar migrations |
| `make shell` | Acessar container |
| `make help` | Ver todos os comandos |
