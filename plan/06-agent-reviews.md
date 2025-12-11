# Revisao do Planejamento com Agentes Especializados

> **Data da Revisao**: 2025-12-10
> **Versao do Planejamento**: 1.0
> **Status**: Em Andamento

Este documento consolida as revisoes do planejamento feitas por cada agente especializado, identificando gaps, melhorias e validacoes.

---

## 1. DevOps Engineer

**Arquivo de Referencia**: `agents/devops-engineer.md`
**Tarefas no Planejamento**: 24 tarefas (Fases 1, 2, 4)

### Validacoes (OK)

- [x] Dockerfile multi-stage correto conforme especificacao do agente
- [x] docker-compose.yml inclui todos os servicos necessarios (db, redis, app, nginx, n8n, certbot)
- [x] Health checks configurados em todos os containers
- [x] Volumes persistentes para dados criticos
- [x] Nginx com configuracao de SSL e headers de seguranca
- [x] Makefile com comandos uteis planejado

### Gaps Identificados

| Gap | Descricao | Acao Necessaria | Prioridade |
|-----|-----------|-----------------|------------|
| GAP-D01 | Prometheus + Grafana nao esta no planejamento | Adicionar como opcional na Fase 4 | Baixa |
| GAP-D02 | Fail2Ban nao mencionado | Adicionar na secao de seguranca (Fase 4) | Media |
| GAP-D03 | GitHub Actions CI/CD nao detalhado | Adicionar tarefa especifica | Media |
| GAP-D04 | Script de backup nao esta nas tarefas | Ja esta em 4.7.4, OK | - |

### Melhorias Sugeridas

1. **Adicionar docker-compose.dev.yml separado**
   - Hot reload para desenvolvimento
   - Volumes montados para codigo fonte
   - Debug habilitado

2. **Adicionar servico de backup no docker-compose**
   - Container dedicado para pg_dump automatico
   - Rotacao de backups

3. **Rate limiting no Nginx**
   - Ja especificado no agente, garantir implementacao

### Novas Tarefas a Adicionar

| ID | Tarefa | Fase | Prioridade |
|----|--------|------|------------|
| 1.1.9 | Criar docker-compose.dev.yml (desenvolvimento) | 1 | Media |
| 4.3.5 | Configurar Fail2Ban no servidor | 4 | Media |
| 4.6.7 | Configurar GitHub Actions CI/CD | 4 | Media |
| 4.6.8 | (Opcional) Adicionar Prometheus + Grafana | 4 | Baixa |

---

## 2. Backend Developer

**Arquivo de Referencia**: `agents/backend-developer.md`
**Tarefas no Planejamento**: 32 tarefas (Fases 1, 2, 3, 4)

### Validacoes (OK)

- [x] Estrutura de pastas conforme especificacao do agente
- [x] FastAPI com middlewares planejado
- [x] Pydantic Settings para configuracao
- [x] SQLAlchemy async configurado
- [x] JWT com bcrypt planejado
- [x] Endpoints REST CRUD especificados

### Gaps Identificados

| Gap | Descricao | Acao Necessaria | Prioridade |
|-----|-----------|-----------------|------------|
| GAP-B01 | Logging estruturado (JSON) nao detalhado | Adicionar tarefa especifica | Media |
| GAP-B02 | Middleware de request logging ausente | Incluir em main.py | Media |
| GAP-B03 | Exception handlers globais nao mencionados | Adicionar na Fase 1 | Alta |
| GAP-B04 | Background tasks nao especificados | Adicionar para emails, etc | Baixa |

### Melhorias Sugeridas

1. **Adicionar exception handlers globais**
   ```python
   @app.exception_handler(HTTPException)
   @app.exception_handler(RequestValidationError)
   ```

2. **Middleware de logging estruturado**
   - JSON format para facilitar parsing
   - Request ID para rastreamento

3. **Health check mais completo**
   - Verificar conexao com DB
   - Verificar conexao com Redis

### Novas Tarefas a Adicionar

