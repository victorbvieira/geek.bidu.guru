# API Instagram - Referência

> **Versão**: 1.1
> **Base URL**: `https://geek.bidu.guru/api/v1/instagram`
> **Última atualização**: 2025-12-17

---

## Visão Geral

Esta API fornece endpoints para automação de posts no Instagram, consumidos pelo workflow n8n do Flow A (Post Diário Automático).

### Funcionalidades

| Funcionalidade | Endpoint | Descrição |
|----------------|----------|-----------|
| Seleção de Produto | `GET /product/random` | Busca produto elegível para posting |
| Template HTML | `GET /template/{id}` | Renderiza template HTML do produto |
| Marcar como Postado | `PATCH /products/{id}/mark-posted` | Registra publicação do produto |
| Estatísticas | `GET /stats` | Métricas de posting |
| HTML → Imagem | `POST /utils/html-to-image` | Converte template HTML em imagem |
| Redimensionar | `POST /utils/resize-image` | Redimensiona/otimiza imagens |

---

## Autenticação

### Método: JWT Bearer Token

Todos os endpoints requerem autenticação via token JWT no header `Authorization`.

```http
Authorization: Bearer <access_token>
```

### Roles Permitidos

| Role | Descrição |
|------|-----------|
| `ADMIN` | Administradores do sistema |
| `AUTOMATION` | Conta de serviço para automações (n8n) |

### Obter Token

```http
POST /api/v1/auth/login
Content-Type: application/x-www-form-urlencoded

username=automation@geek.bidu.guru&password=<senha>
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

### Erros de Autenticação

| Código | Descrição |
|--------|-----------|
| `401 Unauthorized` | Token ausente, inválido ou expirado |
| `403 Forbidden` | Role não autorizado para este endpoint |

---

## Endpoints

### 1. Buscar Produto para Posting

Seleciona um produto aleatório elegível para publicação.

```http
GET /instagram/product/random?days_since_last_post=30
Authorization: Bearer <token>
```

#### Parâmetros de Query

| Parâmetro | Tipo | Obrigatório | Default | Descrição |
|-----------|------|-------------|---------|-----------|
| `days_since_last_post` | int | Não | 30 | Dias mínimos desde o último post |

#### Critérios de Seleção

1. Status `available` (produto disponível)
2. Possui `main_image_url` (imagem obrigatória)
3. Não postado nos últimos X dias (ou nunca postado)
4. Prioriza produtos com menor `post_count`
5. Aleatoriza entre produtos de mesmo `post_count`

#### Response (200 OK)

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Kit Pencil Avengers Blister 4 Itens",
  "slug": "kit-pencil-avengers",
  "short_description": "Material escolar épico dos Vingadores",
  "price": 24.90,
  "currency": "BRL",
  "main_image_url": "https://example.com/avengers-kit.jpg",
  "platform": "amazon",
  "affiliate_redirect_slug": "kit-avengers-amazon",
  "categories": ["material-escolar", "marvel"],
  "tags": ["avengers", "escola", "marvel"],
  "post_count": 0,
  "last_post_date": null,
  "instagram_headline": "DESPERTE SEU HERÓI!",
  "instagram_title": "Material Escolar Épico é Aqui!",
  "instagram_badge": "NOVO NA LOA!",
  "instagram_caption": "🦸 Volta às aulas com estilo!\n\nO kit perfeito para os fãs de Marvel...",
  "instagram_hashtags": ["avengers", "geekgeek", "voltaasaulas", "molin"]
}
```

#### Errors

| Código | Descrição |
|--------|-----------|
| `404 Not Found` | Nenhum produto elegível disponível |

---

### 2. Renderizar Template HTML

Gera o HTML completo do template de post Instagram com os dados do produto.

```http
GET /instagram/template/{product_id}?headline=SUPER%20OFERTA&badge=NOVO
Authorization: Bearer <token>
```

#### Parâmetros de Path

| Parâmetro | Tipo | Obrigatório | Descrição |
|-----------|------|-------------|-----------|
| `product_id` | UUID | Sim | ID do produto |

