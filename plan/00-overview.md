# Planejamento do Projeto - geek.bidu.guru

## Visao Geral

**Projeto**: geek.bidu.guru - Blog de Presentes Geek
**Versao do PRD**: 1.4
**Data de Inicio**: 2025-12-10
**Status**: Planejamento

---

## Objetivos do Projeto

O **geek.bidu.guru** e um blog/portal brasileiro focado em curadoria de presentes e produtos geek, com monetizacao via programas de afiliados (Amazon, Mercado Livre, Shopee).

### Objetivos Principais

1. **Curadoria Automatizada**: Gerar conteudo de qualidade com minimo trabalho manual usando n8n + IA
2. **SEO Otimizado**: Ranquear nas primeiras posicoes para keywords de alta intencao de compra
3. **Monetizacao**: Gerar receita consistente atraves de links de afiliados
4. **Escalabilidade**: Arquitetura preparada para crescer (Docker, cache, CDN)

### Metas de KPIs

| Metrica | 3 meses | 6 meses | 12 meses |
|---------|---------|---------|----------|
| Visitantes/mes | 5.000 | 15.000 | 50.000 |
| Receita mensal | R$ 500 | R$ 2.000 | R$ 5.000+ |
| Posts publicados | 100 | 300 | 700+ |
| Keywords ranqueadas | 50 | 150 | 500+ |

---

## Stack Tecnologica

### Backend
- **Python 3.11+** - Linguagem principal
- **FastAPI** - Framework web (async, alta performance)
- **SQLAlchemy** - ORM
- **Pydantic** - Validacao de dados
- **Alembic** - Migrations de banco de dados

### Frontend
- **Jinja2** - Templates (SSR)
- **HTML5** - Semantico
- **CSS3** - Dark theme padrao, responsivo
- **JavaScript** - Vanilla, minimo necessario

### Banco de Dados
- **PostgreSQL 15+** - Banco principal
- **Redis** - Cache (sessoes, queries)

### Infraestrutura
- **Docker** & **Docker Compose** - Containerizacao
- **Nginx** - Reverse proxy, SSL
- **Certbot** - Certificados Let's Encrypt

### Automacao
- **n8n** - Orquestracao de workflows
- **OpenAI API** - Geracao de conteudo com IA
- **APIs de Afiliados** - Amazon, Mercado Livre, Shopee

### Analytics
- **Google Analytics 4** - Tracking de usuarios
- **Google Search Console** - SEO e indexacao
- **Dashboards customizados** - PostgreSQL + Admin

---

## Fases do Projeto

O projeto esta dividido em **4 fases principais**, conforme definido no PRD:

### Fase 1: Base Tecnica
**Prioridade**: Critica
**Objetivo**: Infraestrutura funcional com MVP do blog

Entregaveis:
- Ambiente Docker completo
- Backend FastAPI funcional
- Banco de dados PostgreSQL com schema
- Sistema de autenticacao JWT
- Templates Jinja2 basicos
- CRUD de posts e produtos
- Sistema de redirecionamento de afiliados

### Fase 2: SEO & Automacao
**Prioridade**: Alta
**Objetivo**: Otimizacao para SEO e automacao com n8n

Entregaveis:
- Sitemap.xml dinamico
- Robots.txt otimizado
- Schema.org (BlogPosting, Product, ItemList)
- Open Graph / Twitter Cards
- Workflows n8n (posts diarios, listicles semanais)
- Integracao com APIs de afiliados
- Sistema de tracking GA4

### Fase 3: IA & Internacionalizacao
**Prioridade**: Media
**Objetivo**: Conteudo inteligente e expansao

Entregaveis:
- Geracao de conteudo com IA
- Pesquisa automatizada de produtos
- Monitoramento de deals
- Sistema de i18n (pt-BR base)
- Cache Redis otimizado

### Fase 4: Growth & Otimizacao
**Prioridade**: Normal
**Objetivo**: Escala e otimizacao continua

Entregaveis:
- Sistema de A/B testing
- Dashboards de analytics
- Alertas e monitoramento
- Otimizacao de performance
- Sistema de newsletter
- Compartilhamento social automatizado

---

## Estrutura de Pastas do Projeto

