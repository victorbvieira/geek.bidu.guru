# Flow A: Post Diario Automatico - Instagram

> **Versao**: 3.2
> **Status**: Pronto para producao
> **Data**: 2025-12-18
> **Responsavel**: Automation Engineer
> **Foco**: Instagram (MVP)

---

## Visao Geral

O **Flow A** e responsavel pela geracao automatica de posts diarios sobre produtos geek no **Instagram**, utilizando IA para criar legendas otimizadas e gerando imagens personalizadas a partir de um template.

### Objetivo
Publicar automaticamente 1 post por dia (as 8h) no Instagram com:
- Imagem gerada a partir de template (com produto, preco, titulo)
- Legenda otimizada para engajamento
- Hashtags relevantes

### KPIs Esperados
- 1 post/dia = 30 posts/mes
- Taxa de publicacao: > 95%
- Tempo medio de execucao: < 2 minutos

---

## Resumo de APIs Disponiveis

> Todas as APIs requerem autenticacao JWT com role `ADMIN` ou `AUTOMATION`.

| Endpoint | Metodo | Descricao | Status |
|----------|--------|-----------|--------|
| `/api/v1/instagram/product/random` | GET | Busca produto aleatorio para posting | ✅ |
| `/api/v1/instagram/template/{id}` | GET | Renderiza template HTML do produto | ✅ |
| `/api/v1/instagram/generate-image` | POST | Gera imagem PNG do produto (template + screenshot) | ✅ |
| `/api/v1/instagram/utils/html-to-image` | POST | Converte HTML para imagem PNG (baixo nivel) | ✅ |
| `/api/v1/instagram/products/{id}/mark-posted` | PATCH | Marca produto como postado + historico | ✅ |
| `/api/v1/instagram/products/{id}/info` | GET | Retorna info de publicacao do produto | ✅ |
| `/api/v1/instagram/products/{id}/history` | GET | Retorna historico de publicacoes | ✅ |
| `/api/v1/instagram/stats` | GET | Estatisticas de posting | ✅ |
| `/api/v1/products/{id}` | GET | Busca produto por ID (para teste manual) | ✅ |
| `/api/v1/products/{id}/instagram-metadata` | PATCH | Salvar metadados Instagram + custo LLM | ✅ |

### Tabelas do Banco de Dados

| Tabela | Descricao |
|--------|-----------|
| `products` | Campos: `last_post_date`, `post_count`, `last_ig_media_id`, `instagram_*` |
| `instagram_post_history` | Historico de publicacoes: `ig_media_id`, `post_url`, `caption`, `posted_at` |

---

## Arquitetura

### Triggers Disponiveis

| Trigger | Endpoint | Uso |
|---------|----------|-----|
| **Automatico (Cron)** | `GET /api/v1/instagram/product/random` | Post diario as 8h (producao) |
| **Manual (Teste)** | `GET /api/v1/products/{id}` | Testar com produto especifico |

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    FLOW A v3.1: POST DIARIO INSTAGRAM                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────┐        ┌──────────────────┐                               │
│  │ 1A. Cron 8h │        │ 1B. Trigger      │                               │
│  │  (Auto)     │        │  Manual (Teste)  │                               │
│  └──────┬──────┘        └────────┬─────────┘                               │
│         │                        │                                          │
│         ▼                        ▼                                          │
│  ┌─────────────────┐    ┌─────────────────────────┐                        │
│  │ 2A. GET /api/v1/│    │ 2B. GET /api/v1/        │                        │
│  │ products/random │    │ products/{product_id}   │                        │
│  └────────┬────────┘    └───────────┬─────────────┘                        │
│           │                         │                                       │
│           └────────────┬────────────┘                                       │
│                        ▼                                                    │
│         ┌──────────────────────────────────────┐                           │
│         │ 3. Verificar campos Instagram        │  ◄── NOVO!                │
│         │ - instagram_headline                 │                           │
│         │ - instagram_title                    │                           │
│         │ - instagram_badge                    │                           │
│         │ - instagram_caption                  │                           │
│         │ - instagram_hashtags                 │                           │
│         └────────────────┬─────────────────────┘                           │
│                          │                                                  │
│              ┌───────────┴───────────┐                                     │
│              │ Dados completos?      │                                     │
│              └───────────┬───────────┘                                     │
│           SIM            │            NAO                                   │
│            │             │             │                                    │
│            ▼             │             ▼                                    │
│  ┌─────────────────┐     │   ┌─────────────────────────────┐               │
│  │ Usar dados      │     │   │ 4. OpenAI: Gerar conteudo   │               │
│  │ pre-cadastrados │     │   │ - Headline (max 40 chars)   │               │
│  │ (custo zero)    │     │   │ - Title (max 100 chars)     │               │
│  └────────┬────────┘     │   │ - Badge (max 20 chars)      │               │
│           │              │   │ - Caption (max 2200 chars)  │               │
│           │              │   │ - Hashtags (5-10)           │               │
│           │              │   └──────────────┬──────────────┘               │
│           │              │                  │                               │
│           │              │                  ▼                               │
│           │              │   ┌─────────────────────────────┐               │
│           │              │   │ 5. PATCH /api/v1/products/  │  ◄── ✅ IMPL  │
│           │              │   │ {id}/instagram-metadata     │               │
│           │              │   │ - Salvar dados gerados      │               │
│           │              │   │ - Registrar custo LLM       │               │
│           │              │   └──────────────┬──────────────┘               │
│           │              │                  │                               │
│           └──────────────┴──────────────────┘                               │
│                          │                                                  │
│                          ▼                                                  │
│         ┌─────────────────────────────────────────┐                        │
│         │ 6. POST /api/v1/instagram/generate-image│  ◄── ✅ IMPLEMENTADO   │
│         │ - Recebe: product_id + overrides        │                        │
│         │ - Gera imagem 1080x1080 do template     │                        │
│         │ - Retorna: imagem em base64             │                        │
│         └────────────────┬────────────────────────┘                        │
│                          │                                                  │
│                          ▼                                                  │
│         ┌─────────────────────────────────────────┐                        │
│         │ 7. Instagram Graph API: Publicar        │                        │
│         │ - Upload da imagem                      │                        │
│         │ - Caption + hashtags                    │                        │
│         └────────────────┬────────────────────────┘                        │
│                          │                                                  │
│                          ▼                                                  │
│         ┌─────────────────────────────────────────┐                        │
│         │ 8. PATCH /api/v1/instagram/products/{id}/│                        │
│         │    mark-posted                          │                        │
│         │ - Atualiza last_post_date               │                        │
│         │ - Incrementa post_count                 │                        │
│         │ - Registra ig_media_id (NOVO!)          │                        │
│         │ - Cria historico em instagram_post_history (NOVO!)               │
│         └────────────────┬────────────────────────┘                        │
│                          │                                                  │
│                          ▼                                                  │
│         ┌─────────────────────────────────────────┐                        │
│         │ 9. Instagram DM: Notificar admin        │                        │
│         └─────────────────────────────────────────┘                        │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Beneficios da Verificacao de Dados Pre-Cadastrados