#### Parâmetros de Query (Opcionais - Override)

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `headline` | string | Override da headline (usa instagram_headline do produto se não informado) |
| `title` | string | Override do título (usa instagram_title ou name do produto) |
| `badge` | string | Override do badge (usa instagram_badge do produto) |

#### Response (200 OK)

Retorna HTML completo renderizado (Content-Type: text/html).

O HTML gerado é um documento completo 1080x1080px com:
- Design estilo gamer/geek com gradiente roxo
- Logo e marca "GEEK BIDU GURU"
- Headline de impacto
- Imagem do produto com moldura
- Título e preço
- Badge (se configurado)
- URL de redirecionamento
- Hashtags no rodapé

#### Uso no n8n

Este endpoint pode ser usado de duas formas:

**Opção A - Direto para html-to-image:**
```
GET /instagram/template/{id} → Response.body → POST /instagram/utils/html-to-image
```

**Opção B - Buscar HTML e processar:**
```javascript
// No nó Code do n8n
const html = $input.first().json.body;
return { html, width: 1080, height: 1080 };
```

#### Errors

| Código | Descrição |
|--------|-----------|
| `404 Not Found` | Produto não encontrado |

---

### 3. Marcar Produto como Postado

Registra que um produto foi publicado em uma rede social.

> **Nota**: Este endpoint foi o número 2 na versão anterior. A numeração foi atualizada com a adição do endpoint de template.

```http
PATCH /instagram/products/{product_id}/mark-posted
Authorization: Bearer <token>
Content-Type: application/json

{
  "platform": "instagram",
  "post_url": "https://instagram.com/p/abc123",
  "caption": "Confira essa oferta incrível!"
}
```

#### Parâmetros de Path

| Parâmetro | Tipo | Obrigatório | Descrição |
|-----------|------|-------------|-----------|
| `product_id` | UUID | Sim | ID do produto |

#### Body

| Campo | Tipo | Obrigatório | Default | Descrição |
|-------|------|-------------|---------|-----------|
| `platform` | string | Não | "instagram" | Plataforma do post |
| `post_url` | string | Não | null | URL do post publicado |
| `caption` | string | Não | null | Caption usada (histórico) |

#### Response (200 OK)

```json
{
  "success": true,
  "product_id": "550e8400-e29b-41d4-a716-446655440000",
  "last_post_date": "2025-12-17T14:30:00Z",
  "post_count": 1
}
```

#### Errors

| Código | Descrição |
|--------|-----------|
| `404 Not Found` | Produto não encontrado |

---

### 4. Estatísticas de Posting

Retorna métricas sobre produtos disponíveis para posting.

```http
GET /instagram/stats?days_since_last_post=30
Authorization: Bearer <token>
```

#### Parâmetros de Query

| Parâmetro | Tipo | Obrigatório | Default | Descrição |
|-----------|------|-------------|---------|-----------|
| `days_since_last_post` | int | Não | 30 | Dias para considerar elegibilidade |

#### Response (200 OK)

```json
{
  "available_for_posting": 45,
  "total_products": 150,
  "days_since_last_post": 30
}
```

---

### 5. Converter HTML em Imagem

Renderiza HTML e retorna como imagem PNG/JPEG.

```http
POST /instagram/utils/html-to-image
Authorization: Bearer <token>
Content-Type: application/json

{
  "html": "<!DOCTYPE html><html>...</html>",
  "width": 1080,
  "height": 1080,
  "format": "png"
}
```

#### Body

| Campo | Tipo | Obrigatório | Default | Descrição |
|-------|------|-------------|---------|-----------|
| `html` | string | Sim | - | HTML completo para renderizar |
| `width` | int | Não | 1080 | Largura em pixels (100-4096) |
| `height` | int | Não | 1080 | Altura em pixels (100-4096) |
| `format` | string | Não | "png" | Formato: "png" ou "jpeg" |

#### Response (200 OK)

```json
{
  "success": true,
  "image_base64": "iVBORw0KGgoAAAANSUhEUgAA...",
  "format": "png",
  "width": 1080,
  "height": 1080,
  "file_size_kb": 245
}
```

