# Fase 3: IA & Internacionalizacao

**Prioridade**: MEDIA
**Objetivo**: Conteudo inteligente e expansao
**Agentes Principais**: Automation Engineer, Content Strategist, Backend Developer, SEO Specialist

---

## Visao Geral da Fase

A Fase 3 aprimora a qualidade do conteudo gerado e prepara para expansao. Ao final desta fase, teremos:
- Prompts otimizados para diferentes tipos de post
- Pesquisa automatizada de produtos com IA
- Monitoramento de deals e ofertas
- Cache Redis implementado
- Sistema de i18n preparado (pt-BR base)

---

## 3.1 Integracao IA Avancada

**Agente Principal**: Content Strategist + Automation Engineer
**Referencia**: `agents/content-strategist.md`, `agents/automation-engineer.md`

### 3.1.1 Prompts Otimizados

**Arquivo**: `n8n/prompts/post_prompts.json`

#### Prompt: Post de Produto Unico

```json
{
    "name": "single_product_post",
    "system_prompt": "Voce e um redator especializado em presentes geek para o blog geek.bidu.guru. Seu tom e amigavel, informativo e entusiasta, mas sem exageros. Voce escreve como um amigo geek dando dicas sinceras.\n\nRegras:\n- Use linguagem acessivel (nem todos sao experts)\n- Inclua referencias geek contextualizadas\n- Foque nos beneficios para quem vai dar de presente\n- Seja honesto sobre pontos negativos\n- Use emojis com moderacao\n- Escreva em portugues brasileiro",
    "user_prompt_template": "Crie um post completo sobre o produto: {{ product.name }}\n\nInformacoes do produto:\n- Preco: R$ {{ product.price }}\n- Plataforma: {{ product.platform }}\n- Descricao: {{ product.description }}\n- Avaliacao: {{ product.rating }} estrelas\n\nO post deve conter:\n1. Titulo atrativo (max 60 caracteres)\n2. Introducao envolvente (2-3 paragrafos)\n3. Secao 'Para quem e ideal'\n4. Secao 'O que voce vai amar' (3-5 pontos)\n5. Secao 'Bom saber' (1-2 pontos de atencao)\n6. Conclusao com CTA\n\nFormato de saida: JSON com campos title, meta_description, content (HTML), keywords (array)",
    "max_tokens": 1500,
    "temperature": 0.7
}
```

#### Prompt: Listicle Top 10

```json
{
    "name": "listicle_top10",
    "system_prompt": "Voce e um curador de presentes geek para o blog geek.bidu.guru. Crie listas comparativas uteis e bem organizadas.\n\nRegras:\n- Apresente produtos em ordem de recomendacao\n- Destaque diferenciais de cada produto\n- Inclua faixa de preco\n- Indique para qual perfil cada produto e melhor\n- Use formatacao clara (numeracao, bullets)",
    "user_prompt_template": "Crie um listicle 'Top 10' sobre: {{ theme }}\n\nProdutos disponiveis:\n{% for p in products %}\n{{ loop.index }}. {{ p.name }} - R$ {{ p.price }} ({{ p.platform }})\n{% endfor %}\n\nO post deve conter:\n1. Titulo no formato '10 Melhores [tema] para [ocasiao/persona]'\n2. Introducao explicando criterios de selecao\n3. Para cada produto:\n   - Porque esta na lista\n   - Para quem e ideal\n   - Preco e onde comprar\n4. Conclusao com dicas finais\n5. FAQ (3-5 perguntas frequentes)\n\nFormato de saida: JSON",
    "max_tokens": 3000,
    "temperature": 0.7
}
```

#### Prompt: Guia Completo

```json
{
    "name": "comprehensive_guide",
    "system_prompt": "Voce e um especialista em presentes geek criando guias educativos e completos para o blog geek.bidu.guru.\n\nRegras:\n- Conteudo aprofundado e util\n- Estrutura clara com H2 e H3\n- Exemplos praticos\n- Links internos sugeridos\n- Otimizado para SEO",
    "user_prompt_template": "Crie um guia completo sobre: {{ topic }}\n\nContexto: {{ context }}\n\nProdutos relacionados para mencionar:\n{% for p in products %}\n- {{ p.name }}\n{% endfor %}\n\nEstrutura esperada:\n1. Titulo no formato 'Como [resultado] - Guia Completo 2025'\n2. Introducao (problema + promessa)\n3. 5-7 secoes principais (H2)\n4. Produtos recomendados intercalados\n5. Conclusao com proximos passos\n6. FAQ (5+ perguntas)\n\nPalavras-alvo: {{ target_keywords | join(', ') }}\n\nFormato de saida: JSON",
    "max_tokens": 4000,
    "temperature": 0.6
}
```

