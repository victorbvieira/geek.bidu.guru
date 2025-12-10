# Instruções para Claude Code - geek.bidu.guru

> **Arquivo de Memória e Contexto**: Este documento contém instruções permanentes para Claude Code ao trabalhar no projeto **geek.bidu.guru**.

---

## 🎯 Sobre o Projeto

**geek.bidu.guru** é um blog/portal de presentes geek com foco em:
- Curadoria de produtos geek (Amazon, Mercado Livre, Shopee)
- Monetização via links de afiliados
- Automação total de conteúdo com n8n e IA
- SEO otimizado para tráfego orgânico
- Stack 100% Python (FastAPI + PostgreSQL + Docker)

**Documentação Principal**:
- **PRD completo**: `PRD.md` - Leia PRIMEIRO para entender o projeto
- **Agentes especializados**: `agents.md` e `agents/README.md`

---

## ⚠️ REGRA FUNDAMENTAL - Sistema de Agentes

**ANTES de responder QUALQUER pergunta sobre este projeto, você DEVE:**

### 1. Consultar o Índice de Agentes
Leia `agents/README.md` para identificar qual agente especialista é mais apropriado para a pergunta.

### 2. Ler o Arquivo do Agente
Acesse e leia completamente o arquivo do agente identificado em `agents/[nome-do-agente].md`.

### 3. Aplicar o Conhecimento Especializado
Use as diretrizes, checklists, exemplos de código e melhores práticas do agente na sua resposta.

### Exemplo de Fluxo:

```
Pergunta: "Como implementar autenticação JWT?"

1. Consultar agents/README.md
   → Identificar: Backend Developer + Security Engineer

2. Ler arquivos:
   → agents/backend-developer.md (implementação)
   → agents/security-engineer.md (segurança)

3. Aplicar conhecimento:
   → Usar código de exemplo do Backend Developer
   → Aplicar práticas de segurança do Security Engineer
   → Combinar ambos na resposta
```

---

## 📋 Agentes Disponíveis (Referência Rápida)

### Negócio
1. **SEO Specialist** → SEO, keywords, meta tags
2. **Content Strategist** → Conteúdo, tom de voz, personas
3. **Affiliate Marketing** → Links, CTR, conversão
4. **UX/UI Designer** → Design, cores, layouts
5. **Data Analyst** → Métricas, KPIs, analytics

### Técnicos
6. **Backend Developer** → FastAPI, APIs, Python
7. **Database Architect** → PostgreSQL, queries, modelagem
8. **DevOps Engineer** → Docker, deploy, infraestrutura
9. **Automation Engineer** → n8n, workflows, IA
10. **Frontend Developer** → Jinja2, HTML/CSS/JS
11. **Security Engineer** → Segurança, OWASP, LGPD

**Índice completo**: `agents/README.md` (Consulte para escolher o agente certo!)

---

## 🛠️ Stack Tecnológica do Projeto

### Backend
- **Python** 3.11+
- **FastAPI** - Framework web
- **SQLAlchemy** - ORM
- **Pydantic** - Validação
- **Jinja2** - Templates (SSR)

### Banco de Dados
- **PostgreSQL** 15+
- Rodando em **Docker container**

### Frontend
- **Server-Side Rendering (SSR)** com Jinja2
- **HTML/CSS** puro (sem frameworks JS)
- **JavaScript vanilla** para interatividade

### Infraestrutura
- **Docker** & **Docker Compose** - TUDO containerizado
- **Nginx** - Reverse proxy
- **VPS** - Deploy
- **Let's Encrypt** - SSL/TLS

### Automação
- **n8n** - Workflows e automação
- **OpenAI API** (ou equivalente) - Geração de conteúdo
- **Amazon API**, **Mercado Livre API**, **Shopee API** - Produtos de afiliados

### Analytics
- **Google Analytics 4** - Tracking
- **Google Search Console** - SEO
- Dashboards customizados no backend

---

## 📁 Estrutura de Diretórios (Importante!)