| Cenario | Custo OpenAI | Tempo |
|---------|--------------|-------|
| Dados pre-cadastrados | **$0.00** | ~0.5s |
| Geracao via IA | ~$0.04/post | ~3-5s |

**Economia estimada**: Se 50% dos produtos tiverem dados pre-cadastrados = **$0.60/mes** de economia.

---

## Template da Imagem Instagram

### Especificacao Visual

Baseado no template de referencia e no guia de branding:

```
┌─────────────────────────────────────────┐
│  ┌─────────────────┐    ┌───────────┐  │
│  │ 🦝 GEEK.BIDU.GURU│    │ HEADLINE! │  │  ← Mascote + Texto Bungee + Headline
│  └─────────────────┘    └───────────┘  │
│                                         │
│         ┌─────────────────┐             │
│         │                 │             │
│         │   IMAGEM DO     │             │  ← Imagem do produto (moldura branca)
│         │    PRODUTO      │             │
│         │                 │             │
│         └─────────────────┘             │
│                      ┌──────────────┐   │
│                      │  R$ 99,90    │   │  ← Preco em destaque (amarelo)
│                      │  NOVO NA LOA!│   │  ← Badge (amarelo)
│                      └──────────────┘   │
│                                         │
│  ══════════════════════════════════════ │
│  TITULO CHAMATIVO DO PRODUTO!           │  ← Titulo (Bungee)
│  https://geek.bidu.guru                 │  ← URL
│  #hashtag1 #hashtag2 #hashtag3          │  ← Hashtags
└─────────────────────────────────────────┘
```

### Dimensoes
- **Tamanho**: 1080x1080px (quadrado, otimo para feed)
- **Formato**: PNG (melhor qualidade) ou JPEG
- **Qualidade**: Alta (95%)

### Paleta de Cores (do Branding)

| Cor | Hex | Uso |
|-----|-----|-----|
| Amarelo Principal | `#F5B81C` | Preco, badge, destaques |
| Roxo Escuro | `#1a1a2e` | Background base |
| Roxo Medio | `#16213e` | Pattern/gradiente |
| Branco | `#FFFFFF` | Textos, moldura produto |
| Preto | `#000000` | Sombras, contornos |

### Tipografia

| Elemento | Fonte | Peso | Tamanho | Cor |
|----------|-------|------|---------|-----|
| Logo texto | **Bungee** | Regular | 32px | `#F5B81C` |
| Headline | **Bungee** | Regular | 48px | `#F5B81C` |
| Preco | **Bungee** | Regular | 64px | `#F5B81C` |
| Badge | **Bungee** | Regular | 24px | `#F5B81C` |
| Titulo | **Bungee** | Regular | 36px | `#FFFFFF` |
| URL | **Press Start 2P** | Regular | 14px | `#FFFFFF` (50% opacity) |
| Hashtags | **Press Start 2P** | Regular | 12px | `#FFFFFF` (70% opacity) |

> **Fontes auxiliares geek**: Press Start 2P (pixel art, Google Fonts) ou Orbitron (sci-fi)

### Assets Necessarios

| Arquivo | Localizacao | Descricao |
|---------|-------------|-----------|
| `mascot-only.png` | `static/logo/` | Mascote guaxinim (ja existe) |
| `background-pattern.png` | `templates/instagram/` | Background geek pattern (a criar) |
| `frame-product.png` | `templates/instagram/` | Moldura branca para produto (a criar) |
| `Bungee-Regular.ttf` | `templates/instagram/fonts/` | Fonte principal (baixar) |
| `PressStart2P-Regular.ttf` | `templates/instagram/fonts/` | Fonte secundaria (baixar) |

### Elementos Dinamicos

| Elemento | Tipo | Limite | Exemplo |
|----------|------|--------|---------|
| `headline` | Texto | 25 chars | "DESPERTE SEU HEROI!" |
| `product_image_url` | URL | - | URL da imagem do produto |
| `current_price` | Numero | - | "R$ 24,90" |
| `badge_text` | Texto | 15 chars | "NOVO NA LOA!" |
| `title` | Texto | 40 chars | "Material Escolar Epico e Aqui!" |
| `hashtags` | Lista | 5-10 tags | ["Geek", "Marvel", "Presente"] |

