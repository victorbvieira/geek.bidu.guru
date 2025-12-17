# Flow A: Post Diario Automatico - Instagram

> **Versao**: 3.0
> **Status**: Em validacao
> **Data**: 2025-12-17
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

## Arquitetura

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    FLOW A v3: POST DIARIO INSTAGRAM                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  [1. Cron 8h]                                                               │
│       │                                                                     │
│       ▼                                                                     │
│  [2. GET /api/v1/products/random]                                          │
│  - Produto nao postado nos ultimos 30 dias                                 │
│  - Disponivel e com imagem                                                  │
│       │                                                                     │
│       ▼                                                                     │
│  [3. OpenAI: Gerar conteudo Instagram]                                     │
│  - Headline criativo (ex: "DESPERTE SEU HEROI!")                           │
│  - Titulo chamativo                                                         │
│  - Legenda (caption) ate 2200 chars                                        │
│  - 5-10 hashtags relevantes                                                │
│       │                                                                     │
│       ▼                                                                     │
│  [4. POST /api/v1/instagram/generate-image]  ◄── API INTERNA               │
│  - Recebe: produto + conteudo gerado                                       │
│  - Gera imagem 1080x1080 a partir do template                              │
│  - Retorna: URL da imagem gerada                                           │
│       │                                                                     │
│       ▼                                                                     │
│  [5. Instagram Graph API: Publicar]                                        │
│  - Upload da imagem                                                         │
│  - Caption + hashtags                                                       │
│       │                                                                     │
│       ▼                                                                     │
│  [6. PATCH /api/v1/products/{id}/mark-posted]                              │
│  - Atualiza last_post_date                                                  │
│  - Incrementa post_count                                                    │
│       │                                                                     │
│       ▼                                                                     │
│  [7. Instagram DM: Notificar admin]                                        │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

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

### 1. GET /api/v1/products/random

Busca produto aleatorio para postar.

**Request:**
```http
GET /api/v1/products/random?days_since_last_post=30&availability=available
Authorization: Bearer {JWT_TOKEN}
```

**Response:**
```json
{
  "id": "uuid",
  "name": "Kit Lapis Vingadores",
  "slug": "kit-lapis-vingadores",
  "short_description": "Kit com 4 lapis dos Vingadores",
  "current_price": 24.90,
  "original_price": 34.90,
  "affiliate_url": "https://amzn.to/xxx",
  "image_url": "https://...",
  "platform": "amazon",
  "category": {"name": "Papelaria", "slug": "papelaria"},
  "tags": ["vingadores", "marvel", "escolar"],
  "last_post_date": null,
  "post_count": 0
}
```

**Logica:**
```sql
SELECT * FROM products
WHERE availability = 'available'
  AND image_url IS NOT NULL
  AND (last_post_date IS NULL OR last_post_date < NOW() - INTERVAL '30 days')
ORDER BY post_count ASC, RANDOM()
LIMIT 1;
```

---

### 2. POST /api/v1/instagram/generate-image

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

### 3. PATCH /api/v1/products/{id}/mark-posted

Marca produto como postado.

**Request:**
```http
PATCH /api/v1/products/{id}/mark-posted
Authorization: Bearer {JWT_TOKEN}
Content-Type: application/json

{
  "platform": "instagram",
  "post_url": "https://instagram.com/p/xxx",
  "caption": "Caption usado no post"
}
```

**Response:**
```json
{
  "success": true,
  "product_id": "uuid",
  "last_post_date": "2025-12-17T08:00:00Z",
  "post_count": 1
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

### Prompt para OpenAI

```
Voce e um social media manager especialista em produtos geek para o Instagram @geek.bidu.guru.

Crie conteudo para postar o seguinte produto:

PRODUTO:
- Nome: {product.name}
- Descricao: {product.short_description}
- Preco: R$ {product.current_price}
- Preco original: R$ {product.original_price}
- Categoria: {product.category.name}

GERE um JSON com:

