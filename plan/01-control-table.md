# Tabela de Controle de Tarefas - geek.bidu.guru

> **Instrucoes**: Atualize o status de cada tarefa conforme o progresso. Use esta tabela como fonte unica de verdade para o acompanhamento do projeto.

## Legenda de Status

| Status | Simbolo | Descricao |
|--------|---------|-----------|
| Pendente | :white_large_square: | Tarefa ainda nao iniciada |
| Em Progresso | :arrow_forward: | Tarefa em andamento |
| Em Revisao | :eyes: | Aguardando revisao/aprovacao |
| Concluido | :white_check_mark: | Tarefa finalizada |
| Bloqueado | :no_entry: | Tarefa bloqueada por dependencia |

---

# FASE 1: BASE TECNICA

## 1.0 Infraestrutura Easypanel (Producao - VPS Hostinger KVM8)

> **NOTA**: PostgreSQL, n8n e Traefik ja existem na VPS. Vamos apenas criar o projeto e databases.

| ID | Tarefa | Agente | Dependencia | Status | Notas |
|----|--------|--------|-------------|--------|-------|
| 1.0.1 | Criar projeto `geek-bidu-guru` no Easypanel | DevOps Engineer | - | :white_check_mark: | Via interface web |
| 1.0.2 | Criar database `geek_bidu_dev` no PostgreSQL | Database Architect | - | :white_check_mark: | Usuario: `geek_app_dev` |
| 1.0.3 | Criar database `geek_bidu_prod` no PostgreSQL | Database Architect | - | :white_check_mark: | Usuario: `geek_app_prod` |
| 1.0.4 | Configurar dominio `geek.bidu.guru` no Traefik | DevOps Engineer | 1.0.1 | :white_check_mark: | SSL automatico |
| 1.0.5 | Configurar variaveis de ambiente no Easypanel | DevOps Engineer | 1.0.3 | :white_check_mark: | DATABASE_URL, SECRET_KEY, etc |

## 1.1 Infraestrutura Docker (Desenvolvimento Local)

| ID | Tarefa | Agente | Dependencia | Status | Notas |
|----|--------|--------|-------------|--------|-------|
| 1.1.1 | Criar Dockerfile para aplicacao FastAPI | DevOps Engineer | - | :white_check_mark: | Multi-stage build |
| 1.1.2 | Criar docker-compose.yml (dev local) | DevOps Engineer | 1.1.1 | :white_check_mark: | db, redis, app |
| 1.1.3 | Configurar servico PostgreSQL local | DevOps Engineer | 1.1.2 | :white_check_mark: | No docker-compose |
| 1.1.4 | Configurar servico Redis local | DevOps Engineer | 1.1.2 | :white_check_mark: | No docker-compose |
| 1.1.5 | Configurar .env.example | DevOps Engineer | - | :white_check_mark: | Completo |
| 1.1.6 | Criar Makefile com comandos uteis | DevOps Engineer | 1.1.2 | :white_check_mark: | 25+ comandos |
| 1.1.7 | Criar .dockerignore | DevOps Engineer | 1.1.1 | :white_check_mark: | Completo |

## 1.2 Backend FastAPI - Estrutura Base

| ID | Tarefa | Agente | Dependencia | Status | Notas |
|----|--------|--------|-------------|--------|-------|
| 1.2.1 | Criar estrutura de pastas src/app/ | Backend Developer | 1.1.2 | :white_check_mark: | Conforme PRD |
| 1.2.2 | Implementar main.py (entry point) | Backend Developer | 1.2.1 | :white_check_mark: | FastAPI + lifespan |
| 1.2.3 | Implementar config.py (Settings) | Backend Developer | 1.2.1 | :white_check_mark: | Pydantic Settings |
| 1.2.4 | Implementar database.py (conexao) | Backend Developer | 1.2.3 | :white_check_mark: | SQLAlchemy async |
| 1.2.5 | Configurar requirements.txt | Backend Developer | - | :white_check_mark: | 30+ dependencias |
| 1.2.6 | Configurar Alembic | Database Architect | 1.2.4 | :white_check_mark: | alembic.ini, env.py configurados |
| 1.2.7 | Implementar exception handlers globais | Backend Developer | 1.2.2 | :white_check_mark: | HTTPException, ValidationError em main.py |
| 1.2.8 | Configurar logging estruturado (JSON) | Backend Developer | 1.2.2 | :white_check_mark: | core/logging.py + pythonjsonlogger |
| 1.2.9 | Implementar health check completo | Backend Developer | 1.2.4 | :white_check_mark: | Verifica DB |

## 1.3 Banco de Dados - Schema

| ID | Tarefa | Agente | Dependencia | Status | Notas |
|----|--------|--------|-------------|--------|-------|
| 1.3.1 | Criar modelo User | Database Architect | 1.2.6 | :white_check_mark: | Roles: admin, editor, author, automation |
| 1.3.2 | Criar modelo Post | Database Architect | 1.2.6 | :white_check_mark: | UUID, slug, SEO fields, status workflow |
| 1.3.3 | Criar modelo Product | Database Architect | 1.2.6 | :white_check_mark: | Affiliate links, prices, platforms |
| 1.3.4 | Criar modelo PostProducts (N:N) | Database Architect | 1.3.2, 1.3.3 | :white_check_mark: | Relationship table |
| 1.3.5 | Criar modelo Category | Database Architect | 1.2.6 | :white_check_mark: | Slug, parent_id, hierarquia |
| 1.3.6 | Criar modelo AffiliateClick | Database Architect | 1.3.3 | :white_check_mark: | Tracking de cliques |
| 1.3.7 | Criar modelo Session | Database Architect | 1.2.6 | :white_check_mark: | models/session.py |
| 1.3.8 | Criar modelo NewsletterSignup | Database Architect | 1.2.6 | :white_check_mark: | Email marketing |
| 1.3.9 | Criar indices otimizados | Database Architect | 1.3.1-1.3.8 | :white_check_mark: | Conforme PRD |
| 1.3.10 | Criar migration inicial | Database Architect | 1.3.9 | :white_check_mark: | alembic revision aplicada |
| 1.3.11 | Criar trigger para updated_at automatico | Database Architect | 1.3.10 | :white_check_mark: | Migration 002 |
| 1.3.12 | Implementar indice GIN para busca full-text | Database Architect | 1.3.10 | :white_check_mark: | Migration 002 |

