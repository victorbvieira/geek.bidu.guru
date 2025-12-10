# Plano de Tracking (GA4) — geek.bidu.guru

Versão: 1.1
Última atualização: 2025-12-10
Relacionado: PRD.md §3, §6.13–6.14, §7 (Analytics), reports/data-analyst-analysis.md

---

## Objetivo

Definir taxonomia de eventos, parâmetros e convenções (UTM/segmentos) para mensurar funis (afiliados, newsletter, orgânico), CTR, engajamento e testes A/B no GA4, com possibilidade de exportação para BigQuery.

---

## Setup

- GA4 via `gtag.js` ou Google Tag Manager (GTM).  
- Habilitar Anonymize IP e Consent Mode quando aplicável (LGPD).  
- Considerar exportação BigQuery (opcional) para análises avançadas.

Snippet base (gtag): ver `agents/data-analyst.md`.

---

## Eventos e Parâmetros

Eventos automáticos do GA4 (page_view etc.) permanecem. A seguir, eventos customizados:

1) `view_post`  
- Quando: ao carregar página de post.  
- Params:  
  - `post_id`, `post_slug`, `post_type` (`product_single|listicle|guide`)  
  - `category`, `tags` (string ou array), `persona_focus` (Ana|Lucas|Marina|mix)  
  - `ab_tests` (lista de IDs ativos no post)

2) `affiliate_click`  
- Quando: clique em link/botão de afiliado.  
- Params:  
  - `product_id`, `product_name`, `platform` (`amazon|mercadolivre|shopee`)  
  - `price` (numérico, quando disponível)  
  - `post_id`, `post_slug`, `position` (`intro|middle|end|sidebar|table`)  
  - `cta_variant` (ex.: `btn-yellow|btn-green|text-link`)  
  - `ab_test_id`, `ab_variant` (se parte de teste)

3) `share`  
- Quando: clique em compartilhar.  
- Params:  
  - `method` (`whatsapp|telegram|facebook|twitter|email|copy`)  
  - `content_type` (`post|product`)  
  - `item_id` (`post_id` ou `product_id`)

4) `sign_up` (newsletter)  
- Quando: submit bem-sucedido.  
- Params:  
  - `method`: `newsletter`  
  - `placement`: `sidebar|footer|inline|modal`

5) `newsletter_optin_view`  
- Quando: opt-in fica visível.  
- Params:  
  - `placement` (mesmo mapa do sign_up)

6) `scroll`  
- Quando: atingir limiares 25/50/75/90%.  
- Params:  
  - `percent_scrolled`, `page_path`

7) `search_used` (se houver busca interna)  
- Params: `query`, `results_count`

8) `filter_used` (se houver filtros)  
- Params: `filter_type`, `filter_value`

9) `ab_exposure`  
- Quando: usuário exposto a um teste A/B.  
- Params: `ab_test_id`, `ab_variant`, `area` (ex.: `cta_button`)

10) `goto_redirect` (servidor)  
- Onde: no endpoint `/goto/{slug}` (server-side tracking adicional).  
- Campos mínimos: `product_id`, `post_id`, `platform`, `timestamp`, `session_id` (cookie)  
- Objetivo: reconciliar cliques no backend (robustez e auditoria).

---

## UTMs e Convenções

- `utm_source`: `google|instagram|facebook|twitter|newsletter|telegram|direct|referral`  
- `utm_medium`: `organic|social|email|cpc|referral`  
- `utm_campaign`:  
  - Posts: `post_{slug}_{yyyy-mm}`  
  - Sazonais: `seasonal_{natal|bf|namorados}_{yyyy}`  
  - Recycling: `recycling_{slug_pilar}_{yyyy-mm}`

- `utm_content`: variantes de CTA (ex.: `btn-yellow|btn-green|text-link`).

---

## Segmentação Recomendada

- Fonte de tráfego: orgânico vs direto vs social vs referral.  
- Dispositivo: mobile vs desktop vs tablet.  
- Persona inferida: pelo campo `persona_focus` e pela categoria/tag.  
- Tipo de conteúdo: `post_type`.  
- Geografia: estado/cidade (GA4).  
- Faixa de preço (quando aplicável): derivada de `price_range` do produto (via join backend → GA4 export).

---

## Privacidade & LGPD

- Não coletar PII no GA4 (sem emails/telefones).  
- Consent Mode quando exigido.  
- Avisos de cookies e de afiliados visíveis.  
- Retenção de dados conforme política de privacidade.

---

## Exportação e Integrações

- BigQuery Export (GA4) para análises de coorte, LTV e segmentações avançadas.
- Integração com Search Console no Looker Studio.
- Integração com backend (PostgreSQL) para cliques de afiliados.

---

## Dimensões Customizadas (GA4)

### Configuração de Dimensões

| Dimensão | Escopo | Tipo | Uso |
|----------|--------|------|-----|
| `persona_focus` | Event | String | Persona alvo do conteúdo (Ana/Lucas/Marina) |
| `post_type` | Event | String | Tipo de post (product_single, listicle, guide) |
| `price_range` | Event | String | Faixa de preço (budget, mid, premium) |
| `affiliate_platform` | Event | String | Plataforma de afiliado (amazon, mercadolivre, shopee) |
| `cta_position` | Event | String | Posição do CTA (intro, middle, end, sidebar) |
| `ab_test_variant` | Event | String | Variante do teste A/B (A, B) |
| `content_age_days` | Event | Number | Idade do conteúdo em dias |
| `franchise` | Event | String | Franquia geek (star_wars, marvel, anime) |

