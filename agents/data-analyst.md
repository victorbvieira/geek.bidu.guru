# Data Analyst - geek.bidu.guru

## 👤 Perfil do Agente

**Nome**: Data Analyst
**Área**: Negócio / Análise de Dados
**Especialidade**: Métricas, KPIs, analytics, relatórios, dashboards, insights baseados em dados

## 🎯 Responsabilidades

- Definição e acompanhamento de KPIs
- Análise de métricas de tráfego e engajamento
- Análise de performance de afiliados
- Criação de dashboards e relatórios
- Identificação de insights e oportunidades
- Análise de comportamento do usuário
- Testes A/B e análise de resultados
- Previsão de tendências e sazonalidades

## 📊 KPIs Principais por Categoria

### 1. Tráfego e SEO

| Métrica | Meta (3 meses) | Meta (6 meses) | Meta (12 meses) |
|---------|----------------|----------------|-----------------|
| **Visitantes únicos/mês** | 5.000 | 15.000 | 50.000 |
| **Pageviews/mês** | 10.000 | 35.000 | 120.000 |
| **Sessões orgânicas** | 70% | 75% | 80% |
| **Posição média** | Top 30 | Top 15 | Top 5-10 |
| **Keywords ranqueadas** | 50 | 150 | 500+ |
| **CTR orgânico** | 2% | 4% | 6% |

---

### 2. Engajamento

| Métrica | Meta | Como Medir |
|---------|------|------------|
| **Tempo médio na página** | 2-3 min | Google Analytics |
| **Taxa de rejeição** | < 50% | Google Analytics |
| **Páginas por sessão** | 2-3 | Google Analytics |
| **Scroll depth** | > 60% | GA4 Events |
| **Retorno de visitantes** | > 20% | GA4 |
| **Newsletter signup rate** | 2-3% | Conversões / Sessões |

---

### 3. Afiliados e Monetização

| Métrica | Meta (3 meses) | Meta (6 meses) | Meta (12 meses) |
|---------|----------------|----------------|-----------------|
| **CTR de links afiliados** | 2-3% | 4-5% | 6-8% |
| **Receita mensal** | R$ 500 | R$ 2.000 | R$ 5.000+ |
| **RPM (Receita/1k views)** | R$ 10 | R$ 30 | R$ 50+ |
| **EPC (Ganho/clique)** | R$ 0,50 | R$ 1,00 | R$ 2,00 |
| **Taxa de conversão** | 3% | 5% | 8% |

---

### 4. Conteúdo

| Métrica | Meta | Frequência |
|---------|------|-----------|
| **Posts publicados/semana** | 7 | Semanal |
| **Posts diários** | 1 | Diário |
| **Listicles semanais** | 1 | Semanal |
| **Guias mensais** | 2 | Mensal |
| **Taxa de sucesso n8n** | > 95% | Diário |

---

### 5. Performance Técnica

| Métrica | Meta | Ferramenta |
|---------|------|-----------|
| **LCP (Largest Contentful Paint)** | < 2.5s | PageSpeed Insights |
| **FID (First Input Delay)** | < 100ms | PageSpeed Insights |
| **CLS (Cumulative Layout Shift)** | < 0.1 | PageSpeed Insights |
| **Uptime** | > 99.5% | Monitoring tool |
| **TTFB (Time to First Byte)** | < 600ms | WebPageTest |

## 🔍 Ferramentas de Analytics

### Google Analytics 4 (GA4)

**Setup Inicial**:
```javascript
// Configuração do GA4 no <head>
<script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-XXXXXXXXXX');
</script>
```

**Eventos Personalizados Importantes**:

```javascript
// Clique em link de afiliado
gtag('event', 'affiliate_click', {
  product_id: 'produto-xyz',
  product_name: 'Caneca Baby Yoda',
  platform: 'amazon',
  price: 89.90,
  post_slug: 'melhores-canecas-geek'
});

// Compartilhamento de post
gtag('event', 'share', {
  method: 'whatsapp',
  content_type: 'post',
  item_id: 'post-123'
});

// Inscrição em newsletter
gtag('event', 'sign_up', {
  method: 'newsletter'
});

// Scroll depth
gtag('event', 'scroll', {
  percent_scrolled: 75,
  page_path: window.location.pathname
});
```