## 1.4 Backend - Autenticacao

| ID | Tarefa | Agente | Dependencia | Status | Notas |
|----|--------|--------|-------------|--------|-------|
| 1.4.1 | Implementar core/security.py | Security Engineer | 1.2.1 | :white_check_mark: | bcrypt + JWT (access/refresh tokens) |
| 1.4.2 | Criar Pydantic schemas auth | Backend Developer | 1.4.1 | :white_check_mark: | TokenResponse, RefreshTokenRequest |
| 1.4.3 | Implementar api/v1/auth.py | Backend Developer | 1.4.2 | :white_check_mark: | /login, /me, /refresh |
| 1.4.4 | Implementar dependencia get_current_user | Backend Developer | 1.4.3 | :white_check_mark: | core/deps.py |
| 1.4.5 | Implementar controle de roles | Security Engineer | 1.4.4 | :white_check_mark: | require_role(), ActiveUser |
| 1.4.6 | Criar middleware de rate limiting | Security Engineer | 1.2.2 | :white_check_mark: | SlowAPI + 3 testes |

## 1.5 Backend - CRUD Posts

| ID | Tarefa | Agente | Dependencia | Status | Notas |
|----|--------|--------|-------------|--------|-------|
| 1.5.1 | Criar Pydantic schemas Post | Backend Developer | 1.3.2 | :white_check_mark: | Create, Update, Response, StatusUpdate |
| 1.5.2 | Implementar repositories/post.py | Backend Developer | 1.5.1 | :white_check_mark: | Business logic no repositorio |
| 1.5.3 | Implementar api/v1/posts.py | Backend Developer | 1.5.2 | :white_check_mark: | REST CRUD completo |
| 1.5.4 | Implementar geracao de slug | Backend Developer | 1.5.2 | :white_check_mark: | Unique, SEO friendly |
| 1.5.5 | Implementar paginacao | Backend Developer | 1.5.3 | :white_check_mark: | Offset-based com PaginatedResponse |
| 1.5.6 | Implementar filtros (categoria, status) | Backend Developer | 1.5.3 | :white_check_mark: | Query params |

## 1.6 Backend - CRUD Products

| ID | Tarefa | Agente | Dependencia | Status | Notas |
|----|--------|--------|-------------|--------|-------|
| 1.6.1 | Criar Pydantic schemas Product | Backend Developer | 1.3.3 | :white_check_mark: | Create, Update, Response, PriceUpdate |
| 1.6.2 | Implementar repositories/product.py | Backend Developer | 1.6.1 | :white_check_mark: | Business logic |
| 1.6.3 | Implementar api/v1/products.py | Backend Developer | 1.6.2 | :white_check_mark: | REST CRUD completo |
| 1.6.4 | Implementar vinculacao post-product | Backend Developer | 1.5.3, 1.6.3 | :white_check_mark: | N:N via post_products |

## 1.7 Backend - Sistema de Afiliados

| ID | Tarefa | Agente | Dependencia | Status | Notas |
|----|--------|--------|-------------|--------|-------|
| 1.7.1 | Implementar api/v1/clicks.py | Backend Developer | 1.6.2 | :white_check_mark: | Registro de cliques |
| 1.7.2 | Implementar rota /goto/{slug} | Backend Developer | 1.7.1 | :white_check_mark: | routers/affiliates.py + 11 testes |
| 1.7.3 | Implementar tracking de cliques | Data Analyst | 1.7.2 | :white_check_mark: | Salvar em affiliate_clicks |
| 1.7.4 | Criar endpoint de estatisticas | Data Analyst | 1.7.3 | :white_check_mark: | /api/v1/clicks/analytics |

## 1.8 Frontend - Templates Base

| ID | Tarefa | Agente | Dependencia | Status | Notas |
|----|--------|--------|-------------|--------|-------|
| 1.8.1 | Criar templates/base.html | Frontend Developer | 1.2.2 | :white_check_mark: | Layout master com SEO |
| 1.8.2 | Criar static/css/main.css | UX/UI Designer | 1.8.1 | :white_check_mark: | Design system CSS |
| 1.8.3 | Criar components/header.html | Frontend Developer | 1.8.1 | :white_check_mark: | Navegacao, logo |
| 1.8.4 | Criar components/footer.html | Frontend Developer | 1.8.1 | :white_check_mark: | Links, copyright |
| 1.8.5 | Criar templates/home.html | Frontend Developer | 1.8.1-1.8.4 | :white_check_mark: | Homepage |
| 1.8.6 | Criar templates/blog/post.html | Frontend Developer | 1.8.1-1.8.4 | :white_check_mark: | Pagina de post |
| 1.8.7 | Criar templates/blog/category.html | Frontend Developer | 1.8.1-1.8.4 | :white_check_mark: | Listagem categoria |
| 1.8.8 | Criar components/product_card.html | Frontend Developer | 1.8.2 | :white_check_mark: | Card de produto + CSS |
| 1.8.9 | Criar components/post_card.html | Frontend Developer | 1.8.2 | :white_check_mark: | Card de post + CSS |
| 1.8.10 | Criar templates/blog/list.html | Frontend Developer | 1.8.1-1.8.4 | :white_check_mark: | **[NOVO]** Listagem de posts |
| 1.8.11 | Criar templates/blog/categories.html | Frontend Developer | 1.8.1-1.8.4 | :white_check_mark: | **[NOVO]** Listagem de categorias |

