# Fase 2: SEO & Automacao

**Prioridade**: ALTA
**Objetivo**: Otimizacao para SEO e automacao com n8n
**Agentes Principais**: SEO Specialist, Automation Engineer, Data Analyst, DevOps Engineer

---

## Visao Geral da Fase

A Fase 2 foca em tornar o site "encontravel" e automatizado. Ao final desta fase, teremos:
- SEO tecnico completo (sitemap, robots, schema.org)
- Open Graph e Twitter Cards funcionando
- n8n configurado e operacional
- Workflows de geracao de conteudo automatizados
- Atualizacao automatica de precos
- Google Analytics 4 integrado

---

## 2.1 SEO Tecnico

**Agente Principal**: SEO Specialist
**Referencia**: `agents/seo-specialist.md`

### 2.1.1 Sitemap.xml Dinamico

**Arquivo**: `src/app/routers/seo.py`

```python
"""
Rotas para SEO: sitemap.xml, robots.txt
"""
from fastapi import APIRouter, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from app.database import get_db
from app.services.post_service import PostService

router = APIRouter()


@router.get("/sitemap.xml", response_class=Response)
async def sitemap(db: AsyncSession = Depends(get_db)):
    """
    Gera sitemap.xml dinamico com todos os posts publicados.

    Inclui:
    - Homepage
    - Paginas de categoria
    - Posts publicados
    - Paginas estaticas (sobre, contato, etc.)
    """
    service = PostService(db)
    posts = await service.get_published_posts()
    categories = await service.get_all_categories()

    xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <!-- Homepage -->
    <url>
        <loc>https://geek.bidu.guru/</loc>
        <changefreq>daily</changefreq>
        <priority>1.0</priority>
    </url>

    <!-- Categorias -->
'''

    for cat in categories:
        xml_content += f'''    <url>
        <loc>https://geek.bidu.guru/categoria/{cat.slug}</loc>
        <changefreq>weekly</changefreq>
        <priority>0.8</priority>
    </url>
'''

    # Posts
    for post in posts:
        lastmod = post.updated_at.strftime("%Y-%m-%d") if post.updated_at else ""
        xml_content += f'''    <url>
        <loc>https://geek.bidu.guru/post/{post.slug}</loc>
        <lastmod>{lastmod}</lastmod>
        <changefreq>monthly</changefreq>
        <priority>0.7</priority>
    </url>
'''

    xml_content += '</urlset>'

    return Response(
        content=xml_content,
        media_type="application/xml"
    )


@router.get("/robots.txt", response_class=Response)
async def robots():
    """
    Retorna robots.txt otimizado para SEO.
    """
    content = """# robots.txt - geek.bidu.guru
User-agent: *
Allow: /

# Bloquear areas administrativas
Disallow: /api/
Disallow: /admin/
Disallow: /auth/

# Sitemap
Sitemap: https://geek.bidu.guru/sitemap.xml
"""
    return Response(content=content, media_type="text/plain")
```

### 2.1.2-2.1.6 Demais Itens SEO Tecnico

**Implementar**:
- Canonical URLs em todos os templates
- Breadcrumbs com Schema.org
- URLs limpas e semanticas
- Redirects 301 para URLs antigas

---

## 2.2 Schema.org / Structured Data

**Agente Principal**: SEO Specialist
**Referencia**: `agents/seo-specialist.md`

### 2.2.1 Schema BlogPosting

**Arquivo**: `src/app/templates/components/schema_blogposting.html`

```html
{% macro render_blogposting(post) %}
<script type="application/ld+json">
{
    "@context": "https://schema.org",
    "@type": "BlogPosting",
    "headline": "{{ post.title }}",
    "description": "{{ post.meta_description or post.excerpt }}",
    "image": "{{ post.featured_image or '/static/images/default-post.jpg' }}",
    "datePublished": "{{ post.published_at.isoformat() if post.published_at else '' }}",
    "dateModified": "{{ post.updated_at.isoformat() if post.updated_at else '' }}",
    "author": {
        "@type": "Person",
        "name": "{{ post.author.full_name }}"
    },
    "publisher": {
        "@type": "Organization",
        "name": "geek.bidu.guru",
        "logo": {
            "@type": "ImageObject",
            "url": "https://geek.bidu.guru/static/images/logo.png"
        }
    },
    "mainEntityOfPage": {
        "@type": "WebPage",
        "@id": "https://geek.bidu.guru/post/{{ post.slug }}"
    }
    {% if post.keywords %},
    "keywords": "{{ post.keywords | join(', ') }}"
    {% endif %}
}
</script>
{% endmacro %}
```