### Elementos Fixos
- **Mascote**: `static/logo/mascot-only.png`
- **Logo texto**: "GEEK BIDU GURU" em Bungee amarelo
- **Background**: Pattern geek roxo/azul com icones
- **URL**: "https://geek.bidu.guru"
- **Moldura**: Frame branco para destacar produto

---

## APIs Internas (FastAPI)

> **AUTENTICACAO OBRIGATORIA**: Todos os endpoints de Instagram requerem token JWT.
> Roles permitidos: `ADMIN` ou `AUTOMATION`.
> Header: `Authorization: Bearer {JWT_TOKEN}`

### 1A. GET /api/v1/instagram/product/random (Trigger Automatico) ✅ IMPLEMENTADO

Busca produto aleatorio elegivel para posting no Instagram.

**Request:**
```http
GET /api/v1/instagram/product/random?days_since_last_post=30
Authorization: Bearer {JWT_TOKEN}
```

**Response:**
```json
{
  "id": "7db20856-b8ea-4795-8e1e-dc6f7cbd3f20",
  "name": "Caneca Star Wars 3D Darth Vader",
  "slug": "caneca-star-wars-3d-darth-vader",
  "short_description": "Caneca 3D oficial Disney",
  "price": 79.90,
  "currency": "BRL",
  "main_image_url": "https://...",
  "platform": "amazon",
  "affiliate_redirect_slug": "caneca-darth-vader",
  "categories": ["star-wars", "cozinha"],
  "tags": ["darth-vader", "disney", "caneca"],
  "post_count": 0,
  "last_post_date": null,
  "instagram_headline": "DESPERTE SEU HEROI!",
  "instagram_title": "Caneca 3D Darth Vader",
  "instagram_badge": "OFERTA!",
  "instagram_caption": "🎮 Comece seu dia com estilo...",
  "instagram_hashtags": ["star-wars", "darth-vader", "geek"]
}
```

**Criterios de Selecao:**
- Status: `available` (disponivel para venda)
- Imagem: Possui `main_image_url` (obrigatorio para post visual)
- Recencia: Nao foi postado nos ultimos X dias (ou nunca postado)
- Prioridade: Produtos menos postados tem preferencia

**Logica SQL:**
```sql
SELECT * FROM products
WHERE availability = 'available'
  AND main_image_url IS NOT NULL
  AND (last_post_date IS NULL OR last_post_date < NOW() - INTERVAL '30 days')
ORDER BY post_count ASC, RANDOM()
LIMIT 1;
```

---

### 1B. GET /api/v1/products/{id} (Trigger Manual - Teste)

Busca produto especifico por ID para teste manual.

**Request:**
```http
GET /api/v1/products/{product_id}
Authorization: Bearer {JWT_TOKEN}
```

**Response:**
```json
{
  "id": "uuid",
  "name": "Kit Lapis Vingadores",
  "slug": "kit-lapis-vingadores",
  "short_description": "Kit com 4 lapis dos Vingadores",
  "price": 24.90,
  "affiliate_url": "https://amzn.to/xxx",
  "main_image_url": "https://...",
  "platform": "amazon",
  "categories": ["papelaria"],
  "tags": ["vingadores", "marvel", "escolar"],
  "last_post_date": null,
  "post_count": 0,
  "instagram_headline": "OFERTA IMPERDIVEL!",
  "instagram_title": "Kit Lapis dos Vingadores",
  "instagram_badge": "NOVO!",
  "instagram_caption": "🦸 Material escolar geek...",
  "instagram_hashtags": ["vingadores", "marvel", "geek"]
}
```

**Uso no n8n:**
- Passar `product_id` como parametro do trigger manual
- Permite testar o fluxo completo com produto especifico
- Util para validar geracao de imagem e publicacao

---

### 2. Logica de Verificacao de Dados Pre-Cadastrados

**IMPORTANTE**: Antes de chamar a OpenAI, verificar se os campos de Instagram ja existem no produto.

#### Campos Obrigatorios para Post

| Campo | Model | Schema | Limite | Obrigatorio |
|-------|-------|--------|--------|-------------|
| `instagram_headline` | `String(50)` | `max_length=40` | 40 chars | Sim |
| `instagram_title` | `String(100)` | `max_length=100` | 100 chars | Sim |
| `instagram_badge` | `String(30)` | `max_length=20` | 20 chars | Sim |
| `instagram_caption` | `Text` | sem limite | 2200 chars | Sim |
| `instagram_hashtags` | `JSONB[]` | `list[str]` | 5-10 items | Sim |

#### Logica de Decisao (n8n IF Node)

```javascript
// Condicao: Todos os campos Instagram estao preenchidos?
const product = $json;

const hasAllInstagramData =
    product.instagram_headline &&
    product.instagram_headline.length > 0 &&
    product.instagram_title &&
    product.instagram_title.length > 0 &&
    product.instagram_badge &&
    product.instagram_badge.length > 0 &&
    product.instagram_caption &&
    product.instagram_caption.length > 0 &&
    product.instagram_hashtags &&
    product.instagram_hashtags.length >= 5;

return hasAllInstagramData;
```

#### Fluxo de Decisao

```
┌─────────────────────────────────────────┐
│ Verificar: hasAllInstagramData == true? │
└───────────────────┬─────────────────────┘
                    │
        ┌───────────┴───────────┐
        │                       │
       SIM                     NAO
        │                       │
        ▼                       ▼
┌───────────────────┐   ┌───────────────────────┐
│ Usar dados do     │   │ Chamar OpenAI         │
│ produto           │   │ (custo ~$0.04)        │
│ (custo: $0.00)    │   │                       │
│                   │   │ Depois:               │
│ Ir para:          │   │ Salvar dados gerados  │
│ generate-image    │   │ Registrar custo       │
└───────────────────┘   └───────────────────────┘
```

---