## 1.9 Frontend - Rotas SSR

| ID | Tarefa | Agente | Dependencia | Status | Notas |
|----|--------|--------|-------------|--------|-------|
| 1.9.1 | Implementar rota / (home) | Frontend Developer | 1.8.5 | :white_check_mark: | GET / em main.py |
| 1.9.2 | Implementar routers/blog.py | Frontend Developer | 1.8.6 | :white_check_mark: | GET /blog/{slug} |
| 1.9.3 | Implementar rota /categoria/{slug} | Frontend Developer | 1.8.7 | :white_check_mark: | GET /categoria/{slug} |
| 1.9.4 | Implementar routers/search.py | Frontend Developer | 1.8.5 | :white_check_mark: | GET /busca + 9 testes |
| 1.9.5 | Implementar paginas de erro | Frontend Developer | 1.8.1 | :white_check_mark: | 404, 500 + 9 testes |
| 1.9.6 | Implementar rota /blog | Frontend Developer | 1.8.10 | :white_check_mark: | **[NOVO]** Listagem de posts |
| 1.9.7 | Implementar rota /categorias | Frontend Developer | 1.8.11 | :white_check_mark: | **[NOVO]** Listagem de categorias |

## 1.10 Seguranca Base

| ID | Tarefa | Agente | Dependencia | Status | Notas |
|----|--------|--------|-------------|--------|-------|
| 1.10.1 | Configurar CORS adequado | Security Engineer | 1.2.2 | :white_check_mark: | Configurado em main.py |
| 1.10.2 | Implementar headers de seguranca | Security Engineer | 1.2.2 | :white_check_mark: | CSP, HSTS, X-Frame-Options + 8 testes |
| 1.10.3 | Sanitizar inputs | Security Engineer | 1.5.3, 1.6.3 | :white_check_mark: | Via Pydantic |
| 1.10.4 | Validar uploads (se houver) | Security Engineer | 1.5.3 | :white_check_mark: | core/uploads.py |
| 1.10.5 | Revisar checklist OWASP Top 10 | Security Engineer | 1.10.1-1.10.4 | :white_check_mark: | 37 testes OWASP - 100% passando (vulnerabilidades corrigidas) |
| 1.10.6 | Definir Content Security Policy (CSP) | Security Engineer | 1.10.2 | :white_check_mark: | Incluido em 1.10.2 |

## 1.11 Painel Administrativo (Admin)

> **NOVA SECAO**: Interface web para gerenciamento de conteudo com controle de acesso por roles.

| ID | Tarefa | Agente | Dependencia | Status | Notas |
|----|--------|--------|-------------|--------|-------|
| 1.11.1 | Criar templates/admin/base.html | Frontend Developer | 1.8.1, 1.4.5 | :white_check_mark: | Layout admin com sidebar |
| 1.11.2 | Criar templates/admin/login.html | Frontend Developer | 1.11.1 | :white_check_mark: | Pagina de login admin |
| 1.11.3 | Criar templates/admin/dashboard.html | Frontend Developer | 1.11.1 | :white_check_mark: | Dashboard com metricas |
| 1.11.4 | Criar templates/admin/posts/list.html | Frontend Developer | 1.11.1 | :white_check_mark: | Listagem de posts com filtros |
| 1.11.5 | Criar templates/admin/posts/form.html | Frontend Developer | 1.11.4 | :white_check_mark: | Criar/editar post |
| 1.11.6 | Criar templates/admin/products/list.html | Frontend Developer | 1.11.1 | :white_check_mark: | Listagem de produtos |
| 1.11.7 | Criar templates/admin/products/form.html | Frontend Developer | 1.11.6 | :white_check_mark: | Criar/editar produto |
| 1.11.8 | Criar templates/admin/categories/list.html | Frontend Developer | 1.11.1 | :white_check_mark: | Listagem de categorias |
| 1.11.9 | Criar templates/admin/users/list.html | Frontend Developer | 1.11.1 | :white_check_mark: | Listagem de usuarios (admin only) |
| 1.11.10 | Implementar routers/admin.py | Backend Developer | 1.11.1-1.11.9 | :white_check_mark: | Rotas SSR protegidas |
| 1.11.11 | Implementar middleware de autenticacao admin | Security Engineer | 1.11.10, 1.4.5 | :white_check_mark: | JWT em cookies no router |
| 1.11.12 | Implementar controle de acesso por role | Security Engineer | 1.11.11 | :white_check_mark: | admin: tudo, editor: posts/products |
| 1.11.13 | Criar static/css/admin.css | UX/UI Designer | 1.11.1 | :white_check_mark: | Estilos do admin |
| 1.11.14 | Criar static/js/admin.js | Frontend Developer | 1.11.1 | :white_check_mark: | Interatividade admin |
| 1.11.15 | Implementar dashboard com metricas | Data Analyst | 1.11.3 | :white_check_mark: | Posts mais vistos, cliques reais |
| 1.11.16 | Criar testes de integracao admin | Backend Developer | 1.11.10-1.11.12 | :white_check_mark: | 34 testes |
| 1.11.17 | Implementar routers/admin_actions.py | Backend Developer | 1.11.10 | :white_check_mark: | **[NOVO]** CRUD completo (POST/DELETE) |
| 1.11.18 | Corrigir enums nos templates | Frontend Developer | 1.11.5, 1.11.7 | :white_check_mark: | **[NOVO]** PostType, ProductAvailability |

## 1.12 Testes Automatizados

> **NOVA SECAO**: Cobertura de testes do projeto.

