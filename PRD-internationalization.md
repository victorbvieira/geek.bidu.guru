# PRD - Internacionalização (i18n) - geek.bidu.guru

**Documento**: Especificação de Internacionalização
**Projeto**: geek.bidu.guru
**Versão**: 1.0
**Data**: 2025-12-10
**Status**: Planejamento

---

## 📋 Índice

1. [Visão Geral](#visão-geral)
2. [Objetivos de Internacionalização](#objetivos-de-internacionalização)
3. [Mercados-Alvo](#mercados-alvo)
4. [Arquitetura de i18n](#arquitetura-de-i18n)
5. [Estrutura de URLs](#estrutura-de-urls)
6. [Banco de Dados](#banco-de-dados)
7. [Estratégia de Tradução](#estratégia-de-tradução)
8. [Localização de Preços e Moedas](#localização-de-preços-e-moedas)
9. [Programas de Afiliados por País](#programas-de-afiliados-por-país)
10. [SEO Internacional](#seo-internacional)
11. [Detecção de Locale](#detecção-de-locale)
12. [Implementação Técnica](#implementação-técnica)
13. [Roadmap de Expansão](#roadmap-de-expansão)

---

## 🌍 Visão Geral

O geek.bidu.guru será construído desde o início com **suporte completo a internacionalização**, permitindo expansão gradual para múltiplos mercados de língua portuguesa e espanhola, com possibilidade futura de expansão para inglês.

### Princípios de i18n

1. **Separação de Conteúdo e Código**: Todo texto visível deve ser externalizável
2. **Localização Completa**: Não apenas tradução, mas adaptação cultural
3. **SEO-First**: Cada locale terá otimização SEO específica
4. **Programas de Afiliados Locais**: Usar plataformas de afiliados de cada país
5. **Performance**: Cache por locale, CDN geográfico

---

## 🎯 Objetivos de Internacionalização

### Objetivo Primário
Permitir que geek.bidu.guru opere em múltiplos países com conteúdo localizado, maximizando receita de afiliados em cada mercado.

### Objetivos Secundários
- **Escala de Tráfego**: Expandir para 5+ países em 24 meses
- **Receita Diversificada**: Reduzir dependência de um único mercado
- **Vantagem Competitiva**: Ser o primeiro blog geek multi-país da América Latina
- **Reuso de Conteúdo**: Traduzir/adaptar conteúdo existente automaticamente

---

## 🗺️ Mercados-Alvo

### Fase 1: Fundação (Meses 1-6)
**Mercado Primário: Brasil**
- Locale: `pt-BR`
- Moeda: BRL (R$)
- Afiliados: Amazon.com.br, Mercado Livre Brasil, Shopee Brasil
- Volume estimado: 100% do tráfego inicial

### Fase 2: Expansão Lusófona (Meses 7-12)
**Mercado Secundário: Portugal**
- Locale: `pt-PT`
- Moeda: EUR (€)
- Afiliados: Amazon.es (entrega PT), Fnac Portugal, Worten
- Volume estimado: +20% de tráfego

**Adaptações necessárias**:
- Vocabulário: "celular" → "telemóvel", "caneca" → "caneca" (igual), "entrega" → "entrega"
- Preços: Conversão BRL → EUR + ajuste de custo de vida
- Produtos: Alguns produtos indisponíveis ou com nomes diferentes

### Fase 3: Expansão Hispânica (Meses 13-18)
**Mercados Terciários: América Latina Hispânica**

**México**:
- Locale: `es-MX`
- Moeda: MXN ($)
- Afiliados: Amazon.com.mx, Mercado Libre México
- Volume estimado: +30% de tráfego

**Argentina**:
- Locale: `es-AR`
- Moeda: ARS ($)
- Afiliados: Mercado Libre Argentina
- Volume estimado: +15% de tráfego

**Colômbia**:
- Locale: `es-CO`
- Moeda: COP ($)
- Afiliados: Amazon.com, Mercado Libre Colombia
- Volume estimado: +10% de tráfego

### Fase 4: Expansão Global (Meses 19-24)
**Mercado Quaternário: Espanha e EUA**

**Espanha**:
- Locale: `es-ES`
- Moeda: EUR (€)
- Afiliados: Amazon.es, El Corte Inglés, MediaMarkt
- Volume estimado: +20% de tráfego

**Estados Unidos (Hispânicos)**:
- Locale: `es-US` (espanhol para hispânicos nos EUA)
- Moeda: USD ($)
- Afiliados: Amazon.com
- Volume estimado: +25% de tráfego

**Estados Unidos (Inglês)**:
- Locale: `en-US`
- Moeda: USD ($)
- Afiliados: Amazon.com, Best Buy, Target
- Volume estimado: +50% de tráfego

---

## 🏗️ Arquitetura de i18n

### Stack Tecnológico

**Backend (Python/FastAPI)**:
- **Biblioteca**: `Babel` (i18n/l10n para Python)
- **Formato de tradução**: `.po` / `.pot` (gettext)
- **Alternativa**: JSON estruturado (mais fácil para automação com IA)

**Templates (Jinja2)**:
```python
# Usando Babel extension
{% trans %}Bem-vindo ao geek.bidu.guru!{% endtrans %}

# Com variáveis
{% trans name=product.name %}Compre {{ name }} agora{% endtrans %}

# Pluralização
{% trans count=products|length %}
  {{ count }} produto encontrado
{% pluralize %}
  {{ count }} produtos encontrados
{% endtrans %}
```

**Alternativa (JSON + custom filter)**:
```python
# Jinja2 template
{{ _('welcome_message') }}
{{ _('buy_now', name=product.name) }}

# Backend carrega JSON por locale
# translations/pt-BR.json
{
  "welcome_message": "Bem-vindo ao geek.bidu.guru!",
  "buy_now": "Compre {name} agora"
}
```

### Estrutura de Arquivos de Tradução

```
geek.bidu.guru/
├── translations/
│   ├── pt-BR/
│   │   ├── LC_MESSAGES/
│   │   │   ├── messages.po
│   │   │   └── messages.mo
│   │   └── metadata.json
│   ├── pt-PT/
│   │   └── ...
│   ├── es-MX/
│   │   └── ...
│   ├── es-AR/
│   │   └── ...
│   └── en-US/
│       └── ...
```

**metadata.json** (por locale):
```json
{
  "locale": "pt-BR",
  "language": "Português (Brasil)",
  "currency": "BRL",
  "currency_symbol": "R$",
  "date_format": "DD/MM/YYYY",
  "number_format": {
    "decimal_separator": ",",
    "thousands_separator": "."
  },
  "affiliate_platforms": [
    "amazon_br",
    "mercado_livre_br",
    "shopee_br"
  ],
  "timezone": "America/Sao_Paulo",
  "is_active": true
}
```

---

## 🔗 Estrutura de URLs

### Estratégia: Subdiretórios por Locale (Recomendado)

**Vantagens**:
- Melhor para SEO (Google recomenda)
- Fácil de gerenciar
- Permite separar por país no Google Search Console
- Não requer configuração de DNS

**Estrutura**:
```
https://geek.bidu.guru/             → Redireciona para locale padrão
https://geek.bidu.guru/pt-br/       → Brasil (padrão)
https://geek.bidu.guru/pt-pt/       → Portugal
https://geek.bidu.guru/es-mx/       → México
https://geek.bidu.guru/es-ar/       → Argentina
https://geek.bidu.guru/es-es/       → Espanha
https://geek.bidu.guru/en-us/       → Estados Unidos
```

### Exemplo de URLs Completas

**Post de Produto Único**:
```
https://geek.bidu.guru/pt-br/caneca-termica-baby-yoda
https://geek.bidu.guru/pt-pt/caneca-termica-baby-yoda
https://geek.bidu.guru/es-mx/taza-termica-baby-yoda
https://geek.bidu.guru/en-us/baby-yoda-thermal-mug
```

**Listicle**:
```
https://geek.bidu.guru/pt-br/top-10-presentes-star-wars
https://geek.bidu.guru/es-mx/top-10-regalos-star-wars
https://geek.bidu.guru/en-us/top-10-star-wars-gifts
```

**Sistema de Redirecionamento /goto/**:
```
https://geek.bidu.guru/pt-br/goto/caneca-baby-yoda-amazon
  ↓ redireciona para
https://amazon.com.br/...?tag=geekbidu-20

https://geek.bidu.guru/es-mx/goto/taza-baby-yoda-amazon
  ↓ redireciona para
https://amazon.com.mx/...?tag=geekbidumx-20
```

### Alternativas (Não Recomendadas)

**Subdomínios**:
```
https://br.geek.bidu.guru/
https://pt.geek.bidu.guru/
https://mx.geek.bidu.guru/
```
❌ **Desvantagens**: Requer certificados SSL separados, configuração de DNS complexa, SEO fragmentado

**Parâmetros de Query**:
```
https://geek.bidu.guru/post?lang=pt-br
```
❌ **Desvantagens**: Péssimo para SEO, confuso para usuários, dificulta cache

**Domínios por País (ccTLD)**:
```
https://geek.bidu.guru/ (Brasil)
https://geek.bidu.pt/ (Portugal)
https://geek.bidu.mx/ (México)
```
❌ **Desvantagens**: Custo alto (domínios múltiplos), SEO fragmentado, difícil de gerenciar

---

## 🗄️ Banco de Dados

### Estratégia: Tabelas de Tradução Separadas

**Modelo**: Posts e Produtos têm conteúdo base + traduções em tabelas relacionadas

#### Schema Principal (Conteúdo Invariante)

```sql
-- Tabela de locales suportados
CREATE TABLE locales (
    code VARCHAR(5) PRIMARY KEY,  -- 'pt-BR', 'es-MX', 'en-US'
    language VARCHAR(50) NOT NULL,  -- 'Português (Brasil)'
    currency VARCHAR(3) NOT NULL,  -- 'BRL', 'EUR', 'USD'
    currency_symbol VARCHAR(5) NOT NULL,  -- 'R$', '€', '$'
    is_active BOOLEAN DEFAULT true,
    is_default BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Dados iniciais
INSERT INTO locales (code, language, currency, currency_symbol, is_active, is_default) VALUES
('pt-BR', 'Português (Brasil)', 'BRL', 'R$', true, true),
('pt-PT', 'Português (Portugal)', 'EUR', '€', false, false),
('es-MX', 'Español (México)', 'MXN', '$', false, false),
('es-AR', 'Español (Argentina)', 'ARS', '$', false, false),
('es-ES', 'Español (España)', 'EUR', '€', false, false),
('en-US', 'English (United States)', 'USD', '$', false, false);
```

#### Schema de Posts (Multilíngue)

```sql
-- Tabela principal de posts (dados invariantes)
CREATE TABLE posts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    type post_type NOT NULL,  -- 'product_single', 'listicle', 'guide'
    status post_status DEFAULT 'draft',

    -- Slug base (sem locale)
    slug_base VARCHAR(200) NOT NULL,  -- 'caneca-baby-yoda'

    -- Dados compartilhados (não dependem de idioma)
    featured_image_url TEXT,
    author_id UUID REFERENCES users(id),
    published_at TIMESTAMP,

    -- Metadados
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(slug_base)
);

CREATE INDEX idx_posts_slug_base ON posts(slug_base);
CREATE INDEX idx_posts_status ON posts(status);

-- Tabela de traduções de posts
CREATE TABLE post_translations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    post_id UUID NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
    locale VARCHAR(5) NOT NULL REFERENCES locales(code),

    -- Slug completo com locale
    slug VARCHAR(250) NOT NULL,  -- 'pt-br/caneca-baby-yoda', 'es-mx/taza-baby-yoda'

    -- Conteúdo traduzido
    title VARCHAR(200) NOT NULL,
    subtitle TEXT,
    intro TEXT,
    body TEXT NOT NULL,
    conclusion TEXT,

    -- SEO traduzido
    seo_title VARCHAR(60),
    seo_description VARCHAR(160),
    seo_keywords TEXT,

    -- Schema.org traduzido
    schema_json JSONB,

    -- Status da tradução
    translation_status VARCHAR(20) DEFAULT 'pending',  -- 'pending', 'auto', 'reviewed', 'published'
    translated_by VARCHAR(50),  -- 'openai-gpt4', 'human', 'deepl'
    translated_at TIMESTAMP,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(post_id, locale),
    UNIQUE(slug)
);

CREATE INDEX idx_post_translations_locale ON post_translations(locale);
CREATE INDEX idx_post_translations_slug ON post_translations(slug);
CREATE INDEX idx_post_translations_status ON post_translations(translation_status);
```

#### Schema de Produtos (Multilíngue)

```sql
-- Tabela principal de produtos (dados invariantes)
CREATE TABLE products (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Identificadores externos (compartilhados globalmente)
    amazon_asin VARCHAR(10),  -- Mesmo ASIN pode existir em múltiplas Amazons
    ean VARCHAR(13),
    upc VARCHAR(12),

    -- Categoria (compartilhada)
    category VARCHAR(100),

    -- Imagens (compartilhadas)
    image_url TEXT,

    -- Metadados
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de traduções de produtos
CREATE TABLE product_translations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id UUID NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    locale VARCHAR(5) NOT NULL REFERENCES locales(code),

    -- Nome traduzido
    name VARCHAR(200) NOT NULL,
    description TEXT,

    -- Status da tradução
    translation_status VARCHAR(20) DEFAULT 'pending',
    translated_by VARCHAR(50),
    translated_at TIMESTAMP,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(product_id, locale)
);

CREATE INDEX idx_product_translations_locale ON product_translations(locale);

-- Tabela de preços por plataforma e locale
CREATE TABLE product_prices (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id UUID NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    locale VARCHAR(5) NOT NULL REFERENCES locales(code),
    platform VARCHAR(50) NOT NULL,  -- 'amazon', 'mercado_livre', 'shopee'

    -- Preço e moeda
    price DECIMAL(10, 2) NOT NULL,
    currency VARCHAR(3) NOT NULL,  -- 'BRL', 'EUR', 'USD'

    -- Disponibilidade
    availability VARCHAR(50),  -- 'available', 'out_of_stock', 'pre_order'

    -- URL de afiliado específica do país
    affiliate_url_raw TEXT NOT NULL,
    affiliate_redirect_slug VARCHAR(200) UNIQUE NOT NULL,

    -- Comissão (pode variar por país)
    commission_percentage DECIMAL(5, 2),

    -- Rating e reviews (podem variar por país)
    rating DECIMAL(3, 2),
    review_count INTEGER,

    -- Atualização
    last_checked TIMESTAMP,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(product_id, locale, platform)
);

CREATE INDEX idx_product_prices_locale ON product_prices(locale);
CREATE INDEX idx_product_prices_platform ON product_prices(platform);
CREATE INDEX idx_product_prices_slug ON product_prices(affiliate_redirect_slug);
```

#### Schema de Affiliate Clicks (Multilíngue)

```sql
-- Tabela de cliques (já internacionalizada)
CREATE TABLE affiliate_clicks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id UUID REFERENCES products(id),
    post_id UUID REFERENCES posts(id),
    locale VARCHAR(5) REFERENCES locales(code),  -- Locale do usuário

    platform VARCHAR(50) NOT NULL,
    ip_address VARCHAR(45),
    user_agent TEXT,
    referer TEXT,

    -- Geolocalização
    country VARCHAR(2),  -- 'BR', 'PT', 'MX'
    region VARCHAR(100),
    city VARCHAR(100),

    clicked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_affiliate_clicks_locale ON affiliate_clicks(locale);
CREATE INDEX idx_affiliate_clicks_country ON affiliate_clicks(country);
CREATE INDEX idx_affiliate_clicks_date ON affiliate_clicks(clicked_at);
```

---

## 🔄 Estratégia de Tradução

### Fluxo de Tradução de Conteúdo

```
┌─────────────────────────────────────────────────────┐
│ 1. Post criado em pt-BR (locale primário)          │
└──────────────┬──────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────┐
│ 2. Trigger: Novo post publicado                    │
│    → n8n Workflow "Traduzir Post"                  │
└──────────────┬──────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────┐
│ 3. Para cada locale ativo (pt-PT, es-MX, etc):     │
│    a) LLM traduz: title, subtitle, body, etc.      │
│    b) Adapta culturalmente:                         │
│       - Moedas (R$ → € → $)                         │
│       - Medidas (metros → pés/polegadas se en-US)   │
│       - Expressões idiomáticas                      │
│    c) SEO localizado:                               │
│       - Keywords research por país                  │
│       - Meta tags traduzidas                        │
└──────────────┬──────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────┐
│ 4. Salva em post_translations com:                 │
│    - translation_status = 'auto'                    │
│    - translated_by = 'openai-gpt4'                  │
└──────────────┬──────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────┐
│ 5. (Opcional) Revisão humana:                      │
│    - Marcar como 'reviewed'                         │
│    - Publicar                                       │
└─────────────────────────────────────────────────────┘
```

### Prompt de Tradução para LLM

```python
# Exemplo de prompt para tradução automática
TRANSLATION_PROMPT = """
Você é um tradutor especializado em conteúdo geek/nerd para e-commerce.

Traduza o seguinte post de blog de {source_locale} para {target_locale}:

**Título**: {title}
**Subtítulo**: {subtitle}
**Corpo**: {body}

**Instruções**:
1. Mantenha o tom de voz: {tone} (casual, entusiasta, técnico)
2. Adapte culturalmente:
   - Moedas: {source_currency} → {target_currency}
   - Expressões: use expressões naturais de {target_locale}
   - Referências: adapte referências culturais se necessário
3. SEO:
   - Título: 50-60 caracteres, incluindo keyword principal
   - Meta description: 150-160 caracteres, persuasiva
4. Mantenha tags HTML e estrutura Markdown
5. NÃO traduza:
   - Nomes de produtos (ex: "Baby Yoda" permanece "Baby Yoda")
   - Nomes de marcas (ex: "Funko Pop" permanece "Funko Pop")
   - Nomes próprios
   - Códigos (ASIN, SKU, etc.)

Retorne JSON com:
{{
  "title": "...",
  "subtitle": "...",
  "body": "...",
  "seo_title": "...",
  "seo_description": "...",
  "seo_keywords": ["keyword1", "keyword2", ...]
}}
"""
```

### Workflow n8n de Tradução

```
┌──────────────┐
│ Webhook:     │
│ Post         │
│ Published    │
└──────┬───────┘
       │
       ▼
┌──────────────────────────┐
│ Get Post Data            │
│ (pt-BR original)         │
└──────┬───────────────────┘
       │
       ▼
┌──────────────────────────┐
│ Get Active Locales       │
│ (pt-PT, es-MX, en-US...) │
└──────┬───────────────────┘
       │
       ▼
┌──────────────────────────┐
│ Loop: For Each Locale    │
└──────┬───────────────────┘
       │
       ▼
┌──────────────────────────┐
│ OpenAI: Translate        │
│ (GPT-4 with prompt)      │
└──────┬───────────────────┘
       │
       ▼
┌──────────────────────────┐
│ Save Translation         │
│ (post_translations)      │
└──────┬───────────────────┘
       │
       ▼
┌──────────────────────────┐
│ Trigger: Product         │
│ Mapping Workflow         │
│ (map products to locale) │
└──────────────────────────┘
```

---

## 💰 Localização de Preços e Moedas

### Conversão de Moedas

**Estratégia**: Não usar conversão direta, mas buscar preço real no marketplace local

**Por quê?**:
- Conversão cambial varia diariamente
- Preços não são proporcionais (R$ 100 no BR ≠ $20 nos EUA)
- Impostos, frete, disponibilidade variam por país

**Implementação**:
```python
# ❌ ERRADO: Conversão direta
price_usd = price_brl / exchange_rate  # Não reflete realidade

# ✅ CORRETO: Buscar preço na Amazon.com, Amazon.com.br, Amazon.com.mx
amazon_br_price = get_amazon_price(asin, marketplace='BR')  # R$ 89,90
amazon_mx_price = get_amazon_price(asin, marketplace='MX')  # $ 450 MXN
amazon_us_price = get_amazon_price(asin, marketplace='US')  # $ 19.99 USD
```

### Formatação de Preços por Locale

```python
# Backend: Função de formatação
def format_price(amount: Decimal, locale: str) -> str:
    locale_config = {
        'pt-BR': {'symbol': 'R$', 'decimal': ',', 'thousands': '.', 'format': '{symbol} {amount}'},
        'pt-PT': {'symbol': '€', 'decimal': ',', 'thousands': '.', 'format': '{amount} {symbol}'},
        'es-MX': {'symbol': '$', 'decimal': '.', 'thousands': ',', 'format': '${amount}'},
        'es-AR': {'symbol': '$', 'decimal': ',', 'thousands': '.', 'format': '${amount}'},
        'es-ES': {'symbol': '€', 'decimal': ',', 'thousands': '.', 'format': '{amount} {symbol}'},
        'en-US': {'symbol': '$', 'decimal': '.', 'thousands': ',', 'format': '${amount}'},
    }

    config = locale_config.get(locale, locale_config['pt-BR'])

    # Formatar número
    amount_str = f"{amount:,.2f}"
    # Substituir separadores
    amount_str = amount_str.replace(',', 'TEMP').replace('.', config['decimal']).replace('TEMP', config['thousands'])

    return config['format'].format(symbol=config['symbol'], amount=amount_str)

# Exemplos
format_price(Decimal('89.90'), 'pt-BR')  # "R$ 89,90"
format_price(Decimal('89.90'), 'pt-PT')  # "89,90 €"
format_price(Decimal('450.00'), 'es-MX')  # "$450.00"
format_price(Decimal('19.99'), 'en-US')  # "$19.99"
```

### Exibição de Múltiplos Preços

**Cenário**: Produto disponível em múltiplos marketplaces

```html
<!-- Template: Comparador de Preços Internacional -->
<div class="price-comparison">
  <h3>{{ _('compare_prices') }}</h3>

  {% for price in product.prices %}
  <div class="price-option" data-locale="{{ price.locale }}">
    <div class="marketplace">
      <img src="/static/icons/{{ price.platform }}.svg" alt="{{ price.platform }}">
      <span>{{ price.platform_name }}</span>
    </div>
    <div class="price">
      <span class="amount">{{ format_price(price.price, price.locale) }}</span>
      <span class="currency">{{ price.currency }}</span>
    </div>
    <a href="/{{ price.locale }}/goto/{{ price.affiliate_redirect_slug }}"
       class="btn-buy" rel="sponsored">
      {{ _('buy_now') }}
    </a>
  </div>
  {% endfor %}
</div>
```

---

## 🤝 Programas de Afiliados por País

### Mapeamento de Plataformas

| País | Locale | Amazon | Mercado Livre | Shopee | Outros |
|------|--------|--------|---------------|--------|--------|
| **Brasil** | pt-BR | Amazon.com.br | ML Brasil | Shopee BR | Americanas, Magalu |
| **Portugal** | pt-PT | Amazon.es (PT) | - | - | Fnac, Worten |
| **México** | es-MX | Amazon.com.mx | ML México | Shopee MX | Liverpool |
| **Argentina** | es-AR | - | ML Argentina | - | - |
| **Colômbia** | es-CO | Amazon.com (CO) | ML Colombia | - | - |
| **Espanha** | es-ES | Amazon.es | - | - | El Corte Inglés |
| **EUA** | en-US | Amazon.com | - | - | Best Buy, Target |

### Configuração de Affiliate Tags por Marketplace

```python
# Tabela: affiliate_programs
CREATE TABLE affiliate_programs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    locale VARCHAR(5) REFERENCES locales(code),
    platform VARCHAR(50) NOT NULL,  -- 'amazon', 'mercado_livre', etc.

    -- Credenciais
    affiliate_id VARCHAR(100) NOT NULL,  -- Tag de afiliado
    api_key VARCHAR(255),
    api_secret VARCHAR(255),

    -- URLs
    base_url TEXT NOT NULL,  -- https://amazon.com.br
    api_endpoint TEXT,

    -- Configurações
    cookie_duration_hours INTEGER,  -- 24 para Amazon, 240 para ML
    commission_rates JSONB,  -- Por categoria

    -- Status
    is_active BOOLEAN DEFAULT true,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(locale, platform)
);

-- Dados iniciais
INSERT INTO affiliate_programs (locale, platform, affiliate_id, base_url, cookie_duration_hours, commission_rates) VALUES
('pt-BR', 'amazon', 'geekbidu-20', 'https://amazon.com.br', 24, '{"electronics": 3, "toys": 5, "books": 8}'),
('pt-BR', 'mercado_livre', 'MLB-GEEKBIDU', 'https://mercadolivre.com.br', 240, '{"default": 5}'),
('pt-BR', 'shopee', 'GEEKBIDUBR', 'https://shopee.com.br', 168, '{"default": 3}'),
('pt-PT', 'amazon', 'geekbidupt-21', 'https://amazon.es', 24, '{"default": 4}'),
('es-MX', 'amazon', 'geekbidumx-20', 'https://amazon.com.mx', 24, '{"default": 4}'),
('es-MX', 'mercado_livre', 'MLM-GEEKBIDU', 'https://mercadolibre.com.mx', 240, '{"default": 6}'),
('en-US', 'amazon', 'geekbidus-20', 'https://amazon.com', 24, '{"default": 4}');
```

### Geração de Links de Afiliados por País

```python
# Backend: Função para gerar link de afiliado
def generate_affiliate_url(
    product_id: UUID,
    locale: str,
    platform: str,
    db: Session
) -> str:
    # Buscar configuração de afiliado
    affiliate_program = db.query(AffiliateProgram).filter(
        AffiliateProgram.locale == locale,
        AffiliateProgram.platform == platform,
        AffiliateProgram.is_active == True
    ).first()

    if not affiliate_program:
        raise ValueError(f"Affiliate program not found for {locale}/{platform}")

    # Buscar preço do produto nesse locale/platform
    product_price = db.query(ProductPrice).filter(
        ProductPrice.product_id == product_id,
        ProductPrice.locale == locale,
        ProductPrice.platform == platform
    ).first()

    if not product_price:
        raise ValueError(f"Product not available in {locale}/{platform}")

    # Construir URL com tag de afiliado
    base_url = product_price.affiliate_url_raw

    # Adicionar tag de afiliado
    if 'amazon' in platform:
        # Amazon format: ?tag=AFFILIATE_TAG
        if '?' in base_url:
            url = f"{base_url}&tag={affiliate_program.affiliate_id}"
        else:
            url = f"{base_url}?tag={affiliate_program.affiliate_id}"
    elif 'mercado_livre' in platform:
        # Mercado Livre format depende do país
        # Geralmente: &meli_aff={AFFILIATE_ID}
        if '?' in base_url:
            url = f"{base_url}&meli_aff={affiliate_program.affiliate_id}"
        else:
            url = f"{base_url}?meli_aff={affiliate_program.affiliate_id}"
    else:
        url = base_url

    # Adicionar UTM parameters
    utm_params = {
        'utm_source': 'geekbiduguru',
        'utm_medium': 'affiliate',
        'utm_campaign': locale,
        'utm_content': product_id
    }

    for key, value in utm_params.items():
        url += f"&{key}={value}"

    return url
```

---

## 🔍 SEO Internacional

### Implementação de Hreflang Tags

**O que é**: Tags HTML que indicam ao Google versões alternativas do conteúdo em outros idiomas.

**Implementação**:
```html
<!-- Template base: head section -->
<head>
  <!-- ... outras meta tags ... -->

  <!-- Hreflang para o próprio locale -->
  <link rel="alternate" hreflang="{{ current_locale }}" href="{{ canonical_url }}" />

  <!-- Hreflang para outros locales -->
  {% for translation in post.translations %}
  <link rel="alternate"
        hreflang="{{ translation.locale }}"
        href="https://geek.bidu.guru/{{ translation.slug }}" />
  {% endfor %}

  <!-- Hreflang x-default (fallback) -->
  <link rel="alternate"
        hreflang="x-default"
        href="https://geek.bidu.guru/pt-br/{{ post.slug_base }}" />
</head>
```

**Exemplo concreto**:
```html
<!-- Post: "Caneca Baby Yoda" -->
<link rel="alternate" hreflang="pt-BR" href="https://geek.bidu.guru/pt-br/caneca-baby-yoda" />
<link rel="alternate" hreflang="pt-PT" href="https://geek.bidu.guru/pt-pt/caneca-baby-yoda" />
<link rel="alternate" hreflang="es-MX" href="https://geek.bidu.guru/es-mx/taza-baby-yoda" />
<link rel="alternate" hreflang="en-US" href="https://geek.bidu.guru/en-us/baby-yoda-mug" />
<link rel="alternate" hreflang="x-default" href="https://geek.bidu.guru/pt-br/caneca-baby-yoda" />
```

### Sitemap Multilingue

```xml
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
        xmlns:xhtml="http://www.w3.org/1999/xhtml">

  <!-- Post em pt-BR -->
  <url>
    <loc>https://geek.bidu.guru/pt-br/caneca-baby-yoda</loc>
    <lastmod>2025-12-10</lastmod>
    <xhtml:link rel="alternate" hreflang="pt-BR" href="https://geek.bidu.guru/pt-br/caneca-baby-yoda" />
    <xhtml:link rel="alternate" hreflang="pt-PT" href="https://geek.bidu.guru/pt-pt/caneca-baby-yoda" />
    <xhtml:link rel="alternate" hreflang="es-MX" href="https://geek.bidu.guru/es-mx/taza-baby-yoda" />
    <xhtml:link rel="alternate" hreflang="en-US" href="https://geek.bidu.guru/en-us/baby-yoda-mug" />
  </url>

  <!-- Post em pt-PT -->
  <url>
    <loc>https://geek.bidu.guru/pt-pt/caneca-baby-yoda</loc>
    <lastmod>2025-12-10</lastmod>
    <xhtml:link rel="alternate" hreflang="pt-BR" href="https://geek.bidu.guru/pt-br/caneca-baby-yoda" />
    <xhtml:link rel="alternate" hreflang="pt-PT" href="https://geek.bidu.guru/pt-pt/caneca-baby-yoda" />
    <xhtml:link rel="alternate" hreflang="es-MX" href="https://geek.bidu.guru/es-mx/taza-baby-yoda" />
    <xhtml:link rel="alternate" hreflang="en-US" href="https://geek.bidu.guru/en-us/baby-yoda-mug" />
  </url>

  <!-- Repetir para cada tradução... -->
</urlset>
```

### Google Search Console - Configuração por Locale

**Estratégia**: Criar "propriedades" separadas no GSC por locale

1. Adicionar domínio como propriedade: `https://geek.bidu.guru/`
2. Usar filtros de URL para segmentar:
   - Filtro 1: URLs que começam com `/pt-br/`
   - Filtro 2: URLs que começam com `/pt-pt/`
   - Filtro 3: URLs que começam com `/es-mx/`
3. Configurar geolocalização:
   - `/pt-br/` → Segmentar Brasil
   - `/pt-pt/` → Segmentar Portugal
   - `/es-mx/` → Segmentar México

### Keywords Research por Locale

**Importante**: Keywords populares variam por país, não apenas por idioma.

**Exemplo: "Presentes Geek"**
| Locale | Keyword Principal | Volume | Dificuldade |
|--------|-------------------|--------|-------------|
| pt-BR | "presentes geek" | 2.400/mês | Média |
| pt-BR | "presente nerd" | 1.800/mês | Média |
| pt-PT | "prendas geek" | 320/mês | Baixa |
| pt-PT | "presentes geek" | 180/mês | Baixa |
| es-MX | "regalos geek" | 1.600/mês | Média |
| es-MX | "regalos frikis" | 800/mês | Baixa |
| en-US | "geek gifts" | 14.800/mês | Alta |
| en-US | "nerd gifts" | 12.100/mês | Alta |

**Implementação no Conteúdo**:
```markdown
<!-- pt-BR -->
# Top 10 Presentes Geek para Namorado em 2025

<!-- pt-PT -->
# Top 10 Prendas Geek para o Namorado em 2025

<!-- es-MX -->
# Top 10 Regalos Geek para tu Novio en 2025

<!-- en-US -->
# Top 10 Geek Gifts for Your Boyfriend in 2025
```

---

## 🌐 Detecção de Locale

### Estratégia Multi-Camada

```
┌─────────────────────────────────────────────────────┐
│ 1. URL explícita (prioridade máxima)               │
│    /pt-br/caneca-baby-yoda → locale = pt-BR        │
└──────────────┬──────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────┐
│ 2. Cookie de preferência do usuário                │
│    Se existe cookie 'user_locale' → usar           │
└──────────────┬──────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────┐
│ 3. Header Accept-Language                          │
│    pt-BR,pt;q=0.9,en-US;q=0.8 → locale = pt-BR     │
└──────────────┬──────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────┐
│ 4. Geolocalização por IP (via CloudFlare)          │
│    IP do Brasil → locale = pt-BR                   │
└──────────────┬──────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────┐
│ 5. Fallback para locale padrão (pt-BR)             │
└─────────────────────────────────────────────────────┘
```

### Implementação no Backend

```python
# FastAPI middleware para detecção de locale
from fastapi import Request
from typing import Optional

def detect_locale(request: Request) -> str:
    # 1. URL explícita
    path = request.url.path
    for locale_code in ['pt-br', 'pt-pt', 'es-mx', 'es-ar', 'es-es', 'en-us']:
        if path.startswith(f'/{locale_code}/'):
            return locale_code.replace('-', '-').upper()  # pt-br → pt-BR

    # 2. Cookie de preferência
    user_locale = request.cookies.get('user_locale')
    if user_locale and is_valid_locale(user_locale):
        return user_locale

    # 3. Header Accept-Language
    accept_language = request.headers.get('accept-language', '')
    preferred_locale = parse_accept_language(accept_language)
    if preferred_locale:
        return preferred_locale

    # 4. Geolocalização por IP (CloudFlare header)
    country = request.headers.get('cf-ipcountry', '')
    locale_by_country = {
        'BR': 'pt-BR',
        'PT': 'pt-PT',
        'MX': 'es-MX',
        'AR': 'es-AR',
        'CO': 'es-CO',
        'ES': 'es-ES',
        'US': 'en-US',
    }
    if country in locale_by_country:
        return locale_by_country[country]

    # 5. Fallback
    return 'pt-BR'

def parse_accept_language(header: str) -> Optional[str]:
    """
    Parseia Accept-Language header
    Exemplo: "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7"
    """
    if not header:
        return None

    # Split por vírgula e ordenar por qualidade (q)
    languages = []
    for lang in header.split(','):
        parts = lang.strip().split(';')
        code = parts[0].strip()
        quality = 1.0
        if len(parts) > 1 and parts[1].startswith('q='):
            try:
                quality = float(parts[1][2:])
            except ValueError:
                pass
        languages.append((code, quality))

    # Ordenar por qualidade (maior primeiro)
    languages.sort(key=lambda x: x[1], reverse=True)

    # Mapear para nossos locales suportados
    locale_map = {
        'pt-BR': 'pt-BR',
        'pt': 'pt-BR',
        'pt-PT': 'pt-PT',
        'es-MX': 'es-MX',
        'es': 'es-MX',  # Fallback para México (maior mercado hispânico)
        'en-US': 'en-US',
        'en': 'en-US',
    }

    for lang_code, _ in languages:
        if lang_code in locale_map:
            return locale_map[lang_code]

    return None
```

### Seletor de Idioma no Frontend

```html
<!-- Header: Seletor de idioma/país -->
<div class="locale-selector">
  <button class="current-locale">
    <img src="/static/flags/{{ current_locale[:2] }}.svg" alt="">
    <span>{{ locale_name }}</span>  <!-- "Português (Brasil)" -->
    <svg class="icon-dropdown">...</svg>
  </button>

  <ul class="locale-dropdown">
    {% for locale in available_locales %}
    <li>
      <a href="/{{ locale.code }}/{{ current_slug }}"
         hreflang="{{ locale.code }}">
        <img src="/static/flags/{{ locale.code[:2] }}.svg" alt="">
        <span>{{ locale.language }}</span>
      </a>
    </li>
    {% endfor %}
  </ul>
</div>
```

**Exemplo visual**:
```
┌─────────────────────────────────────┐
│ 🇧🇷 Português (Brasil)      ▼       │
├─────────────────────────────────────┤
│ 🇧🇷 Português (Brasil)              │
│ 🇵🇹 Português (Portugal)            │
│ 🇲🇽 Español (México)                │
│ 🇦🇷 Español (Argentina)             │
│ 🇪🇸 Español (España)                │
│ 🇺🇸 English (United States)         │
└─────────────────────────────────────┘
```

---

## 💻 Implementação Técnica

### FastAPI Routes com Locale

```python
# app/routers/posts.py
from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session

router = APIRouter()

@router.get("/{locale}/")
async def home(
    locale: str,
    request: Request,
    db: Session = Depends(get_db)
):
    # Validar locale
    if not is_valid_locale(locale):
        raise HTTPException(404)

    # Buscar posts traduzidos para esse locale
    posts = db.query(Post).join(PostTranslation).filter(
        PostTranslation.locale == locale,
        PostTranslation.translation_status == 'published',
        Post.status == 'published'
    ).order_by(Post.published_at.desc()).limit(10).all()

    # Renderizar template
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "posts": posts,
            "locale": locale,
            "locale_name": get_locale_name(locale)
        }
    )

@router.get("/{locale}/{slug}")
async def post_detail(
    locale: str,
    slug: str,
    request: Request,
    db: Session = Depends(get_db)
):
    # Buscar tradução do post
    translation = db.query(PostTranslation).filter(
        PostTranslation.slug == f"{locale}/{slug}",
        PostTranslation.translation_status == 'published'
    ).first()

    if not translation:
        raise HTTPException(404)

    # Buscar post original
    post = db.query(Post).filter(Post.id == translation.post_id).first()

    # Buscar produtos associados (com preços do locale)
    products = db.query(Product).join(ProductPrice).filter(
        Product.id.in_([p.id for p in post.products]),
        ProductPrice.locale == locale
    ).all()

    # Renderizar
    return templates.TemplateResponse(
        f"posts/{post.type}.html",
        {
            "request": request,
            "post": post,
            "translation": translation,
            "products": products,
            "locale": locale
        }
    )

@router.get("/{locale}/goto/{slug}")
async def affiliate_redirect(
    locale: str,
    slug: str,
    request: Request,
    db: Session = Depends(get_db)
):
    # Buscar produto pelo slug
    product_price = db.query(ProductPrice).filter(
        ProductPrice.affiliate_redirect_slug == slug,
        ProductPrice.locale == locale
    ).first()

    if not product_price:
        raise HTTPException(404)

    # Registrar clique
    click = AffiliateClick(
        product_id=product_price.product_id,
        locale=locale,
        platform=product_price.platform,
        ip_address=request.client.host,
        user_agent=request.headers.get('user-agent'),
        referer=request.headers.get('referer'),
        country=request.headers.get('cf-ipcountry')  # CloudFlare
    )
    db.add(click)
    db.commit()

    # Gerar URL final com UTM
    final_url = add_utm_params(
        product_price.affiliate_url_raw,
        {
            'utm_source': 'geekbiduguru',
            'utm_medium': 'affiliate',
            'utm_campaign': locale,
            'utm_content': slug
        }
    )

    # Redirecionar
    return RedirectResponse(url=final_url, status_code=302)
```

### Redirecionamento Automático da Raiz

```python
# app/main.py
@app.get("/")
async def root(request: Request):
    # Detectar locale preferido do usuário
    locale = detect_locale(request)

    # Redirecionar para homepage do locale
    return RedirectResponse(url=f"/{locale}/", status_code=302)
```

### Cache por Locale

```python
# Usar Redis para cache separado por locale
from redis import Redis

redis_client = Redis(host='localhost', port=6379, db=0)

def get_cached_post(slug: str, locale: str):
    cache_key = f"post:{locale}:{slug}"
    cached = redis_client.get(cache_key)

    if cached:
        return json.loads(cached)

    # Buscar do banco
    post = db.query(PostTranslation).filter(
        PostTranslation.slug == f"{locale}/{slug}"
    ).first()

    # Cachear por 1 hora
    redis_client.setex(cache_key, 3600, json.dumps(post.to_dict()))

    return post
```

---

## 📅 Roadmap de Expansão

### Fase 1: Fundação (Meses 1-6)
**Objetivo**: Lançar geek.bidu.guru em pt-BR com infraestrutura i18n pronta

**Entregas**:
- ✅ Schema de banco multilingue
- ✅ Estrutura de URLs com locale (`/pt-br/...`)
- ✅ Sistema de tradução automática (n8n + LLM)
- ✅ Hreflang tags implementadas
- ✅ Sitemap multilingue
- ✅ Seletor de idioma no frontend (mesmo que só pt-BR ativo)
- ✅ Afiliados configurados: Amazon BR, ML BR, Shopee BR

**KPIs**:
- 10.000 pageviews/mês (pt-BR)
- CTR afiliados: 3-5%
- Receita: R$ 1.000-2.000/mês

---

### Fase 2: Primeiro Mercado Internacional (Meses 7-9)
**Objetivo**: Lançar versão pt-PT (Portugal)

**Entregas**:
- ✅ Traduzir 50 posts mais populares (pt-BR → pt-PT)
- ✅ Configurar afiliados: Amazon.es (entrega PT), Fnac, Worten
- ✅ Keywords research específico de Portugal
- ✅ Google Search Console configurado para pt-PT
- ✅ Promoção em redes sociais portuguesas

**Desafios**:
- Adaptar vocabulário ("celular" → "telemóvel")
- Preços em EUR (converter de BRL)
- Produtos disponíveis podem variar

**KPIs**:
- +2.000 pageviews/mês (pt-PT)
- CTR afiliados: 3-4% (teste)
- Receita adicional: €100-200/mês (~R$ 600-1.200)

---

### Fase 3: Expansão Hispânica (Meses 10-15)
**Objetivo**: Lançar versões es-MX, es-AR, es-CO

**Entregas**:
- ✅ Traduzir 100 posts para espanhol
- ✅ Localizar para cada país (México, Argentina, Colômbia)
- ✅ Configurar afiliados: Amazon MX, ML MX, ML AR, ML CO
- ✅ Keywords research em espanhol
- ✅ Campanha de lançamento em redes hispânicas

**Desafios**:
- Variações de espanhol (MX vs AR vs ES)
- Mercados com menor poder aquisitivo (AR, CO)
- Concorrência local maior

**KPIs**:
- +8.000 pageviews/mês (total es-MX, es-AR, es-CO)
- Receita adicional: R$ 1.500-3.000/mês

---

### Fase 4: Mercado Norte-Americano (Meses 16-24)
**Objetivo**: Lançar versão en-US (maior mercado, maior concorrência)

**Entregas**:
- ✅ Traduzir 200 posts para inglês (EUA)
- ✅ Adaptação cultural completa (medidas, expressões)
- ✅ Configurar afiliados: Amazon US, Best Buy, Target
- ✅ Competição SEO intensa (mercado saturado)
- ✅ Investimento em link building e parcerias

**Desafios**:
- SEO muito competitivo ("geek gifts" = 14k buscas/mês, alta dificuldade)
- Necessidade de conteúdo de altíssima qualidade
- Pode exigir investimento em ads (Google Ads, Facebook Ads)

**KPIs**:
- +20.000 pageviews/mês (en-US)
- Receita adicional: $500-1.000/mês (~R$ 2.500-5.000)

---

### Consolidação (Meses 24+)
**Objetivo**: Otimizar e escalar mercados existentes

**Entregas**:
- Expansão para novos nichos (tech, livros, decoração)
- Parcerias diretas com marcas (Funko, LEGO, etc.)
- Programa de afiliados próprio (usuários promovem o site)
- Possível expansão para mais países (Chile, Peru, França, Alemanha)

**KPIs**:
- 100.000+ pageviews/mês (todos os locales)
- Receita: R$ 10.000-20.000/mês

---

## 📝 Checklist de Implementação

### Fase 0: Preparação (Antes do Lançamento)

**Backend**:
- [ ] Criar tabelas de i18n (`locales`, `post_translations`, `product_translations`, `product_prices`, `affiliate_programs`)
- [ ] Implementar função `detect_locale(request)` no middleware
- [ ] Criar rotas com prefixo `/{locale}/`
- [ ] Implementar função `format_price(amount, locale)`
- [ ] Criar sistema de cache por locale (Redis)

**Frontend**:
- [ ] Criar componente de seletor de idioma
- [ ] Adicionar hreflang tags nos templates
- [ ] Implementar tradução de UI (botões, labels, mensagens)
- [ ] Testar responsividade com textos de tamanhos variados (alemão é +30% mais longo que inglês)

**SEO**:
- [ ] Gerar sitemap multilingue
- [ ] Configurar Google Search Console por locale
- [ ] Implementar redirects automáticos (root → locale)
- [ ] Validar Schema.org por locale

**Conteúdo**:
- [ ] Criar workflow n8n de tradução automática
- [ ] Definir processo de revisão humana (opcional)
- [ ] Criar guia de estilo por idioma

**Afiliados**:
- [ ] Cadastrar em programas de afiliados de cada país
- [ ] Configurar tabela `affiliate_programs`
- [ ] Testar geração de links por locale
- [ ] Validar tracking de cliques por locale

---

## 🎓 Considerações Finais

### Vantagens da Internacionalização

1. **Diversificação de Receita**: Menos dependência de um único mercado
2. **Escala de Tráfego**: 5-10x mais potencial de audiência
3. **Vantagem Competitiva**: Poucos blogs geek são multilíngues
4. **Reuso de Conteúdo**: Tradução automática permite escala rápida
5. **Resiliência**: Se um mercado tem baixa, outros compensam

### Desafios a Considerar

1. **Complexidade Técnica**: Sistema mais complexo para manter
2. **Custo de Tradução**: Mesmo automática, exige revisão
3. **SEO Fragmentado**: Competir em múltiplos mercados simultaneamente
4. **Gestão de Afiliados**: Múltiplos programas, múltiplas moedas
5. **Suporte ao Usuário**: Possível necessidade de suporte em múltiplos idiomas

### Recomendação Final

**Implementar infraestrutura i18n desde o Fase 1**, mas **ativar novos locales gradualmente** (um por trimestre) para garantir qualidade e capacidade de otimização.

**Ordem recomendada de expansão**:
1. pt-BR (Meses 1-6): Fundação
2. pt-PT (Meses 7-9): Teste de internacionalização com idioma similar
3. es-MX (Meses 10-12): Maior mercado hispânico
4. es-AR, es-CO (Meses 13-15): Expansão hispânica
5. en-US (Meses 16-24): Maior mercado, maior competição

Com essa estratégia, geek.bidu.guru pode alcançar **5-6 países em 24 meses**, atingindo uma base de audiência potencial de **300+ milhões de falantes de português e espanhol**.

---

**Versão**: 1.0
**Última atualização**: 2025-12-10
**Aprovação**: Pendente
**Responsável**: Equipe Técnica + Automation Engineer