| ID | Tarefa | Fase | Prioridade |
|----|--------|------|------------|
| 1.2.7 | Implementar exception handlers globais | 1 | Alta |
| 1.2.8 | Configurar logging estruturado (JSON) | 1 | Media |
| 1.2.9 | Implementar health check completo (DB + Redis) | 1 | Media |

---

## 3. Database Architect

**Arquivo de Referencia**: `agents/database-architect.md`
**Tarefas no Planejamento**: 14 tarefas (Fases 1, 4)

### Validacoes (OK)

- [x] Todos os modelos principais especificados
- [x] UUID como primary key
- [x] Timestamps (created_at, updated_at)
- [x] Indices planejados
- [x] Alembic para migrations

### Gaps Identificados

| Gap | Descricao | Acao Necessaria | Prioridade |
|-----|-----------|-----------------|------------|
| GAP-DB01 | Triggers para updated_at nao mencionados | Adicionar trigger SQL | Media |
| GAP-DB02 | Funcoes de busca full-text nao planejadas | Adicionar para busca de posts | Media |
| GAP-DB03 | Particao de tabelas grandes nao considerada | Avaliar para affiliate_clicks | Baixa |
| GAP-DB04 | Views materializadas para analytics | Adicionar na Fase 4 | Baixa |

### Melhorias Sugeridas

1. **Trigger para updated_at automatico**
   ```sql
   CREATE OR REPLACE FUNCTION update_updated_at()
   RETURNS TRIGGER AS $$
   BEGIN
       NEW.updated_at = NOW();
       RETURN NEW;
   END;
   $$ LANGUAGE plpgsql;
   ```

2. **Indice GIN para busca full-text**
   ```sql
   CREATE INDEX idx_posts_search ON posts
   USING GIN(to_tsvector('portuguese', title || ' ' || content));
   ```

3. **View materializada para dashboard**
   - Agregacoes pre-calculadas
   - Refresh periodico

### Novas Tarefas a Adicionar

| ID | Tarefa | Fase | Prioridade |
|----|--------|------|------------|
| 1.3.11 | Criar trigger para updated_at automatico | 1 | Media |
| 1.3.12 | Implementar indice GIN para busca full-text | 1 | Media |
| 4.2.6 | Criar views materializadas para dashboards | 4 | Baixa |

---

## 4. Frontend Developer

**Arquivo de Referencia**: `agents/frontend-developer.md`
**Tarefas no Planejamento**: 20 tarefas (Fases 1, 2, 4)

### Validacoes (OK)

- [x] Templates Jinja2 especificados
- [x] Componentes reutilizaveis planejados
- [x] CSS com design system
- [x] Responsividade mobile-first
- [x] Acessibilidade (a11y) mencionada

### Gaps Identificados

| Gap | Descricao | Acao Necessaria | Prioridade |
|-----|-----------|-----------------|------------|
| GAP-F01 | Service Worker para PWA nao planejado | Adicionar como opcional | Baixa |
| GAP-F02 | Minificacao de CSS/JS no build nao detalhada | Especificar ferramentas | Media |
| GAP-F03 | Critical CSS inline nao mencionado | Adicionar para LCP | Media |
| GAP-F04 | Sprites SVG ou icon font nao definidos | Definir abordagem | Baixa |

### Melhorias Sugeridas

1. **Critical CSS inline no head**
   - Extrair CSS above-the-fold
   - Defer CSS nao-critico

2. **Preload de fontes**
   ```html
   <link rel="preload" href="/fonts/Inter.woff2" as="font" crossorigin>
   ```

3. **Image srcset para responsividade**
   ```html
   <img srcset="img-320.jpg 320w, img-640.jpg 640w" sizes="(max-width: 640px) 320px, 640px">
   ```

### Novas Tarefas a Adicionar

| ID | Tarefa | Fase | Prioridade |
|----|--------|------|------------|
| 1.8.10 | Definir estrategia de icones (SVG sprites) | 1 | Baixa |
| 4.6.7 | Implementar Critical CSS inline | 4 | Media |
| 4.6.8 | Configurar image srcset responsivo | 4 | Media |

---

## 5. Security Engineer

**Arquivo de Referencia**: `agents/security-engineer.md`
**Tarefas no Planejamento**: 14 tarefas (Fases 1, 4)