| ID | Tarefa | Agente | Dependencia | Status | Notas |
|----|--------|--------|-------------|--------|-------|
| 1.12.1 | Configurar pytest e fixtures | Backend Developer | 1.2.4 | :white_check_mark: | conftest.py |
| 1.12.2 | Criar testes unitarios security.py | Backend Developer | 1.4.1 | :white_check_mark: | 13 testes |
| 1.12.3 | Criar testes integracao auth | Backend Developer | 1.4.3 | :white_check_mark: | 9 testes |
| 1.12.4 | Criar testes integracao users | Backend Developer | 1.5.3 | :white_check_mark: | 14 testes |
| 1.12.5 | Criar testes integracao posts | Backend Developer | 1.5.3 | :white_check_mark: | 25 testes |
| 1.12.6 | Criar testes integracao products | Backend Developer | 1.6.3 | :white_check_mark: | 20 testes |
| 1.12.7 | Criar testes integracao categories | Backend Developer | 1.5.3 | :white_check_mark: | 16 testes |
| 1.12.8 | Criar testes SSR routes | Frontend Developer | 1.9.1-1.9.3 | :white_check_mark: | 12 testes |
| 1.12.9 | Criar testes integracao newsletter | Backend Developer | 1.3.8 | :white_check_mark: | Existente |

---

# FASE 2: SEO & AUTOMACAO

## 2.1 SEO Tecnico

| ID | Tarefa | Agente | Dependencia | Status | Notas |
|----|--------|--------|-------------|--------|-------|
| 2.1.1 | Implementar geracao de sitemap.xml | SEO Specialist | 1.9.1-1.9.4 | :white_check_mark: | routers/seo.py + 11 testes |
| 2.1.2 | Criar robots.txt otimizado | SEO Specialist | 1.2.2 | :white_check_mark: | Dinamico por ambiente + 3 testes |
| 2.1.3 | Implementar canonical URLs | SEO Specialist | 1.9.1-1.9.4 | :white_check_mark: | Em todas as rotas SSR |
| 2.1.4 | Implementar breadcrumbs | SEO Specialist | 1.9.2 | :white_check_mark: | Em blog/post.html |
| 2.1.5 | Otimizar URLs (slug structure) | SEO Specialist | 1.5.4 | :white_check_mark: | Clean URLs implementadas |
| 2.1.6 | Implementar redirects 301 | SEO Specialist | 1.9.1 | :white_large_square: | Old URLs |

## 2.2 Schema.org / Structured Data

| ID | Tarefa | Agente | Dependencia | Status | Notas |
|----|--------|--------|-------------|--------|-------|
| 2.2.1 | Implementar Schema BlogPosting | SEO Specialist | 1.8.6 | :white_check_mark: | JSON-LD em seo_meta.html |
| 2.2.2 | Implementar Schema Product | SEO Specialist | 1.8.8 | :white_check_mark: | JSON-LD em seo_meta.html |
| 2.2.3 | Implementar Schema ItemList | SEO Specialist | 1.8.7 | :white_check_mark: | JSON-LD em seo_meta.html |
| 2.2.4 | Implementar Schema Organization | SEO Specialist | 1.8.3 | :white_check_mark: | JSON-LD em seo_meta.html |
| 2.2.5 | Implementar Schema BreadcrumbList | SEO Specialist | 2.1.4 | :white_check_mark: | JSON-LD em seo_meta.html |
| 2.2.6 | Criar components/seo_meta.html | SEO Specialist | 2.2.1-2.2.5 | :white_check_mark: | Componente SEO completo

## 2.3 Open Graph & Social

| ID | Tarefa | Agente | Dependencia | Status | Notas |
|----|--------|--------|-------------|--------|-------|
| 2.3.1 | Implementar meta tags Open Graph | SEO Specialist | 1.8.1 | :white_check_mark: | Em base.html |
| 2.3.2 | Implementar Twitter Cards | SEO Specialist | 1.8.1 | :white_check_mark: | Em base.html |
| 2.3.3 | Criar gerador de imagens OG | Frontend Developer | 2.3.1 | :white_large_square: | Dinamico ou template |
| 2.3.4 | Implementar botoes de share | Frontend Developer | 2.3.1 | :white_large_square: | WhatsApp, Telegram, X |

## 2.4 n8n - Configuracao Base

| ID | Tarefa | Agente | Dependencia | Status | Notas |
|----|--------|--------|-------------|--------|-------|
| 2.4.1 | Adicionar n8n ao docker-compose | DevOps Engineer | 1.1.6 | :white_large_square: | Servico separado |
| 2.4.2 | Configurar credenciais n8n | Automation Engineer | 2.4.1 | :white_large_square: | API keys seguras |
| 2.4.3 | Configurar webhook do backend | Automation Engineer | 2.4.2 | :white_large_square: | Endpoint /webhooks/n8n |
| 2.4.4 | Criar usuario automation no sistema | Backend Developer | 1.4.3, 2.4.3 | :white_large_square: | JWT para n8n |

## 2.5 n8n - Workflow A (Post Diario)

| ID | Tarefa | Agente | Dependencia | Status | Notas |
|----|--------|--------|-------------|--------|-------|
| 2.5.1 | Criar workflow base Flow A | Automation Engineer | 2.4.4 | :white_large_square: | Trigger: cron 8h |
| 2.5.2 | Implementar busca de produto aleatorio | Automation Engineer | 2.5.1 | :white_large_square: | Query no banco |
| 2.5.3 | Integrar geracao de conteudo com IA | Automation Engineer | 2.5.2 | :white_large_square: | OpenAI API |
| 2.5.4 | Implementar criacao automatica de post | Automation Engineer | 2.5.3 | :white_large_square: | POST /api/v1/posts |
| 2.5.5 | Implementar notificacao de sucesso/erro | Automation Engineer | 2.5.4 | :white_large_square: | Telegram/Discord |
| 2.5.6 | Testar e validar Flow A | Automation Engineer | 2.5.5 | :white_large_square: | End-to-end |

