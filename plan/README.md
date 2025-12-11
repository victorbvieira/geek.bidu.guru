# Planejamento do Projeto geek.bidu.guru

Este diretorio contem o planejamento completo para execucao do projeto **geek.bidu.guru** - um blog de presentes geek com monetizacao via afiliados.

---

## Infraestrutura de Producao

### VPS Hostinger KVM8 + Easypanel

O projeto sera hospedado em uma **VPS Hostinger KVM8** gerenciada pelo **Easypanel**, aproveitando servicos ja existentes:

```
┌─────────────────────────────────────────────────────────────┐
│                VPS Hostinger KVM8 (Easypanel)               │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  SERVICOS COMPARTILHADOS (ja existentes):                   │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐            │
│  │ PostgreSQL │  │    n8n     │  │  Traefik   │            │
│  │ (DB Pool)  │  │ (Workflows)│  │ (SSL/Proxy)│            │
│  └────────────┘  └────────────┘  └────────────┘            │
│                                                             │
│  PROJETO: geek-bidu-guru (NOVO):                           │
│  ┌─────────────────────────────────────────────┐           │
│  │  app (FastAPI + Jinja2)                     │           │
│  │  redis (cache - opcional)                   │           │
│  │  volumes (static files)                     │           │
│  └─────────────────────────────────────────────┘           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### O que vamos criar vs. O que ja existe

| Componente | Status | Acao |
|------------|--------|------|
| PostgreSQL | :white_check_mark: Existente | Criar databases: `geek_bidu_dev` e `geek_bidu_prod` |
| n8n | :white_check_mark: Existente | Criar workflows especificos |
| Traefik | :white_check_mark: Existente | Configurar dominio `geek.bidu.guru` |
| **App FastAPI** | :new: Novo | Criar container no projeto Easypanel |
| **Redis** | :new: Novo (opcional) | Adicionar ao projeto se necessario |

### Vantagens desta Arquitetura

1. **Simplicidade**: Um unico container para a aplicacao
2. **Recursos Compartilhados**: PostgreSQL e n8n ja configurados e funcionando
3. **SSL Automatico**: Traefik gerencia certificados Let's Encrypt
4. **Deploy Facil**: Push para GitHub → build automatico no Easypanel
5. **Custo Otimizado**: Sem necessidade de servicos adicionais

---

## Estrutura do Planejamento

| Arquivo | Descricao |
|---------|-----------|
| [00-overview.md](00-overview.md) | Visao geral do projeto, stack, estrutura de pastas |
| [01-control-table.md](01-control-table.md) | **TABELA DE CONTROLE** - 193+ tarefas detalhadas |
| [02-phase-1-technical-base.md](02-phase-1-technical-base.md) | Fase 1: Base Tecnica (Docker, FastAPI, DB) |
| [03-phase-2-seo-automation.md](03-phase-2-seo-automation.md) | Fase 2: SEO & Automacao (Schema.org, n8n) |
| [04-phase-3-ai-i18n.md](04-phase-3-ai-i18n.md) | Fase 3: IA & Internacionalizacao |
| [05-phase-4-growth-optimization.md](05-phase-4-growth-optimization.md) | Fase 4: Growth & Otimizacao |
| [06-agent-reviews.md](06-agent-reviews.md) | **REVISAO DOS AGENTES** - Gaps e melhorias identificados |

---

## Como Usar Este Planejamento

### 1. Comece pela Visao Geral
Leia [00-overview.md](00-overview.md) para entender o projeto completo.

### 2. Use a Tabela de Controle
[01-control-table.md](01-control-table.md) contem **193+ tarefas** organizadas por fase e agente.

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

### 5. Consulte a Revisao dos Agentes
O documento [06-agent-reviews.md](06-agent-reviews.md) contem:
- Validacoes de cada agente sobre o planejamento
- Gaps identificados por prioridade (Alta, Media, Baixa)
- Novas tarefas adicionadas apos revisao
- Melhorias sugeridas

---

## Resumo das Fases

### Fase 1: Base Tecnica
**74 tarefas** | Agentes: DevOps, Backend, Database, Frontend, Security

- **Easypanel**: Criar projeto `geek-bidu-guru` e configurar servico `app`
- **Dockerfile**: Imagem otimizada para FastAPI
- **PostgreSQL**: Criar database `geek_bidu_guru` no container compartilhado
- FastAPI com estrutura completa
- Autenticacao JWT
- CRUD de posts e produtos
- Templates Jinja2 basicos
- Sistema de redirecionamento de afiliados
- **[NOVO]** Exception handlers, logging estruturado, CSP
- **Docker Compose local**: Ambiente de desenvolvimento simulando producao

### Fase 2: SEO & Automacao
**50 tarefas** | Agentes: SEO, Automation, Data Analyst, DevOps

- Sitemap.xml e robots.txt
- Schema.org (BlogPosting, Product, ItemList, FAQ)
- Open Graph e Twitter Cards
- **n8n (compartilhado)**: Criar workflows especificos do projeto
- Workflows A, B, C (posts, listicles, precos)
- Google Analytics 4
- **[NOVO]** FAQ Schema, rate limits documentados

### Fase 3: IA & Internacionalizacao
**30 tarefas** | Agentes: Automation, Content, Backend, SEO

- Prompts otimizados por tipo de post
- Workflow E (pesquisa de produtos)
- Workflow F (monitor de deals)
- Cache Redis
- Sistema i18n (pt-BR base)
- **[NOVO]** QA automatizado de conteudo, retry logic

### Fase 4: Growth & Otimizacao
**50 tarefas** | Agentes: Data Analyst, DevOps, Automation, Security

- Sistema de A/B testing
- Dashboards de analytics
- Sistema de alertas
- Newsletter
- Social sharing automatizado
- Otimizacao de performance
- LGPD compliance
- Documentacao final
- **[NOVO]** Search Console API, Critical CSS, pip-audit

---

## Distribuicao por Agente (Atualizada)

| Agente | Tarefas | Principal em |
|--------|---------|--------------|
| Backend Developer | 35 | Fases 1, 2, 3, 4 |
| Automation Engineer | 30 | Fases 2, 3, 4 |
| DevOps Engineer | 25 | Fases 1, 2, 4 |
| Frontend Developer | 22 | Fases 1, 2, 4 |
| SEO Specialist | 20 | Fases 2, 3, 4 |
| Data Analyst | 20 | Fases 1, 2, 4 |
| Database Architect | 16 | Fases 1, 4 |
| Security Engineer | 17 | Fases 1, 4 |
| Content Strategist | 8 | Fases 3, 4 |
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

1. ~~Revisar este planejamento com cada agente especializado~~ :white_check_mark: **Concluido**
2. Criar a pasta `src/` com a estrutura inicial
3. Iniciar a **Fase 1** pelo item 1.1.1 (Dockerfile)
4. Atualizar a tabela de controle conforme progresso
5. Priorizar os 3 gaps de alta prioridade identificados na revisao

---

**Versao do Planejamento**: 1.2 (atualizado para Easypanel + VPS Hostinger)
**Data**: 2025-12-11
**Projeto**: geek.bidu.guru
**Total de Tarefas**: 193+
