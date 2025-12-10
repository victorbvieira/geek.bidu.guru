# Análise Data Analyst - geek.bidu.guru

**Data**: 2025-12-10
**Versão PRD**: 1.3
**Analista**: Data Analyst
**Documentos**: PRD.md, PRD-affiliate-strategy.md, PRD-internationalization.md, PRD-design-system.md

---

## 1. Resumo Executivo

O projeto possui **KPIs bem definidos** nas seções 3 do PRD, mas apresenta **lacunas críticas** em especificação técnica de tracking, modelagem de dados para analytics, dashboards operacionais e automações de insights.

**Score de Maturidade Analytics: 6.5/10** - KPIs definidos, mas falta implementação técnica detalhada.

**Oportunidades principais**: Data warehouse (BigQuery), cohort analysis, predictive analytics, real-time dashboards, attribution modeling e automação de alertas podem **3-5x a eficiência** na tomada de decisão.

---

## 2. TOP 5 GAPS CRÍTICOS

### 2.1. Tracking Plan (GA4) Não Documentado
**Severidade**: Alta
**Impacto**: Dados inconsistentes, impossibilidade de medir KPIs definidos

**O que falta**: Especificação completa de eventos GA4, parâmetros, triggers, data layer.

### 2.2. Modelagem de Dados para Analytics Incompleta
**Severidade**: Alta
**Impacto**: Queries lentas, impossibilidade de análises complexas

**O que falta**: Tabelas de fatos/dimensões, índices, views materializadas, procedures.

### 2.3. Dashboards Operacionais Não Especificados
**Severidade**: Média-Alta
**Impacto**: Decisões baseadas em intuição ao invés de dados

**O que falta**: Mockups, queries SQL, métricas por dashboard, refresh rate.

### 2.4. Sistema de Alertas Automáticos Não Implementado
**Severidade**: Média
**Impacto**: Problemas descobertos tarde demais

**O que falta**: Thresholds, canais de notificação (Telegram/Slack), automações n8n.

### 2.5. Attribution Modeling Não Definido
**Severidade**: Média
**Impacto**: Impossibilidade de otimizar mix de canais

**O que falta**: Modelo de atribuição (first-click, last-click, linear, data-driven).

---

## 3. TOP 5 OPORTUNIDADES

### 3.1. Data Warehouse (BigQuery) + Looker Studio
**Potencial**: Altíssimo
**Esforço**: Alto

Export GA4 → BigQuery permite análises SQL avançadas, cohorts, LTV, custom funnels.

**Benefício**: 10x mais poder analítico, queries complexas em segundos.

### 3.2. Real-Time Dashboard (WebSockets)
**Potencial**: Alto
**Esforço**: Médio

Dashboard ao vivo com métricas em tempo real (visitantes online, cliques afiliados últimas 24h).

**Benefício**: Decisões rápidas, detecção imediata de anomalias.

### 3.3. Cohort Analysis & LTV
**Potencial**: Alto
**Esforço**: Médio

Agrupar usuários por mês de aquisição, analisar retenção e valor no tempo.

**Benefício**: Otimizar CAC vs LTV, identificar períodos mais lucrativos.

### 3.4. Predictive Analytics (Churn, Conversão)
**Potencial**: Médio-Alto
**Esforço**: Alto

ML para prever probabilidade de conversão, churn de usuários, produtos que vão trend.

**Benefício**: Ações proativas, personalização avançada.

### 3.5. Automated Insights (Anomaly Detection)
**Potencial**: Alto
**Esforço**: Médio

Sistema que detecta automaticamente quedas/picos e gera insights.

**Benefício**: Economia de tempo, insights que passariam despercebidos.

---

## 4. GAPS DETALHADOS (12 identificados)

### 2.1. Tracking Plan GA4 Não Documentado

**Eventos críticos faltando especificação**:

```javascript
// EVENTOS DE AFILIADOS
gtag('event', 'affiliate_click', {
  product_id: 'prod-123',
  product_name: 'Caneca Baby Yoda',
  platform: 'amazon',  // ou 'mercadolivre', 'shopee'
  price: 89.90,
  post_slug: 'caneca-baby-yoda',
  link_position: 'top',  // 'middle', 'bottom'
  device: 'mobile',  // 'desktop', 'tablet'
  affiliate_score: 85  // scorecard do produto
});

// SCROLL DEPTH
gtag('event', 'scroll', {
  percent_scrolled: 25,  // 25%, 50%, 75%, 100%
  page_path: window.location.pathname
});

// NEWSLETTER SIGNUP
gtag('event', 'sign_up', {
  method: 'newsletter',
  source: 'sidebar',  // 'popup', 'inline', 'footer'
  persona_inferred: 'ana'  // baseado em comportamento
});

// COMPARTILHAMENTO
gtag('event', 'share', {
  method: 'whatsapp',  // 'telegram', 'twitter', 'facebook', 'copy_link'
  content_type: 'post',
  item_id: 'post-slug'
});

// SEARCH INTERNO
gtag('event', 'search', {
  search_term: 'presentes até 100 reais',
  search_results: 15
});

// QUIZ COMPLETION
gtag('event', 'quiz_complete', {
  quiz_name: 'Que Tipo de Geek É Você?',
  quiz_result: 'gamer',
  products_recommended: 5
});
```

