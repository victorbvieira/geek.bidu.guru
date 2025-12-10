# Core Web Vitals — Monitoramento

Versão: 1.0  
Última atualização: 2025-12-10  
Relacionado: PRD.md §7, docs/analytics/tracking-plan.md

---

## Metas

- LCP < 2.5s (bom), 2.5–4.0s (precisa melhorar), > 4.0s (ruim)  
- INP < 200ms (bom), 200–500ms (precisa melhorar), > 500ms (ruim)  
- CLS < 0.1 (bom), 0.1–0.25 (precisa melhorar), > 0.25 (ruim)

---

## Instrumentação

```html
<script src="https://unpkg.com/web-vitals@3/dist/web-vitals.iife.js"></script>
<script>
  (function(){
    const sendToGA = (metric) => {
      window.gtag && gtag('event', metric.name, {
        value: Math.round(metric.value),
        event_category: 'Web Vitals',
        event_label: metric.id,
        non_interaction: true
      });
    };
    webVitals.getLCP(sendToGA);
    webVitals.getINP(sendToGA);
    webVitals.getCLS(sendToGA);
  })();
 </script>
```

Alertas: integrar com Fluxo H (PRD §11.8) quando métricas piorarem por N dias consecutivos.

