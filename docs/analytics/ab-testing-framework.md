# Framework de Testes A/B — geek.bidu.guru

Versão: 1.0  
Última atualização: 2025-12-10  
Relacionado: PRD.md §6.14, docs/analytics/tracking-plan.md

---

## Processo

1) Hipótese (formato): "Se [mudança], então [impacto], porque [racional]"  
2) Priorizar via ICE (Impact, Confidence, Effort)  
3) Definir métrica primária (ex.: CTR de `affiliate_click`) e guardrails (bounce, tempo)  
4) Desenho do teste: variantes, divisão de tráfego, amostra mínima/duração  
5) Implementação: bucketização de usuários, exposição (`ab_exposure`), coleta de eventos  
6) Análise estatística (proporções/qui-quadrado)  
7) Decisão e rollout do vencedor  
8) Registro de aprendizados (wiki)

---

## Instrumentação

- GA4: incluir `ab_test_id` e `ab_variant` em `affiliate_click`, e disparar `ab_exposure` na renderização do CTA.  
- Backend: opcionalmente registrar exposições/eventos em `ab_tests` e `ab_test_events` para auditoria.

### Esquema sugerido (backend)

`ab_tests`  
- `id` (UUID, PK)  
- `name`, `hypothesis`, `primary_metric`  
- `area` (ex.: `cta_button`)  
- `start_at`, `end_at`, `status` (`running|paused|completed`)  
- `variant_a_pct`, `variant_b_pct`

`ab_test_events`  
- `id` (PK)  
- `test_id` (FK)  
- `variant` (`A|B`)  
- `session_id`  
- `event_type` (`exposure|view|click`)  
- `occurred_at`

---

## Amostra e Significância

- N mínimo por variante: usar calculadora (baseline CTR, lift esperado, power 80%, alfa 5%).  
- Duração recomendada: ≥ 7 dias cobrindo ciclos semanais.  
- Encerrar cedo apenas com critérios pré-definidos.

---

## Roadmap Inicial de Testes (6 meses)

1) Cor do botão CTA (amarelo vs verde) — métrica: CTR  
2) Posição do CTA (início vs meio) — métrica: CTR  
3) Texto do CTA ("Ver Preço" vs "Ver Oferta") — métricas: CTR + conversão  
4) Tabela comparativa vs lista simples — métrica: tempo na página  
5) Sidebar sticky (desktop) — métrica: cliques em sidebar