### 2.2.2 Schema Product

**Arquivo**: `src/app/templates/components/schema_product.html`

```html
{% macro render_product(product) %}
<script type="application/ld+json">
{
    "@context": "https://schema.org",
    "@type": "Product",
    "name": "{{ product.name }}",
    "description": "{{ product.description }}",
    "image": "{{ product.image_url }}",
    "brand": {
        "@type": "Brand",
        "name": "{{ product.brand or 'Generico' }}"
    },
    "offers": {
        "@type": "Offer",
        "url": "https://geek.bidu.guru/goto/{{ product.affiliate_redirect_slug }}",
        "priceCurrency": "{{ product.currency or 'BRL' }}",
        "price": "{{ product.price }}",
        "availability": "{{ 'https://schema.org/InStock' if product.is_available else 'https://schema.org/OutOfStock' }}",
        "seller": {
            "@type": "Organization",
            "name": "{{ product.platform | capitalize }}"
        }
    }
    {% if product.rating %},
    "aggregateRating": {
        "@type": "AggregateRating",
        "ratingValue": "{{ product.rating }}",
        "reviewCount": "{{ product.review_count or 1 }}"
    }
    {% endif %}
}
</script>
{% endmacro %}
```

### 2.2.3 Schema ItemList (Listicles)

**Arquivo**: `src/app/templates/components/schema_itemlist.html`

```html
{% macro render_itemlist(post, products) %}
<script type="application/ld+json">
{
    "@context": "https://schema.org",
    "@type": "ItemList",
    "name": "{{ post.title }}",
    "description": "{{ post.meta_description or post.excerpt }}",
    "numberOfItems": {{ products | length }},
    "itemListElement": [
        {% for product in products %}
        {
            "@type": "ListItem",
            "position": {{ loop.index }},
            "item": {
                "@type": "Product",
                "name": "{{ product.name }}",
                "image": "{{ product.image_url }}",
                "url": "https://geek.bidu.guru/goto/{{ product.affiliate_redirect_slug }}",
                "offers": {
                    "@type": "Offer",
                    "price": "{{ product.price }}",
                    "priceCurrency": "BRL"
                }
            }
        }{% if not loop.last %},{% endif %}
        {% endfor %}
    ]
}
</script>
{% endmacro %}
```

### 2.2.4-2.2.6 Demais Schemas

Consultar `agents/seo-specialist.md` para:
- Schema Organization
- Schema BreadcrumbList
- Template reutilizavel seo_meta.html

---

## 2.3 Open Graph & Social

**Agente Principal**: SEO Specialist + Frontend Developer
**Referencia**: `agents/seo-specialist.md`, `agents/frontend-developer.md`

### 2.3.1 Meta Tags Open Graph

**Arquivo**: `src/app/templates/components/social_meta.html`

```html
{% macro render_social_meta(page) %}
<!-- Open Graph / Facebook -->
<meta property="og:type" content="{{ page.og_type or 'article' }}">
<meta property="og:url" content="{{ page.canonical_url }}">
<meta property="og:title" content="{{ page.og_title or page.title }}">
<meta property="og:description" content="{{ page.og_description or page.meta_description }}">
<meta property="og:image" content="{{ page.og_image or '/static/images/og-default.jpg' }}">
<meta property="og:site_name" content="geek.bidu.guru">
<meta property="og:locale" content="pt_BR">

<!-- Twitter -->
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:site" content="@geekbiduguru">
<meta name="twitter:title" content="{{ page.og_title or page.title }}">
<meta name="twitter:description" content="{{ page.og_description or page.meta_description }}">
<meta name="twitter:image" content="{{ page.og_image or '/static/images/og-default.jpg' }}">

<!-- Pinterest -->
<meta name="pinterest-rich-pin" content="true">
{% endmacro %}
```

### 2.3.4 Botoes de Share

**Arquivo**: `src/app/templates/components/social_share.html`

