# Integração n8n - geek.bidu.guru

> Documentação da integração com n8n para automação de conteúdo e produtos.

---

## Visão Geral

O sistema utiliza o n8n existente na VPS Hostinger para automação de:
- Criação de posts via IA
- Importação/atualização de produtos de afiliados
- Monitoramento de preços

A comunicação é feita via webhooks HTTP com autenticação por API Key.

---

## Configuração

### 1. Variáveis de Ambiente

Adicione no `.env` da aplicação:

```bash
# n8n Integration
N8N_WEBHOOK_URL=https://n8n.seudominio.com    # URL base do n8n na VPS
N8N_API_KEY=sua-api-key-segura-aqui           # Gere com: openssl rand -hex 32
```

### 2. Usuário de Automação

O sistema cria automaticamente um usuário `automation` via migration:
- **Email**: `automation@geek.bidu.guru`
- **Role**: `automation`
- **Senha**: Hash inválido (não permite login via senha)

Este usuário é utilizado como autor de posts criados via n8n.

---

## Endpoints Disponíveis

Base URL: `https://geek.bidu.guru/webhooks/n8n`

### Autenticação

Todos os endpoints requerem o header:
```
X-N8N-API-Key: {N8N_API_KEY}
```

### Health Check

```http
GET /webhooks/n8n/health
```

Resposta:
```json
{
  "success": true,
  "message": "Webhook n8n operacional",
  "data": {
    "timestamp": "2025-12-12T18:00:00Z",
    "version": "1.0.0"
  }
}
```

### Criar Post

```http
POST /webhooks/n8n/posts
Content-Type: application/json
X-N8N-API-Key: {API_KEY}

{
  "title": "Titulo do Post",
  "slug": "titulo-do-post",
  "content": "Conteudo em Markdown...",
  "subtitle": "Subtitulo opcional",
  "seo_title": "Titulo SEO (max 60 chars)",
  "seo_description": "Descricao SEO (max 160 chars)",
  "post_type": "product_single",
  "status": "draft",
  "featured_image_url": "https://...",
  "tags": ["tag1", "tag2"],
  "product_ids": ["uuid1", "uuid2"]
}
```

Tipos de post (`post_type`):
- `product_single` - Review de produto único
- `product_list` - Lista de produtos (top 10, etc)
- `guide` - Guia/tutorial
- `news` - Notícia

Status (`status`):
- `draft` - Rascunho
- `published` - Publicado

### Criar/Atualizar Produto

```http
POST /webhooks/n8n/products
Content-Type: application/json
X-N8N-API-Key: {API_KEY}

{
  "name": "Nome do Produto",
  "slug": "nome-do-produto",
  "short_description": "Descricao curta",
  "long_description": "Descricao completa...",
  "current_price": 199.90,
  "original_price": 299.90,
  "affiliate_url": "https://amazon.com.br/dp/ASIN?tag=geek",
  "image_url": "https://...",
  "platform": "amazon",
  "availability": "available",
  "tags": ["categoria1", "categoria2"]
}
```

Plataformas (`platform`):
- `amazon`
- `mercado_livre`
- `shopee`
- `outros`

Disponibilidade (`availability`):
- `available` - Disponível
- `unavailable` - Indisponível
- `preorder` - Pré-venda
- `discontinued` - Descontinuado

**Comportamento**: Se o `slug` já existir, atualiza o produto. Caso contrário, cria um novo.

### Atualizar Preço

```http
POST /webhooks/n8n/price-update
Content-Type: application/json
X-N8N-API-Key: {API_KEY}

{
  "slug": "nome-do-produto",
  "current_price": 179.90,
  "original_price": 299.90,
  "availability": "available"
}
```

Identificação por `slug` ou `product_id` (UUID).

---

## Configuração no n8n

### 1. Criar Credencial

No n8n, crie uma credencial do tipo "Header Auth":
- **Name**: `Geek Bidu API Key`
- **Header Name**: `X-N8N-API-Key`
- **Header Value**: (mesmo valor de `N8N_API_KEY` no .env)

### 2. Workflow de Exemplo: Criar Post

```
[Trigger] → [OpenAI] → [HTTP Request] → [Notification]
```

1. **Trigger**: Schedule, Webhook, ou manual
2. **OpenAI**: Gera conteúdo do post
3. **HTTP Request**:
   - Method: POST
   - URL: `https://geek.bidu.guru/webhooks/n8n/posts`
   - Authentication: Header Auth (credencial criada)
   - Body: JSON com dados do post

### 3. Workflow de Exemplo: Importar Produtos Amazon

```
[Schedule] → [Amazon PA API] → [Loop] → [HTTP Request]
```

1. **Schedule**: Executa diariamente
2. **Amazon PA API**: Busca produtos por categoria
3. **Loop**: Itera sobre produtos
4. **HTTP Request**: POST para `/webhooks/n8n/products`

### 4. Workflow de Exemplo: Monitorar Preços

```
[Schedule] → [HTTP Request (GET produtos)] → [Loop] → [Scraper] → [Compare] → [HTTP Request (update)]
```

---

## Códigos de Resposta

| Código | Significado |
|--------|-------------|
| 200 | Sucesso |
| 400 | Dados inválidos (falta campo obrigatório) |
| 401 | API Key inválida ou ausente |
| 404 | Recurso não encontrado |
| 409 | Conflito (slug duplicado para posts) |
| 503 | Serviço indisponível (API Key não configurada ou usuário automation não existe) |

---

## Segurança

1. **API Key**: Use uma chave forte (mínimo 32 caracteres)
2. **HTTPS**: Sempre use HTTPS em produção
3. **Timing Attack**: Comparação segura via `hmac.compare_digest`
4. **Rate Limiting**: Considere adicionar limites se necessário
5. **Logs**: Tentativas de acesso inválido são logadas

---

## Troubleshooting

### Erro 401 - API Key inválida
- Verifique se o header `X-N8N-API-Key` está correto
- Confirme que `N8N_API_KEY` está configurado no `.env`

### Erro 503 - Usuário automation não encontrado
- Execute a migration: `alembic upgrade head`
- Verifique se o usuário existe no banco

### Erro 503 - API Key não configurada
- Adicione `N8N_API_KEY` no `.env` e reinicie a aplicação

### Produto não está atualizando
- Verifique se o `slug` está exatamente igual
- Confirme que o endpoint está recebendo os dados corretos

---

## Testes

Execute os testes de integração:

```bash
cd src
pytest tests/integration/test_webhooks.py -v
```

Testes disponíveis:
- Health check (autenticação válida/inválida)
- Criação de posts
- Criação/atualização de produtos
- Atualização de preços

---

**Versão**: 1.0
**Última atualização**: 2025-12-12