```
geek.bidu.guru/
├── PRD.md                      # LEIA PRIMEIRO
├── agents.md                   # Índice de agentes (padrão agents.md)
├── CLAUDE.MD                   # Este arquivo
├── agents/                     # Agentes especializados
│   ├── README.md               # Índice detalhado - CONSULTE SEMPRE
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
├── app/
│   ├── main.py                 # Entry point FastAPI
│   ├── api/v1/                 # Endpoints da API
│   ├── models/                 # Modelos SQLAlchemy
│   ├── schemas/                # Pydantic schemas
│   ├── services/               # Lógica de negócio
│   ├── routers/                # Rotas SSR (site)
│   ├── templates/              # Jinja2 templates
│   ├── static/                 # CSS, JS, imagens
│   └── utils/                  # Utilitários
├── tests/
├── migrations/                 # Alembic migrations
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml
├── .env.example
├── requirements.txt
└── README.md
```

---

## 🎨 Diretrizes de Código

### Estilo Python
- **PEP 8** compliant
- **Type hints** sempre que possível
- **Docstrings** em funções públicas
- **Black** para formatação
- **Ruff** para linting

### Segurança (CRÍTICO!)
- **NUNCA** commitar secrets (`.env` no `.gitignore`)
- **SEMPRE** usar ORM ou parametrized queries (prevenir SQL Injection)
- **SEMPRE** validar input com Pydantic
- **SEMPRE** hash de senhas com bcrypt
- **SEMPRE** HTTPS em produção

### Git Commits
- Mensagens claras em português
- Formato: `tipo: descrição curta`
  - `feat:` nova funcionalidade
  - `fix:` correção de bug
  - `docs:` documentação
  - `refactor:` refatoração
  - `test:` testes

---

## 🚀 Comandos Úteis (Lembre o usuário quando relevante)

### Docker
```bash
# Subir containers
docker-compose up -d

# Ver logs
docker-compose logs -f app

# Migrations
docker-compose run --rm app alembic upgrade head

# Shell do container
docker-compose exec app /bin/bash

# Parar tudo
docker-compose down
```

### Makefile (se existir)
```bash
make help        # Ver todos os comandos
make up          # Subir containers
make logs        # Ver logs
make migrate     # Rodar migrations
make test        # Executar testes
```

---

## 📝 Ao Criar Código

### Backend (FastAPI)
**Consulte**: `agents/backend-developer.md`

Sempre incluir:
- Type hints
- Pydantic schemas para validação
- Tratamento de erros
- Logging adequado
- Docstrings

### Banco de Dados (PostgreSQL)
**Consulte**: `agents/database-architect.md`

Sempre:
- Usar UUID como PK
- Adicionar índices apropriados
- Timestamps (created_at, updated_at)
- Migrations via Alembic

### Templates (Jinja2)
**Consulte**: `agents/frontend-developer.md`

Sempre:
- HTML semântico
- Acessibilidade (aria-labels, alt text)
- SEO (meta tags, structured data)
- Responsivo (mobile-first)

### Workflows (n8n)
**Consulte**: `agents/automation-engineer.md`

Sempre:
- Error handling
- Retry logic
- Rate limiting
- Logging de execução

---

## 🔍 Quando Sugerir Soluções

### Sempre Pergunte Primeiro

Se a solução pode ser implementada de múltiplas formas, pergunte ao usuário:
- "Você prefere implementar X ou Y?"
- "Qual abordagem faz mais sentido para seu caso?"

### Priorize Simplicidade

- Solução mais simples que funciona > solução complexa e "elegante"
- Código legível > código "clever"
- Consistência com o projeto > padrões externos

### Considere o Contexto

Antes de sugerir uma biblioteca/ferramenta nova:
1. Verificar se já existe algo similar no projeto
2. Considerar o tamanho (evitar dependências pesadas desnecessárias)
3. Verificar compatibilidade com a stack

---

## ✅ Checklist Antes de Implementar Features

### Features de Backend
- [ ] Consultou `agents/backend-developer.md`?
- [ ] Pydantic schemas criados?
- [ ] Endpoints documentados (FastAPI auto-docs)?
- [ ] Autenticação/autorização implementada?
- [ ] Testes criados?
- [ ] Consultou `agents/security-engineer.md` para segurança?

### Features de Frontend
- [ ] Consultou `agents/frontend-developer.md`?
- [ ] Consultou `agents/ux-ui-designer.md` para design?
- [ ] Template responsivo?
- [ ] Acessível (a11y)?
- [ ] SEO otimizado (consultou `agents/seo-specialist.md`)?

### Features de Automação
- [ ] Consultou `agents/automation-engineer.md`?
- [ ] Fluxo n8n documentado?
- [ ] Error handling implementado?
- [ ] Integração com backend testada?

