# Planejamento do Projeto geek.bidu.guru

Este diretorio contem o planejamento completo para execucao do projeto **geek.bidu.guru** - um blog de presentes geek com monetizacao via afiliados.

---

## Estrutura do Planejamento

| Arquivo | Descricao |
|---------|-----------|
| [00-overview.md](00-overview.md) | Visao geral do projeto, stack, estrutura de pastas |
| [01-control-table.md](01-control-table.md) | **TABELA DE CONTROLE** - 187 tarefas detalhadas |
| [02-phase-1-technical-base.md](02-phase-1-technical-base.md) | Fase 1: Base Tecnica (Docker, FastAPI, DB) |
| [03-phase-2-seo-automation.md](03-phase-2-seo-automation.md) | Fase 2: SEO & Automacao (Schema.org, n8n) |
| [04-phase-3-ai-i18n.md](04-phase-3-ai-i18n.md) | Fase 3: IA & Internacionalizacao |
| [05-phase-4-growth-optimization.md](05-phase-4-growth-optimization.md) | Fase 4: Growth & Otimizacao |

---

## Como Usar Este Planejamento

### 1. Comece pela Visao Geral
Leia [00-overview.md](00-overview.md) para entender o projeto completo.

### 2. Use a Tabela de Controle
[01-control-table.md](01-control-table.md) contem **187 tarefas** organizadas por fase e agente.

**Atualize o status conforme o progresso:**
- :white_large_square: Pendente
- :arrow_forward: Em Progresso
- :eyes: Em Revisao
- :white_check_mark: Concluido
- :no_entry: Bloqueado

### 3. Execute Fase por Fase
Siga a ordem das fases:
1. **Fase 1** - Base Tecnica (critica)
2. **Fase 2** - SEO & Automacao (alta)
3. **Fase 3** - IA & i18n (media)
4. **Fase 4** - Growth & Otimizacao (normal)

### 4. Consulte os Agentes
Antes de cada tarefa, consulte o agente especializado em `agents/`:

| Area | Agente |
|------|--------|
| Backend | [backend-developer.md](../agents/backend-developer.md) |
| Banco de Dados | [database-architect.md](../agents/database-architect.md) |
| DevOps | [devops-engineer.md](../agents/devops-engineer.md) |
| Frontend | [frontend-developer.md](../agents/frontend-developer.md) |
| Automacao | [automation-engineer.md](../agents/automation-engineer.md) |
| Seguranca | [security-engineer.md](../agents/security-engineer.md) |
| SEO | [seo-specialist.md](../agents/seo-specialist.md) |
| Conteudo | [content-strategist.md](../agents/content-strategist.md) |
| Analytics | [data-analyst.md](../agents/data-analyst.md) |
| Design | [ux-ui-designer.md](../agents/ux-ui-designer.md) |
| Afiliados | [affiliate-marketing-specialist.md](../agents/affiliate-marketing-specialist.md) |

---

## Resumo das Fases

### Fase 1: Base Tecnica
**68 tarefas** | Agentes: DevOps, Backend, Database, Frontend, Security

- Docker & Docker Compose
- FastAPI com estrutura completa
- PostgreSQL com schema
- Autenticacao JWT
- CRUD de posts e produtos
- Templates Jinja2 basicos
- Sistema de redirecionamento de afiliados

### Fase 2: SEO & Automacao
**48 tarefas** | Agentes: SEO, Automation, Data Analyst, DevOps

- Sitemap.xml e robots.txt
- Schema.org (BlogPosting, Product, ItemList)
- Open Graph e Twitter Cards
- n8n configurado
- Workflows A, B, C (posts, listicles, precos)
- Google Analytics 4

### Fase 3: IA & Internacionalizacao
**26 tarefas** | Agentes: Automation, Content, Backend, SEO

- Prompts otimizados por tipo de post
- Workflow E (pesquisa de produtos)
- Workflow F (monitor de deals)
- Cache Redis
- Sistema i18n (pt-BR base)

### Fase 4: Growth & Otimizacao
**45 tarefas** | Agentes: Data Analyst, DevOps, Automation, Security

- Sistema de A/B testing
- Dashboards de analytics
- Sistema de alertas
- Newsletter
- Social sharing automatizado
- Otimizacao de performance
- LGPD compliance
- Documentacao final

---

## Distribuicao por Agente

| Agente | Tarefas | Principal em |
|--------|---------|--------------|
| Backend Developer | 32 | Fases 1, 2, 3, 4 |
| Automation Engineer | 28 | Fases 2, 3, 4 |
| DevOps Engineer | 24 | Fases 1, 2, 4 |
| Frontend Developer | 20 | Fases 1, 2, 4 |
| SEO Specialist | 18 | Fases 2, 3, 4 |
| Data Analyst | 18 | Fases 1, 2, 4 |
| Database Architect | 14 | Fases 1, 4 |
| Security Engineer | 14 | Fases 1, 4 |
| Content Strategist | 6 | Fases 3, 4 |
| UX/UI Designer | 4 | Fase 1 |
| Affiliate Marketing | 2 | Fase 1 |

---

## Documentos de Referencia

| Documento | Descricao |
|-----------|-----------|
| [PRD.md](../PRD.md) | Documento de Requisitos (v1.4) |
| [PRD-design-system.md](../PRD-design-system.md) | Sistema de Design |
| [PRD-affiliate-strategy.md](../PRD-affiliate-strategy.md) | Estrategia de Afiliados |
| [PRD-internationalization.md](../PRD-internationalization.md) | Internacionalizacao |
| [docs/analytics/tracking-plan.md](../docs/analytics/tracking-plan.md) | Plano GA4 |

---

## Proximos Passos

1. Revisar este planejamento com cada agente especializado
2. Criar a pasta `src/` com a estrutura inicial
3. Iniciar a **Fase 1** pelo item 1.1.1 (Dockerfile)
4. Atualizar a tabela de controle conforme progresso

---

**Versao do Planejamento**: 1.0
**Data**: 2025-12-10
**Projeto**: geek.bidu.guru
**Total de Tarefas**: 187