## 2.6 n8n - Workflow B (Listicle Semanal)

| ID | Tarefa | Agente | Dependencia | Status | Notas |
|----|--------|--------|-------------|--------|-------|
| 2.6.1 | Criar workflow base Flow B | Automation Engineer | 2.5.6 | :white_large_square: | Trigger: semanal |
| 2.6.2 | Implementar selecao de 10 produtos | Automation Engineer | 2.6.1 | :white_large_square: | Por categoria/tema |
| 2.6.3 | Implementar geracao de listicle | Automation Engineer | 2.6.2 | :white_large_square: | Top 10 format |
| 2.6.4 | Testar e validar Flow B | Automation Engineer | 2.6.3 | :white_large_square: | End-to-end |

## 2.7 n8n - Workflow C (Atualizacao de Precos)

| ID | Tarefa | Agente | Dependencia | Status | Notas |
|----|--------|--------|-------------|--------|-------|
| 2.7.1 | Criar workflow base Flow C | Automation Engineer | 2.4.4 | :white_large_square: | Trigger: 4x/dia |
| 2.7.2 | Integrar API Amazon | Automation Engineer | 2.7.1 | :white_large_square: | Product Advertising |
| 2.7.3 | Integrar API Mercado Livre | Automation Engineer | 2.7.1 | :white_large_square: | Items API |
| 2.7.4 | Implementar atualizacao de precos | Automation Engineer | 2.7.2, 2.7.3 | :white_large_square: | PATCH /products |
| 2.7.5 | Implementar alerta de indisponibilidade | Automation Engineer | 2.7.4 | :white_large_square: | Produto fora de estoque |
| 2.7.6 | Testar e validar Flow C | Automation Engineer | 2.7.5 | :white_large_square: | End-to-end |

## 2.8 Google Analytics 4

| ID | Tarefa | Agente | Dependencia | Status | Notas |
|----|--------|--------|-------------|--------|-------|
| 2.8.1 | Configurar conta GA4 | Data Analyst | 1.8.1 | :white_large_square: | Property e stream |
| 2.8.2 | Implementar gtag.js no base.html | Data Analyst | 2.8.1 | :white_large_square: | Tracking basico |
| 2.8.3 | Implementar eventos customizados | Data Analyst | 2.8.2 | :white_large_square: | affiliate_click, share |
| 2.8.4 | Configurar Google Search Console | SEO Specialist | 2.8.1 | :white_large_square: | Verificacao |
| 2.8.5 | Criar static/js/analytics.js | Data Analyst | 2.8.3 | :white_large_square: | Event helpers |
| 2.8.6 | Implementar tracking de scroll | Data Analyst | 2.8.5 | :white_large_square: | 25%, 50%, 75%, 100% |

---

# FASE 3: IA & INTERNACIONALIZACAO

## 3.1 Integracao LiteLLM (Multi-Provider LLM)

> **NOVA SECAO**: Integracao com multiplos provedores de LLM via LiteLLM para otimizar custos e performance.
> Cada funcionalidade pode usar um modelo diferente conforme necessidade (custo vs qualidade).

| ID | Tarefa | Agente | Dependencia | Status | Notas |
|----|--------|--------|-------------|--------|-------|
| 3.1.1 | Adicionar litellm ao requirements.txt | Backend Developer | 1.2.5 | :white_large_square: | pip install litellm |
| 3.1.2 | Criar core/llm/config.py | Backend Developer | 3.1.1 | :white_large_square: | Configuracao de modelos por funcao |
| 3.1.3 | Criar core/llm/client.py | Backend Developer | 3.1.2 | :white_large_square: | Cliente LiteLLM unificado |
| 3.1.4 | Implementar LLMConfig model | Backend Developer | 3.1.2 | :white_large_square: | Pydantic settings para cada provider |
| 3.1.5 | Configurar provider OpenRouter (free tier) | Backend Developer | 3.1.3 | :white_large_square: | Para tarefas simples (slugs, tags) |
| 3.1.6 | Configurar provider OpenAI | Backend Developer | 3.1.3 | :white_large_square: | Para geracao de conteudo (GPT-4) |
| 3.1.7 | Configurar provider Anthropic (opcional) | Backend Developer | 3.1.3 | :white_large_square: | Claude como alternativa |
| 3.1.8 | Criar services/llm_service.py | Backend Developer | 3.1.3-3.1.6 | :white_large_square: | Abstrai chamadas por tipo de tarefa |
| 3.1.9 | Implementar generate_slug() | Backend Developer | 3.1.8 | :white_large_square: | Usa modelo free (OpenRouter) |
| 3.1.10 | Implementar generate_content() | Backend Developer | 3.1.8 | :white_large_square: | Usa OpenAI GPT-4 |
| 3.1.11 | Implementar generate_seo_meta() | Backend Developer | 3.1.8 | :white_large_square: | Usa modelo intermediario |
| 3.1.12 | Implementar fallback entre providers | Backend Developer | 3.1.8 | :white_large_square: | Se um falhar, usa outro |
| 3.1.13 | Criar testes unitarios LLM service | Backend Developer | 3.1.8-3.1.12 | :white_large_square: | Mocks para providers |
| 3.1.14 | Documentar configuracao de providers | Backend Developer | 3.1.13 | :white_large_square: | .env.example + README |

### Mapeamento de Modelos por Funcionalidade

