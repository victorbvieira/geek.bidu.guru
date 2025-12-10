# Agents Configuration - geek.bidu.guru

> **IMPORTANTE**: Este arquivo segue o padrão [agents.md](https://agents.md/) para definição de agentes especializados.

## 📋 Consulta Obrigatória

**ANTES de responder QUALQUER pergunta sobre o projeto geek.bidu.guru, você DEVE:**

1. **Consultar o índice de agentes**: `agents/README.md`
2. **Identificar o agente especialista** mais apropriado para a pergunta
3. **Ler o arquivo do agente** identificado
4. **Aplicar o conhecimento e diretrizes** do agente na sua resposta

Se a pergunta envolver múltiplas áreas (ex: SEO + Backend), consulte TODOS os agentes relevantes.

---

## 🎯 Agentes Especializados Disponíveis

### Agentes de Negócio

#### 1. SEO Specialist
- **Arquivo**: `agents/seo-specialist.md`
- **Quando usar**: Questões sobre otimização para motores de busca, keywords, meta tags, dados estruturados, sitemap, robots.txt, Open Graph
- **Exemplos de perguntas**:
  - "Como otimizar o SEO de um post?"
  - "Quais meta tags devemos usar?"
  - "Como implementar Schema.org?"

#### 2. Content Strategist
- **Arquivo**: `agents/content-strategist.md`
- **Quando usar**: Estratégia de conteúdo, calendário editorial, personas, tom de voz, tipos de post, curadoria de produtos
- **Exemplos de perguntas**:
  - "Qual o tom de voz ideal para o blog?"
  - "Como estruturar um post de listicle?"
  - "Quais personas devemos considerar?"

#### 3. Affiliate Marketing Specialist
- **Arquivo**: `agents/affiliate-marketing-specialist.md`
- **Quando usar**: Links de afiliados, CTR, conversão, monetização, plataformas de afiliados (Amazon, ML, Shopee)
- **Exemplos de perguntas**:
  - "Como otimizar CTR de links de afiliados?"
  - "Qual CTA usar para converter melhor?"
  - "Como implementar o sistema /goto/?"

#### 4. UX/UI Designer
- **Arquivo**: `agents/ux-ui-designer.md`
- **Quando usar**: Design de interfaces, experiência do usuário, paleta de cores, tipografia, componentes, responsividade
- **Exemplos de perguntas**:
  - "Quais cores usar no projeto?"
  - "Como deve ser o layout da homepage?"
  - "Como criar um botão de CTA eficaz?"

#### 5. Data Analyst
- **Arquivo**: `agents/data-analyst.md`
- **Quando usar**: Métricas, KPIs, analytics, dashboards, relatórios, testes A/B
- **Exemplos de perguntas**:
  - "Quais KPIs devemos monitorar?"
  - "Como analisar performance de posts?"
  - "Como fazer testes A/B?"

---

### Agentes Técnicos

#### 6. Backend Developer (Python/FastAPI)
- **Arquivo**: `agents/backend-developer.md`
- **Quando usar**: APIs REST, FastAPI, lógica de negócio, endpoints, SQLAlchemy, Pydantic, Jinja2
- **Exemplos de perguntas**:
  - "Como criar um endpoint de posts?"
  - "Como implementar autenticação JWT?"
  - "Qual estrutura de projeto usar?"

#### 7. Database Architect (PostgreSQL)
- **Arquivo**: `agents/database-architect.md`
- **Quando usar**: Modelagem de dados, queries SQL, índices, performance de banco, migrations
- **Exemplos de perguntas**:
  - "Como modelar a tabela de posts?"
  - "Quais índices criar para performance?"
  - "Como fazer query de top produtos?"

#### 8. DevOps Engineer (Docker)
- **Arquivo**: `agents/devops-engineer.md`
- **Quando usar**: Docker, docker-compose, deploy, infraestrutura, CI/CD, Nginx, monitoramento
- **Exemplos de perguntas**:
  - "Como configurar o docker-compose?"
  - "Como fazer deploy na VPS?"
  - "Como configurar Nginx com SSL?"

#### 9. Automation Engineer (n8n)
- **Arquivo**: `agents/automation-engineer.md`
- **Quando usar**: Workflows n8n, automação, integrações com APIs, geração de conteúdo com IA
- **Exemplos de perguntas**:
  - "Como criar fluxo de post diário?"
  - "Como integrar com Amazon API?"
  - "Como usar LLM para gerar conteúdo?"

#### 10. Frontend Developer (Jinja2/SSR)
- **Arquivo**: `agents/frontend-developer.md`
- **Quando usar**: Templates Jinja2, HTML/CSS, JavaScript, responsividade, componentes
- **Exemplos de perguntas**:
  - "Como criar template de post?"
  - "Como implementar busca no frontend?"
  - "Como fazer botões de compartilhamento?"

#### 11. Security Engineer
- **Arquivo**: `agents/security-engineer.md`
- **Quando usar**: Segurança, OWASP Top 10, autenticação, autorização, LGPD, proteção contra vulnerabilidades
- **Exemplos de perguntas**:
  - "Como prevenir SQL Injection?"
  - "Como implementar rate limiting?"
  - "Como estar em compliance com LGPD?"

---

## 🔄 Fluxo de Trabalho com Agentes

### Exemplo de Uso

**Pergunta do usuário**: "Como criar um post otimizado para SEO sobre presentes de Natal?"

**Processo do Assistente**:

1. **Identificar agentes relevantes**:
   - SEO Specialist (otimização)
   - Content Strategist (estrutura e tom)
   - Affiliate Marketing Specialist (links e CTAs)

2. **Consultar arquivos**:
   - Ler `agents/seo-specialist.md`
   - Ler `agents/content-strategist.md`
   - Ler `agents/affiliate-marketing-specialist.md`

3. **Aplicar conhecimento combinado**:
   - Usar checklist SEO do SEO Specialist
   - Aplicar estrutura de listicle do Content Strategist
   - Implementar CTAs do Affiliate Marketing Specialist

4. **Fornecer resposta completa e contextualizada**

---

## 📚 Estrutura de Arquivos

```
geek.bidu.guru/
├── agents.md                           # Este arquivo (índice principal)
├── CLAUDE.MD                           # Instruções para Claude Code
├── PRD.md                              # Product Requirements Document (v1.4)
├── PRD-design-system.md                # Sistema de design completo (v1.1)
├── PRD-affiliate-strategy.md           # Estratégia de afiliados (v1.1)
├── PRD-internationalization.md         # Internacionalização
├── agents/
│   ├── README.md                       # Índice detalhado de agentes
│   ├── seo-specialist.md
│   ├── content-strategist.md
│   ├── affiliate-marketing-specialist.md
│   ├── ux-ui-designer.md
│   ├── data-analyst.md
│   ├── backend-developer.md
│   ├── database-architect.md
│   ├── devops-engineer.md
│   ├── automation-engineer.md
│   ├── frontend-developer.md
│   └── security-engineer.md
├── docs/
│   ├── analytics/
│   │   ├── tracking-plan.md            # Plano de tracking GA4 (v1.1)
│   │   ├── dashboards.md               # Especificação de dashboards
│   │   ├── ab-testing-framework.md     # Framework de testes A/B
│   │   └── reporting-cadence.md        # Cadência de relatórios
│   ├── content/
│   │   └── ...
│   └── seo/
│       └── ...
└── reports/
    └── consolidated-analysis.md        # Análise consolidada dos 6 especialistas
```

---

## 🎯 Diretrizes para IAs

### Quando Consultar Agentes

**SEMPRE consulte agentes quando**:
- Responder perguntas técnicas sobre implementação
- Fornecer orientações sobre design ou UX
- Recomendar práticas de SEO ou conteúdo
- Explicar estrutura de banco de dados
- Sugerir fluxos de automação
- Recomendar métricas ou análises
- Orientar sobre segurança

**NÃO é necessário consultar agentes para**:
- Perguntas gerais não relacionadas ao projeto
- Conversas casuais
- Confirmações simples

### Como Consultar

```
1. Usuário faz pergunta
2. Identificar área(s) da pergunta
3. Consultar agents/README.md
4. Localizar agente(s) apropriado(s)
5. Ler arquivo(s) do(s) agente(s)
6. Aplicar conhecimento na resposta
7. Referenciar seções específicas quando relevante
```

### Formato de Resposta Recomendado

Ao aplicar conhecimento de agentes, você pode opcionalmente referenciar:

```markdown
**[Consultando: SEO Specialist]**

Para otimizar o SEO do post, siga este checklist:
- Título com keyword no início (max 60 chars)
- Meta description atrativa (150-160 chars)
- ...

**[Consultando: Content Strategist]**

Para o tom de voz, mantenha:
- Linguagem acessível e amigável
- Referências geek contextualizadas
- ...
```

---

## 🔧 Manutenção

### Atualização de Agentes

Quando adicionar ou modificar um agente:

1. ✅ Criar/atualizar arquivo em `agents/`
2. ✅ Atualizar `agents/README.md`
3. ✅ Atualizar este arquivo (`agents.md`)
4. ✅ Atualizar `CLAUDE.MD` se necessário

### Versionamento

- **Versão atual**: 1.1
- **Última atualização**: 2025-12-10
- **Projeto**: geek.bidu.guru

### Documentos Auxiliares Importantes

Para uma visão completa do projeto, consulte também:

| Documento | Descrição | Quando Consultar |
|-----------|-----------|------------------|
| `PRD.md` | Documento principal de requisitos | Visão geral do projeto |
| `PRD-design-system.md` | Sistema de design completo | Cores, tipografia, componentes |
| `PRD-affiliate-strategy.md` | Estratégia de afiliados | CTAs, conversão, tracking |
| `docs/analytics/tracking-plan.md` | Plano GA4 | Eventos, métricas, funis |
| `reports/consolidated-analysis.md` | Análise dos especialistas | Gaps e oportunidades |

---

## 📖 Referências

- **Padrão agents.md**: https://agents.md/
- **PRD do Projeto**: `PRD.md`
- **Índice de Agentes**: `agents/README.md`

---

**Este arquivo é parte do sistema de memória e contexto do projeto geek.bidu.guru. Deve ser consultado antes de qualquer resposta relacionada ao projeto.**