### 3. PATCH /api/v1/products/{id}/instagram-metadata (NOVO)

Salva os metadados de Instagram gerados pela IA e registra o custo.

**Request:**
```http
PATCH /api/v1/products/{id}/instagram-metadata
Authorization: Bearer {JWT_TOKEN}
Content-Type: application/json

{
  "instagram_headline": "DESPERTE SEU HEROI!",
  "instagram_title": "Material Escolar Epico e Aqui!",
  "instagram_badge": "NOVO NA LOA!",
  "instagram_caption": "🦸 Comece o ano letivo com estilo heroico!...",
  "instagram_hashtags": ["Vingadores", "Marvel", "GeekGeek"],
  "llm_cost": {
    "provider": "openai",
    "model": "gpt-4o-mini",
    "input_tokens": 250,
    "output_tokens": 180,
    "cost_usd": 0.00043
  }
}
```

**Response:**
```json
{
  "success": true,
  "product_id": "uuid",
  "updated_fields": [
    "instagram_headline",
    "instagram_title",
    "instagram_badge",
    "instagram_caption",
    "instagram_hashtags"
  ],
  "llm_cost_registered": true,
  "total_llm_cost_usd": 0.00043
}
```

**Logica:**
1. Atualizar campos de Instagram no produto
2. Registrar custo do LLM no historico do produto
3. Retornar confirmacao

---

### 4. POST /api/v1/instagram/generate-image

Gera imagem para Instagram a partir do template.

**Request:**
```http
POST /api/v1/instagram/generate-image
Authorization: Bearer {JWT_TOKEN}
Content-Type: application/json

{
  "product_id": "uuid",
  "headline": "DESPERTE SEU HEROI!",
  "title": "Material Escolar Epico e Aqui!",
  "badge_text": "NOVO NA LOA!",
  "hashtags": ["#Vingadores", "#GeekGeek", "#VoltaAsAulas", "#Marvel", "#Presente"]
}
```

**Response:**
```json
{
  "success": true,
  "image_url": "https://geek.bidu.guru/static/generated/instagram/abc123.png",
  "image_path": "/static/generated/instagram/abc123.png",
  "dimensions": {
    "width": 1080,
    "height": 1080
  },
  "file_size_kb": 245
}
```

**Implementacao:**
1. Carregar template HTML/CSS
2. Substituir variaveis (headline, preco, imagem, etc)
3. Renderizar HTML para imagem usando Playwright ou Pillow
4. Salvar em `/static/generated/instagram/`
5. Retornar URL publica

---

### 5. PATCH /api/v1/instagram/products/{id}/mark-posted ✅ IMPLEMENTADO

Marca produto como postado e registra no historico.

**Request:**
```http
PATCH /api/v1/instagram/products/{product_id}/mark-posted
Authorization: Bearer {JWT_TOKEN}
Content-Type: application/json

{
  "platform": "instagram",
  "post_url": "https://instagram.com/p/xxx",
  "ig_media_id": "17841234567890123",
  "caption": "Caption usado no post"
}
```

**Response:**
```json
{
  "success": true,
  "product_id": "7db20856-b8ea-4795-8e1e-dc6f7cbd3f20",
  "last_post_date": "2025-12-18T12:29:14.526448Z",
  "post_count": 1,
  "ig_media_id": "17841234567890123",
  "history_id": "733a899d-8ee6-4b3b-92b8-8a6d2a1fd0a2"
}
```

**Campos atualizados no produto:**
- `last_post_date`: Data/hora atual (UTC)
- `post_count`: Incrementa em 1
- `last_post_platform`: Nome da plataforma (ex: "instagram")
- `last_post_url`: URL do post publicado
- `last_ig_media_id`: IG Media ID retornado pela Graph API

**Historico criado:**
Para Instagram, cria registro na tabela `instagram_post_history` com:
- `product_id`: UUID do produto
- `ig_media_id`: ID retornado pela Graph API
- `post_url`: URL do post
- `caption`: Caption usada
- `posted_at`: Data/hora da publicacao

---

### 6. GET /api/v1/instagram/products/{id}/info ✅ IMPLEMENTADO (NOVO)

Retorna informacoes de publicacao Instagram de um produto.

**Request:**
```http
GET /api/v1/instagram/products/{product_id}/info
Authorization: Bearer {JWT_TOKEN}
```

**Response:**
```json
{
  "product_id": "7db20856-b8ea-4795-8e1e-dc6f7cbd3f20",
  "last_ig_media_id": "17841234567890123",
  "last_post_date": "2025-12-18T12:29:14.526448Z",
  "post_count": 1,
  "last_post_url": "https://www.instagram.com/p/TEST123456/",
  "history": [
    {
      "id": "733a899d-8ee6-4b3b-92b8-8a6d2a1fd0a2",
      "product_id": "7db20856-b8ea-4795-8e1e-dc6f7cbd3f20",
      "ig_media_id": "17841234567890123",
      "post_url": "https://www.instagram.com/p/TEST123456/",
      "caption": "OFERTA IMPERDIVEL! ...",
      "posted_at": "2025-12-18T12:29:14.526448Z",
      "created_at": "2025-12-18T12:29:14.565875Z"
    }
  ]
}
```

---

### 7. GET /api/v1/instagram/products/{id}/history ✅ IMPLEMENTADO (NOVO)

Retorna historico completo de publicacoes Instagram de um produto.

**Request:**
```http
GET /api/v1/instagram/products/{product_id}/history?limit=20
Authorization: Bearer {JWT_TOKEN}
```