| Funcionalidade | Provider Padrao | Modelo | Justificativa |
|----------------|-----------------|--------|---------------|
| Geracao de slugs | OpenRouter | mistral-7b-free | Tarefa simples, custo zero |
| Geracao de tags | OpenRouter | mistral-7b-free | Tarefa simples, custo zero |
| SEO meta description | OpenRouter | llama-3-8b | Qualidade media, baixo custo |
| Conteudo de posts | OpenAI | gpt-4-turbo | Alta qualidade, criatividade |
| Listicles (Top 10) | OpenAI | gpt-4-turbo | Alta qualidade, estrutura |
| Traducoes (i18n) | Anthropic | claude-3-haiku | Bom para traducao, custo medio |
| Revisao gramatical | OpenRouter | llama-3-70b | Boa qualidade, custo baixo |

## 3.2 Integracao IA - Prompts e Templates

| ID | Tarefa | Agente | Dependencia | Status | Notas |
|----|--------|--------|-------------|--------|-------|
| 3.2.1 | Criar prompts otimizados | Content Strategist | 3.1.8 | :white_large_square: | Para diferentes tipos de post |
| 3.2.2 | Implementar variacao de tom | Content Strategist | 3.2.1 | :white_large_square: | Conforme persona |
| 3.2.3 | Criar sistema de templates de conteudo | Automation Engineer | 3.2.1 | :white_large_square: | Reusaveis |
| 3.2.4 | Implementar revisao automatica | Automation Engineer | 3.2.3 | :white_large_square: | Gramatica, SEO |
| 3.2.5 | Implementar geracao de meta description | SEO Specialist | 3.2.3 | :white_large_square: | Automatica |

## 3.3 n8n - Workflow E (Pesquisa de Produtos)

| ID | Tarefa | Agente | Dependencia | Status | Notas |
|----|--------|--------|-------------|--------|-------|
| 3.3.1 | Criar workflow Flow E | Automation Engineer | 2.7.6 | :white_large_square: | Pesquisa inteligente |
| 3.3.2 | Implementar busca por trends | Automation Engineer | 3.3.1 | :white_large_square: | Google Trends API |
| 3.3.3 | Implementar analise de concorrentes | Automation Engineer | 3.3.2 | :white_large_square: | Scraping seguro |
| 3.3.4 | Implementar sugestao de novos produtos | Automation Engineer | 3.3.3 | :white_large_square: | Com IA (usa 3.1.x) |
| 3.3.5 | Testar e validar Flow E | Automation Engineer | 3.3.4 | :white_large_square: | End-to-end |

## 3.4 n8n - Workflow F (Monitor de Deals)

| ID | Tarefa | Agente | Dependencia | Status | Notas |
|----|--------|--------|-------------|--------|-------|
| 3.4.1 | Criar workflow Flow F | Automation Engineer | 2.7.6 | :white_large_square: | Monitor de ofertas |
| 3.4.2 | Implementar deteccao de queda de preco | Automation Engineer | 3.4.1 | :white_large_square: | > 20% desconto |
| 3.4.3 | Implementar criacao de post urgente | Automation Engineer | 3.4.2 | :white_large_square: | "Oferta relampago" |
| 3.4.4 | Implementar alerta para admin | Automation Engineer | 3.4.3 | :white_large_square: | Telegram |
| 3.4.5 | Testar e validar Flow F | Automation Engineer | 3.4.4 | :white_large_square: | End-to-end |

## 3.5 Cache Redis

| ID | Tarefa | Agente | Dependencia | Status | Notas |
|----|--------|--------|-------------|--------|-------|
| 3.5.1 | Implementar utils/cache.py | Backend Developer | 1.1.4 | :white_large_square: | Redis client |
| 3.5.2 | Cachear queries frequentes | Backend Developer | 3.5.1 | :white_large_square: | Posts, produtos |
| 3.5.3 | Implementar cache de sessoes | Backend Developer | 3.5.1 | :white_large_square: | JWT blacklist |
| 3.5.4 | Implementar invalidacao inteligente | Backend Developer | 3.5.2 | :white_large_square: | On update/delete |

## 3.6 Internacionalizacao (i18n)

| ID | Tarefa | Agente | Dependencia | Status | Notas |
|----|--------|--------|-------------|--------|-------|
| 3.6.1 | Estruturar sistema i18n | Backend Developer | 1.2.2 | :white_large_square: | Flask-Babel ou similar |
| 3.6.2 | Criar arquivos de traducao pt-BR | Content Strategist | 3.6.1 | :white_large_square: | Base inicial |
| 3.6.3 | Implementar deteccao de idioma | Backend Developer | 3.6.1 | :white_large_square: | Accept-Language |
| 3.6.4 | Adaptar templates para i18n | Frontend Developer | 3.6.1-3.6.3 | :white_large_square: | {{ _('texto') }} |
| 3.6.5 | Implementar hreflang tags | SEO Specialist | 3.6.4 | :white_large_square: | SEO internacional |

---

# FASE 4: GROWTH & OTIMIZACAO

## 4.1 Sistema de A/B Testing

| ID | Tarefa | Agente | Dependencia | Status | Notas |
|----|--------|--------|-------------|--------|-------|
| 4.1.1 | Criar modelo ABTest | Database Architect | 3.5.4 | :white_large_square: | Tabela de testes |
| 4.1.2 | Criar modelo ABTestEvent | Database Architect | 4.1.1 | :white_large_square: | Eventos de teste |
| 4.1.3 | Implementar services/ab_test_service.py | Data Analyst | 4.1.1-4.1.2 | :white_large_square: | Logica de testes |
| 4.1.4 | Implementar atribuicao de variante | Data Analyst | 4.1.3 | :white_large_square: | Consistente por sessao |
| 4.1.5 | Implementar analise estatistica | Data Analyst | 4.1.4 | :white_large_square: | Chi-square, significancia |
| 4.1.6 | Criar dashboard de A/B tests | Data Analyst | 4.1.5 | :white_large_square: | Admin interface |