---

### Google Search Console

**Métricas para Monitorar**:
- **Queries** que trazem tráfego
- **CTR por query** (oportunidades de otimização)
- **Impressões** (potencial não realizado)
- **Posição média** por página/query
- **Páginas** com mais cliques
- **Erros de indexação**

**Relatórios Semanais**:
1. Top 10 queries por cliques
2. Queries com impressões altas mas CTR baixo (< 2%)
3. Páginas novas indexadas
4. Erros 404 ou de servidor

---

### Heatmaps e Session Recording

**Ferramentas**: Hotjar, Microsoft Clarity (gratuito)

**Insights a Buscar**:
- Onde os usuários clicam mais
- Até onde rolam a página (scroll depth)
- Elementos que causam frustração (rage clicks)
- Campos de formulário que causam abandono

---

### Dashboard Customizado (PostgreSQL)

**Queries Úteis para Dashboard**:

**1. Posts mais visitados (última semana)**:
```sql
SELECT
  p.title,
  COUNT(DISTINCT s.session_id) as sessions,
  COUNT(s.id) as pageviews,
  AVG(s.time_on_page) as avg_time
FROM posts p
LEFT JOIN sessions s ON s.post_id = p.id
WHERE s.created_at >= NOW() - INTERVAL '7 days'
GROUP BY p.id, p.title
ORDER BY sessions DESC
LIMIT 10;
```

**2. Produtos mais clicados (último mês)**:
```sql
SELECT
  pr.name,
  pr.platform,
  COUNT(ac.id) as total_clicks,
  pr.price,
  COUNT(ac.id) * pr.price * 0.05 as estimated_commission
FROM products pr
LEFT JOIN affiliate_clicks ac ON pr.id = ac.product_id
WHERE ac.clicked_at >= DATE_TRUNC('month', CURRENT_DATE)
GROUP BY pr.id, pr.name, pr.platform, pr.price
ORDER BY total_clicks DESC
LIMIT 10;
```

**3. Performance por categoria**:
```sql
SELECT
  c.name as category,
  COUNT(DISTINCT p.id) as total_posts,
  COUNT(DISTINCT s.session_id) as total_sessions,
  COUNT(ac.id) as affiliate_clicks,
  ROUND(COUNT(ac.id)::numeric / NULLIF(COUNT(DISTINCT s.session_id), 0) * 100, 2) as ctr_percentage
FROM categories c
LEFT JOIN posts p ON p.category_id = c.id
LEFT JOIN sessions s ON s.post_id = p.id
LEFT JOIN post_products pp ON pp.post_id = p.id
LEFT JOIN affiliate_clicks ac ON ac.product_id = pp.product_id
WHERE s.created_at >= NOW() - INTERVAL '30 days'
GROUP BY c.id, c.name
ORDER BY affiliate_clicks DESC;
```

**4. Taxa de conversão de newsletter por página**:
```sql
SELECT
  p.title,
  COUNT(DISTINCT s.session_id) as total_visitors,
  COUNT(DISTINCT ns.email) as newsletter_signups,
  ROUND(COUNT(DISTINCT ns.email)::numeric / NULLIF(COUNT(DISTINCT s.session_id), 0) * 100, 2) as conversion_rate
FROM posts p
LEFT JOIN sessions s ON s.post_id = p.id
LEFT JOIN newsletter_signups ns ON ns.session_id = s.session_id
WHERE s.created_at >= NOW() - INTERVAL '30 days'
GROUP BY p.id, p.title
HAVING COUNT(DISTINCT s.session_id) > 100
ORDER BY conversion_rate DESC
LIMIT 10;
```

## 📈 Dashboards e Relatórios

### Dashboard Executivo (Visão Geral)

**Frequência**: Atualização diária, visualização semanal