### Validacoes (OK)

- [x] OWASP Top 10 checklist incluido
- [x] JWT com bcrypt
- [x] Rate limiting planejado
- [x] CORS configurado
- [x] Headers de seguranca
- [x] LGPD compliance na Fase 4

### Gaps Identificados

| Gap | Descricao | Acao Necessaria | Prioridade |
|-----|-----------|-----------------|------------|
| GAP-S01 | CSP (Content Security Policy) nao detalhado | Especificar politica | Alta |
| GAP-S02 | Rotacao de secrets nao planejada | Adicionar procedimento | Media |
| GAP-S03 | Auditoria de dependencias (pip-audit) | Adicionar no CI/CD | Media |
| GAP-S04 | 2FA para admin nao mencionado | Considerar para futuro | Baixa |

### Melhorias Sugeridas

1. **Content Security Policy detalhado**
   ```
   Content-Security-Policy: default-src 'self'; script-src 'self' https://www.googletagmanager.com; img-src 'self' data: https:; style-src 'self' 'unsafe-inline';
   ```

2. **pip-audit no CI/CD**
   ```yaml
   - name: Security audit
     run: pip-audit --require-hashes
   ```

3. **Rotacao de JWT secrets**
   - Documentar procedimento
   - Sem downtime

### Novas Tarefas a Adicionar

| ID | Tarefa | Fase | Prioridade |
|----|--------|------|------------|
| 1.10.6 | Definir Content Security Policy (CSP) | 1 | Alta |
| 4.7.7 | Configurar pip-audit no CI/CD | 4 | Media |
| 4.7.8 | Documentar procedimento de rotacao de secrets | 4 | Media |

---

## 6. Automation Engineer

**Arquivo de Referencia**: `agents/automation-engineer.md`
**Tarefas no Planejamento**: 28 tarefas (Fases 2, 3, 4)

### Validacoes (OK)

- [x] Todos os workflows n8n especificados (A-F)
- [x] Integracao com OpenAI
- [x] APIs de afiliados planejadas
- [x] Notificacoes Telegram
- [x] Error handling em workflows

### Gaps Identificados

| Gap | Descricao | Acao Necessaria | Prioridade |
|-----|-----------|-----------------|------------|
| GAP-A01 | Workflow de limpeza de dados antigos | Adicionar Flow G | Baixa |
| GAP-A02 | Retry logic nao detalhado | Especificar em cada flow | Media |
| GAP-A03 | Rate limiting para APIs externas | Documentar limites | Media |
| GAP-A04 | Backup de workflows n8n | Adicionar export automatico | Baixa |

### Melhorias Sugeridas

1. **Retry configuration padrao**
   ```json
   {
     "retry": {
       "maxRetries": 3,
       "waitBetweenRetries": 5000
     }
   }
   ```

2. **Rate limiting por API**
   - Amazon: 1 req/sec
   - Mercado Livre: 10 req/sec
   - OpenAI: conforme plano

3. **Export automatico de workflows**
   - Cron diario exportando JSONs
   - Commit no repositorio

### Novas Tarefas a Adicionar

| ID | Tarefa | Fase | Prioridade |
|----|--------|------|------------|
| 2.5.7 | Documentar rate limits de APIs externas | 2 | Media |
| 3.3.6 | Configurar retry logic padrao em workflows | 3 | Media |
| 4.5.6 | Implementar export automatico de workflows n8n | 4 | Baixa |

---

## 7. SEO Specialist

**Arquivo de Referencia**: `agents/seo-specialist.md`
**Tarefas no Planejamento**: 18 tarefas (Fases 2, 3, 4)

### Validacoes (OK)

- [x] Sitemap.xml dinamico
- [x] Robots.txt otimizado
- [x] Schema.org completo (BlogPosting, Product, ItemList)
- [x] Open Graph e Twitter Cards
- [x] Canonical URLs

### Gaps Identificados

