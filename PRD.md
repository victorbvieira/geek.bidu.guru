
# PRD – geek.bidu.guru – Blog de Presentes Geek com Automação e IA

**Versão:** 1.4
**Responsável:** Squad Conteúdo & Automação
**Stack:** Python (frontend + backend), PostgreSQL, n8n, integrações com APIs de afiliados (Amazon, Mercado Livre, Shopee)
**Domínio:** `https://geek.bidu.guru`

**Documentos Complementares:**
- **[PRD-affiliate-strategy.md](PRD-affiliate-strategy.md)** - Estratégia detalhada de marketing de afiliados
- **[PRD-internationalization.md](PRD-internationalization.md)** - Especificação de internacionalização (i18n)
- **[PRD-design-system.md](PRD-design-system.md)** - Sistema de design, componentes e especificações de UX/UI

---

## 1. Visão Geral do Produto

O objetivo é criar o **geek.bidu.guru**, um portal de referência em **presentes geek** no Brasil, com foco em:

- Ajudar usuários a encontrarem presentes geek por **ocasião**, **perfil**, **fandom** e **faixa de preço**.
- Monetizar por meio de **links de afiliados** (Amazon, Mercado Livre, Shopee), com automação para:
  - Cadastro e atualização de produtos.
  - Criação de posts diários e semanais.
  - Geração de textos e descrições via IA.
- Ser altamente otimizado para **SEO** e para **compartilhamento em redes sociais**, com um guia visual coerente e um layout que fale diretamente com o público geek.

Este PRD considera o projeto como um **produto completo**, e não apenas um MVP.

---

## 2. Objetivos de Negócio

1. **Monetização com afiliados**
   - Gerar receita recorrente a partir de cliques e conversões em links de afiliados (Amazon, Mercado Livre, Shopee).
   - Maximizar CTR e taxa de conversão por meio de posicionamento inteligente e copy otimizada.

2. **Autoridade em SEO para presentes geek**
   - Ser referência orgânica para termos como:
     - “presentes geek”
     - “presentes geek baratos”
     - “10 melhores presentes geek de natal”
     - “presentes geek para namorado/namorada/dev/gamer”

3. **Alta automação e escalabilidade de conteúdo**
   - Posts **diários** com pelo menos 1 item (produto único).
   - Posts **semanais** do tipo lista (“Top 10 melhores presentes…”).
   - Rotina automática de **atualização de preços** e disponibilidade.
   - Fluxo de **pesquisa qualificada com IA** para encontrar itens, montar descrições e links de afiliado.

4. **Construção de audiência e recorrência**
   - Crescimento de tráfego orgânico.
   - Captura de leads (newsletter) e aumento de visitantes recorrentes.
   - Presença ativa em redes sociais com compartilhamento simplificado.

---

## 3. KPIs e Métricas

- **SEO / Tráfego**
  - Visitantes orgânicos/mês.
  - Posição média em keywords alvo.
  - CTR orgânico (Search Console).

- **Afiliados**
  - **CTR (Click-Through Rate)**: % de visualizações que resultam em cliques nos links de afiliados
  - **EPC (Earnings Per Click)**: Ganho médio por cada clique em link de afiliado
  - **RPM (Revenue Per Mille)**: Receita por 1.000 visualizações de página
  - **Taxa de Conversão**: % de cliques que resultam em compras (quando disponível via APIs)
  - **AOV (Average Order Value)**: Valor médio de cada pedido convertido
  - Cliques em links de afiliado/post
  - Conversões (quando dados forem disponibilizados pelas plataformas)
  - Receita mensal por plataforma (Amazon, Mercado Livre, Shopee)

**Benchmarks por Plataforma** (detalhes em [PRD-affiliate-strategy.md](PRD-affiliate-strategy.md)):

| Plataforma | CTR Alvo | Conv. Rate | Comissão Média | RPM Alvo | Cookie Duration | Prioridade |
|------------|----------|------------|----------------|----------|-----------------|------------|
| **Mercado Livre** | 3-5% | 6-10% | 4-8% | R$ 20-30 | 10 dias | ⭐⭐⭐⭐⭐ Muito Alta |
| **Amazon** | 4-6% | 5-8% | 3-5% | R$ 15-25 | 24h | ⭐⭐⭐⭐ Alta |
| **Shopee** | 2-4% | 4-6% | 2-4% | R$ 8-15 | 7 dias | ⭐⭐⭐ Média |

- **Conteúdo & Automação**
  - Número de posts publicados/dia e/semana.
  - Sucesso dos fluxos n8n (% execuções sem erro).
  - Tempo médio do fluxo (da pesquisa ao post publicado).

- **Engajamento**
  - Tempo médio na página.
  - Scroll-depth médio.
  - Cliques em botões de compartilhamento.

### 3.1. KPIs por Persona (Mensal)

Para acompanhamento mensal segmentado por persona (via GA4, dimensões/segmentos por categoria/tag de post, parâmetro `persona_focus` ou taxonomia):

| Persona | Sessões orgânicas | Tempo médio | Rejeição | Cliques afiliados | CTR afiliados | Receita estimada |
|---|---:|---:|---:|---:|---:|---:|
| Ana | — | — | — | — | — | — |
| Lucas | — | — | — | — | — | — |
| Marina | — | — | — | — | — | — |

- Meta inicial (90 dias):  
  - Tempo médio: Ana > 2:00, Lucas > 3:00, Marina > 3:30  
  - CTR afiliados: Ana > 4%, Lucas > 5%, Marina > 4%  
  - Receita/sessão: calibrar após 60 dias de dados

Relatório mensal: consolidar tendências, conteúdos top por persona e ajustes de calendário/priorização.

### 3.2. Metas SMART (12 meses)

| Métrica | Baseline | 3 meses | 6 meses | 12 meses | Como medir |
|---|---:|---:|---:|---:|---|
| Tráfego orgânico (sessões/mês) | 0 | 5.000 | 15.000 | 50.000 | GA4 |
| CTR orgânico (SERP) | — | 2% | 4% | 6% | Search Console |
| Keywords ranqueadas | 0 | 50 | 150 | 500+ | Ahrefs/SEMrush |
| Bounce rate | — | < 55% | < 50% | < 45% | GA4 |
| Tempo na página | — | 1:30 | 2:00 | 2:30 | GA4 |
| CTR de afiliados | — | 2–3% | 4–5% | 6–8% | Backend + GA4 |
| Receita mensal (R$) | 0 | 500 | 2.000 | 5.000+ | Programas de afiliados |
| RPM (R$/1k views) | — | 10 | 30 | 50+ | Calculado |
| Posts publicados/mês | 0 | 30 | 30 | 30 | Backend |
| Assinantes newsletter | 0 | 200 | 1.000 | 5.000 | Plataforma de email |

Observação: revisar baseline após primeiros 30–60 dias de operação para calibrar metas.

### 3.3. North Star & Drivers

- North Star Metric: Receita mensal de afiliados.  
- Primary drivers: CTR de afiliados, sessões orgânicas, taxa de conversão nas plataformas.  
- Secondary drivers: posts publicados, keywords ranqueadas, tempo na página, RPM.  
- Governance: reuniões quinzenais para revisão dos drivers e ações corretivas.

### 3.4. SEO KPIs (expandido)

| Métrica | 3 meses | 6 meses | 12 meses |
|---|---:|---:|---:|
| Keywords ranqueadas (totais) | 100+ | 300+ | 1000+ |
| Keywords em Top 3 | 10 | 30 | 100 |
| Featured snippets | 2 | 10 | 30 |
| Domain Rating (DR) | 10+ | 20+ | 30+ |
| Backlinks (domínios ref.) | 30+ | 120+ | 300+ |
| Páginas indexadas | 50+ | 150+ | 500+ |