**Response:**
```json
{
  "items": [
    {
      "id": "733a899d-8ee6-4b3b-92b8-8a6d2a1fd0a2",
      "product_id": "7db20856-b8ea-4795-8e1e-dc6f7cbd3f20",
      "ig_media_id": "17841234567890123",
      "post_url": "https://www.instagram.com/p/TEST123456/",
      "caption": "OFERTA IMPERDIVEL! ...",
      "posted_at": "2025-12-18T12:29:14.526448Z",
      "created_at": "2025-12-18T12:29:14.565875Z"
    }
  ],
  "total": 1
}
```

---

### 8. GET /api/v1/instagram/stats ✅ IMPLEMENTADO

Retorna estatisticas de posting para monitoramento.

**Request:**
```http
GET /api/v1/instagram/stats?days_since_last_post=30
Authorization: Bearer {JWT_TOKEN}
```

**Response:**
```json
{
  "available_for_posting": 0,
  "total_products": 1,
  "days_since_last_post": 30
}
```

---

## Geracao de Imagem: Opcoes de Implementacao

### Opcao A: Pillow (Python) - RECOMENDADO

**Pros:**
- Ja temos Pillow no projeto (usado para OG images)
- Sem dependencias externas
- Rapido e leve

**Cons:**
- Mais complexo para layouts elaborados
- Menos flexivel que HTML/CSS

**Implementacao:**
```python
# services/instagram_image.py
from PIL import Image, ImageDraw, ImageFont
import httpx

async def generate_instagram_image(
    product: Product,
    headline: str,
    title: str,
    badge_text: str,
    hashtags: list[str]
) -> str:
    # 1. Carregar background template
    bg = Image.open("templates/instagram/background.png")

    # 2. Baixar e redimensionar imagem do produto
    product_img = await download_and_resize(product.image_url, (400, 400))

    # 3. Compor imagem
    bg.paste(product_img, (340, 200))  # Posicao central

    # 4. Adicionar textos
    draw = ImageDraw.Draw(bg)
    draw.text((700, 50), headline, font=headline_font, fill="yellow")
    draw.text((650, 650), f"R$ {product.current_price:.2f}", font=price_font, fill="yellow")
    # ... mais textos

    # 5. Salvar
    filename = f"{uuid4()}.png"
    path = f"static/generated/instagram/{filename}"
    bg.save(path, "PNG", quality=95)

    return f"/static/generated/instagram/{filename}"
```

### Opcao B: Playwright (HTML to Image)

**Pros:**
- Template em HTML/CSS (facil de editar)
- Flexibilidade total de design
- Suporta fontes web, gradientes, etc

**Cons:**
- Dependencia pesada (Chromium)
- Mais lento (~2-3s por imagem)
- Mais memoria

**Implementacao:**
```python
# services/instagram_image.py
from playwright.async_api import async_playwright

async def generate_instagram_image_playwright(
    product: Product,
    headline: str,
    title: str,
    badge_text: str,
    hashtags: list[str]
) -> str:
    # 1. Renderizar template Jinja2
    html = templates.get_template("instagram/post_template.html").render(
        product=product,
        headline=headline,
        title=title,
        badge_text=badge_text,
        hashtags=hashtags
    )

    # 2. Screenshot com Playwright
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width": 1080, "height": 1080})
        await page.set_content(html)

        filename = f"{uuid4()}.png"
        path = f"static/generated/instagram/{filename}"
        await page.screenshot(path=path)

        await browser.close()

    return f"/static/generated/instagram/{filename}"
```

### Recomendacao

**Usar Pillow** para MVP:
- Ja temos experiencia com OG images
- Mais leve e rapido
- Podemos migrar para Playwright depois se necessario

---

## Conteudo Gerado por IA

> **IMPORTANTE**: Este passo so e executado se os campos de Instagram do produto estiverem vazios/incompletos.
> Se o produto ja tiver os dados pre-cadastrados, pular para a geracao de imagem (economia de custo).

### Limites dos Campos (Alinhados com Schema)

| Campo | Schema Limit | Prompt Limit | Validacao |
|-------|--------------|--------------|-----------|
| `instagram_headline` | max 40 chars | max 40 chars | MAIUSCULAS, com ! |
| `instagram_title` | max 100 chars | max 100 chars | Chamativo |
| `instagram_badge` | max 20 chars | max 20 chars | Ex: NOVO!, -30% |
| `instagram_caption` | sem limite | max 2200 chars | Com emojis e CTA |
| `instagram_hashtags` | list[str] | 5-10 items | Sem # no inicio |

### Prompt para OpenAI

```
Voce e um social media manager especialista em produtos geek para o Instagram @geek.bidu.guru.

Crie conteudo para postar o seguinte produto:

PRODUTO:
- Nome: {product.name}
- Descricao: {product.short_description}
- Preco: R$ {product.price}
- Categoria: {product.categories[0]}
- Tags: {product.tags}

GERE um JSON com:

{
  "instagram_headline": "Frase de impacto (max 40 chars, MAIUSCULAS, com ! no final)",
  "instagram_title": "Titulo chamativo para a imagem (max 100 chars)",
  "instagram_badge": "Texto do badge (max 20 chars, ex: NOVO!, OFERTA!, -30%)",
  "instagram_caption": "Legenda completa (max 2200 chars). Envolvente, emojis moderados, call-to-action, link na bio.",
  "instagram_hashtags": ["lista", "de", "5", "a", "10", "hashtags", "relevantes", "sem", "simbolo", "#"]
}

DIRETRIZES:
- Tom: Entusiasmado mas autentico, como um amigo geek
- Use emojis com moderacao (3-5 por caption)
- Inclua call-to-action (link na bio)
- Hashtags: mix de populares (geek, nerd) e especificas (vingadores, marvel)
- Se tiver desconto, destaque no instagram_badge (ex: "-28% OFF!")
- instagram_headline deve ser impactante e curto (MAX 40 CARACTERES!)
- instagram_badge deve ter MAX 20 CARACTERES!

VALIDACAO CRITICA:
- instagram_headline: EXATAMENTE max 40 caracteres
- instagram_badge: EXATAMENTE max 20 caracteres
- instagram_hashtags: entre 5 e 10 items, SEM o simbolo #
```

