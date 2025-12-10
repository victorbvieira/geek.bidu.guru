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

---

## Dashboard de Conteúdo (Editores/SEO)

- Atualização: semanal.  
- Métricas: Top posts (pageviews/tempo/CTR afiliado), performance por categoria, keywords (novas/perdidas), calendário de publicações (draf/agenda).  
- Insights: oportunidades (categorias com pouco conteúdo mas alto RPM/CTR).

---

## Dashboard de Afiliados (Marketing)

- Atualização: diária.  
- Métricas: receita por plataforma, top produtos, top posts por receita, CTR por tipo de post, funil de afiliados (view → click → redirect → conversão), alertas (links quebrados/produtos esgotados).  
- Segmentos: plataforma, persona_focus, dispositivo.

---

## Relatórios Automatizados

- Diário (resumo de ontem): tráfego, top post, cliques afiliados, falhas n8n.  
- Semanal (executivo): evolução das métricas-chave, destaques, alertas.  
- Mensal (profundo): análise de SEO, coortes/retorno, receita por plataforma, aprendizados de testes A/B, plano do mês seguinte.  
- Trimestral: tendências, sazonalidades, planejamento de picos (Natal/BF/namorados).

Automação sugerida: n8n enviando PDF/links para Telegram/Email.