### Métricas Customizadas

| Métrica | Tipo | Uso |
|---------|------|-----|
| `affiliate_revenue_estimate` | Currency | Receita estimada do clique |
| `product_score` | Number | Score interno do produto (0-100) |
| `scroll_depth_at_click` | Number | % scrollado no momento do clique |

---

## Eventos Avançados (Fase 2+)

### 11) `wishlist_add`
- Quando: usuário adiciona produto à wishlist
- Params:
  - `product_id`, `product_name`, `price`
  - `platform`, `franchise`

### 12) `wishlist_remove`
- Quando: usuário remove produto da wishlist
- Params:
  - `product_id`

### 13) `price_alert_set`
- Quando: usuário configura alerta de preço
- Params:
  - `product_id`, `target_price`, `current_price`

### 14) `price_alert_triggered`
- Quando: alerta de preço é acionado
- Params:
  - `product_id`, `old_price`, `new_price`, `discount_percent`

### 15) `quiz_start`
- Quando: usuário inicia quiz de recomendação
- Params:
  - `quiz_type` (presente_ideal, qual_geek, etc.)

### 16) `quiz_complete`
- Quando: usuário completa quiz
- Params:
  - `quiz_type`, `result_persona`, `products_shown`

### 17) `compare_view`
- Quando: usuário visualiza comparativo de produtos
- Params:
  - `product_ids` (array), `category`

### 18) `email_optin`
- Quando: usuário se inscreve via formulário específico
- Params:
  - `source` (post, modal, footer, sidebar)
  - `incentive` (cupom, ebook, none)

---

## Funis de Conversão

### Funil 1: Afiliado Completo
```
page_view → view_post → scroll (50%) → affiliate_click → [conversão externa]
```

### Funil 2: Newsletter
```
page_view → newsletter_optin_view → sign_up
```

### Funil 3: Wishlist → Compra
```
page_view → wishlist_add → price_alert_set → price_alert_triggered → affiliate_click
```

### Funil 4: Quiz → Conversão
```
quiz_start → quiz_complete → affiliate_click
```

---

## Alertas Automatizados

### Configurar alertas no GA4 para:

1. **Queda de Tráfego**: >30% queda vs semana anterior
2. **CTR Baixo**: CTR de afiliados <2% em 24h
3. **Bounce Rate Alto**: >60% em posts novos
4. **Erro de Tracking**: Eventos sem parâmetros obrigatórios

### Implementação de Alertas (n8n)

```javascript
// Verificar anomalias diariamente
const metricsToCheck = {
  'affiliate_click_rate': { threshold: 0.02, direction: 'below' },
  'bounce_rate': { threshold: 0.60, direction: 'above' },
  'pageviews': { threshold: -0.30, direction: 'change' }
};
```

---

## Integração com Microsoft Clarity

### Eventos de Heatmap

Configurar para rastrear:
- Cliques em botões de afiliado
- Scroll depth em posts longos
- Rage clicks (frustração)
- Dead clicks (cliques sem resposta)

### Sessões para Análise

Filtrar sessões por:
- Usuários que clicaram em afiliados
- Usuários que abandonaram antes do CTA
- Mobile vs Desktop

---

## Código de Implementação

### gtag.js - Eventos Principais

```javascript
// affiliate_click
function trackAffiliateClick(productData, postData, ctaData) {
  gtag('event', 'affiliate_click', {
    product_id: productData.id,
    product_name: productData.name,
    platform: productData.platform,
    price: productData.price,
    post_id: postData.id,
    post_slug: postData.slug,
    position: ctaData.position,
    cta_variant: ctaData.variant,
    scroll_depth: getScrollDepth(),
    ab_test_id: ctaData.abTestId || null,
    ab_variant: ctaData.abVariant || null
  });
}

// scroll tracking
let scrollMilestones = [25, 50, 75, 90];
let trackedMilestones = [];

window.addEventListener('scroll', () => {
  const scrollPercent = Math.round(
    (window.scrollY / (document.documentElement.scrollHeight - window.innerHeight)) * 100
  );

  scrollMilestones.forEach(milestone => {
    if (scrollPercent >= milestone && !trackedMilestones.includes(milestone)) {
      trackedMilestones.push(milestone);
      gtag('event', 'scroll', {
        percent_scrolled: milestone,
        page_path: window.location.pathname
      });
    }
  });
});

// Helper: Get current scroll depth
function getScrollDepth() {
  return Math.round(
    (window.scrollY / (document.documentElement.scrollHeight - window.innerHeight)) * 100
  );
}
```

### Data Layer para GTM

```javascript
// Push para data layer
dataLayer.push({
  event: 'affiliate_click',
  ecommerce: {
    items: [{
      item_id: productData.id,
      item_name: productData.name,
      affiliation: productData.platform,
      price: productData.price
    }]
  }
});
```

---

## Validação e QA

### Checklist de Validação

- [ ] Todos os eventos disparam no GA4 Debug View
- [ ] Parâmetros obrigatórios estão presentes
- [ ] Valores de enum estão corretos
- [ ] Eventos não duplicam
- [ ] Mobile e desktop comportamento idêntico
- [ ] Consent mode funciona corretamente

### Ferramenta de Teste

Usar Google Tag Assistant ou GA4 Debugger para validar implementação antes de produção.