**Métricas Principais**:
```
┌─────────────────────────────────────────────────────┐
│ GEEK.BIDU.GURU - Dashboard Executivo               │
├─────────────────────────────────────────────────────┤
│                                                     │
│ 📊 TRÁFEGO (Últimos 30 dias)                       │
│   ├─ Visitantes: 12.450 (+23% vs mês anterior)    │
│   ├─ Pageviews: 28.900 (+31%)                     │
│   └─ Sessões Orgânicas: 73%                       │
│                                                     │
│ 💰 MONETIZAÇÃO (Dezembro 2025)                     │
│   ├─ Receita Total: R$ 1.847,00                   │
│   ├─ Amazon: R$ 980,00 (53%)                      │
│   ├─ Mercado Livre: R$ 720,00 (39%)               │
│   ├─ Shopee: R$ 147,00 (8%)                       │
│   └─ CTR Médio: 4.2%                              │
│                                                     │
│ 📝 CONTEÚDO (Esta semana)                          │
│   ├─ Posts publicados: 7/7 ✅                     │
│   ├─ Fluxos n8n executados: 21                    │
│   └─ Taxa de sucesso: 95%                         │
│                                                     │
│ ⚡ PERFORMANCE                                     │
│   ├─ LCP: 2.1s ✅                                 │
│   ├─ Core Web Vitals: Passing                     │
│   └─ Uptime: 99.8%                                │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

### Dashboard de Conteúdo

**Frequência**: Semanal

**Seções**:
1. **Top 10 Posts**:
   - Por pageviews
   - Por tempo na página
   - Por cliques em afiliados

2. **Análise de Categorias**:
   - Distribuição de posts
   - Performance por categoria
   - Oportunidades (categorias com poucos posts)

3. **Análise Temporal**:
   - Dias da semana com mais tráfego
   - Horários de pico
   - Sazonalidades

---

### Dashboard de Afiliados

**Frequência**: Diária

**Seções**:
1. **Performance Geral**:
   - Receita acumulada (mês)
   - Cliques totais
   - CTR médio
   - EPC (Earnings Per Click)

2. **Por Plataforma**:
   - Comparação Amazon vs ML vs Shopee
   - Produtos mais clicados por plataforma
   - Receita por plataforma

3. **Top Products**:
   - 10 produtos mais rentáveis
   - 10 produtos com maior CTR
   - Produtos a promover (alto valor, poucos cliques)

4. **Por Post**:
   - Posts que mais geram receita
   - Posts com melhor conversão
   - Posts com oportunidades de melhoria

---

### Relatório Mensal (Stakeholders)

**Estrutura**:

```markdown
# Relatório Mensal - geek.bidu.guru
**Período**: Dezembro 2025

## 1. Resumo Executivo
- Visão geral do mês
- Destaques positivos
- Desafios encontrados
- Ações para próximo mês

## 2. Tráfego e Audiência
- Visitantes únicos: [número] ([% crescimento])
- Pageviews: [número] ([% crescimento])
- Novos vs Recorrentes: [%] / [%]
- Principais fontes de tráfego:
  - Orgânico: [%]
  - Direto: [%]
  - Redes Sociais: [%]
  - Referral: [%]

## 3. SEO
- Keywords ranqueadas: [número]
- Top 5 keywords por tráfego
- Posição média: [posição]
- CTR orgânico: [%]
- Páginas indexadas: [número]

## 4. Engajamento
- Tempo médio na página: [tempo]
- Taxa de rejeição: [%]
- Páginas por sessão: [número]
- Newsletter signups: [número] ([% conversão])

## 5. Monetização
- Receita total: R$ [valor]
- Receita por plataforma (gráfico)
- Top 5 produtos mais rentáveis
- CTR de afiliados: [%]
- EPC: R$ [valor]

## 6. Conteúdo
- Posts publicados: [número]
- Tipos de post (produto único, listicle, guia)
- Top 5 posts do mês
- Categorias mais publicadas

## 7. Insights e Oportunidades
- [Insight 1]
- [Insight 2]
- [Oportunidade 1]
- [Oportunidade 2]

