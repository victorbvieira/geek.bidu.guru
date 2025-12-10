# Dashboards & Relatórios — geek.bidu.guru

Versão: 1.0  
Última atualização: 2025-12-10  
Relacionado: PRD.md §3, §7 (Analytics), §11 (Relatórios)

---

## Ferramentas

- Looker Studio (gratuito) com conectores GA4 e Search Console.  
- Metabase/Redash (opcional) conectado ao PostgreSQL (cliques de afiliados).  
- Exportação GA4 → BigQuery (opcional) para coortes/LTV.

---

## Dashboard Executivo (Stakeholders)

- Atualização: diária (visão semanal).  
- Métricas: North Star (Receita mensal), tráfego (visitantes/pageviews), conversão (CTR afiliados, taxa de conversão quando disponível), conteúdo (posts publicados, sucesso n8n), performance (Core Web Vitals, uptime).  
- Segmentos: fonte de tráfego, dispositivo, tipo de conteúdo.

Template (Looker Studio) sugerido:
- Fontes: Conector GA4 (propriedade do site), Conector Search Console (Site Impression), opcional CSV/Sheets para metas.  
- Páginas:  
  - Visão Geral: North Star, tráfego 30 dias, mix de canais, dispositivos.  
  - Afiliados: CTR, EPC/RPM (campos calculados), por plataforma (se integrar dados externos).  
  - SEO: queries top, CTR por query, páginas top por cliques.  
- Filtros: intervalo de datas, dispositivo, fonte/mídia, `post_type`, `persona_focus`.  
- Campos calculados:  
  - `affiliate_ctr = affiliate_clicks / sessions`  
  - `rpm = (revenue / pageviews) * 1000` (se receita disponível)

---

## Dashboard de Conteúdo (Editores/SEO)

- Atualização: semanal.  
- Métricas: Top posts (pageviews/tempo/CTR afiliado), performance por categoria, keywords (novas/perdidas), calendário de publicações (draf/agenda).  
- Insights: oportunidades (categorias com pouco conteúdo mas alto RPM/CTR).

Template (Looker Studio) sugerido:
- Fontes: GA4 (eventos `view_post`, `affiliate_click`, `scroll`), Search Console (páginas).  
- Seções/Gráficos:  
  - Tabela Top Posts (pageviews, avg engagement time, affiliate_clicks, CTR).  
  - Heatmap por dia/hora.  
  - Performance por categoria e `post_type`.  
  - Keywords (SC): novas/perdidas/melhores ganhos.  
- Filtros: data, categoria, `post_type`, `persona_focus`.  
- Campos: `affiliate_ctr`, `scroll_50_rate` (se event count/users), `avg_time`.

---

## Dashboard de Afiliados (Marketing)

- Atualização: diária.  
- Métricas: receita por plataforma, top produtos, top posts por receita, CTR por tipo de post, funil de afiliados (view → click → redirect → conversão), alertas (links quebrados/produtos esgotados).  
- Segmentos: plataforma, persona_focus, dispositivo.

Template (Looker Studio) sugerido:
- Fontes: GA4 (eventos), planilha/API com receita por plataforma (se disponível), PostgreSQL (cliques `affiliate_clicks`/`goto_redirect` via conector).  
- Seções/Gráficos:  
  - Receita por plataforma (mês/dia).  
  - Top 10 produtos e posts por cliques/receita.  
  - Funil: view → click → redirect → conversão (se dados).  
  - Tabela por `post_type` e `platform` com CTR/RPM.  
- Filtros: data, plataforma, `post_type`, `persona_focus`.  
- Campos: `rpm`, `epc = revenue / clicks` (se receita disponível).

---

## Relatórios Automatizados

- Diário (resumo de ontem): tráfego, top post, cliques afiliados, falhas n8n.  
- Semanal (executivo): evolução das métricas-chave, destaques, alertas.  
- Mensal (profundo): análise de SEO, coortes/retorno, receita por plataforma, aprendizados de testes A/B, plano do mês seguinte.  
- Trimestral: tendências, sazonalidades, planejamento de picos (Natal/BF/namorados).

Automação sugerida: n8n enviando PDF/links para Telegram/Email.

---

## Dashboard de SEO (Especializado)

- Atualização: diária (visão semanal/mensal).  
- Métricas: keywords ranqueadas totais, top 3, featured snippets, DR/DA (se disponível), backlinks totais/novos, páginas indexadas, CTR orgânico, posição média.  
- SERP Features: PAA, Image Packs, Video Carousels (quando integrável).  
- Seções:  
  - Visão geral (KPIs vs metas).  
  - Keywords (ganhos/perdas).  
  - Páginas top (cliques/CTR/posições).  
  - Backlinks (novos/domínios referenciadores).  
- Fontes: Search Console, GA4, ferramenta externa (planilha) para DR/backlinks se não houver conector.  
- Filtros: data, tipo de conteúdo, cluster (ocasião/perfil/preço), persona_focus.