## 4.2 Dashboards de Analytics

| ID | Tarefa | Agente | Dependencia | Status | Notas |
|----|--------|--------|-------------|--------|-------|
| 4.2.1 | Criar dashboard executivo | Data Analyst | 2.8.6 | :white_large_square: | Visao geral |
| 4.2.2 | Criar dashboard de conteudo | Data Analyst | 4.2.1 | :white_large_square: | Posts performance |
| 4.2.3 | Criar dashboard de afiliados | Data Analyst | 4.2.1 | :white_large_square: | Receita, CTR |
| 4.2.4 | Criar dashboard de SEO | SEO Specialist | 4.2.1 | :white_large_square: | Rankings, keywords |
| 4.2.5 | Implementar exportacao de relatorios | Data Analyst | 4.2.1-4.2.4 | :white_large_square: | PDF, CSV |

## 4.3 Sistema de Alertas

| ID | Tarefa | Agente | Dependencia | Status | Notas |
|----|--------|--------|-------------|--------|-------|
| 4.3.1 | Implementar alertas criticos | DevOps Engineer | 3.4.4 | :white_large_square: | Site down, erros 500 |
| 4.3.2 | Implementar alertas de trafego | Data Analyst | 4.3.1 | :white_large_square: | Quedas > 30% |
| 4.3.3 | Implementar alertas de n8n | Automation Engineer | 4.3.1 | :white_large_square: | Falhas de workflow |
| 4.3.4 | Configurar integracao Telegram | DevOps Engineer | 4.3.1-4.3.3 | :white_large_square: | Bot de alertas |

## 4.4 Newsletter

| ID | Tarefa | Agente | Dependencia | Status | Notas |
|----|--------|--------|-------------|--------|-------|
| 4.4.1 | Implementar formulario de signup | Frontend Developer | 3.4.4 | :white_check_mark: | Em home.html |
| 4.4.2 | Implementar api/v1/newsletter.py | Backend Developer | 4.4.1 | :white_check_mark: | POST /subscribe |
| 4.4.3 | Implementar double opt-in | Backend Developer | 4.4.2 | :white_large_square: | Email de confirmacao |
| 4.4.4 | Criar workflow de newsletter | Automation Engineer | 4.4.3 | :white_large_square: | n8n Flow G |
| 4.4.5 | Implementar unsubscribe | Backend Developer | 4.4.3 | :white_large_square: | LGPD compliance |

## 4.5 n8n - Workflow D (Social Share)

| ID | Tarefa | Agente | Dependencia | Status | Notas |
|----|--------|--------|-------------|--------|-------|
| 4.5.1 | Criar workflow Flow D | Automation Engineer | 4.4.4 | :white_large_square: | Auto-share |
| 4.5.2 | Integrar Twitter/X API | Automation Engineer | 4.5.1 | :white_large_square: | Postar automatico |
| 4.5.3 | Integrar Telegram Channel | Automation Engineer | 4.5.1 | :white_large_square: | Canal publico |
| 4.5.4 | Implementar agendamento inteligente | Automation Engineer | 4.5.2-4.5.3 | :white_large_square: | Melhores horarios |
| 4.5.5 | Testar e validar Flow D | Automation Engineer | 4.5.4 | :white_large_square: | End-to-end |

## 4.6 Otimizacao de Performance

| ID | Tarefa | Agente | Dependencia | Status | Notas |
|----|--------|--------|-------------|--------|-------|
| 4.6.1 | Otimizar Core Web Vitals | Frontend Developer | 4.2.1 | :white_large_square: | LCP < 2.5s |
| 4.6.2 | Implementar lazy loading | Frontend Developer | 4.6.1 | :white_large_square: | Imagens |
| 4.6.3 | Minificar CSS/JS | DevOps Engineer | 4.6.1 | :white_large_square: | Build step |
| 4.6.4 | Configurar CDN | DevOps Engineer | 4.6.3 | :white_large_square: | Cloudflare ou similar |
| 4.6.5 | Implementar preconnect/prefetch | Frontend Developer | 4.6.4 | :white_large_square: | Resource hints |
| 4.6.6 | Otimizar queries do banco | Database Architect | 4.6.1 | :white_large_square: | EXPLAIN ANALYZE |

## 4.7 Seguranca Avancada

| ID | Tarefa | Agente | Dependencia | Status | Notas |
|----|--------|--------|-------------|--------|-------|
| 4.7.1 | Implementar LGPD compliance completo | Security Engineer | 4.4.5 | :white_large_square: | Consent, dados |
| 4.7.2 | Criar politica de privacidade | Security Engineer | 4.7.1 | :white_large_square: | Pagina /privacidade |
| 4.7.3 | Implementar cookie consent | Security Engineer | 4.7.1 | :white_large_square: | Banner LGPD |
| 4.7.4 | Configurar backup automatizado | DevOps Engineer | 4.7.1 | :white_large_square: | PostgreSQL dumps |
| 4.7.5 | Implementar logs de auditoria | Security Engineer | 4.7.4 | :white_large_square: | Acoes de admin |
| 4.7.6 | Realizar penetration test | Security Engineer | 4.7.1-4.7.5 | :white_large_square: | Auditoria final |

## 4.8 Documentacao Final

| ID | Tarefa | Agente | Dependencia | Status | Notas |
|----|--------|--------|-------------|--------|-------|
| 4.8.1 | Atualizar README.md | DevOps Engineer | 4.7.6 | :white_large_square: | Setup, deploy |
| 4.8.2 | Documentar API (OpenAPI/Swagger) | Backend Developer | 4.7.6 | :white_check_mark: | Auto-gerado FastAPI |
| 4.8.3 | Criar guia de operacoes | DevOps Engineer | 4.8.1 | :white_large_square: | Runbook |
| 4.8.4 | Documentar workflows n8n | Automation Engineer | 4.8.1 | :white_large_square: | Cada flow |
| 4.8.5 | Criar manual do editor | Content Strategist | 4.8.1 | :white_large_square: | Para usuarios |