### Mudanças no Banco
- [ ] Consultou `agents/database-architect.md`?
- [ ] Migration criada (Alembic)?
- [ ] Índices apropriados?
- [ ] Backup antes de aplicar em produção?

---

## 🎯 Objetivos de Negócio (Lembrar sempre!)

1. **Monetização**: Links de afiliados são a fonte de receita principal
2. **SEO**: Tráfego orgânico é essencial - otimizar TUDO
3. **Automação**: Mínimo trabalho manual, máximo conteúdo gerado
4. **Performance**: Site rápido = melhor SEO + melhor conversão
5. **Escalabilidade**: Preparar para crescer (Docker, cache, etc.)

---

## 🚨 Red Flags - Nunca Fazer!

- ❌ **Commitar** `.env` ou secrets
- ❌ **SQL direto** sem parametrização (SQL Injection!)
- ❌ **DEBUG=True** em produção
- ❌ **CORS** com `allow_origins=["*"]` em produção
- ❌ **Senhas** em plain text
- ❌ **Código** sem type hints
- ❌ **Deploy** sem testar migrations
- ❌ **Ignorar** agentes especializados ao responder

---

## 💡 Princípios de Desenvolvimento

### 1. Consulte Agentes SEMPRE
Não importa quão simples a pergunta pareça, **sempre** verifique se há um agente especialista relevante.

### 2. Segurança em Primeiro Lugar
Melhor prevenir que remediar. Consulte `agents/security-engineer.md` frequentemente.

### 3. SEO é Prioridade
Todo conteúdo deve ser otimizado para SEO. Consulte `agents/seo-specialist.md`.

### 4. Performance Importa
- Cache quando possível
- Queries otimizadas
- Imagens comprimidas
- CSS/JS minificados

### 5. Automação é Rei
Se algo pode ser automatizado com n8n, deve ser. Consulte `agents/automation-engineer.md`.

---

## 📚 Ordem de Leitura Recomendada (Para Novos Contextos)

1. **PRD.md** - Entender o projeto completo
2. **agents/README.md** - Conhecer todos os agentes disponíveis
3. **agents.md** - Entender o sistema de agentes
4. **Este arquivo (CLAUDE.MD)** - Instruções específicas para Claude Code
5. **Agentes específicos conforme necessário**

---

## 🔄 Fluxo de Trabalho Ideal

```
┌─────────────────────────────────────┐
│ Usuário faz pergunta/pedido         │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│ Claude consulta agents/README.md    │
│ Identifica agente(s) relevante(s)   │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│ Claude lê arquivo(s) do(s) agente(s)│
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│ Claude aplica conhecimento           │
│ especializado na resposta            │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│ Resposta contextualizada e completa │
│ com exemplos de código quando        │
│ apropriado                           │
└─────────────────────────────────────┘
```

---

## 📞 Comunicação com o Usuário

### Tom de Voz
- **Profissional** mas **acessível**
- **Claro** e **objetivo**
- **Sem emojis excessivos** (apenas quando muito relevante)
- **Português brasileiro**

### Ao Fornecer Código
- **Explicar** o que o código faz
- **Destacar** pontos importantes
- **Referenciar** o agente consultado quando relevante
- **Incluir comentários** em partes complexas

### Ao Explicar Conceitos
- **Partir do mais simples** para o mais complexo
- **Dar exemplos práticos** do contexto do projeto
- **Referenciar documentação** quando apropriado

---

## 🎓 Aprendizado Contínuo

### Se Encontrar Informação Conflitante
1. PRD.md tem prioridade máxima
2. Agentes especializados vêm em seguida
3. Se ainda houver dúvida, pergunte ao usuário

### Se Agente Não Existir
Se a pergunta for sobre uma área sem agente específico:
1. Use seu melhor julgamento
2. Consulte agentes relacionados
3. Sugira ao usuário criar um novo agente se a área for recorrente

---

## ✨ Lembre-se

**Você é parte de uma equipe de especialistas virtuais**. Os agentes em `agents/` representam o conhecimento acumulado e as melhores práticas do projeto. **Consulte-os sempre** para fornecer respostas consistentes, precisas e alinhadas com a visão do projeto geek.bidu.guru.

---

**Versão**: 1.0
**Última atualização**: 2025-12-10
**Projeto**: geek.bidu.guru
**Repositório**: `A:\Repositorios\geek.bidu.guru`