{
  "headline": "Frase de impacto curta para a imagem (max 25 chars, MAIUSCULAS, com ! no final)",
  "title": "Titulo chamativo para a imagem (max 40 chars)",
  "badge_text": "Texto do badge (max 15 chars, ex: NOVO!, OFERTA!, -30%)",
  "caption": "Legenda completa para o Instagram (max 2000 chars). Deve ser envolvente, usar emojis moderadamente, ter call-to-action e mencionar o link na bio.",
  "hashtags": ["lista", "de", "10", "hashtags", "relevantes", "sem", "o", "simbolo", "#"]
}

DIRETRIZES:
- Tom: Entusiasmado mas autentico, como um amigo geek
- Use emojis com moderacao (3-5 por caption)
- Inclua call-to-action (link na bio)
- Hashtags: mix de populares (#geek, #nerd) e especificas (#vingadores, #marvel)
- Se tiver desconto, destaque no badge_text (ex: "-28% OFF!")
- headline deve ser impactante e curto
```

### Exemplo de Resposta

```json
{
  "headline": "DESPERTE SEU HEROI!",
  "title": "Material Escolar Epico e Aqui!",
  "badge_text": "NOVO NA LOA!",
  "caption": "🦸 Comece o ano letivo com estilo heroico!\n\nEsse kit de lapis dos Vingadores e perfeito pra quem quer arrasar na escola com muito estilo geek. Capitao America, Homem de Ferro e toda a turma reunida!\n\n✨ Kit completo com 4 itens\n💰 Por apenas R$ 24,90\n\nCorre que ta acabando! Link na bio 👆\n\n#Vingadores #Marvel #GeekGeek #VoltaAsAulas #MaterialEscolar #PresenteGeek #Nerd #HQs #Avengers #LojaGeek",
  "hashtags": ["Vingadores", "Marvel", "GeekGeek", "VoltaAsAulas", "MaterialEscolar", "PresenteGeek", "Nerd", "HQs", "Avengers", "LojaGeek"]
}
```

---

## Fluxo Completo n8n

```
┌────────────────────────────────────────────────────────────────────────────┐
│                         WORKFLOW N8N: FLOW A                               │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                            │
│  ┌─────────┐                                                               │
│  │ Schedule│  Cron: 0 8 * * * (8h BRT)                                    │
│  └────┬────┘                                                               │
│       │                                                                    │
│       ▼                                                                    │
│  ┌─────────────────────────────────────┐                                  │
│  │ HTTP Request                        │                                  │
│  │ GET {{API_URL}}/api/v1/products/random                                 │
│  │ Headers: Authorization: Bearer {{JWT}}                                  │
│  └────┬────────────────────────────────┘                                  │
│       │                                                                    │
│       ▼                                                                    │
│  ┌─────────────────────────────────────┐                                  │
│  │ IF: Produto encontrado?             │                                  │
│  │ Condition: {{$json.id}} exists      │                                  │
│  └────┬─────────────────┬──────────────┘                                  │
│       │ SIM             │ NAO                                              │
│       ▼                 ▼                                                  │
│  ┌─────────────┐   ┌─────────────┐                                        │
│  │ OpenAI      │   │ Notificar   │                                        │
│  │ Gerar       │   │ "Sem        │                                        │
│  │ conteudo    │   │ produtos"   │                                        │
│  └────┬────────┘   └─────────────┘                                        │
│       │                                                                    │
│       ▼                                                                    │
│  ┌─────────────────────────────────────┐                                  │
│  │ HTTP Request                        │                                  │
│  │ POST {{API_URL}}/api/v1/instagram/generate-image                       │
│  │ Body: {product_id, headline, title, badge, hashtags}                   │
│  └────┬────────────────────────────────┘                                  │
│       │                                                                    │
│       ▼                                                                    │
│  ┌─────────────────────────────────────┐                                  │
│  │ Facebook Graph API                  │                                  │
│  │ POST /{ig-user-id}/media            │                                  │
│  │ image_url: {{$json.image_url}}      │                                  │
│  │ caption: {{openai.caption}}         │                                  │
│  └────┬────────────────────────────────┘                                  │
│       │                                                                    │
│       ▼                                                                    │
│  ┌─────────────────────────────────────┐                                  │
│  │ Facebook Graph API                  │                                  │
│  │ POST /{ig-user-id}/media_publish    │                                  │
│  │ creation_id: {{$json.id}}           │                                  │
│  └────┬────────────────────────────────┘                                  │
│       │                                                                    │
│       ▼                                                                    │
│  ┌─────────────────────────────────────┐                                  │
│  │ HTTP Request                        │                                  │
│  │ PATCH {{API_URL}}/api/v1/products/{{id}}/mark-posted                   │
│  └────┬────────────────────────────────┘                                  │
│       │                                                                    │
│       ▼                                                                    │
│  ┌─────────────────────────────────────┐                                  │
│  │ Instagram DM (ou Telegram)          │                                  │
│  │ "Post publicado com sucesso!"       │                                  │
│  └─────────────────────────────────────┘                                  │
│                                                                            │
└────────────────────────────────────────────────────────────────────────────┘
```

---

## Campos Novos no Modelo Product

```python
# models/product.py - Novos campos para controle de posts

class Product(Base):
    # ... campos existentes ...

    # Controle de publicacao
    last_post_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Data do ultimo post sobre este produto"
    )
    post_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        comment="Quantidade de vezes que foi postado"
    )
    last_post_platform: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        comment="Plataforma do ultimo post (instagram, tiktok, etc)"
    )
    last_post_url: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
        comment="URL do ultimo post publicado"
    )