**Parâmetros personalizados GA4**:
```javascript
// Configuração global
gtag('config', 'G-XXXXXXXXXX', {
  custom_map: {
    'dimension1': 'persona_inferred',
    'dimension2': 'affiliate_platform',
    'dimension3': 'price_range',
    'dimension4': 'product_category',
    'metric1': 'affiliate_score'
  }
});
```

### 2.2. Modelagem de Dados para Analytics Incompleta

**Tabelas faltantes**:

```sql
-- Tabela de fatos: sessões agregadas (performance)
CREATE TABLE fact_sessions (
    date DATE NOT NULL,
    hour SMALLINT NOT NULL,
    post_id UUID REFERENCES posts(id),
    device VARCHAR(20),
    source VARCHAR(50),
    persona_inferred VARCHAR(20),
    sessions INT DEFAULT 0,
    pageviews INT DEFAULT 0,
    total_time_seconds INT DEFAULT 0,
    affiliate_clicks INT DEFAULT 0,
    newsletter_signups INT DEFAULT 0,
    PRIMARY KEY (date, hour, post_id, device, source)
);

CREATE INDEX idx_fact_sessions_date ON fact_sessions(date DESC);
CREATE INDEX idx_fact_sessions_post ON fact_sessions(post_id, date DESC);

-- Tabela de fatos: cliques de afiliados (detalhado)
CREATE TABLE fact_affiliate_clicks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    clicked_at TIMESTAMP NOT NULL DEFAULT NOW(),
    product_id UUID NOT NULL REFERENCES products(id),
    post_id UUID REFERENCES posts(id),
    session_id VARCHAR(100),
    user_id UUID,
    platform VARCHAR(20) NOT NULL,
    link_position VARCHAR(20),
    device VARCHAR(20),
    country VARCHAR(2),
    region VARCHAR(50),
    city VARCHAR(100),
    scroll_depth_pct SMALLINT,
    time_on_page_seconds INT,
    is_bot BOOLEAN DEFAULT FALSE,
    is_suspicious BOOLEAN DEFAULT FALSE,
    estimated_commission_brl DECIMAL(10,2)
);

CREATE INDEX idx_affiliate_clicks_time ON fact_affiliate_clicks(clicked_at DESC);
CREATE INDEX idx_affiliate_clicks_product ON fact_affiliate_clicks(product_id, clicked_at DESC);
CREATE INDEX idx_affiliate_clicks_post ON fact_affiliate_clicks(post_id, clicked_at DESC);
CREATE INDEX idx_affiliate_clicks_platform ON fact_affiliate_clicks(platform, clicked_at DESC);

-- View materializada: performance diária por post
CREATE MATERIALIZED VIEW mv_daily_post_performance AS
SELECT
    date,
    post_id,
    p.title,
    p.type,
    p.category_id,
    SUM(sessions) as total_sessions,
    SUM(pageviews) as total_pageviews,
    SUM(total_time_seconds) / NULLIF(SUM(sessions), 0) as avg_time_seconds,
    SUM(affiliate_clicks) as total_affiliate_clicks,
    ROUND(SUM(affiliate_clicks)::numeric / NULLIF(SUM(sessions), 0) * 100, 2) as ctr_pct,
    SUM(newsletter_signups) as newsletter_signups
FROM fact_sessions fs
JOIN posts p ON p.id = fs.post_id
GROUP BY date, post_id, p.title, p.type, p.category_id;

CREATE UNIQUE INDEX ON mv_daily_post_performance(date, post_id);

-- Refresh diário via cron
-- REFRESH MATERIALIZED VIEW CONCURRENTLY mv_daily_post_performance;
```

**Procedures para relatórios**:

```sql
-- Top produtos por receita estimada (último mês)
CREATE OR REPLACE FUNCTION get_top_products_by_revenue(
    days_back INT DEFAULT 30,
    limit_rows INT DEFAULT 10
)
RETURNS TABLE (
    product_id UUID,
    product_name VARCHAR,
    platform VARCHAR,
    total_clicks BIGINT,
    estimated_revenue_brl DECIMAL,
    avg_commission_per_click DECIMAL,
    ctr_vs_views DECIMAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        p.id,
        p.name,
        p.platform,
        COUNT(ac.id) as total_clicks,
        SUM(ac.estimated_commission_brl) as estimated_revenue,
        AVG(ac.estimated_commission_brl) as avg_commission,
        ROUND(
            COUNT(ac.id)::numeric /
            NULLIF((SELECT SUM(pageviews) FROM fact_sessions fs
                    JOIN post_products pp ON pp.post_id = fs.post_id
                    WHERE pp.product_id = p.id
                    AND fs.date >= CURRENT_DATE - days_back), 0) * 100,
            2
        ) as ctr
    FROM products p
    LEFT JOIN fact_affiliate_clicks ac ON ac.product_id = p.id
    WHERE ac.clicked_at >= NOW() - (days_back || ' days')::INTERVAL
    GROUP BY p.id, p.name, p.platform
    ORDER BY estimated_revenue DESC
    LIMIT limit_rows;
END;
$$ LANGUAGE plpgsql;
```