| Gap | Descricao | Acao Necessaria | Prioridade |
|-----|-----------|-----------------|------------|
| GAP-SEO01 | FAQ Schema nao mencionado | Adicionar para posts com FAQ | Media |
| GAP-SEO02 | Video Schema nao planejado | Considerar para futuro | Baixa |
| GAP-SEO03 | Sitemap de imagens nao especificado | Adicionar se muitas imagens | Baixa |
| GAP-SEO04 | AMP nao considerado | Avaliar necessidade | Baixa |

### Melhorias Sugeridas

1. **FAQ Schema para listicles**
   ```json
   {
     "@type": "FAQPage",
     "mainEntity": [...]
   }
   ```

2. **Sitemap index para sites grandes**
   - Separar posts, categorias, produtos

3. **Monitoramento de Core Web Vitals**
   - Integrar com Search Console API

### Novas Tarefas a Adicionar

| ID | Tarefa | Fase | Prioridade |
|----|--------|------|------------|
| 2.2.7 | Implementar FAQ Schema para posts com FAQ | 2 | Media |
| 2.1.7 | Criar sitemap index (se > 1000 URLs) | 2 | Baixa |

---

## 8. Content Strategist

**Arquivo de Referencia**: `agents/content-strategist.md`
**Tarefas no Planejamento**: 6 tarefas (Fases 3, 4)

### Validacoes (OK)

- [x] Personas definidas no PRD
- [x] Tom de voz especificado
- [x] Tipos de conteudo planejados
- [x] Calendario editorial mencionado

### Gaps Identificados

| Gap | Descricao | Acao Necessaria | Prioridade |
|-----|-----------|-----------------|------------|
| GAP-C01 | Guia de estilo editorial nao esta no codigo | Criar arquivo de referencia | Media |
| GAP-C02 | Templates de conteudo para IA nao versionados | Versionar em Git | Media |
| GAP-C03 | Processo de QA de conteudo gerado | Definir workflow de revisao | Alta |

### Melhorias Sugeridas

1. **Arquivo de guia editorial no repo**
   - `docs/content/style-guide.md`
   - Referenciar nos prompts

2. **QA de conteudo automatizado**
   - Verificar length minimo
   - Verificar keywords presentes
   - Verificar links funcionando

### Novas Tarefas a Adicionar

| ID | Tarefa | Fase | Prioridade |
|----|--------|------|------------|
| 3.1.6 | Criar guia de estilo editorial versionado | 3 | Media |
| 3.1.7 | Implementar QA automatizado de conteudo | 3 | Alta |

---

## 9. Data Analyst

**Arquivo de Referencia**: `agents/data-analyst.md`
**Tarefas no Planejamento**: 18 tarefas (Fases 1, 2, 4)

### Validacoes (OK)

- [x] KPIs definidos
- [x] GA4 configurado
- [x] Eventos customizados planejados
- [x] Dashboards especificados
- [x] A/B testing planejado

### Gaps Identificados

| Gap | Descricao | Acao Necessaria | Prioridade |
|-----|-----------|-----------------|------------|
| GAP-DA01 | Integracao com Search Console API | Adicionar para dashboard SEO | Media |
| GAP-DA02 | Cohort analysis nao planejado | Considerar para futuro | Baixa |
| GAP-DA03 | Funnel visualization | Adicionar no dashboard | Media |

### Melhorias Sugeridas

1. **Search Console API para dashboard SEO**
   - Queries e impressoes
   - Posicao media

2. **Funnel de conversao**
   - Pageview -> Scroll -> Click Affiliate -> (Conversao externa)

### Novas Tarefas a Adicionar

| ID | Tarefa | Fase | Prioridade |
|----|--------|------|------------|
| 4.2.7 | Integrar Search Console API no dashboard | 4 | Media |
| 4.2.8 | Implementar visualizacao de funnel | 4 | Media |

---

## 10. UX/UI Designer

**Arquivo de Referencia**: `agents/ux-ui-designer.md`
**Tarefas no Planejamento**: 4 tarefas (Fase 1)

### Validacoes (OK)

- [x] Design system definido
- [x] Paleta de cores especificada
- [x] Tipografia definida
- [x] Componentes de UI especificados

### Gaps Identificados