```

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

| Tarefa | Prioridade | Status |
|--------|------------|--------|
| Migration: campos de controle em Product | Alta | ⬜ |
| Endpoint `GET /api/v1/products/random` | Alta | ⬜ |
| Endpoint `POST /api/v1/instagram/generate-image` | Alta | ⬜ |
| Endpoint `PATCH /api/v1/products/{id}/mark-posted` | Alta | ⬜ |
| Service `instagram_image.py` (Pillow) | Alta | ⬜ |
| Criar assets do template (background, logo, fonts) | Alta | ⬜ |
| Testes dos endpoints | Media | ⬜ |

### Instagram

| Tarefa | Prioridade | Status |
|--------|------------|--------|
| Converter conta para Business | Alta | ⬜ |
| Criar Facebook Page vinculada | Alta | ⬜ |
| Criar Facebook App | Alta | ⬜ |
| Solicitar permissoes (App Review) | Alta | ⬜ |
| Gerar Access Token | Alta | ⬜ |

### n8n

| Tarefa | Prioridade | Status |
|--------|------------|--------|
| Criar credencial Backend (Header Auth) | Alta | ⬜ |
| Criar credencial OpenAI | Alta | ⬜ |
| Criar credencial Facebook/Instagram | Alta | ⬜ |
| Montar workflow | Alta | ⬜ |
| Testar execucao manual | Alta | ⬜ |
| Ativar schedule | Alta | ⬜ |

---

## Proximos Passos

### Ordem de Implementacao

1. **Backend - Migration e Endpoints**
   - [ ] Criar migration para campos de controle
   - [ ] Implementar `GET /products/random`
   - [ ] Implementar `PATCH /products/{id}/mark-posted`

2. **Backend - Geracao de Imagem**
   - [ ] Criar assets do template (background, logo, fonts)
   - [ ] Implementar `services/instagram_image.py`
   - [ ] Implementar `POST /instagram/generate-image`
   - [ ] Testar geracao de imagem

3. **Instagram - Configuracao**
   - [ ] Converter conta para Business
   - [ ] Criar Facebook Page
   - [ ] Criar Facebook App
   - [ ] Configurar permissoes

4. **n8n - Workflow**
   - [ ] Montar workflow completo
   - [ ] Testar manualmente
   - [ ] Ativar schedule

---

## Estimativa de Custos

| Item | Custo |
|------|-------|
| OpenAI (30 posts/mes) | ~$1.20/mes |
| Instagram Graph API | Gratuito |
| Armazenamento imagens | Negligivel |
| **Total** | **~$1.20/mes** |

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