### 2.3. Dashboards Operacionais Não Especificados

**Dashboard 1: Executivo (Visão Geral Diária)**

```sql
-- Query principal
WITH today_metrics AS (
    SELECT
        SUM(sessions) as sessions_today,
        SUM(pageviews) as pageviews_today,
        SUM(affiliate_clicks) as clicks_today,
        ROUND(SUM(affiliate_clicks)::numeric / NULLIF(SUM(sessions), 0) * 100, 2) as ctr_today
    FROM fact_sessions
    WHERE date = CURRENT_DATE
),
yesterday_metrics AS (
    SELECT
        SUM(sessions) as sessions_yesterday,
        SUM(pageviews) as pageviews_yesterday,
        SUM(affiliate_clicks) as clicks_yesterday
    FROM fact_sessions
    WHERE date = CURRENT_DATE - 1
),
revenue_today AS (
    SELECT
        COUNT(*) as total_clicks,
        SUM(estimated_commission_brl) as revenue_estimate,
        AVG(estimated_commission_brl) as epc
    FROM fact_affiliate_clicks
    WHERE clicked_at >= CURRENT_DATE
)
SELECT
    t.sessions_today,
    ROUND((t.sessions_today - y.sessions_yesterday)::numeric / NULLIF(y.sessions_yesterday, 0) * 100, 1) as sessions_change_pct,
    t.pageviews_today,
    t.clicks_today,
    t.ctr_today,
    r.revenue_estimate,
    r.epc
FROM today_metrics t, yesterday_metrics y, revenue_today r;
```

**Mockup Dashboard Executivo**:
```
┌─────────────────────────────────────────────────────┐
│ GEEK.BIDU.GURU - Dashboard Executivo              │
│ Atualizado: 10/12/2025 15:42 🔄                    │
├─────────────────────────────────────────────────────┤
│                                                     │
│ 📊 HOJE (10/Dez)                                   │
│   ├─ Sessões: 847 (+12% vs ontem) ↗              │
│   ├─ Pageviews: 2.103 (+15%)                      │
│   ├─ Cliques Afiliados: 42 (CTR: 5.0%)           │
│   └─ Receita Estimada: R$ 76,80                  │
│                                                     │
│ 💰 ÚLTIMOS 30 DIAS                                 │
│   ├─ Receita Total: R$ 1.847,00                   │
│   ├─ Amazon: R$ 980,00 (53%) 🟢                  │
│   ├─ Mercado Livre: R$ 720,00 (39%) 🔵          │
│   └─ Shopee: R$ 147,00 (8%) 🟡                   │
│                                                     │
│ 📈 TOP 5 POSTS (Últimos 7 dias)                   │
│   1. "10 Presentes Geek de Natal" - R$ 320 | 89↗│
│   2. "Caneca Baby Yoda Review" - R$ 180 | 67↗   │
│   3. "Setup Gamer Completo" - R$ 156 | 54↗      │
│   4. "Presentes até R$100" - R$ 132 | 48↗       │
│   5. "Funko Pop: Guia" - R$ 98 | 41↗            │
│                                                     │
│ ⚠️ ALERTAS                                         │
│   - Post "Teclado Mecânico" com CTR abaixo 2%    │
│   - Produto "Mouse Gamer X" indisponível          │
│                                                     │
└─────────────────────────────────────────────────────┘
```

**Dashboard 2: Afiliados (Detalhado)**

Queries e métricas:
- Performance por plataforma (Amazon vs ML vs Shopee)
- EPC por dispositivo (mobile vs desktop)
- CTR por posição de link (top vs middle vs bottom)
- Heatmap de cliques por hora do dia
- Funil: Pageview → Scroll 50% → Scroll 100% → Click
- Produtos com alto tráfego mas baixo CTR (oportunidades)

**Dashboard 3: Conteúdo**

- Posts publicados vs planejados (calendário editorial)
- Distribuição por tipo (produto único 60%, listicle 25%, guia 15%)
- Tempo médio na página por categoria
- Taxa de rejeição por persona inferida
- Content gaps (keywords com impressões mas sem posts)

### 2.4. Sistema de Alertas Não Implementado