```html
{% macro render_share_buttons(url, title) %}
<div class="social-share" role="group" aria-label="Compartilhar">
    <!-- WhatsApp -->
    <a href="https://wa.me/?text={{ title | urlencode }}%20{{ url | urlencode }}"
       class="share-btn share-whatsapp"
       target="_blank"
       rel="noopener"
       aria-label="Compartilhar no WhatsApp">
        <svg><!-- WhatsApp icon --></svg>
        <span>WhatsApp</span>
    </a>

    <!-- Telegram -->
    <a href="https://t.me/share/url?url={{ url | urlencode }}&text={{ title | urlencode }}"
       class="share-btn share-telegram"
       target="_blank"
       rel="noopener"
       aria-label="Compartilhar no Telegram">
        <svg><!-- Telegram icon --></svg>
        <span>Telegram</span>
    </a>

    <!-- Twitter/X -->
    <a href="https://twitter.com/intent/tweet?url={{ url | urlencode }}&text={{ title | urlencode }}"
       class="share-btn share-twitter"
       target="_blank"
       rel="noopener"
       aria-label="Compartilhar no X">
        <svg><!-- X icon --></svg>
        <span>X</span>
    </a>

    <!-- Copiar Link -->
    <button class="share-btn share-copy"
            data-url="{{ url }}"
            aria-label="Copiar link">
        <svg><!-- Copy icon --></svg>
        <span>Copiar</span>
    </button>
</div>
{% endmacro %}
```

---

## 2.4 n8n - Configuracao Base

**Agente Principal**: Automation Engineer + DevOps Engineer
**Referencia**: `agents/automation-engineer.md`, `agents/devops-engineer.md`

### 2.4.1 Adicionar n8n ao Docker Compose

**Atualizar**: `docker/docker-compose.yml`

```yaml
  n8n:
    image: n8nio/n8n:latest
    container_name: geek_n8n
    environment:
      - N8N_BASIC_AUTH_ACTIVE=true
      - N8N_BASIC_AUTH_USER=${N8N_USER:-admin}
      - N8N_BASIC_AUTH_PASSWORD=${N8N_PASSWORD:-changeme}
      - N8N_HOST=localhost
      - N8N_PORT=5678
      - N8N_PROTOCOL=http
      - WEBHOOK_URL=http://localhost:5678/
      - GENERIC_TIMEZONE=America/Sao_Paulo
      - DB_TYPE=postgresdb
      - DB_POSTGRESDB_HOST=db
      - DB_POSTGRESDB_PORT=5432
      - DB_POSTGRESDB_DATABASE=${DB_NAME:-geek_bidu}
      - DB_POSTGRESDB_USER=${DB_USER:-geek}
      - DB_POSTGRESDB_PASSWORD=${DB_PASSWORD:-geek_secret}
    volumes:
      - n8n_data:/home/node/.n8n
    ports:
      - "5678:5678"
    depends_on:
      - db
    restart: unless-stopped

volumes:
  n8n_data:
```

### 2.4.2-2.4.4 Configuracao de Credenciais

**Configurar no n8n**:
1. **Credencial HTTP Header Auth** para API interna:
   - Header: `Authorization`
   - Value: `Bearer {JWT_TOKEN_AUTOMATION}`

2. **Credencial OpenAI**:
   - API Key: `{OPENAI_API_KEY}`

3. **Credenciais de Afiliados**:
   - Amazon Product Advertising API
   - Mercado Livre API
   - Shopee API

---

## 2.5 n8n - Workflow A (Post Diario)

**Agente Principal**: Automation Engineer
**Referencia**: `agents/automation-engineer.md`

### Especificacao do Flow A

**Nome**: `flow-a-daily-post`
**Trigger**: Cron (diariamente as 8h BRT)
**Objetivo**: Criar automaticamente 1 post de produto unico por dia

### Estrutura do Workflow

```
[Cron Trigger: 8h BRT]
    |
    v
[HTTP Request: GET /api/v1/products/random]
    |
    v
[IF: Produto encontrado?]
    |-- Sim --> [OpenAI: Gerar conteudo]
    |               |
    |               v
    |           [HTTP Request: POST /api/v1/posts]
    |               |
    |               v
    |           [IF: Post criado?]
    |               |-- Sim --> [Telegram: Notificar sucesso]
    |               |-- Nao --> [Telegram: Notificar erro]
    |
    |-- Nao --> [Telegram: Notificar "sem produtos"]
```