Dashboards e acompanhamento: `docs/analytics/dashboards.md` (Dashboard de SEO).  
Plano de link building: `docs/seo/link-building.md`.

---

## 4. Público-Alvo & Personas (Resumo)

- **Ana (27, “compradora de presentes”)**
  - Não é expert em cultura geek, mas quer agradar amigos/parceiros.
  - Busca listas prontas, ideias rápidas, por faixa de preço e ocasião.

- **Lucas (21, gamer/geek raiz)**
  - Já consome cultura geek no dia a dia.
  - Quer produtos diferenciados para si e para presentes entre amigos.

- **Marina (30, profissional de TI/dev)**
  - Usa gadgets e itens geeks no trabalho.
  - Procura presentes geek “úteis”, para home office, setup, etc.

Documentos detalhados: ver `docs/content/personas-expanded.md` (jornada, objeções, canais e priorização por persona).

---

## 5. Proposta de Valor & Diferenciais

- Curadoria de presentes geek com **contexto** (para quem, quando, por quê).
- Conteúdo otimizado para **SEO**, **compartilhamento** e **conversão em afiliados**.
- **Automação robusta** com n8n e IA:
  - Busca inteligente de produtos nas APIs de afiliados.
  - Sugestão automática de descrição, título, SEO e estrutura de post.
  - Atualização recorrente de preço e disponibilidade.
- **Experiência visual geek**: identidade própria, moderna, divertida e confiável.

---

## 6. Escopo Funcional

### 6.1. Tipos de Conteúdo

1. **Post de Produto Único**
   - Foco em um produto com análise detalhada.
   - Indicado para posts diários.

2. **Post Lista (Listicle)**
   - Ex.: “10 melhores presentes geeks de Natal 2025”.
   - Indicado para posts semanais ou especiais de datas comemorativas.

3. **Guia / Artigo de Conteúdo**
   - Ex.: “Como escolher um presente geek para devs”.
   - Conteúdo evergreen para SEO.

Cada post deve conter: título, slug, subtítulo, conteúdo (Markdown/HTML), imagem destacada, categoria, tags, produtos associados, metadados de SEO, dados estruturados, botões de compartilhamento e CTAs para afiliados.

Templates detalhados (estrutura, tamanhos, CTAs e checklist SEO): `docs/content/templates.md`.  
Otimização para featured snippets (definições, listas, tabelas, FAQ/HowTo): `docs/seo/featured-snippets.md`.

---

### 6.2. Gestão de Produtos (Afiliados)

**Entidade Produto Geek:**

- `id` (UUID)
- `name`
- `slug`
- `short_description`
- `long_description`
- `price`
- `currency` (BRL)
- `price_range` (até 50, 50–100, 100–200, +200)
- `main_image_url`
- `images` (lista)
- `affiliate_url_raw`
- `affiliate_redirect_slug` (ex.: `/r/caneca-bidu-guru`)
- `platform` (`amazon`, `mercadolivre`, `shopee`)
- `platform_product_id` (ID do produto na plataforma)
- `categories` / `tags`
- `availability` (`available`, `unavailable`, `unknown`)
- `rating` (opcional)
- `review_count` (opcional)
- `internal_score` (ranking interno)
- `last_price_update` (timestamp)

**Requisitos:**

- CRUD completo de produtos via painel e API.
- Associação de múltiplos produtos a um post.
- Sistema interno de redirecionamento de afiliados:
  - Endpoint: `/goto/{affiliate_redirect_slug}`
  - Contabiliza clique e redireciona para `affiliate_url_raw`.
  - Permite mudar links de afiliado sem alterar posts antigos.

**Critérios de Curadoria de Produtos**
- Adotar scorecard objetivo para seleção e diversidade do portfólio (categorias e faixas de preço)
- Processo contínuo de descoberta, triagem semanal e fila de publicação integrada ao n8n
- Detalhes completos: `docs/content/curation-scorecard.md`