#### Errors

| Código | Descrição |
|--------|-----------|
| `500 Internal Server Error` | Playwright não instalado ou erro na renderização |

#### Requisitos

Este endpoint requer Playwright instalado no servidor:

```bash
pip install playwright
playwright install chromium
```

---

### 6. Redimensionar Imagem

Redimensiona e otimiza imagens para Instagram.

```http
POST /instagram/utils/resize-image
Authorization: Bearer <token>
Content-Type: multipart/form-data

file: <arquivo_imagem>
width: 1080
height: 1080
quality: 85
maintain_aspect: true
```

#### Form Data

| Campo | Tipo | Obrigatório | Default | Descrição |
|-------|------|-------------|---------|-----------|
| `file` | File | Sim | - | Arquivo de imagem (PNG, JPEG, WEBP) |
| `width` | int | Não | 1080 | Largura desejada (100-4096) |
| `height` | int | Não | 1080 | Altura desejada (100-4096) |
| `quality` | int | Não | 85 | Qualidade JPEG (1-100) |
| `maintain_aspect` | bool | Não | true | Manter proporção original |

#### Response (200 OK)

```json
{
  "success": true,
  "image_base64": "/9j/4AAQSkZJRgABAQEA...",
  "format": "jpeg",
  "width": 1080,
  "height": 1080,
  "file_size_kb": 120,
  "original_size_kb": 450
}
```

#### Errors

| Código | Descrição |
|--------|-----------|
| `400 Bad Request` | Formato de imagem inválido |

---

## Fluxo de Uso (n8n)

### Diagrama do Flow A

```
┌─────────────────────────────────────────────────────────────────┐
│                     FLOW A - POST DIÁRIO                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. [Cron Trigger]                                             │
│        │                                                        │
│        ▼                                                        │
│  2. [HTTP Request] GET /instagram/product/random               │
│        │                                                        │
│        ▼                                                        │
│  3. [HTTP Request] GET /instagram/template/{product_id}        │
│        │                                                        │
│        ▼                                                        │
│  4. [HTTP Request] POST /instagram/utils/html-to-image         │
│        │            (passa o HTML do template)                  │
│        ▼                                                        │
│  5. [HTTP Request] Publica via Instagram Graph API             │
│        │                                                        │
│        ▼                                                        │
│  6. [HTTP Request] PATCH /instagram/products/{id}/mark-posted  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Exemplo n8n - HTTP Request Node

**Autenticação:**
```json
{
  "authentication": "genericCredentialType",
  "genericAuthType": "httpHeaderAuth",
  "headerParameters": {
    "parameters": [
      {
        "name": "Authorization",
        "value": "Bearer {{ $credentials.instagramApiToken }}"
      }
    ]
  }
}
```

---

## Campos Instagram no Cadastro de Produtos

Os produtos podem ter metadados Instagram pré-configurados:

| Campo | Tipo | Max Length | Descrição |
|-------|------|------------|-----------|
| `instagram_headline` | string | 50 | Headline de impacto (ex: "OFERTA IMPERDÍVEL!") |
| `instagram_title` | string | 100 | Título curto para Instagram |
| `instagram_badge` | string | 30 | Texto do badge (ex: "NOVO!", "BEST SELLER") |
| `instagram_caption` | text | - | Caption pré-definida completa |
| `instagram_hashtags` | array | 30 items | Lista de hashtags (sem #) |

Estes campos são retornados pelo endpoint `/product/random` e podem ser usados diretamente no template.

---

## Rate Limits

| Endpoint | Limite |
|----------|--------|
| Todos | 100 requests/minuto por token |

---

## Changelog

| Versão | Data | Alterações |
|--------|------|------------|
| 1.1 | 2025-12-17 | Adicionado endpoint GET /template/{id} para renderizar HTML |
| 1.0 | 2025-12-17 | Versão inicial |

---

## Suporte

Para dúvidas ou problemas:
- Abrir issue no repositório GitHub
- Consultar documentação do Flow A: `docs/workflows/FLOW-A-POST-DIARIO.md`