**Alertas prioritários**:

```python
# alerts.py - Executar via cron a cada hora

import psycopg2
import requests
from datetime import datetime, timedelta

def send_telegram(message, level='info'):
    emoji = {'critical': '🚨', 'warning': '⚠️', 'info': 'ℹ️', 'success': '✅'}
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')

    formatted = f"{emoji[level]} **geek.bidu.guru**\n{message}"

    requests.post(
        f"https://api.telegram.org/bot{bot_token}/sendMessage",
        json={'chat_id': chat_id, 'text': formatted, 'parse_mode': 'Markdown'}
    )

# ALERTA 1: Queda de tráfego
def check_traffic_drop(conn):
    query = """
    WITH today AS (
        SELECT SUM(sessions) as sessions_today
        FROM fact_sessions
        WHERE date = CURRENT_DATE AND hour <= EXTRACT(hour FROM NOW())
    ),
    last_week AS (
        SELECT SUM(sessions) as sessions_last_week
        FROM fact_sessions
        WHERE date = CURRENT_DATE - 7 AND hour <= EXTRACT(hour FROM NOW())
    )
    SELECT
        t.sessions_today,
        l.sessions_last_week,
        ROUND((t.sessions_today - l.sessions_last_week)::numeric /
              NULLIF(l.sessions_last_week, 0) * 100, 1) as change_pct
    FROM today t, last_week l;
    """
    cur = conn.cursor()
    cur.execute(query)
    row = cur.fetchone()

    if row and row[2] < -30:  # Queda > 30%
        send_telegram(
            f"⚠️ **Queda de Tráfego**\n"
            f"Hoje: {row[0]} sessões\n"
            f"Semana passada (mesmo horário): {row[1]}\n"
            f"Variação: {row[2]}%",
            level='warning'
        )

# ALERTA 2: CTR de afiliados baixo
def check_low_ctr(conn):
    query = """
    SELECT
        ROUND(COUNT(ac.id)::numeric / NULLIF(SUM(fs.sessions), 0) * 100, 2) as ctr
    FROM fact_sessions fs
    LEFT JOIN fact_affiliate_clicks ac ON ac.clicked_at >= CURRENT_DATE
    WHERE fs.date >= CURRENT_DATE - 7;
    """
    cur = conn.cursor()
    cur.execute(query)
    ctr = cur.fetchone()[0]

    if ctr and ctr < 2.0:  # CTR < 2%
        send_telegram(
            f"⚠️ **CTR Afiliados Baixo**\n"
            f"CTR últimos 7 dias: {ctr}%\n"
            f"Meta: >= 3%\n"
            f"Ação: Revisar CTAs e posicionamento",
            level='warning'
        )

# ALERTA 3: Produto indisponível em post popular
def check_unavailable_products(conn):
    query = """
    SELECT p.name, pr.title, pr.slug
    FROM products p
    JOIN post_products pp ON pp.product_id = p.id
    JOIN posts pr ON pr.id = pp.post_id
    JOIN mv_daily_post_performance dp ON dp.post_id = pr.id
    WHERE p.availability = 'unavailable'
    AND dp.date >= CURRENT_DATE - 7
    AND dp.total_sessions > 100
    LIMIT 5;
    """
    cur = conn.cursor()
    cur.execute(query)
    rows = cur.fetchall()

    if rows:
        msg = "⚠️ **Produtos Indisponíveis em Posts Populares**\n\n"
        for row in rows:
            msg += f"- {row[0]} em '{row[1]}' ({row[2]})\n"
        send_telegram(msg, level='warning')

# ALERTA 4: Novo post no Top 10 (sucesso!)
def check_new_top_performer(conn):
    query = """
    SELECT p.title, p.slug, dp.total_sessions, dp.ctr_pct
    FROM mv_daily_post_performance dp
    JOIN posts p ON p.id = dp.post_id
    WHERE dp.date = CURRENT_DATE - 1
    AND p.publish_at >= CURRENT_DATE - 30
    ORDER BY dp.total_sessions DESC
    LIMIT 10;
    """
    cur = conn.cursor()
    cur.execute(query)
    rows = cur.fetchall()

    if rows:
        top = rows[0]
        send_telegram(
            f"✅ **Novo Post de Sucesso!**\n"
            f"'{top[0]}' teve {top[2]} sessões ontem\n"
            f"CTR: {top[3]}%\n"
            f"Link: geek.bidu.guru/{top[1]}",
            level='success'
        )

# Executar todos os checks
if __name__ == '__main__':
    conn = psycopg2.connect(os.getenv('DATABASE_URL'))
    check_traffic_drop(conn)
    check_low_ctr(conn)
    check_unavailable_products(conn)
    check_new_top_performer(conn)
    conn.close()
```

### 2.5. Attribution Modeling Não Definido

**Problema**: PRD não especifica como atribuir conversões quando usuário visita múltiplas vezes por diferentes canais.