---

# RESUMO POR FASE

| Fase | Total Tarefas | Concluidas | Pendentes | Progresso |
|------|---------------|------------|-----------|-----------|
| Fase 1 | 95 | 95 | 0 | 100% |
| Fase 2 | 48 | 13 | 35 | 27% |
| Fase 3 | 40 | 0 | 40 | 0% |
| Fase 4 | 45 | 4 | 41 | 9% |
| **TOTAL** | **228** | **112** | **116** | **49%** |

---

# RESUMO POR AGENTE

| Agente | Total Tarefas | Concluidas | Fases |
|--------|---------------|------------|-------|
| Backend Developer | 54 | 30 | 1, 2, 3, 4 |
| DevOps Engineer | 24 | 8 | 1, 2, 4 |
| Automation Engineer | 28 | 0 | 2, 3, 4 |
| Database Architect | 16 | 10 | 1, 4 |
| Frontend Developer | 29 | 15 | 1, 2, 4 |
| Security Engineer | 16 | 6 | 1, 4 |
| SEO Specialist | 18 | 4 | 2, 3, 4 |
| Data Analyst | 18 | 1 | 1, 2, 4 |
| UX/UI Designer | 5 | 2 | 1 |
| Content Strategist | 6 | 0 | 3, 4 |
| Affiliate Marketing | 2 | 1 | 1 |

---

# PROXIMAS TAREFAS PRIORITARIAS

Com base no progresso atual, as proximas tarefas prioritarias sao:

## Fase 1 (Finalizar Base Tecnica - 99% concluido)
1. ~~**1.0.1** - Criar projeto no Easypanel (VPS)~~ :white_check_mark:
2. ~~**1.0.4** - Configurar dominio no Traefik (VPS)~~ :white_check_mark:
3. ~~**1.0.5** - Configurar variaveis de ambiente (VPS)~~ :white_check_mark:
4. **1.10.5** - Revisar checklist OWASP Top 10

## Fase 2 (SEO & Automacao - 27% concluido)
1. ~~**2.1.3** - Canonical URLs~~ :white_check_mark:
2. ~~**2.2.x** - Schema.org / Structured Data~~ :white_check_mark: (todos os 6 schemas)
3. **2.1.6** - Redirects 301 (old URLs)
4. **2.4.x** - Configuracao n8n
5. **2.7.2** - Integracao API Amazon

## Fase 3 (IA & Internacionalizacao - 0% concluido)
> **PRIORIDADE**: Integracao LiteLLM deve ser feita antes dos workflows de automacao que usam IA

1. **3.1.1-3.1.3** - Setup inicial LiteLLM (client + config)
2. **3.1.5-3.1.6** - Configurar providers OpenRouter (free) e OpenAI
3. **3.1.8** - Criar LLM service abstrato
4. **3.1.9-3.1.11** - Implementar funcoes (slug, content, SEO)
5. **3.1.12** - Fallback entre providers

---

**Versao**: 3.0
**Ultima atualizacao**: 2025-12-12
**Projeto**: geek.bidu.guru
**Testes**: 294 passando (incluindo 34 admin + 24 SEO)

---

# CHANGELOG

## v3.0 (2025-12-12)
- :sparkles: **NOVA SECAO 3.1**: Integracao LiteLLM (Multi-Provider LLM)
  - 14 novas tarefas para integracao com multiplos provedores de LLM
  - Mapeamento de modelos por funcionalidade (custo vs qualidade)
  - OpenRouter (free tier) para tarefas simples (slugs, tags)
  - OpenAI GPT-4 para geracao de conteudo de alta qualidade
  - Anthropic Claude como alternativa para traducoes
  - Sistema de fallback entre providers
- :pencil: Renumeradas secoes da Fase 3 (3.2 a 3.6)
- :chart_with_upwards_trend: Total de tarefas: 214 → 228 (+14)

## v2.9 (2025-12-12)
- :white_check_mark: Criados 24 testes para funcionalidades SEO (test_seo.py)
  - TestCanonicalURLs (5 testes)
  - TestMetaRobots (4 testes)
  - TestSchemaOrg (5 testes)
  - TestOpenGraph (5 testes)
  - TestTwitterCards (3 testes)
  - TestSEOIntegration (2 testes)

## v2.8 (2025-12-12)
- :white_check_mark: 2.1.3 - Canonical URLs implementadas em todas as rotas SSR
- :white_check_mark: 2.2.1 - Schema BlogPosting (JSON-LD)
- :white_check_mark: 2.2.2 - Schema Product (JSON-LD)
- :white_check_mark: 2.2.3 - Schema ItemList (JSON-LD)
- :white_check_mark: 2.2.4 - Schema Organization (JSON-LD)
- :white_check_mark: 2.2.5 - Schema BreadcrumbList (JSON-LD)
- :white_check_mark: 2.2.6 - Criado components/seo_meta.html (componente SEO reutilizavel)
- :sparkles: Adicionado meta robots (noindex para paginas de busca)
- :sparkles: Adicionado Schema WebSite com SearchAction

## v2.7 (2025-12-12)
- :white_check_mark: 1.0.1 - Projeto criado no Easypanel
- :white_check_mark: 1.0.4 - Dominio configurado no Traefik
- :white_check_mark: 1.0.5 - Variaveis de ambiente configuradas
- :wrench: Corrigido: Adicionados metodos `search` e `count_search` em ProductRepository e UserRepository (erros 500 no admin)