### 3.1.2 Variacao de Tom por Persona

**Arquivo**: `n8n/prompts/persona_modifiers.json`

```json
{
    "personas": {
        "ana_compradora": {
            "description": "Compradora de presentes, nao-geek",
            "tone_modifier": "Use linguagem simples, explique referencias geek, foque em 'como vai impressionar quem receber', destaque facilidade de compra",
            "cta_style": "Ver Presente",
            "price_focus": "custo-beneficio"
        },
        "lucas_geek_raiz": {
            "description": "Geek entusiasta, compra para si",
            "tone_modifier": "Use referencias geek avancadas, foque em qualidade e autenticidade, compare com alternativas, seja tecnico quando relevante",
            "cta_style": "Garantir o Meu",
            "price_focus": "qualidade"
        },
        "marina_dev": {
            "description": "Desenvolvedora, foco em produtividade",
            "tone_modifier": "Destaque funcionalidade e durabilidade, mencione casos de uso no trabalho, seja objetivo e pratico",
            "cta_style": "Ver Especificacoes",
            "price_focus": "investimento"
        }
    }
}
```

### 3.1.3-3.1.5 Sistema de Templates e Revisao

**Implementar**:
- Templates de conteudo reutilizaveis
- Revisao automatica com IA (gramatica, SEO)
- Geracao automatica de meta description

---

## 3.2 n8n - Workflow E (Pesquisa de Produtos)

**Agente Principal**: Automation Engineer
**Referencia**: `agents/automation-engineer.md`

### Especificacao do Flow E

**Nome**: `flow-e-product-research`
**Trigger**: Cron (semanal, domingos as 22h)
**Objetivo**: Descobrir novos produtos trending para adicionar ao catalogo

### Estrutura do Workflow

```
[Cron Trigger: Domingo 22h]
    |
    v
[Google Trends: Buscar termos geek em alta]
    |
    v
[OpenAI: Analisar trends e sugerir categorias]
    |
    v
[Split: Por plataforma]
    |-- Amazon --> [Amazon API: Buscar produtos]
    |-- ML --> [Mercado Livre API: Buscar produtos]
    |-- Shopee --> [Shopee: Scraping seguro]
    |
    v
[Merge resultados]
    |
    v
[OpenAI: Filtrar e ranquear produtos]
    |
    v
[HTTP Request: POST /api/v1/products/suggestions]
    |
    v
[Telegram: Notificar admin com resumo]
```

### Nodes Principais

**1. Google Trends API**
```javascript
// Buscar trends de termos geek no Brasil
const trends = await googleTrends.interestOverTime({
    keyword: ['presente geek', 'funko pop', 'action figure', 'gadget geek'],
    geo: 'BR',
    startTime: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000),
});
```

**2. OpenAI - Analisar Trends**
```json
{
    "prompt": "Analise os seguintes termos em tendencia e sugira 5 categorias de produtos geek para pesquisar:\n\nTrends: {{ trends }}\n\nRetorne JSON com: { categories: [string], search_queries: [string] }"
}
```

**3. Filtro de Qualidade**
```json
{
    "prompt": "Analise os seguintes produtos e selecione os 10 melhores para um blog de presentes geek:\n\n{{ products }}\n\nCriterios:\n- Avaliacao >= 4 estrelas\n- Preco entre R$30 e R$500\n- Visual atrativo\n- Potencial de conversao\n\nRetorne JSON com os produtos selecionados e justificativa"
}
```

---

## 3.3 n8n - Workflow F (Monitor de Deals)

**Agente Principal**: Automation Engineer
**Referencia**: `agents/automation-engineer.md`

### Especificacao do Flow F

**Nome**: `flow-f-deal-monitor`
**Trigger**: Cron (a cada 2 horas)
**Objetivo**: Detectar quedas de preco significativas e criar posts de oferta

### Estrutura do Workflow

```
[Cron Trigger: A cada 2h]
    |
    v
[HTTP Request: GET /api/v1/products/with-price-history]
    |
    v
[Code: Calcular variacao de preco]
    |
    v
[IF: Desconto >= 20%?]
    |-- Sim --> [OpenAI: Gerar post de oferta]
    |               |
    |               v
    |           [HTTP Request: POST /api/v1/posts]
    |               |
    |               v
    |           [Telegram: Alerta "Oferta Detectada!"]
    |
    |-- Nao --> [No Operation]
```