**Modelos sugeridos**:

```
CENÁRIO: Usuário visita 3x antes de clicar em afiliado
├─ Visita 1: Google Orgânico → Post "10 Presentes Geek"
├─ Visita 2: Direto → Homepage
└─ Visita 3: Newsletter → Post "Caneca Baby Yoda" → CLICK

MODELOS DE ATRIBUIÇÃO:
├─ First-Click: 100% crédito para Google Orgânico
├─ Last-Click: 100% crédito para Newsletter
├─ Linear: 33% Google, 33% Direto, 33% Newsletter
├─ Time-Decay: 20% Google, 30% Direto, 50% Newsletter
└─ Data-Driven (ML): Baseado em padrões históricos
```

**Implementação recomendada**: Last-Click (simples) na Fase 1, Linear na Fase 2, Data-Driven na Fase 3.

**Tabela necessária**:
```sql
CREATE TABLE user_touchpoints (
    id UUID PRIMARY KEY,
    session_id VARCHAR(100),
    user_id UUID,
    touchpoint_at TIMESTAMP NOT NULL,
    source VARCHAR(50),
    medium VARCHAR(50),
    campaign VARCHAR(100),
    content VARCHAR(200),
    post_id UUID,
    is_conversion BOOLEAN DEFAULT FALSE
);
```

### 2.6. Cohort Analysis Não Implementado

**O que falta**: Queries e dashboards para análise de cohorts (usuários agrupados por mês de aquisição).

**Query sugerida**:
```sql
-- Retenção por cohort (mês de primeira visita)
WITH cohorts AS (
    SELECT
        user_id,
        DATE_TRUNC('month', MIN(session_start)) as cohort_month
    FROM user_sessions
    GROUP BY user_id
),
cohort_activity AS (
    SELECT
        c.cohort_month,
        DATE_TRUNC('month', us.session_start) as activity_month,
        COUNT(DISTINCT us.user_id) as active_users
    FROM cohorts c
    JOIN user_sessions us ON us.user_id = c.user_id
    GROUP BY c.cohort_month, DATE_TRUNC('month', us.session_start)
),
cohort_size AS (
    SELECT cohort_month, COUNT(*) as cohort_size
    FROM cohorts
    GROUP BY cohort_month
)
SELECT
    ca.cohort_month,
    cs.cohort_size,
    ca.activity_month,
    EXTRACT(month FROM AGE(ca.activity_month, ca.cohort_month)) as months_since_acquisition,
    ca.active_users,
    ROUND(ca.active_users::numeric / cs.cohort_size * 100, 1) as retention_pct
FROM cohort_activity ca
JOIN cohort_size cs ON cs.cohort_month = ca.cohort_month
ORDER BY ca.cohort_month, months_since_acquisition;
```

**Visualização sugerida**: Heatmap com cohort_month no eixo Y e months_since_acquisition no eixo X.

### 2.7. Funis de Conversão Não Instrumentados

**Funil 1: Tráfego Orgânico → Conversão Afiliados**
```
Google Search → Landing Page → Scroll 50% → Scroll 100% → Click Afiliado
       ↓            ↓              ↓              ↓               ↓
    10.000       7.500 (75%)    5.250 (70%)    3.675 (70%)     294 (8%)
```

**Funil 2: Newsletter → Conversão**
```
Newsletter Sent → Open → Click Post → Click Afiliado
       ↓            ↓         ↓             ↓
     5.000      2.000 (40%)  800 (40%)    64 (8%)
```

**Implementação**: Eventos GA4 + tabela `funnel_events` no PostgreSQL para análise SQL.

### 2.8. Testes A/B Não Estruturados

**PRD menciona framework A/B** (seção 9.5) mas falta:
- Calculadora de tamanho de amostra
- Significância estatística (chi-square test)
- Duration mínima (1-2 semanas)
- Documentação de hipóteses

**Função SQL sugerida**:
```sql
CREATE OR REPLACE FUNCTION analyze_ab_test(test_id_param UUID)
RETURNS TABLE (
    variant CHAR(1),
    exposures BIGINT,
    conversions BIGINT,
    conversion_rate DECIMAL,
    confidence_95_lower DECIMAL,
    confidence_95_upper DECIMAL,
    p_value DECIMAL,
    is_significant BOOLEAN
) AS $$
-- Implementar chi-square test e confidence intervals
-- ...
$$ LANGUAGE plpgsql;
```

### 2.9. LTV (Lifetime Value) Não Calculado

**O que falta**: Métrica de valor no tempo de cada usuário.

**Cálculo simples**:
```sql
SELECT
    user_id,
    COUNT(DISTINCT session_id) as total_sessions,
    SUM(estimated_commission_brl) as total_revenue,
    ROUND(SUM(estimated_commission_brl) / NULLIF(COUNT(DISTINCT session_id), 0), 2) as revenue_per_session,
    DATE_TRUNC('month', MIN(first_session)) as cohort_month,
    EXTRACT(days FROM NOW() - MIN(first_session)) as days_since_acquisition
FROM user_activity_aggregated
GROUP BY user_id;
```