### Exemplo de Resposta

```json
{
  "instagram_headline": "DESPERTE SEU HEROI!",
  "instagram_title": "Material Escolar Epico e Aqui!",
  "instagram_badge": "NOVO NA LOJA!",
  "instagram_caption": "🦸 Comece o ano letivo com estilo heroico!\n\nEsse kit de lapis dos Vingadores e perfeito pra quem quer arrasar na escola com muito estilo geek. Capitao America, Homem de Ferro e toda a turma reunida!\n\n✨ Kit completo com 4 itens\n💰 Por apenas R$ 24,90\n\nCorre que ta acabando! Link na bio 👆\n\n#Vingadores #Marvel #GeekGeek #VoltaAsAulas #MaterialEscolar #PresenteGeek #Nerd #HQs #Avengers #LojaGeek",
  "instagram_hashtags": ["Vingadores", "Marvel", "GeekGeek", "VoltaAsAulas", "MaterialEscolar", "PresenteGeek", "Nerd", "HQs", "Avengers", "LojaGeek"]
}

### Pos-Geracao: Salvar e Registrar Custo

Apos receber a resposta da OpenAI, o n8n deve:

1. **Chamar PATCH /api/v1/products/{id}/instagram-metadata** com:
   - Os 5 campos gerados (headline, title, badge, caption, hashtags)
   - Informacoes de custo do LLM (tokens, modelo, custo USD)

2. **Calculo de Custo (gpt-4o-mini)**:
   ```javascript
   // Precos gpt-4o-mini (2024):
   // Input: $0.00015 / 1K tokens
   // Output: $0.0006 / 1K tokens

   const inputTokens = $json.usage.prompt_tokens;
   const outputTokens = $json.usage.completion_tokens;

   const costUsd =
     (inputTokens / 1000) * 0.00015 +
     (outputTokens / 1000) * 0.0006;

   // Exemplo: 250 input + 180 output = ~$0.00043
   ```

---

## Fluxo Completo n8n

```
┌────────────────────────────────────────────────────────────────────────────┐
│                    WORKFLOW N8N: FLOW A v3.1                               │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                            │
│  ┌─────────────┐          ┌──────────────────┐                            │
│  │ Schedule    │          │ Manual Trigger   │                            │
│  │ 0 8 * * *   │          │ (Webhook/Button) │                            │
│  │ (Auto)      │          │ param: product_id│                            │
│  └──────┬──────┘          └────────┬─────────┘                            │
│         │                          │                                       │
│         ▼                          ▼                                       │
│  ┌─────────────────┐      ┌────────────────────────┐                      │
│  │ HTTP Request    │      │ HTTP Request           │                      │
│  │ GET /products/  │      │ GET /products/         │                      │
│  │ random          │      │ {{$json.product_id}}   │                      │
│  └────────┬────────┘      └───────────┬────────────┘                      │
│           │                           │                                    │
│           └─────────────┬─────────────┘                                    │
│                         ▼                                                  │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │ IF: Produto encontrado?                                             │  │
│  │ Condition: {{$json.id}} exists                                      │  │
│  └────────┬────────────────────────────────────────┬───────────────────┘  │
│           │ SIM                                    │ NAO                   │
│           ▼                                        ▼                       │
│  ┌─────────────────────────────────────┐   ┌─────────────────────────┐    │
│  │ IF: Dados Instagram completos?      │   │ Notificar               │    │
│  │ Condition:                          │   │ "Sem produto"           │    │
│  │   instagram_headline &&             │   └─────────────────────────┘    │
│  │   instagram_title &&                │                                  │
│  │   instagram_badge &&                │   ◄── NOVO! Verificacao          │
│  │   instagram_caption &&              │                                  │
│  │   instagram_hashtags.length >= 5    │                                  │
│  └───────┬──────────────────┬──────────┘                                  │
│          │ SIM              │ NAO                                         │
│          │ (Custo $0)       │ (Custo ~$0.04)                              │
│          │                  ▼                                             │
│          │         ┌───────────────────────────────┐                      │
│          │         │ OpenAI: Gerar conteudo        │                      │
│          │         │ Model: gpt-4o-mini            │                      │
│          │         │ Prompt: ver secao acima       │                      │
│          │         └────────────────┬──────────────┘                      │
│          │                          │                                     │
│          │                          ▼                                     │
│          │         ┌───────────────────────────────┐                      │
│          │         │ HTTP Request                  │  ◄── NOVO!           │
│          │         │ PATCH /products/{id}/         │                      │
│          │         │ instagram-metadata            │                      │
│          │         │ Body: dados + custo LLM       │                      │
│          │         └────────────────┬──────────────┘                      │
│          │                          │                                     │
│          └──────────────────────────┤                                     │
│                                     ▼                                     │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │ HTTP Request                                                        │  │
│  │ POST {{API_URL}}/api/v1/instagram/generate-image                    │  │
│  │ Body: {product_id, headline, title, badge, hashtags}                │  │
│  └──────────────────────────────────┬──────────────────────────────────┘  │
│                                     │                                     │
│                                     ▼                                     │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │ Facebook Graph API: Criar container                                 │  │
│  │ POST /{ig-user-id}/media                                            │  │
│  │ image_url: {{$json.image_url}}                                      │  │
│  │ caption: {{instagram_caption}} + hashtags                           │  │
│  └──────────────────────────────────┬──────────────────────────────────┘  │
│                                     │                                     │
│                                     ▼                                     │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │ Facebook Graph API: Publicar                                        │  │
│  │ POST /{ig-user-id}/media_publish                                    │  │
│  │ creation_id: {{$json.id}}                                           │  │
│  └──────────────────────────────────┬──────────────────────────────────┘  │
│                                     │                                     │
│                                     ▼                                     │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │ HTTP Request                                                        │  │
│  │ PATCH {{API_URL}}/api/v1/products/{id}/mark-posted                  │  │
│  └──────────────────────────────────┬──────────────────────────────────┘  │
│                                     │                                     │
│                                     ▼                                     │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │ Notificacao: Instagram DM (ou Telegram)                             │  │
│  │ "Post publicado com sucesso!"                                       │  │
│  │ Incluir: nome produto, URL post, custo LLM (se houve)               │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
│                                                                            │
└────────────────────────────────────────────────────────────────────────────┘
```

### Configuracao do Trigger Manual (Webhook)

Para testes, configurar um webhook que recebe o `product_id`:

```javascript
// Webhook URL: https://n8n.seudominio.com/webhook/instagram-post-manual
// Method: POST
// Body esperado:
{
  "product_id": "uuid-do-produto"
}