**Scorecard de Produtos para Afiliados** (detalhes em [PRD-affiliate-strategy.md](PRD-affiliate-strategy.md#scorecard-de-produtos)):

Sistema de pontuação de 0-100 para priorizar produtos com maior potencial de conversão e receita:

- **Comissão (30%)**: Produtos com comissão 5-10% recebem pontuação máxima
- **Preço Sweet Spot (25%)**: Faixa ideal R$ 50-150 (melhor taxa de conversão)
- **Disponibilidade (20%)**: Produtos disponíveis têm prioridade; escassez pode ajudar conversão
- **Rating (15%)**: Avaliação mínima 4.0, ideal 4.5+
- **Popularidade (10%)**: Número de reviews como indicador de demanda

**Uso**: Produtos com score >= 70 são priorizados nos fluxos automáticos de geração de conteúdo.

**Atualização**: Scores recalculados diariamente via job automático considerando mudanças de preço, disponibilidade e avaliações.

---

### 6.3. SEO & Dados Estruturados

- **SEO On-page**
  - Campo de palavra-chave foco.
  - `seo_title`, `seo_description` customizáveis.
  - Uso de H1/H2/H3 coerente.
  - ALT-text em imagens.

- **Dados Estruturados (Schema.org)**
  - Base global: `Organization` + `WebSite` (com `SearchAction`).
  - Páginas: `BlogPosting` / `Article` (posts) e `BreadcrumbList` (breadcrumbs).
  - Listas: `ItemList` (Top 10 etc.).
  - Produtos: `Product` com `AggregateRating` quando aplicável.
  - FAQ/Guias: `FAQPage` e `HowTo` quando pertinente.
  - Vídeos (Fase 3): `VideoObject`.
  - Exemplos completos: `docs/seo/schema-examples.md`.

- **Infra SEO Técnica**
  - `sitemap.xml` automático (posts, categorias, produtos).
  - `robots.txt` configurável.
  - Tags `canonical`.
  - Open Graph e Twitter Cards.
  - Diretrizes avançadas: `docs/seo/crawl-indexing.md`.

---

### 6.4. Otimização de CTAs e Conversão de Afiliados

**Estratégia de Posicionamento de CTAs** (detalhes em [PRD-affiliate-strategy.md](PRD-affiliate-strategy.md#otimização-de-ctas)):

- **3 CTAs por Produto**: Posicionamento estratégico em:
  1. **Início**: Após introdução (primeiros 2-3 parágrafos) - para leitores decididos
  2. **Meio**: Após características ou benefícios - para leitores em consideração
  3. **Fim**: Antes da conclusão - última oportunidade de conversão

- **Variações de Botões para Testes A/B**:
  - Amarelo com urgência: "🛒 Comprar Agora com Frete Grátis"
  - Roxo marca: "Ver na [Plataforma]" (transparência de destino)
  - Verde conversão: "✓ Garantir Desconto" (benefício explícito)

- **Otimização Mobile**:
  - Botões full-width em dispositivos móveis
  - Altura mínima 44px (Apple Human Interface Guidelines)
  - Sticky CTA no footer após 50% de scroll

**Técnicas de Conversão**:
- **Urgência e Escassez**: Countdown timers, "Últimas X unidades", "Oferta expira em..."
- **Prova Social**: Avaliações, número de compradores, "Produto mais vendido"
- **Comparadores de Preço**: Tabelas mostrando mesmo produto em múltiplas plataformas
- **Ancoragem de Preços**: Mostrar preço original riscado vs. oferta atual
- **Cross-Sell**: "Quem comprou também levou..."

**Framework de Testes A/B** (implementação em [PRD-affiliate-strategy.md](PRD-affiliate-strategy.md#testes-ab)):

Testes prioritários:
1. Cor do botão de CTA (amarelo vs. roxo vs. verde)
2. Texto do CTA ("Ver Preço" vs. "Comprar Agora" vs. "Ver Oferta")
3. Posição do CTA principal (após intro vs. após características)
4. Sticky CTA mobile (com vs. sem)
5. Disclaimer (destacado vs. discreto)

**Sistema de Tracking Expandido**:

Campos adicionais na tabela `affiliate_clicks`:
- `device` (mobile, desktop, tablet)
- `country`, `region`, `city` (geolocalização via CloudFlare)
- `link_position` (top, middle, bottom)
- `scroll_depth_percentage` (quanto o usuário scrollou)
- `is_suspicious`, `is_bot` (proteção contra fraude)

**Dashboard de Afiliados** (especificação completa em [PRD-affiliate-strategy.md](PRD-affiliate-strategy.md#dashboard-e-analytics)):
- Overview diário: receita estimada, cliques totais, CTR médio, EPC
- Breakdown por plataforma e dispositivo
- Top 10 produtos mais clicados
- Top 10 posts mais rentáveis
- Alertas automáticos de performance (alta/baixa/oportunidades)

---

### 6.5. Compartilhamento

- Botões de compartilhamento em cada post:
  - WhatsApp, Telegram, X, Facebook, e-mail.
  - Botão “Copiar link” com feedback visual.

- Em cada produto:
  - Botão “Ver produto” (via `/goto/...`).
  - Botão “Copiar link do produto”.

---

### 6.6. Internacionalização (i18n)

**Visão Geral** (especificação completa em [PRD-internationalization.md](PRD-internationalization.md)):

O geek.bidu.guru será construído desde o início com **suporte completo a internacionalização**, permitindo expansão gradual para múltiplos mercados.

**Estrutura de URLs**:
```
https://geek.bidu.guru/pt-br/       → Brasil (padrão)
https://geek.bidu.guru/pt-pt/       → Portugal
https://geek.bidu.guru/es-mx/       → México
https://geek.bidu.guru/es-ar/       → Argentina
https://geek.bidu.guru/es-es/       → Espanha
https://geek.bidu.guru/en-us/       → Estados Unidos
```

**Arquitetura Multi-idioma**:
- Tabelas de tradução separadas (`post_translations`, `product_translations`)
- Preços localizados por país e plataforma (`product_prices` com locale)
- Programas de afiliados por país (Amazon.com.br, Amazon.com.mx, Amazon.com, etc.)
- Hreflang tags para SEO internacional
- Detecção automática de locale (URL > Cookie > Accept-Language > IP > fallback)

**Roadmap de Expansão**:
1. **Fase 1 (Meses 1-6)**: Brasil (pt-BR) - Fundação com infraestrutura i18n pronta
2. **Fase 2 (Meses 7-9)**: Portugal (pt-PT) - Primeira expansão internacional
3. **Fase 3 (Meses 10-15)**: América Latina Hispânica (es-MX, es-AR, es-CO)
4. **Fase 4 (Meses 16-24)**: Espanha (es-ES) e Estados Unidos (en-US)

**Tradução Automática**:
- Workflow n8n integrado com LLM para tradução de conteúdo
- Adaptação cultural (não apenas tradução literal)
- Keywords research por país/idioma
- Status de tradução (pending, auto, reviewed, published)

**Benefícios**:
- Escala de tráfego 5-10x (múltiplos mercados)
- Diversificação de receita (menos dependência de um país)
- Vantagem competitiva (poucos blogs geek multilíngues)
- Potencial de audiência: 300+ milhões (português + espanhol)

---

### 6.7. Backend & Painel Administrativo (Python)

- Backend em Python com:
  - **FastAPI** (sugestão) para API REST e backend de aplicação.
  - Jinja2 para renderização de templates HTML (SSR para SEO).
  - `sqlalchemy` + `asyncpg` ou equivalente para PostgreSQL.

- Painel administrativo com autenticação:
  - CRUD de posts.
  - CRUD de produtos.
  - Gestão de categorias, tags, usuários.
  - Filtros por status, tipo, data, plataforma, etc.
  - Dashboard simples com métricas (posts mais vistos, produtos mais clicados etc.).

---

### 6.6. Frontend (Python SSR)

- Templates HTML/Jinja2 servidos pelo FastAPI.
- Estrutura de páginas:
  - Home (`/`)
  - Página de categoria
  - Página de post
  - Página de produto (opcional)
  - Página estática (Sobre, Contato, Política de Privacidade).

- Responsivo (mobile-first) e otimizado para Core Web Vitals.

---

### 6.7. Autenticação e Perfis

- **Perfis de usuário:**
  - `admin`: acesso total.
  - `editor`: pode revisar, editar e publicar posts.
  - `author`: cria e edita, mas não publica.
  - `automation`: usuário técnico para chamadas da API pelo n8n.

- Autenticação:
  - JWT ou sessão (FastAPI Users, por exemplo).
  - API protegida por token (para n8n).

---

### 6.8. Busca e Recomendação

- Busca interna por título, conteúdo, tags, categorias.
- Recomendação de posts related:
  - Baseado em categoria, tags e produtos em comum.
- Futuro: ranking baseado em cliques reais e engajamento.

---

### 6.9. Compliance e Termos de Uso (Afiliados)

Para garantir a conformidade com os programas de afiliados (Amazon, Mercado Livre, Shopee) e boas práticas de SEO, o sistema deve seguir rigorosamente as seguintes regras:

1.  **Aviso Legal (Disclaimer) Obrigatório:**
    - **Amazon:** É obrigatório exibir a frase exata: **"Como Associado Amazon, ganho com compras qualificadas."** em local visível (próximo aos links ou rodapé).
    - **Geral:** Exibir aviso claro de que o site contém links de afiliados e pode receber comissão.
    - **Redes Sociais:** Uso obrigatório de hashtags como `#ad`, `#publi`, `#afiliado`.

2.  **Atributos de Link (SEO):**
    - Todos os links de saída para afiliados devem conter o atributo `rel="sponsored"` (ou `rel="nofollow"`), conforme diretrizes do Google.
    - Exemplo: `<a href="..." rel="sponsored" target="_blank">Ver na Amazon</a>`

3.  **Documentação de Referência:**
    - Consultar os detalhes completos em:
      - `docs/termos-de-uso/amazon-associados.md`
      - `docs/termos-de-uso/mercado-livre-afiliados.md`
      - `docs/termos-de-uso/shopee-afiliados.md`

---

### 6.10. Calendário Editorial & Sazonalidades

- Estrutura semanal base:  
  Segunda (Top 10), Ter/Qua/Qui (produto único), Sexta (produto + mini‑guia), Sábado (guia/evergreen).  
- Rotação mensal orientada a personas: Semana 1 (Ana), Semana 2 (Lucas), Semana 3 (Marina), Semana 4 (mix).  
- Planejamento anual com sazonalidades (Natal, Black Friday, Dia dos Namorados etc.), buffers evergreen/seasonal e timeline de preparação.

Detalhamento completo: `docs/content/editorial-calendar.md`.

### 6.11. Seasonal Content Hubs

Hubs sazonais perenes (ex.: `/natal/`, `/black-friday/`, `/dia-dos-namorados/`) atuam como páginas pilar que concentram e distribuem tráfego para conteúdos e produtos da data. Estrutura, SEO e operação: `docs/content/seasonal-hubs.md`.

### 6.12. Content Recycling (1 → 24)

Sistema para transformar pilares (listicles/guias) em múltiplos formatos (posts individuais, infográfico, social, vídeo, newsletter, thread). Processo, métricas e UTMs: `docs/content/content-recycling.md`.

### 6.15. Content Hubs & Internal Linking

Estratégia de hubs e clusters para dominar tópicos-chave com pillars e links internos estruturados.  
Regras e mapeamento: `docs/content/content-hubs.md` e `docs/seo/internal-linking.md`.  
Conectar com estratégia de keywords: `docs/seo/keyword-strategy.md`.

### 6.16. Estrutura de URLs & Canonicals

Padrões de URL por tipo de página (posts, categorias, ocasiões, tags, produtos) e regras de canonical/redirects.  
Diretrizes: `docs/seo/url-structure.md`.

### 6.13. Funis de Conversão

Definições e instrumentação dos funis de Tráfego Orgânico, Afiliados e Newsletter. Ver `docs/analytics/funnels.md` e o Plano de Tracking (GA4) em `docs/analytics/tracking-plan.md`.

### 6.14. Framework de Testes A/B

Processo padronizado (hipótese → ICE → execução → análise → rollout) com instrumentação em GA4 e opcional no backend. Detalhes: `docs/analytics/ab-testing-framework.md`.

---

## 7. Requisitos Não Funcionais

- **Banco de dados:** PostgreSQL (v14+).
- **Performance:**
  - Core Web Vitals: LCP < 2,5s; INP < 200ms; CLS < 0,1.
  - Uso de cache (HTTP cache, cache de consultas).
  - CDN para assets estáticos e imagens.
  - Monitoramento de Web Vitals: `docs/seo/web-vitals-monitoring.md`.
  - Otimização de imagens (WebP/srcset/lazy): `docs/seo/image-optimization.md`.
- **Segurança:**
  - HTTPS obrigatório.
  - Proteção contra SQL Injection, XSS, CSRF.
  - Rate limit em endpoints sensíveis.
- **Escalabilidade & Infraestrutura:**
  - **Docker:** Deploy e desenvolvimento baseados 100% em Docker.
  - **Banco de Dados:** PostgreSQL rodando em container Docker separado (já existente na VPS); para desenvolvimento local, utilizar container local para simulação.
  - **Orquestração:** Docker Compose para gerenciar os serviços.
  - Possibilidade de replicação do banco no futuro.
- **Analytics:**
  - **GA4** com plano de tracking de eventos e parâmetros conforme `docs/analytics/tracking-plan.md`.
  - **Dashboards** (Looker Studio/Metabase) conforme `docs/analytics/dashboards.md` e cadência `docs/analytics/reporting-cadence.md`.
  - **Heatmaps/Recordings:** Microsoft Clarity (ou similar) para insights qualitativos.
  - **Exportação BigQuery (opcional):** habilitar para coortes e LTV.
- **LGPD:**
  - Política de cookies.
  - Coleta explícita de consentimento para newsletter.
- **Observabilidade:**
  - Logging estruturado.
  - Integração com ferramentas de monitoramento (Grafana/Prometheus, etc.).

---

## 8. Arquitetura Técnica (Alta Nível)

- **Infraestrutura:**
  - **Docker Compose:** Orquestração de todos os serviços.
  - **VPS:** Utilização de diretório na própria VPS para persistência de dados (volumes mapeados no Docker Compose).
- **Backend:** FastAPI (Python)  
- **Frontend:** Templates Jinja2 (SSR) servidos pelo FastAPI  
- **Banco de Dados:** PostgreSQL (Container Docker)
- **ORM:** SQLAlchemy (ou equivalente)  
- **Armazenamento de Imagens:** Diretório estático na VPS (volume Docker) ou S3-compatible.  
- **Automação:** n8n (self-hosted) rodando via Docker  
- **Integrações Externas:**
  - Amazon Product Advertising API (quando configurada).
  - Mercado Livre API.
  - Shopee API (quando disponível para afiliados).

---

## 9. Modelagem de Dados (Simplificada)

### 9.1. Tabela `posts`

- `id` (UUID, PK)
- `type` (`product_single`, `listicle`, `guide`)
- `title`
- `slug`
- `subtitle`
- `content` (text)
- `featured_image_url`
- `category_id` (FK)
- `tags` (array ou tabela associativa `post_tags`)
- `seo_focus_keyword`
- `seo_title`
- `seo_description`
- `status` (`draft`, `review`, `scheduled`, `published`, `archived`)
- `publish_at` (timestamp)
- `created_at`
- `updated_at`
- `shared` (bool, default false)

### 9.2. Tabela `products`

- `id` (UUID, PK)
- `name`
- `slug`
- `short_description`
- `long_description`
- `price` (numeric)
- `currency` (varchar, ex. `BRL`)
- `price_range` (varchar)
- `main_image_url`
- `images` (jsonb)
- `affiliate_url_raw`
- `affiliate_redirect_slug` (unique)
- `platform` (enum: `amazon`, `mercadolivre`, `shopee`)
- `platform_product_id`
- `categories` (jsonb ou relacional)
- `tags` (jsonb ou relacional)
- `availability` (enum)
- `rating` (numeric)
- `review_count` (int)
- `internal_score` (numeric)
- `last_price_update` (timestamp)
- `created_at`
- `updated_at`

### 9.3. Tabela `post_products` (muitos para muitos)

- `id` (PK)
- `post_id` (FK)
- `product_id` (FK)
- `position` (ordem do produto no post)

### 9.4. Tabela `users`

- `id` (PK)
- `name`
- `email`
- `password_hash`
- `role`
- `created_at`
- `updated_at`

### 9.5. Testes A/B

Tabelas para instrumentação e auditoria de experimentos A/B. Ver também `docs/analytics/ab-testing-framework.md`.

#### 9.5.1. Tabela `ab_tests`

Campos:
- `id` UUID (PK)
- `name` (varchar)
- `hypothesis` (text)
- `primary_metric` (varchar) — ex.: `affiliate_ctr`
- `area` (varchar) — ex.: `cta_button`, `listicle_table`
- `target_type` (varchar) — ex.: `post`, `sitewide`
- `target_id` (UUID, nullable) — FK opcional para `posts.id` quando aplicável
- `status` (enum: `running`, `paused`, `completed`)
- `variant_a_pct` (numeric)
- `variant_b_pct` (numeric)
- `start_at` (timestamp)
- `end_at` (timestamp, nullable)
- `created_at`, `updated_at`

DDL sugerido:
```sql
CREATE TABLE ab_tests (
  id UUID PRIMARY KEY,
  name VARCHAR(160) NOT NULL,
  hypothesis TEXT NOT NULL,
  primary_metric VARCHAR(64) NOT NULL,
  area VARCHAR(64) NOT NULL,
  target_type VARCHAR(32) NOT NULL,
  target_id UUID NULL REFERENCES posts(id),
  status VARCHAR(16) NOT NULL CHECK (status IN ('running','paused','completed')),
  variant_a_pct NUMERIC(5,2) NOT NULL DEFAULT 50.00,
  variant_b_pct NUMERIC(5,2) NOT NULL DEFAULT 50.00,
  start_at TIMESTAMP NOT NULL,
  end_at TIMESTAMP NULL,
  created_at TIMESTAMP NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);
```

#### 9.5.2. Tabela `ab_test_events`

Campos:
- `id` (PK)
- `test_id` (FK → `ab_tests.id`)
- `variant` (enum: `A`, `B`)
- `session_id` (varchar, para correlacionar com GA4/export)
- `event_type` (enum: `exposure`, `view`, `click`)
- `post_id` (FK opcional para `posts.id`)
- `occurred_at` (timestamp)

DDL sugerido:
```sql
CREATE TABLE ab_test_events (
  id UUID PRIMARY KEY,
  test_id UUID NOT NULL REFERENCES ab_tests(id),
  variant CHAR(1) NOT NULL CHECK (variant IN ('A','B')),
  session_id VARCHAR(64) NOT NULL,
  event_type VARCHAR(16) NOT NULL CHECK (event_type IN ('exposure','view','click')),
  post_id UUID NULL REFERENCES posts(id),
  occurred_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_ab_events_test_time ON ab_test_events (test_id, occurred_at);
CREATE INDEX idx_ab_events_session ON ab_test_events (session_id);
```

---

## 10. Especificação de API (REST – Resumo)

### 10.1. Autenticação

- `POST /api/auth/login`
  - Request: email, senha.
  - Response: token JWT.
- API para n8n usa header `Authorization: Bearer <token>` ou `x-api-key` específico para usuário `automation`.

### 10.2. Posts

- `POST /api/posts`
  - Cria post.
- `PUT /api/posts/{id}`
  - Atualiza post.
- `POST /api/posts/{id}/publish`
  - Publica post (status → `published`, define `publish_at`).
- `GET /api/posts`
  - Lista posts (com filtros por status, tipo, data, etc.).
- `GET /api/posts/{id}`
  - Detalhes de post.

### 10.3. Produtos

- `POST /api/products`
  - Cria produto.
- `PUT /api/products/{id}`
  - Atualiza produto (preço, descrição, etc.).
- `GET /api/products`
  - Lista produtos com filtros (categoria, tag, plataforma, disponibilidade, etc.).
- `GET /api/products/{id}`

### 10.4. Redirecionamento de Afiliado

- `GET /goto/{affiliate_redirect_slug}`
  - Registra clique (tabela de cliques ou tracking) e redireciona 302 para `affiliate_url_raw`.

---

## 11. Fluxos no n8n

### 11.1. Fluxo A – Post Diário (1 Produto)

**Objetivo:** criar automaticamente um post diário com um produto.

**Gatilho:**
- Node `Cron` – 1x/dia (ex.: 08h00).

**Passos (simplificado):**
1. `HTTP Request` → `GET /api/products?availability=available&limit=50&sort=random`  
2. `Function` → escolher 1 produto não utilizado recentemente (pode consultar uma planilha ou campo interno “last_used_in_post”).  
3. Node de IA (LLM) → gerar:
   - Título.
   - Introdução.
   - Parágrafo descrevendo o produto.
   - Call-to-action.
   - Sugestão de `seo_title`, `seo_description` e palavra-chave foco.  
4. `HTTP Request` → `POST /api/posts` com `type="product_single"`, `status="draft"` ou diretamente `published`.  
5. Opcional: `HTTP Request` → `POST /api/posts/{id}/publish` se publicação direta.  
6. Notificar time (Telegram/Slack/e-mail).

---

### 11.2. Fluxo B – Post Semanal “Top 10”

**Objetivo:** criar um post semanal com lista de 10 produtos.

**Gatilho:**
- `Cron` – 1x/semana (ex.: segunda 09h00).

**Passos (simplificado):**
1. `Set` / `IF` → define tema (ex.: Natal, Dia dos Namorados, Amigo Secreto).  
2. `HTTP Request` → `GET /api/products?tag=natal&availability=available&limit=50&sort=internal_score_desc`.  
3. `Function` → escolher 10 produtos (evitar repetição recente).  
4. Node de IA (LLM) → gerar:
   - Introdução sobre o tema.
   - Mini descrições para cada item (1 a 10).
   - Conclusão com CTA.  
5. `HTTP Request` → `POST /api/posts` (`type="listicle"`, `products=[lista de ids]`).  
6. Publicação automática ou revisão manual.  
7. Disparo para fluxo de compartilhamento (Fluxo D).

---

### 11.3. Fluxo C – Atualização de Preços (APIs Amazon, Mercado Livre, Shopee)

**Objetivo:** atualizar preço/disponibilidade dos produtos de forma recorrente.

**Gatilho:**
- `Cron` – por exemplo, 1x/dia (madrugada).

**Passos:**

1. `HTTP Request` → `GET /api/products?last_price_update<hoje-2-dias&limit=100`  
   - Busca produtos que não são atualizados há X dias.

2. `Split In Batches` → processar produtos em lotes para não exceder rate limits.

3. Para cada produto, ramo condicional (`Switch`/`IF`) por `platform`:
   - **Amazon**  
     - `HTTP Request` → Amazon Product Advertising API (ou outro endpoint disponível).  
     - Recebe preço, disponibilidade, rating, etc.
   - **Mercado Livre**  
     - `HTTP Request` → API Mercado Livre (`/items/{idProduto}` etc.).  
   - **Shopee**  
     - `HTTP Request` → API Shopee (partner/affiliate API, se disponível).  

4. `Function` → padroniza resposta: `price`, `availability`, `rating`, `review_count`.

5. `HTTP Request` → `PUT /api/products/{id}` com dados atualizados e `last_price_update=now()`.

6. Log de status (sucesso/erro) em planilha, banco ou serviço de log.

> Observação: se a integração for mais simples no backend Python (por questão de SDKs), este fluxo pode apenas chamar um endpoint do backend que, internamente, faz as consultas às APIs dos afiliados. O PRD permite ambos os cenários; a decisão fica a cargo da implementação.

---

### 11.4. Fluxo D – Compartilhamento Automático de Post Publicado

**Objetivo:** ao publicar um post, disparar textos prontos para redes/canais.

**Gatilho:**

- **Opção recomendada:** o backend chama um Webhook do n8n quando um post entra em `status=published`.

**Passos:**

1. `Webhook` (n8n) recebe `title`, `url`, `summary`, `type`, `tags`.  
2. Node de IA (LLM) → gera variações de texto para:
   - WhatsApp/Telegram (mensagem mais pessoal).
   - X/Twitter (texto curto).
   - LinkedIn (texto mais descritivo).
3. (Opcional) Encurtar links via Bitly/Rebrandly (`HTTP Request`).  
4. Enviar mensagens:
   - Telegram bot.
   - E-mail com sugestões de texto.
   - Integração com ferramentas de agendamento (Buffer, etc.).  
5. `HTTP Request` → `PUT /api/posts/{id}` com `shared=true` para evitar duplicidade.

---

### 11.5. Fluxo E – Pesquisa Qualificada com IA (Descoberta de Itens e Montagem de Post)

**Objetivo:** permitir que o time (ou um gatilho semanal) acione um fluxo que:

1. Usa IA para entender um **tema de post** (ex.: “presentes geek até 100 reais para devs”).  
2. Pesquisa produtos nas APIs dos afiliados.  
3. Seleciona os melhores itens.  
4. Gera automaticamente descrição, texto e links de afiliado e cria o post.

**Gatilhos possíveis:**

- Formulário interno (Typeform/Google Forms) + Webhook n8n.  
- Execução manual no próprio n8n (node `Webhook` ou `Manual Trigger`).  
- Cron semanal com temas pré-definidos.

**Passos (visão geral):**

1. **Receber tema/briefing**  
   - Node `Webhook` recebe JSON com:
     - `tema` (ex.: “presentes geek até 100 reais para devs”).  
     - `quantidade_itens` (ex.: 10).  
     - `faixa_preco` (ex.: até R$ 100).  
     - `ocasião` (ex.: “aniversário”).  

2. **IA – Interpretação do Tema**  
   - Node de IA (LLM) → transforma tema em parâmetros estruturados:
     - palavras-chave de busca,
     - tags/ocasião,
     - plataformas prioritárias (por ex.: começar por Amazon e Mercado Livre).  

3. **Busca nas APIs dos Afiliados**  
   - Para cada plataforma (por ordem de prioridade):
     - `HTTP Request` → API da Amazon, Mercado Livre, Shopee com os termos de busca e filtros de preço.  
   - Agrupar resultados em uma lista bruta de produtos.

4. **IA – Seleção dos Melhores Produtos**  
   - Node de IA (LLM ou lógica tradicional com função) para:
     - filtrar produtos irrelevantes,
     - remover duplicados,
     - escolher os `N` melhores (por relevância, preço, avaliação etc.).  

5. **Criar/Atualizar Produtos no Blog**  
   - Para cada produto selecionado:
     - `HTTP Request` → `POST /api/products` (ou `PUT` se já existir `platform_product_id`).  
   - Receber lista de `product_ids` do blog.

6. **IA – Montagem do Conteúdo do Post**  
   - Node de IA:
     - Gera título sugestivo,
     - Introdução,
     - Descrição resumida de cada item,
     - Conclusão com CTA,
     - `seo_title`, `seo_description`, `focus_keyword`.  

7. **Criação do Post**  
   - `HTTP Request` → `POST /api/posts` com:
     - `type="listicle"`,
     - `products=[lista de product_ids]`,
     - conteúdo em Markdown/HTML,
     - status `draft` ou `scheduled`.  

8. **Revisão / Publicação**  
   - Editor revisa no painel ou há um segundo fluxo n8n que publica automaticamente conforme regras.

---

### 11.6. Fluxo F – Monitoramento de Oportunidades (Descontos e Redes Sociais)

**Objetivo:** Monitorar sites de promoções e perfis de redes sociais para identificar produtos geek com desconto, gerar link de afiliado e criar postagem automaticamente.

**Gatilho:**
- `Cron` (ex.: a cada 30 min) ou `Webhook` de monitoramento externo.

**Passos:**
1. **Monitoramento:**
   - Node `HTTP Request` / `HTML Extract` para ler sites de descontos ou APIs de redes sociais.
   - Filtrar por palavras-chave (ex.: "geek", "nerd", "lego", "funko", "marvel").
2. **Detecção de Oportunidade:**
   - Verificar se o desconto é real (comparar com histórico ou preço base).
   - Verificar se é um produto "geek" válido.
3. **Geração de Link:**
   - Criar link de afiliado para a oferta encontrada.
4. **Criação do Post:**
   - Node de IA (LLM) para gerar título chamativo ("Corre! Promoção de X..."), descrição rápida e CTA.
   - `HTTP Request` → `POST /api/posts` (tipo `product_single` ou `deal`).
5. **Publicação e Divulgação:**
   - Publicar imediatamente.
   - Acionar **Fluxo D** para divulgar nas redes sociais do blog.

### 11.7. Fluxo G – Relatórios Automatizados

Objetivo: enviar relatórios diário/semanal/mensal para stakeholders.  
Gatilho: Cron diário/semanal/mensal.  
Passos (alto nível):
1) Coletar métricas de GA4/Search Console/PostgreSQL (cliques afiliados)  
2) Compilar resumo e links de dashboards (Looker Studio)  
3) Enviar via Telegram/Email aos destinatários  
Especificação de conteúdo/cadência: `docs/analytics/reporting-cadence.md`.

### 11.8. Fluxo H – Alertas e Monitoramento

Objetivo: alertar automaticamente sobre anomalias ou falhas.  
Gatilho: Cron a cada X minutos + checagens (uptime, tráfego, n8n).  
Exemplos de alertas: queda de tráfego > 30% (vs semana anterior), CTR < 2%, falha em fluxo A/B, erro 500.  
Implementação sugerida: integração Telegram conforme exemplo em `agents/data-analyst.md` (seção de alertas), com thresholds configuráveis.

### 11.9. Fluxo I – Content Refresh

Objetivo: atualizar e reotimizar conteúdos com base em performance e sazonalidade.  
Gatilhos: Cron mensal (top performers) e trimestral (sazonais).  
Passos:  
1) Identificar páginas alvo (GA4/SC: pageviews, CTR, queda de posições).  
2) Recomendar atualizações (novas keywords, +100–200 palavras, novos produtos/preços).  
3) Criar tarefas para editores; reindexar via Search Console.  
Regras: ver plano em `docs/content/editorial-calendar.md` (buffers) e orientações de SEO.

### 11.10. Fluxo J – Content Gap (Search Console)

Objetivo: detectar gaps de conteúdo e gerar briefs.  
Gatilho: Cron semanal.  
Passos:  
1) Ler queries com impressões > X e CTR < 2%.  
2) Sugerir novos posts/sections com base em `docs/seo/keyword-strategy.md`.  
3) Enfileirar ideias no board editorial.