**LTV médio por cohort**: Essencial para otimizar CAC (Customer Acquisition Cost) se houver paid ads no futuro.

### 2.10. CAC (Customer Acquisition Cost) Não Rastreado

**Se implementar paid ads** (Google Ads, Meta Ads), é crítico rastrear:
```
CAC = Total Spend / New Users Acquired
ROI = (Revenue - Spend) / Spend * 100
```

**Tabela necessária**:
```sql
CREATE TABLE marketing_spend (
    date DATE PRIMARY KEY,
    platform VARCHAR(50),
    campaign VARCHAR(100),
    spend_brl DECIMAL(10,2),
    impressions INT,
    clicks INT,
    new_users INT
);
```

### 2.11. Data Quality Monitoring Não Implementado

**O que falta**: Sistema que valida dados continuamente.

**Checks prioritários**:
- Eventos GA4 chegando corretamente (volume diário esperado)
- Tabelas fact_* sendo populadas
- Preços de produtos atualizados (last_price_update < 48h)
- Posts sem produtos associados
- Links de afiliados quebrados

**Implementação**: Job daily n8n que roda queries de validação e alerta se algo está errado.

### 2.12. Export para BigQuery Não Configurado

**PRD menciona BigQuery** (seção 7) como "opcional" mas é **altamente recomendado**.

**Benefícios**:
- Queries SQL avançadas em datasets gigantes
- Integração nativa com Looker Studio (dashboards)
- Machine Learning integrado (BigQuery ML)
- Retenção ilimitada de dados

**Setup**:
1. Habilitar export GA4 → BigQuery (gratuito até 1M events/dia)
2. Criar scheduled queries para popular tabelas agregadas
3. Conectar Looker Studio para visualizações

---

## 5. OPORTUNIDADES DETALHADAS (10 identificadas)

### 3.1. Data Warehouse (BigQuery) + Looker Studio
**Benefício**: Análises SQL avançadas, dashboards bonitos, compartilhamento fácil.
**Custo**: ~$50-200/mês dependendo do volume.

### 3.2. Real-Time Dashboard (WebSockets + Redis)
**Benefício**: Decisões rápidas, gamificação interna (equipe vê métricas ao vivo).
**Stack**: FastAPI + WebSockets + Redis Pub/Sub.

### 3.3. Cohort Analysis Completo
**Benefício**: Entender retenção, identificar meses de alta qualidade, calcular LTV.

### 3.4. Predictive Analytics
**Modelos prioritários**:
- Probabilidade de conversão (score 0-100 por sessão)
- Churn prediction (usuários que não voltam)
- Trending products (produtos que vão viralizar)

**Stack**: Python (scikit-learn), PostgreSQL, cron daily.

### 3.5. Automated Insights
**Sistema que gera insights automaticamente**:
- "Post X teve CTR 3x maior que média - analisar o que funcionou"
- "Tráfego mobile aumentou 40% - otimizar mobile"
- "Produto Y tem alto tráfego mas baixo CTR - revisar CTA"

**Implementação**: Job diário que compara métricas e gera relatório.

### 3.6. Benchmarking Externo
**Comparar com concorrentes e indústria**:
- Ahrefs/SEMrush: DR, keywords, backlinks
- SimilarWeb: Tráfego estimado de concorrentes
- Industry benchmarks: CTR médio para nicho

### 3.7. Geolocation Analytics
**Análise por região/cidade**:
- Quais cidades geram mais conversões?
- Horários de pico por timezone
- Produtos populares por região (Sul vs Nordeste)

**Implementação**: Capturar IP → CloudFlare headers → tabela `geo_data`.

### 3.8. Heatmaps & Session Recordings Integrados
**Microsoft Clarity** (gratuito) já mencionado no PRD.

**Análise adicional**: Exportar dados de Clarity para PostgreSQL via API para cruzar com outras métricas.

### 3.9. Custom Attribution Model (Data-Driven)
**Machine Learning para atribuição**:
- Treinar modelo com histórico de conversões
- Aprender quais touchpoints são mais importantes
- Alocar crédito proporcionalmente

**Requer**: 6-12 meses de dados, expertise em ML.

### 3.10. Data Democratization (Self-Service BI)
**Permitir que toda equipe acesse dados facilmente**:
- Looker Studio com acesso compartilhado
- Metabase self-hosted para queries SQL
- Documentação de tabelas e métricas (data dictionary)

---

## 6. SUGESTÕES DE MELHORIAS (10 identificadas)

### 4.1. KPIs - Adicionar Confidence Intervals
**Situação Atual**: KPIs apresentados como números absolutos.
**Sugestão**: Adicionar intervalos de confiança (IC 95%).