### Calculo de Variacao

```javascript
// Node: Calcular variacao de preco
const products = $input.all();
const deals = [];

for (const product of products) {
    const currentPrice = product.price;
    const previousPrice = product.price_history[product.price_history.length - 2]?.price;

    if (previousPrice && currentPrice < previousPrice) {
        const discount = ((previousPrice - currentPrice) / previousPrice) * 100;

        if (discount >= 20) {
            deals.push({
                ...product,
                discount_percent: Math.round(discount),
                previous_price: previousPrice,
                savings: previousPrice - currentPrice
            });
        }
    }
}

return deals.map(d => ({ json: d }));
```

### Prompt para Post de Oferta

```json
{
    "prompt": "Crie um post URGENTE de oferta para o produto:\n\n{{ product.name }}\nPreco anterior: R$ {{ product.previous_price }}\nPreco atual: R$ {{ product.price }}\nDesconto: {{ product.discount_percent }}%\nEconomia: R$ {{ product.savings }}\n\nO post deve:\n- Ter titulo com urgencia (use 'Oferta' ou 'Preco Baixou')\n- Destacar a economia\n- Criar senso de urgencia\n- Ser curto e direto (max 300 palavras)\n\nFormato: JSON"
}
```

---

## 3.4 Cache Redis

**Agente Principal**: Backend Developer
**Referencia**: `agents/backend-developer.md`

### 3.4.1 utils/cache.py

**Arquivo**: `src/app/utils/cache.py`

```python
"""
Utilitarios de cache com Redis.
"""
import json
from typing import Optional, Any
from datetime import timedelta
import redis.asyncio as redis
from app.config import settings

# Cliente Redis global
redis_client: Optional[redis.Redis] = None


async def get_redis() -> redis.Redis:
    """Retorna cliente Redis, criando se necessario."""
    global redis_client
    if redis_client is None:
        redis_client = redis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True
        )
    return redis_client


async def cache_get(key: str) -> Optional[Any]:
    """Busca valor no cache."""
    client = await get_redis()
    value = await client.get(key)
    if value:
        return json.loads(value)
    return None


async def cache_set(
    key: str,
    value: Any,
    expire: Optional[timedelta] = None
) -> None:
    """Salva valor no cache."""
    client = await get_redis()
    serialized = json.dumps(value, default=str)
    if expire:
        await client.setex(key, expire, serialized)
    else:
        await client.set(key, serialized)


async def cache_delete(key: str) -> None:
    """Remove valor do cache."""
    client = await get_redis()
    await client.delete(key)


async def cache_delete_pattern(pattern: str) -> None:
    """Remove valores que correspondem ao padrao."""
    client = await get_redis()
    keys = await client.keys(pattern)
    if keys:
        await client.delete(*keys)


def cache_key(*args) -> str:
    """Gera chave de cache a partir de argumentos."""
    return ":".join(str(arg) for arg in args)


# Decorator para cache de funcoes
def cached(prefix: str, expire_minutes: int = 60):
    """Decorator que cacheia resultado de funcao async."""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Gerar chave baseada nos argumentos
            key_parts = [prefix, func.__name__] + [str(a) for a in args]
            key = cache_key(*key_parts)

            # Tentar buscar do cache
            cached_value = await cache_get(key)
            if cached_value is not None:
                return cached_value

            # Executar funcao e cachear
            result = await func(*args, **kwargs)
            await cache_set(key, result, timedelta(minutes=expire_minutes))
            return result

        return wrapper
    return decorator
```

### 3.4.2 Cachear Queries Frequentes

**Exemplo**: `src/app/services/post_service.py`

```python
from app.utils.cache import cached, cache_delete_pattern

class PostService:

    @cached(prefix="posts", expire_minutes=30)
    async def get_published_posts(self, limit: int = 20) -> List[Post]:
        """Lista posts publicados (cacheado por 30min)."""
        # Query no banco...
        pass

    @cached(prefix="post", expire_minutes=60)
    async def get_post_by_slug(self, slug: str) -> Optional[Post]:
        """Busca post por slug (cacheado por 1h)."""
        # Query no banco...
        pass

    async def update_post(self, post_id: UUID, data: PostUpdate) -> Post:
        """Atualiza post e invalida cache."""
        post = await self._update_in_db(post_id, data)

        # Invalidar caches relacionados
        await cache_delete_pattern("posts:*")
        await cache_delete_pattern(f"post:*:{post.slug}")

        return post
```

### 3.4.3-3.4.4 Cache de Sessoes e Invalidacao