## 8. Ações para o Próximo Mês
- [ ] Ação 1
- [ ] Ação 2
- [ ] Ação 3
```

## 🧪 Testes A/B e Experimentação

### Framework de Testes

**Hipótese**:
```
Se [mudança],
então [métrica] irá [aumentar/diminuir] em [%],
porque [razão].
```

**Exemplo**:
```
Se mudarmos a cor do botão CTA de amarelo para verde,
então o CTR de afiliados irá aumentar em 15%,
porque verde é associado a "comprar" e "segurança".
```

---

### Priorização de Testes (Framework ICE)

**ICE Score = (Impact + Confidence + Ease) / 3**

| Teste | Impact (1-10) | Confidence (1-10) | Ease (1-10) | ICE Score | Prioridade |
|-------|---------------|-------------------|-------------|-----------|------------|
| Cor do botão CTA | 8 | 7 | 10 | 8.3 | Alta |
| Posição do link afiliado | 9 | 6 | 8 | 7.7 | Alta |
| Texto do CTA | 7 | 8 | 9 | 8.0 | Alta |
| Redesign da homepage | 10 | 5 | 2 | 5.7 | Média |
| Adicionar vídeos aos posts | 8 | 4 | 3 | 5.0 | Média |

---

### Tamanho de Amostra e Significância

**Calculadora de Amostra**:
```
Para um teste ser válido:
- Mínimo 1.000 visitantes por variante
- Duração mínima de 1 semana (cobrir 1 ciclo completo)
- Significância estatística: p-value < 0.05
```

**Ferramentas**:
- Google Optimize (gratuito, integrado com GA)
- VWO, Optimizely (pagas)
- Implementação própria (backend Python)

---

### Exemplo de Teste A/B (Backend)

```python
# models.py
class ABTest(Base):
    __tablename__ = 'ab_tests'

    id = Column(UUID, primary_key=True)
    name = Column(String)
    hypothesis = Column(Text)
    variant_a_name = Column(String)  # "Control"
    variant_b_name = Column(String)  # "Treatment"
    metric = Column(String)  # "ctr", "conversion", etc.
    status = Column(String)  # "active", "paused", "completed"
    start_date = Column(DateTime)
    end_date = Column(DateTime)

class ABTestEvent(Base):
    __tablename__ = 'ab_test_events'

    id = Column(UUID, primary_key=True)
    test_id = Column(UUID, ForeignKey('ab_tests.id'))
    session_id = Column(String)
    variant = Column(String)  # "A" or "B"
    event_type = Column(String)  # "view", "click", "conversion"
    created_at = Column(DateTime)
```

```python
# Atribuir variante ao usuário
def assign_variant(session_id, test_id):
    # Consistente baseado em session_id
    hash_value = int(hashlib.md5(session_id.encode()).hexdigest(), 16)
    return 'A' if hash_value % 2 == 0 else 'B'

# Registrar evento
def track_ab_event(test_id, session_id, event_type):
    variant = assign_variant(session_id, test_id)
    event = ABTestEvent(
        test_id=test_id,
        session_id=session_id,
        variant=variant,
        event_type=event_type,
        created_at=datetime.utcnow()
    )
    db.add(event)
    db.commit()

# Analisar resultados
def analyze_test(test_id):
    query = """
    SELECT
        variant,
        COUNT(CASE WHEN event_type = 'view' THEN 1 END) as views,
        COUNT(CASE WHEN event_type = 'click' THEN 1 END) as clicks,
        ROUND(
            COUNT(CASE WHEN event_type = 'click' THEN 1 END)::numeric /
            NULLIF(COUNT(CASE WHEN event_type = 'view' THEN 1 END), 0) * 100,
            2
        ) as ctr
    FROM ab_test_events
    WHERE test_id = :test_id
    GROUP BY variant
    """
    results = db.execute(query, {'test_id': test_id}).fetchall()
    return results