| Gap | Descricao | Acao Necessaria | Prioridade |
|-----|-----------|-----------------|------------|
| GAP-UX01 | Prototipo/mockups nao mencionados | Opcional, mas util | Baixa |
| GAP-UX02 | Testes de usabilidade nao planejados | Considerar na Fase 4 | Baixa |
| GAP-UX03 | Dark/Light theme switch nao especificado | Definir se necessario | Baixa |

### Melhorias Sugeridas

1. **Figma ou mockups de referencia**
   - Link para designs
   - Ou exportar como imagens

2. **Theme switch**
   - Implementar se houver demanda
   - CSS variables facilitam

---

## 11. Affiliate Marketing Specialist

**Arquivo de Referencia**: `agents/affiliate-marketing-specialist.md`
**Tarefas no Planejamento**: 2 tarefas (Fase 1)

### Validacoes (OK)

- [x] Sistema de redirecionamento planejado
- [x] Tracking de cliques especificado
- [x] Divulgacao de afiliados mencionada

### Gaps Identificados

| Gap | Descricao | Acao Necessaria | Prioridade |
|-----|-----------|-----------------|------------|
| GAP-AF01 | Dashboard especifico de afiliados nao detalhado | Ja esta em 4.2.3 | - |
| GAP-AF02 | Comparacao de performance entre plataformas | Adicionar metricas | Media |
| GAP-AF03 | EPC tracking nao implementavel (sem API conversao) | Documentar limitacao | Baixa |

### Melhorias Sugeridas

1. **Comparacao de plataformas**
   - CTR por plataforma
   - Produtos mais clicados por plataforma

2. **UTM parameters**
   - Adicionar UTMs aos links externos
   - Rastrear origem do trafego

---

## Resumo de Gaps por Prioridade

### Alta Prioridade

| ID | Gap | Agente | Acao |
|----|-----|--------|------|
| GAP-B03 | Exception handlers globais | Backend | Adicionar tarefa 1.2.7 |
| GAP-S01 | CSP nao detalhado | Security | Adicionar tarefa 1.10.6 |
| GAP-C03 | QA de conteudo gerado | Content | Adicionar tarefa 3.1.7 |

### Media Prioridade

| ID | Gap | Agente | Acao |
|----|-----|--------|------|
| GAP-D02 | Fail2Ban | DevOps | Adicionar tarefa 4.3.5 |
| GAP-D03 | GitHub Actions | DevOps | Adicionar tarefa 4.6.7 |
| GAP-B01 | Logging estruturado | Backend | Adicionar tarefa 1.2.8 |
| GAP-DB01 | Trigger updated_at | Database | Adicionar tarefa 1.3.11 |
| GAP-F03 | Critical CSS | Frontend | Adicionar tarefa 4.6.7 |
| GAP-A02 | Retry logic | Automation | Adicionar tarefa 3.3.6 |
| GAP-SEO01 | FAQ Schema | SEO | Adicionar tarefa 2.2.7 |
| GAP-C02 | Templates versionados | Content | Adicionar tarefa 3.1.6 |
| GAP-DA01 | Search Console API | Data | Adicionar tarefa 4.2.7 |

### Baixa Prioridade

| ID | Gap | Agente | Acao |
|----|-----|--------|------|
| GAP-D01 | Prometheus + Grafana | DevOps | Opcional |
| GAP-F01 | Service Worker PWA | Frontend | Futuro |
| GAP-A04 | Backup workflows n8n | Automation | Adicionar tarefa 4.5.6 |

---

## Conclusao da Revisao

### Estatisticas

- **Validacoes OK**: 52 itens
- **Gaps Alta Prioridade**: 3
- **Gaps Media Prioridade**: 10
- **Gaps Baixa Prioridade**: 6
- **Novas Tarefas Sugeridas**: 19

### Proximos Passos

1. Atualizar a tabela de controle (`01-control-table.md`) com as novas tarefas
2. Priorizar os 3 gaps de alta prioridade na Fase 1
3. Incluir gaps de media prioridade nas fases correspondentes
4. Avaliar gaps de baixa prioridade apos MVP

---

**Versao**: 1.0
**Data**: 2025-12-10
**Revisado por**: Todos os 11 agentes especializados