**Implementar**:
- JWT blacklist em Redis
- Invalidacao em cascata ao atualizar conteudo
- TTL adequado por tipo de dado

---

## 3.5 Internacionalizacao (i18n)

**Agente Principal**: Backend Developer + Content Strategist
**Referencia**: `agents/backend-developer.md`

### 3.5.1 Estrutura i18n

**Instalar**: `pip install babel`

**Arquivo**: `src/app/i18n.py`

```python
"""
Configuracao de internacionalizacao.
"""
from babel import Locale
from babel.support import Translations
from pathlib import Path
from functools import lru_cache

LOCALES_DIR = Path(__file__).parent / "locales"
SUPPORTED_LOCALES = ["pt_BR", "en_US", "es_ES"]
DEFAULT_LOCALE = "pt_BR"


@lru_cache()
def get_translations(locale: str) -> Translations:
    """Carrega traducoes para o locale."""
    try:
        return Translations.load(LOCALES_DIR, [locale])
    except:
        return Translations.load(LOCALES_DIR, [DEFAULT_LOCALE])


def get_locale_from_request(accept_language: str) -> str:
    """Detecta locale a partir do header Accept-Language."""
    if not accept_language:
        return DEFAULT_LOCALE

    # Parse do header
    for lang in accept_language.split(","):
        lang = lang.split(";")[0].strip().replace("-", "_")
        if lang in SUPPORTED_LOCALES:
            return lang
        # Tentar apenas o idioma base
        base_lang = lang.split("_")[0]
        for supported in SUPPORTED_LOCALES:
            if supported.startswith(base_lang):
                return supported

    return DEFAULT_LOCALE
```

### 3.5.2 Arquivos de Traducao

**Estrutura**:
```
src/app/locales/
├── pt_BR/
│   └── LC_MESSAGES/
│       ├── messages.po
│       └── messages.mo
├── en_US/
│   └── LC_MESSAGES/
│       └── ...
└── es_ES/
    └── LC_MESSAGES/
        └── ...
```

**Exemplo**: `locales/pt_BR/LC_MESSAGES/messages.po`

```
# Portuguese (Brazil) translations
msgid ""
msgstr ""
"Language: pt_BR\n"
"Content-Type: text/plain; charset=UTF-8\n"

msgid "home.title"
msgstr "Presentes Geek Perfeitos | geek.bidu.guru"

msgid "home.hero.title"
msgstr "Encontre o presente geek perfeito"

msgid "home.hero.subtitle"
msgstr "Listas, reviews e ideias criadas por geeks, para geeks"

msgid "nav.home"
msgstr "Inicio"

msgid "nav.categories"
msgstr "Categorias"

msgid "nav.about"
msgstr "Sobre"

msgid "product.buy_button"
msgstr "Ver Oferta"

msgid "product.price_from"
msgstr "A partir de"

msgid "footer.affiliate_disclosure"
msgstr "Este site contem links de afiliados. Saiba mais."
```

### 3.5.3-3.5.5 Implementacao nos Templates

**Middleware de Locale**:

```python
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

class LocaleMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        accept_language = request.headers.get("Accept-Language", "")
        request.state.locale = get_locale_from_request(accept_language)
        request.state.translations = get_translations(request.state.locale)
        response = await call_next(request)
        return response
```

**No Template**:

```html
<h1>{{ _('home.hero.title') }}</h1>
<p>{{ _('home.hero.subtitle') }}</p>
```

**hreflang tags**:

```html
<link rel="alternate" hreflang="pt-BR" href="https://geek.bidu.guru{{ request.path }}">
<link rel="alternate" hreflang="en" href="https://geek.bidu.guru/en{{ request.path }}">
<link rel="alternate" hreflang="x-default" href="https://geek.bidu.guru{{ request.path }}">
```

---

## Criterios de Conclusao da Fase 3

- [ ] Prompts de IA documentados e testados
- [ ] Flow E descobre novos produtos semanalmente
- [ ] Flow F detecta e publica ofertas automaticamente
- [ ] Cache Redis funcionando (verificar hits/misses)
- [ ] Sistema i18n configurado (pt-BR funcional)
- [ ] Arquivos de traducao base criados
- [ ] Performance de queries melhorada com cache

---

## Proxima Fase

Apos concluir a Fase 3, avance para:
- **Fase 4**: Growth & Otimizacao (`05-phase-4-growth-optimization.md`)

---

**Versao**: 1.0
**Data**: 2025-12-10
**Projeto**: geek.bidu.guru