```
geek.bidu.guru/
├── src/                          # CODIGO FONTE DA APLICACAO
│   ├── app/
│   │   ├── main.py               # Entry point FastAPI
│   │   ├── config.py             # Configuracoes
│   │   ├── database.py           # Conexao PostgreSQL
│   │   ├── api/
│   │   │   └── v1/               # Endpoints REST API
│   │   │       ├── posts.py
│   │   │       ├── products.py
│   │   │       ├── auth.py
│   │   │       ├── affiliates.py
│   │   │       └── analytics.py
│   │   ├── models/               # Modelos SQLAlchemy
│   │   │   ├── post.py
│   │   │   ├── product.py
│   │   │   ├── user.py
│   │   │   └── analytics.py
│   │   ├── schemas/              # Pydantic schemas
│   │   │   ├── post.py
│   │   │   ├── product.py
│   │   │   ├── user.py
│   │   │   └── analytics.py
│   │   ├── services/             # Logica de negocio
│   │   │   ├── post_service.py
│   │   │   ├── product_service.py
│   │   │   ├── affiliate_service.py
│   │   │   └── seo_service.py
│   │   ├── routers/              # Rotas SSR (site)
│   │   │   ├── home.py
│   │   │   ├── post.py
│   │   │   ├── category.py
│   │   │   └── search.py
│   │   ├── templates/            # Jinja2 templates
│   │   │   ├── base.html
│   │   │   ├── home.html
│   │   │   ├── post.html
│   │   │   ├── category.html
│   │   │   ├── search.html
│   │   │   └── components/
│   │   │       ├── header.html
│   │   │       ├── footer.html
│   │   │       ├── product_card.html
│   │   │       ├── post_card.html
│   │   │       └── seo_meta.html
│   │   ├── static/               # Arquivos estaticos
│   │   │   ├── css/
│   │   │   │   ├── main.css
│   │   │   │   └── components/
│   │   │   ├── js/
│   │   │   │   ├── main.js
│   │   │   │   └── analytics.js
│   │   │   └── images/
│   │   └── utils/                # Utilitarios
│   │       ├── security.py
│   │       ├── cache.py
│   │       └── helpers.py
│   ├── tests/                    # Testes automatizados
│   │   ├── unit/
│   │   ├── integration/
│   │   └── e2e/
│   └── migrations/               # Alembic migrations
│       ├── alembic.ini
│       ├── env.py
│       └── versions/
├── docker/                       # Configuracoes Docker
│   ├── Dockerfile
│   ├── docker-compose.yml
│   ├── docker-compose.prod.yml
│   └── nginx/
│       └── nginx.conf
├── n8n/                          # Workflows n8n (exportados)
│   ├── workflows/
│   │   ├── flow-a-daily-post.json
│   │   ├── flow-b-weekly-listicle.json
│   │   ├── flow-c-price-update.json
│   │   ├── flow-d-social-share.json
│   │   ├── flow-e-product-research.json
│   │   └── flow-f-deal-monitor.json
│   └── credentials/
├── plan/                         # Planejamento do projeto
│   ├── 00-overview.md            # Este arquivo
│   ├── 01-control-table.md       # Tabela de controle
│   ├── 02-phase-1-technical-base.md
│   ├── 03-phase-2-seo-automation.md
│   ├── 04-phase-3-ai-i18n.md
│   ├── 05-phase-4-growth-optimization.md
│   └── README.md
├── agents/                       # Agentes especializados
├── docs/                         # Documentacao auxiliar
├── reports/                      # Relatorios e analises
├── .env.example                  # Variaveis de ambiente
├── requirements.txt              # Dependencias Python
├── Makefile                      # Comandos uteis
├── PRD.md                        # Documento de requisitos
└── README.md                     # Documentacao principal
```

---

## Agentes Especializados

O projeto conta com **11 agentes especializados** para diferentes areas:

### Agentes de Negocio
| Agente | Arquivo | Area Principal |
|--------|---------|----------------|
| SEO Specialist | `agents/seo-specialist.md` | SEO, keywords, meta tags |
| Content Strategist | `agents/content-strategist.md` | Conteudo, tom de voz, personas |
| Affiliate Marketing | `agents/affiliate-marketing-specialist.md` | Links, CTR, conversao |
| UX/UI Designer | `agents/ux-ui-designer.md` | Design, cores, layouts |
| Data Analyst | `agents/data-analyst.md` | Metricas, KPIs, analytics |

### Agentes Tecnicos
| Agente | Arquivo | Area Principal |
|--------|---------|----------------|
| Backend Developer | `agents/backend-developer.md` | FastAPI, APIs, Python |
| Database Architect | `agents/database-architect.md` | PostgreSQL, queries, modelagem |
| DevOps Engineer | `agents/devops-engineer.md` | Docker, deploy, infraestrutura |
| Automation Engineer | `agents/automation-engineer.md` | n8n, workflows, IA |
| Frontend Developer | `agents/frontend-developer.md` | Jinja2, HTML/CSS/JS |
| Security Engineer | `agents/security-engineer.md` | Seguranca, OWASP, LGPD |

---

## Documentacao de Referencia

| Documento | Descricao |
|-----------|-----------|
| `PRD.md` | Documento de requisitos completo (v1.4) |
| `PRD-design-system.md` | Sistema de design (cores, tipografia, componentes) |
| `PRD-affiliate-strategy.md` | Estrategia de afiliados |
| `PRD-internationalization.md` | Internacionalizacao |
| `docs/analytics/tracking-plan.md` | Plano de tracking GA4 |
| `reports/consolidated-analysis.md` | Analise consolidada dos especialistas |

---

## Proximos Passos

1. Revisar a **Tabela de Controle** (`01-control-table.md`) para visao de todas as tarefas
2. Iniciar pela **Fase 1** (`02-phase-1-technical-base.md`) - Base Tecnica
3. Consultar o agente apropriado antes de cada tarefa
4. Atualizar status das tarefas conforme progresso

---

**Versao**: 1.0
**Data**: 2025-12-10
**Projeto**: geek.bidu.guru