### Nodes do Workflow

**1. Cron Trigger**
```json
{
    "parameters": {
        "rule": {
            "interval": [{"field": "cronExpression", "expression": "0 8 * * *"}]
        }
    },
    "name": "Cron: 8h BRT",
    "type": "n8n-nodes-base.cron"
}
```

**2. HTTP Request - Buscar Produto**
```json
{
    "parameters": {
        "method": "GET",
        "url": "http://app:8000/api/v1/products/random",
        "authentication": "genericCredentialType",
        "genericAuthType": "httpHeaderAuth"
    },
    "name": "Buscar Produto Aleatorio"
}
```

**3. OpenAI - Gerar Conteudo**
```json
{
    "parameters": {
        "model": "gpt-4",
        "messages": {
            "values": [
                {
                    "role": "system",
                    "content": "Voce e um redator especializado em presentes geek..."
                },
                {
                    "role": "user",
                    "content": "Crie um post sobre o produto: {{ $json.name }}..."
                }
            ]
        }
    },
    "name": "Gerar Conteudo com IA"
}
```

**4. HTTP Request - Criar Post**
```json
{
    "parameters": {
        "method": "POST",
        "url": "http://app:8000/api/v1/posts",
        "body": {
            "title": "={{ $json.generated_title }}",
            "content": "={{ $json.generated_content }}",
            "post_type": "single_product",
            "status": "published"
        }
    },
    "name": "Criar Post via API"
}
```

**5. Telegram - Notificar**
```json
{
    "parameters": {
        "chatId": "={{ $env.TELEGRAM_CHAT_ID }}",
        "text": "Post criado: {{ $json.title }}\nURL: https://geek.bidu.guru/post/{{ $json.slug }}"
    },
    "name": "Notificar Telegram"
}
```

### Arquivo de Exportacao

**Salvar em**: `n8n/workflows/flow-a-daily-post.json`

---

## 2.6 n8n - Workflow B (Listicle Semanal)

**Agente Principal**: Automation Engineer
**Referencia**: `agents/automation-engineer.md`

### Especificacao do Flow B

**Nome**: `flow-b-weekly-listicle`
**Trigger**: Cron (segundas-feiras as 10h BRT)
**Objetivo**: Criar 1 listicle "Top 10" por semana

### Estrutura do Workflow

```
[Cron Trigger: Segunda 10h]
    |
    v
[HTTP Request: GET /api/v1/products?limit=10&category=random]
    |
    v
[OpenAI: Gerar listicle]
    |
    v
[HTTP Request: POST /api/v1/posts]
    |
    v
[Telegram: Notificar]
```

---

## 2.7 n8n - Workflow C (Atualizacao de Precos)

**Agente Principal**: Automation Engineer
**Referencia**: `agents/automation-engineer.md`

### Especificacao do Flow C

**Nome**: `flow-c-price-update`
**Trigger**: Cron (4x ao dia: 6h, 12h, 18h, 00h)
**Objetivo**: Manter precos atualizados de todos os produtos

### Estrutura do Workflow

```
[Cron Trigger: 4x/dia]
    |
    v
[HTTP Request: GET /api/v1/products?needs_update=true]
    |
    v
[Split In Batches: 10 produtos por vez]
    |
    v
[Switch: Por plataforma]
    |-- Amazon --> [Amazon API: Buscar preco]
    |-- ML --> [Mercado Livre API: Buscar preco]
    |-- Shopee --> [Shopee API: Buscar preco]
    |
    v
[Merge]
    |
    v
[HTTP Request: PATCH /api/v1/products/bulk-update]
    |
    v
[IF: Produto indisponivel?]
    |-- Sim --> [Telegram: Alertar admin]
    |-- Nao --> [No Operation]
```

### Integracao com APIs de Afiliados

**Amazon Product Advertising API**:
```javascript
// Node: Buscar na Amazon
const params = {
    PartnerTag: process.env.AMAZON_AFFILIATE_TAG,
    PartnerType: 'Associates',
    Marketplace: 'www.amazon.com.br',
    ItemIds: items.map(i => i.external_id),
    Resources: ['Offers.Listings.Price', 'Offers.Listings.Availability']
};
```

