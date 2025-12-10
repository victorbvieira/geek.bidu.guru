# Plano de Tracking (GA4) — geek.bidu.guru

Versão: 1.0  
Última atualização: 2025-12-10  
Relacionado: PRD.md §3, §6.13–6.14, §7 (Analytics)

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