// Uso via curl:
curl -X POST https://n8n.seudominio.com/webhook/instagram-post-manual \
  -H "Content-Type: application/json" \
  -d '{"product_id": "550e8400-e29b-41d4-a716-446655440000"}'
```

---

## Campos no Modelo Product

> **NOTA**: Os campos de controle de posts e metadados Instagram ja existem no modelo.
> Ver `src/app/models/product.py` para implementacao atual.

### Campos de Controle de Posts (ja implementados)

```python
# models/product.py - Campos existentes

class Product(Base):
    # Controle de publicacao
    last_post_date: Mapped[datetime | None]      # Data do ultimo post
    post_count: Mapped[int]                       # Vezes postado
    last_post_platform: Mapped[str | None]        # instagram, tiktok, etc
    last_post_url: Mapped[str | None]             # URL do post

    # Metadados Instagram (pre-configuracao)
    instagram_headline: Mapped[str | None]        # max 50 chars
    instagram_title: Mapped[str | None]           # max 100 chars
    instagram_badge: Mapped[str | None]           # max 30 chars
    instagram_caption: Mapped[str | None]         # Text (sem limite)
    instagram_hashtags: Mapped[list]              # JSONB array
```

### Novo: Historico de Custos LLM (a implementar)

Para rastrear gastos com IA por produto, criar uma nova tabela ou campo JSONB:

```python
# Opcao A: Campo JSONB no Product (simples)
class Product(Base):
    # ... campos existentes ...

    llm_cost_history: Mapped[list] = mapped_column(
        JSONBType,
        default=list,
        server_default="[]",
        comment="Historico de custos com LLM [{date, provider, model, tokens, cost_usd}]"
    )
    total_llm_cost_usd: Mapped[float] = mapped_column(
        Numeric(10, 6),
        default=0,
        server_default="0",
        comment="Custo total acumulado com LLM (USD)"
    )