**Mercado Livre API**:
```javascript
// Node: Buscar no ML
const url = `https://api.mercadolibre.com/items/${item.external_id}`;
// Retorna: price, available_quantity, status
```

---

## 2.8 Google Analytics 4

**Agente Principal**: Data Analyst
**Referencia**: `agents/data-analyst.md`

### 2.8.1-2.8.2 Configuracao Base GA4

**Arquivo**: `src/app/templates/components/analytics.html`

```html
{% macro render_ga4(measurement_id) %}
<!-- Google Analytics 4 -->
<script async src="https://www.googletagmanager.com/gtag/js?id={{ measurement_id }}"></script>
<script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){dataLayer.push(arguments);}
    gtag('js', new Date());
    gtag('config', '{{ measurement_id }}', {
        'page_title': document.title,
        'page_location': window.location.href,
        'page_path': window.location.pathname
    });
</script>
{% endmacro %}
```

### 2.8.3 Eventos Customizados

**Arquivo**: `src/app/static/js/analytics.js`

```javascript
/**
 * Analytics helpers para GA4
 */
const Analytics = {
    /**
     * Rastreia clique em link de afiliado
     */
    trackAffiliateClick: function(productId, productName, platform, price, postSlug) {
        gtag('event', 'affiliate_click', {
            product_id: productId,
            product_name: productName,
            platform: platform,
            price: price,
            post_slug: postSlug
        });
    },

    /**
     * Rastreia compartilhamento
     */
    trackShare: function(method, contentType, itemId) {
        gtag('event', 'share', {
            method: method,
            content_type: contentType,
            item_id: itemId
        });
    },

    /**
     * Rastreia inscricao em newsletter
     */
    trackNewsletterSignup: function(location) {
        gtag('event', 'sign_up', {
            method: 'newsletter',
            location: location
        });
    },

    /**
     * Rastreia scroll depth
     */
    trackScrollDepth: function(percent) {
        gtag('event', 'scroll', {
            percent_scrolled: percent,
            page_path: window.location.pathname
        });
    }
};

// Auto-track affiliate clicks
document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('a[href^="/goto/"]').forEach(function(link) {
        link.addEventListener('click', function(e) {
            const data = this.dataset;
            Analytics.trackAffiliateClick(
                data.productId,
                data.productName,
                data.platform,
                data.price,
                data.postSlug
            );
        });
    });
});

// Auto-track scroll depth
(function() {
    let scrollMarks = [25, 50, 75, 100];
    let scrolled = [];

    window.addEventListener('scroll', function() {
        const scrollTop = window.scrollY;
        const docHeight = document.documentElement.scrollHeight - window.innerHeight;
        const scrollPercent = Math.round((scrollTop / docHeight) * 100);

        scrollMarks.forEach(function(mark) {
            if (scrollPercent >= mark && !scrolled.includes(mark)) {
                scrolled.push(mark);
                Analytics.trackScrollDepth(mark);
            }
        });
    });
})();
```

### 2.8.4 Google Search Console

**Acoes**:
1. Verificar propriedade via DNS ou meta tag
2. Submeter sitemap.xml
3. Solicitar indexacao das paginas principais
4. Configurar alertas de erros

---

## Criterios de Conclusao da Fase 2

- [ ] sitemap.xml gera corretamente com todos os posts
- [ ] robots.txt acessivel e correto
- [ ] Schema.org implementado (testar com Google Rich Results Test)
- [ ] Open Graph funciona (testar com Facebook Debugger)
- [ ] Twitter Cards funciona (testar com Twitter Card Validator)
- [ ] n8n acessivel em `http://localhost:5678`
- [ ] Flow A cria posts automaticamente
- [ ] Flow B cria listicles semanalmente
- [ ] Flow C atualiza precos (testar manualmente)
- [ ] GA4 rastreia pageviews
- [ ] Eventos customizados funcionam (affiliate_click, share)
- [ ] Search Console verificado e sitemap submetido

---

## Proxima Fase

Apos concluir a Fase 2, avance para:
- **Fase 3**: IA & Internacionalizacao (`04-phase-3-ai-i18n.md`)

---

**Versao**: 1.0
**Data**: 2025-12-10
**Projeto**: geek.bidu.guru