---

## 12. Guia de Comunicação Visual & Layout

> **Especificação Completa**: Ver [PRD-design-system.md](PRD-design-system.md) para design tokens, componentes, acessibilidade, performance e implementação detalhada do sistema de design.

### 12.1. Posicionamento de Marca

- **Nome/Site:** geek.bidu.guru  
- **Personalidade:**  
  - Nerd, divertida, bem-humorada, porém confiável e “explicativa”.  
  - Mistura de “amigo geek que ajuda” com “curador especializado em presentes”.  

- **Tom de voz:**  
  - Próximo, informal controlado, sem gírias excessivas.  
  - Frases claras, objetivas, com pitadas de referências geek (sem exagero).

Guia de estilo completo (brand voice chart, exemplos e diretrizes para IA): `docs/content/style-guide.md`.

### 12.2. Paleta de Cores (sugestão)

- **Cor primária:**  
  - Roxo/neon geek: `#7C3AED` (referência a universo de tecnologia, magia, ficção científica).

- **Cores secundárias:**  
  - Ciano/teal tecnológico: `#06B6D4`  
  - Amarelo destaque (botões/CTAs): `#FACC15`

- **Neutros:**  
  - Fundo escuro (modo dark como padrão visual, com opção de light):  
    - Background: `#020617`  
    - Cartões: `#0F172A`  
  - Texto principal: `#F9FAFB`  
  - Texto secundário: `#9CA3AF`