# Exemplo de entrada no historico:
# {
#   "date": "2025-12-18T08:00:00Z",
#   "provider": "openai",
#   "model": "gpt-4o-mini",
#   "input_tokens": 250,
#   "output_tokens": 180,
#   "cost_usd": 0.00043,
#   "purpose": "instagram_content"
# }
```

```python
# Opcao B: Tabela separada (mais robusto, para analytics)
class LLMCostLog(Base, UUIDMixin, TimestampMixin):
    """Registro de custos com LLM por produto."""

    __tablename__ = "llm_cost_logs"

    product_id: Mapped[UUID] = mapped_column(
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    provider: Mapped[str] = mapped_column(String(50))  # openai, anthropic, etc
    model: Mapped[str] = mapped_column(String(100))    # gpt-4o-mini, etc
    input_tokens: Mapped[int] = mapped_column(Integer)
    output_tokens: Mapped[int] = mapped_column(Integer)
    cost_usd: Mapped[float] = mapped_column(Numeric(10, 6))
    purpose: Mapped[str] = mapped_column(String(100))  # instagram_content, etc

    # Relacionamento
    product: Mapped["Product"] = relationship(back_populates="llm_costs")
```

### Recomendacao

**Para MVP**: Usar **Opcao A** (campo JSONB) - mais simples e rapido de implementar.

**Para Analytics futuro**: Migrar para **Opcao B** (tabela separada) quando precisar de:
- Relatorios de custo por periodo
- Comparacao entre modelos
- Budget alerts

---

## Estrutura de Arquivos

```
src/app/
├── api/v1/endpoints/
│   └── instagram.py          # Endpoints de Instagram (generate-image)
├── services/
│   └── instagram_image.py    # Geracao de imagem com Pillow
├── templates/
│   └── instagram/
│       ├── background.png    # Background pattern geek
│       ├── logo.png          # Logo GEEK.BIDU.GURU
│       ├── frame.png         # Moldura do produto
│       └── fonts/
│           ├── headline.ttf  # Fonte para headlines
│           └── body.ttf      # Fonte para textos
└── static/
    └── generated/
        └── instagram/        # Imagens geradas (gitignore)
```

---

## Requisitos de Implementacao

### Backend (FastAPI)

| Tarefa | Prioridade | Status | Notas |
|--------|------------|--------|-------|
| Migration: campos de controle em Product | Alta | ✅ | Ja implementado |
| Migration: campos instagram_* em Product | Alta | ✅ | Ja implementado |
| Migration: campo last_ig_media_id em Product | Alta | ✅ | Migration 023 |
| Migration: tabela instagram_post_history | Alta | ✅ | Migration 023 |
| Endpoint `GET /api/v1/instagram/product/random` | Alta | ✅ | Testado e funcionando |
| Endpoint `GET /api/v1/instagram/template/{id}` | Alta | ✅ | Renderiza HTML |
| Endpoint `POST /api/v1/instagram/utils/html-to-image` | Alta | ✅ | Playwright |
| Endpoint `PATCH /api/v1/instagram/products/{id}/mark-posted` | Alta | ✅ | Com ig_media_id e historico |
| Endpoint `GET /api/v1/instagram/products/{id}/info` | Alta | ✅ | Dados de publicacao |
| Endpoint `GET /api/v1/instagram/products/{id}/history` | Alta | ✅ | Historico completo |
| Endpoint `GET /api/v1/instagram/stats` | Alta | ✅ | Estatisticas de posting |
| Endpoint `GET /api/v1/products/{id}` | Alta | ✅ | Ja existe |
| Endpoint `POST/PATCH/DELETE /api/v1/products` | Alta | ✅ | Autenticacao adicionada |
| Migration: campos llm_cost | Alta | ✅ | Campos ai_* no Product (ja existem) |
| Endpoint `PATCH /api/v1/products/{id}/instagram-metadata` | Alta | ✅ | Salvar + custo LLM |
| Endpoint `POST /api/v1/instagram/generate-image` | Alta | ✅ | Template + screenshot em 1 chamada |
| Testes automatizados dos endpoints | Media | ⬜ | |

### Instagram

| Tarefa | Prioridade | Status |
|--------|------------|--------|
| Converter conta para Business | Alta | ⬜ |
| Criar Facebook Page vinculada | Alta | ⬜ |
| Criar Facebook App | Alta | ⬜ |
| Solicitar permissoes (App Review) | Alta | ⬜ |
| Gerar Access Token | Alta | ⬜ |

### n8n

| Tarefa | Prioridade | Status | Notas |
|--------|------------|--------|-------|
| Criar credencial Backend (Header Auth) | Alta | ⬜ | |
| Criar credencial OpenAI | Alta | ⬜ | |
| Criar credencial Facebook/Instagram | Alta | ⬜ | |
| Montar workflow - Trigger Automatico | Alta | ⬜ | Schedule 8h |
| Montar workflow - Trigger Manual (NOVO) | Alta | ⬜ | Webhook teste |
| Implementar IF: verificar dados Instagram | Alta | ⬜ | Evitar custo IA |
| Implementar calculo custo LLM | Alta | ⬜ | Tokens → USD |
| Testar execucao manual | Alta | ⬜ | |
| Ativar schedule | Alta | ⬜ | |

---

## Proximos Passos

### Ordem de Implementacao

1. **Backend - Migration e Endpoints (Fase 1)** ✅ CONCLUIDO
   - [x] Criar migration para campos de controle de posts
   - [x] Criar migration para campos instagram_*
   - [x] Criar migration para last_ig_media_id e instagram_post_history
   - [x] Implementar `GET /instagram/product/random`
   - [x] Implementar `PATCH /instagram/products/{id}/mark-posted`
   - [x] Implementar `GET /instagram/products/{id}/info`
   - [x] Implementar `GET /instagram/products/{id}/history`
   - [x] Implementar `GET /instagram/stats`
   - [x] Adicionar autenticacao nos endpoints de products

2. **Backend - Geracao de Imagem (Fase 2)** ✅ CONCLUIDO
   - [x] Criar template HTML `post_produto.html`
   - [x] Implementar `GET /instagram/template/{id}` (renderiza HTML)
   - [x] Implementar `POST /instagram/utils/html-to-image` (Playwright)
   - [x] Testar geracao de imagem

3. **Instagram - Configuracao (Fase 3)** ⬜ PENDENTE
   - [ ] Converter conta para Business
   - [ ] Criar Facebook Page
   - [ ] Criar Facebook App
   - [ ] Configurar permissoes

4. **n8n - Workflow (Fase 4)** ⬜ PENDENTE
   - [ ] Montar workflow - Trigger Automatico (Schedule 8h)
   - [ ] Montar workflow - Trigger Manual (Webhook)
   - [ ] Implementar IF: verificar dados Instagram pre-cadastrados
   - [ ] Implementar calculo de custo LLM (tokens → USD) (opcional)
   - [ ] Testar execucao manual com produto especifico
   - [ ] Ativar schedule

---

## Estimativa de Custos

### Custo por Post

| Cenario | Custo OpenAI | Notas |
|---------|--------------|-------|
| Dados pre-cadastrados | **$0.00** | Economia total |
| Geracao via gpt-4o-mini | ~$0.0004 | ~250 in + 180 out tokens |

### Custo Mensal (30 posts)

| Cenario | Custo/mes |
|---------|-----------|
| 100% gerado por IA | ~$0.012/mes |
| 50% pre-cadastrado | ~$0.006/mes |
| 100% pre-cadastrado | **$0.00/mes** |

| Item | Custo |
|------|-------|
| OpenAI (pior caso) | ~$0.02/mes |
| Instagram Graph API | Gratuito |
| Armazenamento imagens | Negligivel |
| **Total** | **< $0.05/mes** |

> **Nota**: O custo real e muito menor que a estimativa anterior ($1.20)
> devido ao uso do gpt-4o-mini em vez de gpt-4.

---

## Referencias

- [Instagram Graph API - Content Publishing](https://developers.facebook.com/docs/instagram-api/guides/content-publishing)
- [Pillow Documentation](https://pillow.readthedocs.io/)
- [docs/N8N-INTEGRATION.md](../N8N-INTEGRATION.md)

---

**Aprovacoes:**

| Papel | Nome | Data | Status |
|-------|------|------|--------|
| Product Owner | - | - | ⬜ Pendente |
| Tech Lead | - | - | ⬜ Pendente |