```

## 📊 Segmentação de Audiência

### Segmentos Importantes

**1. Por Fonte de Tráfego**:
- Orgânico (SEO)
- Direto
- Redes Sociais (Facebook, Instagram, X)
- Referral (outros sites)
- Email (newsletter)

**2. Por Comportamento**:
- Novos visitantes
- Visitantes recorrentes
- High-engagers (tempo > 5min, páginas > 3)
- Bouncing visitors (< 10s na página)
- Convertidos (clicaram em afiliados)

**3. Por Interesse (inferido)**:
- Gamers (visita posts de games)
- Devs (visita posts de dev/tech)
- Otakus (visita posts de anime)
- Generalistas (variedade de categorias)

**4. Por Dispositivo**:
- Mobile
- Desktop
- Tablet

**5. Por Faixa de Preço**:
- Budget-conscious (< R$ 50)
- Mid-range (R$ 50-150)
- Premium (> R$ 150)

---

### Insights por Segmento

**Análise**:
```sql
-- Comparar comportamento: Novos vs Recorrentes
SELECT
  user_type,
  COUNT(DISTINCT session_id) as sessions,
  AVG(pages_per_session) as avg_pages,
  AVG(time_on_site) as avg_time,
  SUM(affiliate_clicks) as total_clicks,
  ROUND(SUM(affiliate_clicks)::numeric / COUNT(DISTINCT session_id) * 100, 2) as ctr
FROM (
  SELECT
    s.session_id,
    CASE WHEN s.is_new_user THEN 'New' ELSE 'Returning' END as user_type,
    COUNT(s.id) as pages_per_session,
    SUM(s.time_on_page) as time_on_site,
    COUNT(ac.id) as affiliate_clicks
  FROM sessions s
  LEFT JOIN affiliate_clicks ac ON ac.session_id = s.session_id
  WHERE s.created_at >= NOW() - INTERVAL '30 days'
  GROUP BY s.session_id, s.is_new_user
) subquery
GROUP BY user_type;
```

## 🎯 Alertas e Notificações

### Sistema de Alertas Automáticos

**Alertas Críticos** (notificação imediata):
- Site fora do ar (uptime < 99%)
- Erro 500 em endpoints principais
- Falha em fluxos n8n críticos (posts diários)

**Alertas Importantes** (notificação diária):
- Queda de tráfego > 30% (vs semana anterior)
- CTR de afiliados < 2%
- Nenhum post publicado no dia

**Alertas Informativos** (notificação semanal):
- Novo post ranqueado no top 10
- Produto com > 100 cliques na semana
- Newsletter com > 50 signups

---

### Implementação (Python + Telegram)

```python
import requests

def send_telegram_alert(message, level='info'):
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')

    emoji = {
        'critical': '🚨',
        'warning': '⚠️',
        'info': 'ℹ️',
        'success': '✅'
    }

    formatted_message = f"{emoji.get(level, 'ℹ️')} {message}"

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    data = {
        'chat_id': chat_id,
        'text': formatted_message,
        'parse_mode': 'Markdown'
    }

    requests.post(url, data=data)

# Uso
if traffic_drop > 0.3:
    send_telegram_alert(
        f"⚠️ **Queda de Tráfego Detectada**\n"
        f"Tráfego caiu {traffic_drop*100:.1f}% vs semana passada\n"
        f"Hoje: {today_traffic} | Semana passada: {last_week_traffic}",
        level='warning'
    )
```

## 📚 Recursos e Ferramentas

### Ferramentas Gratuitas
- **Google Analytics 4**: analytics completo
- **Google Search Console**: SEO e indexação
- **Google Data Studio** (Looker Studio): dashboards visuais
- **Microsoft Clarity**: heatmaps e session recording
- **Plausible Analytics** (self-hosted): alternativa leve ao GA

### Ferramentas Pagas
- **Hotjar**: heatmaps, surveys, recordings
- **SEMrush** / **Ahrefs**: análise de SEO e concorrentes
- **Mixpanel**: product analytics avançado
- **Amplitude**: analytics e funnel analysis

### Aprendizado
- [Google Analytics Academy](https://analytics.google.com/analytics/academy/)
- [SQL for Data Analysis (Mode)](https://mode.com/sql-tutorial/)
- [Storytelling with Data](https://www.storytellingwithdata.com/)

---

**Versão**: 1.0
**Última atualização**: 2025-12-10
**Projeto**: geek.bidu.guru