> O blog pode adotar **dark theme** como identidade principal (reforça o universo geek), com a possibilidade futura de um toggle light/dark.

**Design Tokens** (especificação completa em [PRD-design-system.md](PRD-design-system.md#design-tokens)):

O sistema de design utiliza **CSS Custom Properties** para garantir consistência e facilitar manutenção:

```css
:root {
  /* Primary Colors (Purple Geek) */
  --color-primary-500: #7C3AED;
  --color-primary-600: #6D28D9;

  /* Accent Colors (Yellow CTA) */
  --color-accent-500: #FACC15;
  --color-accent-600: #F59E0B;

  /* Dark Theme Backgrounds */
  --bg-primary: #020617;
  --bg-secondary: #0F172A;
  --bg-tertiary: #1E293B;

  /* Spacing (4px scale) */
  --space-4: 1rem;      /* 16px */
  --space-6: 1.5rem;    /* 24px */
  --space-8: 2rem;      /* 32px */

  /* Touch Targets */
  --touch-target-min: 44px;
}
```

### 12.3. Tipografia

- **Títulos (H1, H2):**  
  - Fonte sans-serif forte como **Poppins** ou **Montserrat**, peso 600–700.  
- **Texto corrido:**  
  - Fonte **Inter** ou **Roboto**, peso 400–500.  
- **Destaques/códigos:**  
  - Monospace leve (ex.: **JetBrains Mono**) para pequenos detalhes geeks (opcional).

### 12.4. Iconografia & Ilustrações

- Ícones simples de linha (outline), estilo minimalista, com detalhes em roxo e ciano.  
- Ilustrações e imagens:
  - Preferência por fotos de produtos em bom recorte, sobre fundos neutros.  
  - Elementos gráficos que remetam a:
    - espaço, galáxia, pixels, controles, circuitos, etc., mas de forma discreta.

### 12.5. Layout – Home (`/`)

Seções sugeridas:

1. **Hero**
   - Fundo escuro com gradiente roxo/ciano.
   - Título grande: “Encontre o presente geek perfeito em poucos cliques”.
   - Subtítulo: “Listas, reviews e ideias criadas por geeks, para geeks – com os melhores achados da Amazon, Mercado Livre e Shopee.”
   - CTA: “Ver presentes por ocasião” + “Presentes até R$ 100”.

2. **Seção de Destaques**
   - Cards de posts em destaque (últimos “Top 10”).

3. **Navegação por Ocasião**
   - Ícones grandes: Natal, Aniversário, Amigo Secreto, Dia dos Namorados etc.

4. **Categorias por Perfil/Fandom**
   - Gamer, Otaku, Dev, Boardgamer, Star Wars, Marvel, etc.

5. **Newsletter**
   - Bloco simples com CTA: “Receba as melhores ideias de presentes geek toda semana”.

6. **Posts Recentes**
   - Lista dos posts mais novos (produto único + listas).

### 12.6. Layout – Página de Post

Estrutura sugerida:

- Breadcrumbs: Home > Categoria > Título do Post.  
- Título (H1) grande, seguido de subtítulo (opcional).  
- Bloco de informações:
  - Data de publicação.
  - Tags/categoria.
  - Botões de compartilhamento (WhatsApp, Telegram, etc.) logo no topo.  
- Conteúdo em colunas horizontais:
  - Coluna principal com texto, listas e imagens.
  - Sidebar (em desktop) com:
    - “Presentes em destaque”.
    - Newsletter.
    - Links para outros posts.
    - **Aviso Legal (Disclaimer):** Texto visível sobre afiliação (ex.: "Como Associado Amazon...").

- Para posts de lista:
  - Cada item numerado com:
    - Foto do produto.
    - Nome.
    - Descrição curta.
    - Faixa de preço (indicativa).
    - Botão “Ver no [Amazon/Mercado Livre/Shopee]” (via `/goto/...`).

### 12.7. Layout – Responsivo

- Mobile-first:
  - Menus colapsados (hambúrguer).
  - Cards em coluna única.
  - Botões grandes, fáceis de clicar (tamanho mínimo 44px de altura).

### 12.8. Acessibilidade (WCAG 2.1 AA)

**Requisitos Obrigatórios** (detalhes em [PRD-design-system.md](PRD-design-system.md#acessibilidade)):

- **Contraste de Cores**: Mínimo 4.5:1 para texto normal, 3:1 para texto grande (18px+ ou 14px+ bold)
- **Navegação por Teclado**: Todos os elementos interativos acessíveis via Tab, Enter e Espaço
- **Skip Links**: Link "Pular para conteúdo" no topo da página
- **Focus Visible**: Estados de foco claramente visíveis em todos os elementos interativos
- **ARIA Labels**: Uso correto de `aria-label`, `aria-labelledby` e `role` onde necessário
- **Alt Text**: Todas as imagens com texto alternativo descritivo
- **Estrutura Semântica**: Uso correto de HTML5 semântico (`<header>`, `<nav>`, `<main>`, `<article>`, `<aside>`, `<footer>`)

**Checklist de Validação**:
- [ ] Contraste validado com Lighthouse/WAVE
- [ ] Navegação por teclado testada em todas as páginas
- [ ] Leitores de tela compatíveis (NVDA/JAWS)
- [ ] Formulários com labels e mensagens de erro claras

### 12.9. Performance e Otimização de Imagens

**Metas de Performance** (alinhadas com Core Web Vitals em seção 7):

- **LCP (Largest Contentful Paint)**: < 2s (ideal), < 2.5s (aceitável)
- **FID (First Input Delay)**: < 50ms (ideal), < 100ms (aceitável)
- **CLS (Cumulative Layout Shift)**: < 0.05 (ideal), < 0.1 (aceitável)

**Estratégias de Otimização de Imagens** (especificação completa em [PRD-design-system.md](PRD-design-system.md#performance-e-imagens)):

- **Formato WebP**: Prioridade para WebP com fallback JPG/PNG
- **Responsive Images**: Uso de `srcset` e `sizes` para diferentes breakpoints
- **Lazy Loading**: `loading="lazy"` em todas as imagens abaixo da dobra
- **Dimensionamento**: Especificar `width` e `height` para evitar CLS
- **CDN**: Servir imagens via CDN com cache agressivo

**Exemplo de Implementação**:
```html
<picture>
  <source type="image/webp" srcset="
    /images/produto-320.webp 320w,
    /images/produto-640.webp 640w,
    /images/produto-1024.webp 1024w
  " sizes="(max-width: 640px) 100vw, 50vw">
  <img src="/images/produto-640.jpg"
       alt="Descrição do produto"
       width="640" height="480"
       loading="lazy">
</picture>
```

**Critical CSS**: Inline de CSS crítico (above-the-fold) para acelerar FCP (First Contentful Paint)

**Font Loading**: Estratégia de `font-display: swap` para evitar FOIT (Flash of Invisible Text)

---

## 13. Roadmap Macro (Resumo)

- **Fase 1 – Base técnica (Python + PostgreSQL + Design System)**
  - Implementar backend FastAPI + PostgreSQL.
  - Modelagem de dados (posts, produtos, relacionamentos).
  - **Implementar Design System** conforme [PRD-design-system.md](PRD-design-system.md):
    - Setup de design tokens (CSS custom properties)
    - Sistema de cores com dark theme como padrão
    - Tipografia responsiva com clamp()
    - Grid system (12 colunas)
    - Componentes base (botões, cards, formulários)
    - Acessibilidade WCAG 2.1 AA (contraste, navegação por teclado, ARIA)
    - Performance (responsive images, lazy loading, critical CSS)
  - Templates Jinja2 com layout baseado no design system.
  - Painel administrativo simples.
  - API REST para posts/produtos.

- **Fase 2 – SEO & Automação Core**
  - Implementar sitemap, robots, Open Graph, schema básico.
  - Configurar fluxos n8n A (post diário) e B (top 10 semanal).
  - Implementar redirecionamento `/goto`.
  - Implementar Fluxo C (atualização de preços).
  - Formalizar calendário editorial anual e scorecard de curadoria (documentos vinculados no PRD).
  - Criar hubs sazonais prioritários (`/natal/`, `/black-friday/`, `/dia-dos-namorados/`).
  - Implementar **framework de Testes A/B** (docs/analytics/ab-testing-framework.md).
  - Configurar **GA4** conforme plano de tracking e **Clarity** (heatmaps).
  - Publicar **dashboards** (Executivo, Conteúdo, Afiliados) e **relatórios automatizados**.
  - Documentar **estratégia de keywords** e iniciar **featured snippets** (FAQ/HowTo/listas/tabelas).
  - Implementar **schemas avançados** e **internal linking** (hubs & clusters).

- **Fase 3 – IA, Pesquisa Qualificada e Internacionalização**
  - Implementar Fluxo E (pesquisa qualificada com IA).
  - Refinar copy gerada via IA (guidelines, prompts).
  - Operacionalizar Content Recycling (1 → 24) conforme documento, com automações para sociais/newsletter.
  - Iniciar **exportação BigQuery** (GA4) e análises de **coortes/LTV**.
  - **Video SEO** (VideoObject + video sitemap) e rollout de conteúdos em vídeo.
  - **Internacionalização**: Implementar infraestrutura completa de i18n conforme [PRD-internationalization.md](PRD-internationalization.md)
    - Tabelas de tradução e localização
    - Workflow de tradução automática (n8n + LLM)
    - Hreflang tags e sitemap multilingue
    - Lançamento Portugal (pt-PT) como primeiro mercado internacional
  - **Estratégia de Afiliados Avançada**: Implementar melhorias conforme [PRD-affiliate-strategy.md](PRD-affiliate-strategy.md)
    - Dashboard completo de afiliados com métricas detalhadas
    - Sistema de scorecard de produtos
    - Framework de testes A/B estruturado
    - Otimização de CTAs e técnicas de conversão
    - Sistema de alertas automáticos
  - **Voice Search**: conteúdo conversacional + `Speakable` (quando aplicável).

- **Fase 4 – Crescimento & Otimização**
  - Quiz, newsletter mais robusta, testes A/B.
  - Recomendações personalizadas.
  - Otimização contínua de SEO e conversão.

---

## 14. Gaps Identificados e Plano de Ação

> **Documento de Referência**: Ver [reports/consolidated-analysis.md](reports/consolidated-analysis.md) para análise completa dos 6 especialistas.

### 14.1. Resumo de Scores por Área

| Área | Score | Status |
|------|-------|--------|
| Affiliate Marketing | 8.5/10 | Fundação sólida, otimização avançada pendente |
| Content Strategy | 7/10 | Estrutura boa, operacionalização necessária |
| Data/Analytics | 6.5/10 | Gaps em tracking e dashboards |
| SEO | 6.5/10 | Técnico bom, estratégia a documentar |
| UX/UI | 7/10 | Design tokens e acessibilidade a completar |

### 14.2. TOP 5 Quick Wins (Alta Prioridade)

1. **Urgência e Escassez nos CTAs**
   - Countdown timers, badges "Últimas X unidades", alertas "Preço baixou!"
   - Impacto: +15-25% conversão
   - Detalhes: [PRD-affiliate-strategy.md](PRD-affiliate-strategy.md#urgência-e-escassez)

2. **Plano de Tracking GA4 Formal**
   - Eventos, parâmetros customizados, dimensões por persona
   - Impacto: Visibilidade completa do funil
   - Documento: `docs/analytics/tracking-plan.md`

3. **Design Tokens Completos**
   - CSS custom properties (espaçamento, shadows, z-index, animações)
   - Impacto: Consistência visual, manutenção facilitada
   - Detalhes: [PRD-design-system.md](PRD-design-system.md#design-tokens)

4. **Keywords Strategy Documentada**
   - Volumes de busca, dificuldade, clusters semânticos por persona
   - Impacto: +40-60% potencial de tráfego orgânico
   - Documento: `docs/seo/keyword-strategy.md`

5. **Templates de Conteúdo Operacionais**
   - Seções obrigatórias, tamanhos, CTAs, schema por tipo de post
   - Impacto: Qualidade consistente, automação facilitada
   - Documento: `docs/content/templates.md`

### 14.3. Gaps por Área

#### SEO (Prioridade Alta)
- [ ] Estratégia de keywords não documentada
- [ ] Content hubs e pillar pages ausentes
- [ ] Featured snippets strategy não implementada
- [ ] Internal linking structure não definida
- [ ] Link building strategy não documentada
- [ ] Voice search não contemplada
- [ ] Image SEO não especificado

**Documentos a criar:**
- `docs/seo/keyword-strategy.md`
- `docs/seo/internal-linking.md`
- `docs/seo/featured-snippets.md`
- `docs/seo/link-building.md`
- `docs/seo/image-seo.md`

#### Affiliate Marketing (Prioridade Alta)
- [ ] Urgência/escassez não implementada
- [ ] Email marketing estruturado ausente
- [ ] Cross-sell/upsell limitado
- [ ] Programa de indicação inexistente
- [ ] Histórico de preços não integrado
- [ ] Alertas de wishlist não implementados

**Documentos a criar:**
- `docs/affiliate/email-marketing.md`
- `docs/affiliate/urgency-scarcity.md`
- `docs/affiliate/referral-program.md`

#### Analytics (Prioridade Alta)
- [ ] Plano de tracking GA4 não formalizado
- [ ] Dashboards não especificados
- [ ] Sistema de alertas manual
- [ ] Análise de coortes/LTV não planejada
- [ ] Funnels não instrumentados

**Documentos a criar:**
- `docs/analytics/tracking-plan.md`
- `docs/analytics/dashboards.md`
- `docs/analytics/alerts-system.md`

#### Content (Prioridade Média)
- [ ] Templates não detalhados operacionalmente
- [ ] Processo de curadoria informal
- [ ] Estratégia UGC ausente
- [ ] Content recycling não automatizado
- [ ] Quizzes interativos não implementados

**Documentos a criar:**
- `docs/content/templates.md` (detalhar)
- `docs/content/curation-scorecard.md`
- `docs/content/ugc-strategy.md`

#### UX/UI (Prioridade Média)
- [ ] Design tokens incompletos
- [ ] Acessibilidade WCAG 2.1 AA parcial
- [ ] Estados de componentes não documentados
- [ ] Dark/light mode toggle não implementado
- [ ] Skeleton loading não padronizado

**Documentos a atualizar:**
- [PRD-design-system.md](PRD-design-system.md)

### 14.4. Roadmap de Implementação

#### Quick Wins (Semanas 1-2)
- Design tokens completos
- Plano de tracking GA4
- Elementos de urgência/escassez

#### Fase A (Mês 1)
- Keywords strategy com clusters
- Dashboard Executivo
- Content hubs principais
- Sistema de alertas

#### Fase B (Meses 2-3)
- Featured snippets optimization
- Email marketing sequences
- Internal linking structure
- Cross-sell/upsell

#### Fase C (Meses 4-6)
- UGC/Reviews system
- Video SEO
- Programmatic SEO
- International expansion

### 14.5. KPIs de Evolução

| Métrica | Baseline | 3 meses | 6 meses | 12 meses |
|---------|----------|---------|---------|----------|
| SEO Score | 6.5/10 | 7.5/10 | 8.5/10 | 9/10 |
| Affiliate Score | 8.5/10 | 9/10 | 9.5/10 | 9.5/10 |
| Data Score | 6.5/10 | 8/10 | 9/10 | 9.5/10 |
| Design Score | 7/10 | 8/10 | 9/10 | 9/10 |
| Content Score | 7/10 | 8/10 | 8.5/10 | 9/10 |

---

Este PRD descreve o **geek.bidu.guru** como um produto completo: do backend em Python com PostgreSQL, passando pela camada visual, até a malha de automação com n8n, integrações com afiliados e fluxos de IA para pesquisa e criação de conteúdo.