**Exemplo**:
```
CTR Afiliados: 4.5% (IC 95%: 4.1% - 4.9%)
Receita Mensal: R$ 1.847 (IC 95%: R$ 1.680 - R$ 2.014)
```

### 4.2. Metas SMART - Adicionar Baseline Real
**Situação Atual**: Metas começam do zero (baseline 0).
**Sugestão**: Após 30-60 dias, revisar baseline com dados reais e ajustar metas.

### 4.3. North Star Metric - Adicionar Leading Indicators
**Situação Atual**: North Star = Receita mensal (lagging indicator).
**Sugestão**: Adicionar leading indicators:
- CTR afiliados (prediz receita)
- Sessões orgânicas (prediz CTR)
- Posts publicados (prediz sessões)

### 4.4. Dashboards - Adicionar Comparativos Históricos
**Situação Atual**: Métricas absolutas.
**Sugestão**: Sempre mostrar vs período anterior e vs mesmo período ano anterior.

### 4.5. Alertas - Implementar Machine Learning
**Situação Atual**: Thresholds fixos (CTR < 2%, queda > 30%).
**Sugestão**: ML para detectar anomalias baseado em padrões históricos (mais preciso).

### 4.6. Segmentação - Adicionar RFM
**RFM** (Recency, Frequency, Monetary):
- **R**: Última visita (dias atrás)
- **F**: Frequência de visitas (sessões/mês)
- **M**: Valor monetário (comissões geradas)

**Segmentos**:
- Champions (RFM alto): 111, 112, 121, 122
- Loyal (FM alto, R médio): 211, 212
- At Risk (R baixo, FM alto): 311, 312
- Lost (RFM baixo): 333

### 4.7. Testes A/B - Adicionar Multi-Armed Bandit
**Situação Atual**: A/B tradicional (50/50 split).
**Sugestão**: Multi-Armed Bandit aloca mais tráfego para variante vencedora dinamicamente.

### 4.8. Funis - Adicionar Drop-off Reasons
**Situação Atual**: Funil mostra onde usuários saem.
**Sugestão**: Capturar motivo (via hotjar, pesquisa exit-intent, session replay analysis).

### 4.9. Reports - Automatizar Geração e Envio
**Situação Atual**: PRD menciona reports mas não automação completa.
**Sugestão**: n8n workflow que gera PDF do relatório mensal e envia via email automaticamente dia 1 de cada mês.

### 4.10. Data Catalog - Documentar Tabelas e Métricas
**Situação Atual**: Sem documentação centralizada de dados.
**Sugestão**: Data dictionary em `/docs/analytics/data-catalog.md`:
```markdown
## Tabela: fact_sessions

**Descrição**: Sessões agregadas por hora para performance queries.

| Coluna | Tipo | Descrição | Exemplo |
|--------|------|-----------|---------|
| date | DATE | Data da sessão | 2025-12-10 |
| hour | SMALLINT | Hora (0-23) | 14 |
| post_id | UUID | ID do post visitado | abc-123... |
| device | VARCHAR(20) | mobile, desktop, tablet | mobile |
| sessions | INT | Total de sessões | 42 |
| affiliate_clicks | INT | Cliques em afiliados | 3 |

**Refresh**: Atualizada a cada hora via cron.
**Owner**: Data Team
```

---

## 7. AMPLIAÇÕES DE ESCOPO (5 identificadas)

### 5.1. Data Warehouse (BigQuery)
**Descrição**: Export GA4 + tabelas PostgreSQL → BigQuery para análises avançadas.
**Prioridade**: Alta (implementar Fase 2).
**Custo**: ~$50-200/mês.

### 5.2. Machine Learning Platform
**Descrição**: Modelos preditivos (conversão, churn, trending products, personalização).
**Prioridade**: Média (Fase 3, após 6 meses de dados).
**Stack**: Python (scikit-learn, TensorFlow), Jupyter Notebooks, MLflow.

### 5.3. Customer Data Platform (CDP)
**Descrição**: Unificar dados de GA4, PostgreSQL, newsletter, redes sociais em perfil único de usuário.
**Benefícios**: Segmentação avançada, personalização 1:1.
**Ferramentas**: Segment (paid), RudderStack (open-source).
**Prioridade**: Baixa (Fase 4, após 12 meses).

### 5.4. Real-Time Event Streaming
**Descrição**: Kafka/Redis Streams para processar eventos em tempo real.
**Benefícios**: Dashboards ao vivo, recomendações em tempo real.
**Prioridade**: Baixa (over-engineering para escala atual).

### 5.5. Data Science Team
**Descrição**: Contratar analista de dados dedicado (após 12 meses).
**Responsabilidades**:
- Análises ad-hoc
- Experimentos A/B
- Machine Learning
- Relatórios executivos
**Prioridade**: Média (quando receita justificar).

