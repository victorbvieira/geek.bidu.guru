# Funis de Conversão — geek.bidu.guru

Versão: 1.0  
Última atualização: 2025-12-10  
Relacionado: PRD.md §6.13, docs/analytics/tracking-plan.md

---

## Funil de Tráfego Orgânico

Impressões (SERP) → Cliques (Search Console) → Pageviews (GA4 `page_view`)

KPIs: CTR orgânico, posição média, páginas com mais cliques, queries com alto potencial (impressões altas/CTR baixo).

---

## Funil de Afiliados (Principal)

1) Visualização de Post (`view_post`)  
2) Scroll ≥ 50% (`scroll` 50/75/90)  
3) Clique em Afiliado (`affiliate_click`)  
4) Redirecionamento registrado (`goto_redirect` backend)  
5) Compra na loja (dados quando disponíveis)

Métricas derivadas: CTR do CTA, drop-off por etapa, taxa de chegada à loja, taxa de conversão (quando possível), RPM e EPC.

Ações típicas: mover CTA acima da dobra, validar preço/estoque antes do redirect, testes A/B de cor/posição/texto.

---

## Funil de Newsletter

1) Exposição de opt-in (`newsletter_optin_view`)  
2) Submit (`sign_up`, method=newsletter)  
3) Double opt-in confirmado (via plataforma de email)  
4) Abertura do primeiro email (open rate)  
5) Clique em link do email (email CTR)

Métricas: taxa de conversão opt-in, confirmação, engajamento inicial.

---

## Visualização e Drop-off

Construir visualizações no Looker Studio ou Metabase, filtrando por: tipo de post, persona_focus, dispositivo e fonte. Priorizar etapas com maior drop-off para ações.