---

## 8. PLANO DE AÇÃO RECOMENDADO

### Curto Prazo (1-3 meses) - CRÍTICO

**ALTA Prioridade**:
- [ ] **Documentar tracking plan GA4** completo (todos os eventos + parâmetros)
- [ ] **Criar tabelas fact_sessions e fact_affiliate_clicks** com índices
- [ ] **Implementar 3 dashboards** (Executivo, Afiliados, Conteúdo)
- [ ] **Sistema de alertas básico** (Telegram: queda tráfego, CTR baixo, produtos indisponíveis)
- [ ] **Configurar views materializadas** (mv_daily_post_performance)

**MÉDIA Prioridade**:
- [ ] Documentar modelo de atribuição (começar com Last-Click)
- [ ] Criar funções SQL para relatórios comuns (get_top_products_by_revenue)
- [ ] Setup Microsoft Clarity (heatmaps)

### Médio Prazo (3-6 meses)

**Implementações**:
- [ ] **Export GA4 → BigQuery** + scheduled queries
- [ ] **Looker Studio dashboards** conectados ao BigQuery
- [ ] **Cohort analysis** completa (retenção, LTV)
- [ ] **Funis instrumentados** (GA4 + PostgreSQL)
- [ ] **Data quality monitoring** (jobs diários de validação)
- [ ] **Automated insights** (job que gera insights semanais)

**Testes**:
- [ ] Framework A/B com significância estatística
- [ ] 5-10 experimentos rodando (CTAs, posicionamento, copy)

### Longo Prazo (6-12 meses)

**Grandes Projetos**:
- [ ] **Machine Learning models** (conversão, churn, trending)
- [ ] **Predictive analytics** em produção
- [ ] **Real-time dashboard** (WebSockets)
- [ ] **Attribution modeling** avançado (Linear → Data-Driven)
- [ ] **Data democratization** (Metabase self-service)
- [ ] **Contratar Data Analyst** dedicado

**Otimizações**:
- [ ] Geolocation analytics (análise por região)
- [ ] RFM segmentation
- [ ] Multi-Armed Bandit A/B
- [ ] Data catalog completo

---

## 9. MÉTRICAS DE SUCESSO

### KPIs de Analytics

| Métrica | Baseline | 3 Meses | 6 Meses | 12 Meses |
|---------|----------|---------|---------|----------|
| **Data Quality Score** | - | 85% | 92% | 98% |
| **Dashboard Usage** (views/semana) | 0 | 50 | 150 | 300 |
| **Alertas Enviados** (por mês) | 0 | 20 | 30 | 40 |
| **Insights Acionáveis** (por mês) | 0 | 5 | 10 | 15 |
| **A/B Tests Rodando** (simultâneos) | 0 | 2 | 5 | 10 |
| **Query Response Time** (dashboard principal) | - | <3s | <2s | <1s |

### Impacto em KPIs de Negócio

**Expectativa**: Analytics robusto → decisões melhores → métricas melhores.

| KPI Negócio | Baseline | Com Analytics (+6 meses) | Melhoria |
|-------------|----------|--------------------------|----------|
| **CTR Afiliados** | 3% | 5-6% | +67-100% |
| **Receita/Mês** | R$ 1.000 | R$ 3.000-4.000 | +200-300% |
| **Tempo na Página** | 2min | 3min | +50% |
| **Taxa Rejeição** | 55% | 45% | -18% |

**Correlação**: Melhores dados → melhores decisões → melhores resultados.

---

## 10. CONCLUSÃO

O geek.bidu.guru possui **KPIs bem definidos** mas **lacunas críticas** na implementação técnica de analytics.

### Ações Imediatas (30 dias):
1. ✅ **Tracking plan GA4** completo documentado
2. ✅ **Tabelas fact_sessions e fact_affiliate_clicks** criadas
3. ✅ **3 dashboards** operacionais (Executivo, Afiliados, Conteúdo)
4. ✅ **Sistema de alertas** Telegram (4 alertas prioritários)

### Quick Wins (90 dias):
1. 🎯 **BigQuery export** (análises SQL avançadas)
2. 🎯 **Cohort analysis** (entender retenção e LTV)
3. 🎯 **Automated insights** (economia de tempo)
4. 🎯 **Data quality monitoring** (confiança nos dados)

### Diferenciais (6-12 meses):
1. 🚀 **Machine Learning** (predictive analytics)
2. 🚀 **Real-time dashboard** (decisões rápidas)
3. 🚀 **Attribution avançado** (Data-Driven)
4. 🚀 **Data Analyst** dedicado (análises profundas)

Implementação dessas sugestões pode **3-5x a eficiência** na tomada de decisão e **aumentar receita 200-300%** via otimizações data-driven.

---

**Analista**: Data Analyst
**Data**: 10/12/2025
**Status**: Análise Completa
