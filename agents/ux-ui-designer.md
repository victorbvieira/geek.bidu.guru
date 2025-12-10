# UX/UI Designer - geek.bidu.guru

## 👤 Perfil do Agente

**Nome**: UX/UI Designer
**Área**: Negócio / Design
**Especialidade**: Experiência do usuário, design de interfaces, identidade visual, usabilidade

## 🎯 Responsabilidades

- Design de interfaces (UI) para web
- Experiência do usuário (UX) otimizada
- Definição de identidade visual da marca
- Criação de guia de estilo e design system
- Prototipagem e wireframes
- Otimização de conversão através do design
- Responsividade e mobile-first design
- Acessibilidade (a11y)

## 📊 KPIs Principais

- **Core Web Vitals**:
  - LCP (Largest Contentful Paint) < 2.5s
  - FID (First Input Delay) < 100ms
  - CLS (Cumulative Layout Shift) < 0.1
- **Taxa de rejeição** (bounce rate) < 50%
- **Tempo médio na página** > 2min
- **Cliques em CTAs** (taxa de conversão)
- **Mobile usability score** > 90
- **Acessibilidade score** > 90

## 🎨 Identidade Visual

### Paleta de Cores

**Cores Primárias**:
```css
:root {
  /* Roxo/Violeta Geek - Cor principal da marca */
  --primary-500: #7C3AED;
  --primary-600: #6D28D9;
  --primary-700: #5B21B6;

  /* Ciano/Teal Tecnológico - Cor secundária */
  --secondary-500: #06B6D4;
  --secondary-600: #0891B2;

  /* Amarelo/Dourado - CTAs e destaques */
  --accent-500: #FACC15;
  --accent-600: #F59E0B;
}
```

**Cores Neutras (Dark Theme - Padrão)**:
```css
:root {
  /* Backgrounds */
  --bg-primary: #020617;      /* Fundo principal (slate-950) */
  --bg-secondary: #0F172A;    /* Cards e containers (slate-900) */
  --bg-tertiary: #1E293B;     /* Elementos elevados (slate-800) */

  /* Textos */
  --text-primary: #F9FAFB;    /* Texto principal (gray-50) */
  --text-secondary: #9CA3AF;  /* Texto secundário (gray-400) */
  --text-muted: #6B7280;      /* Texto discreto (gray-500) */

  /* Borders */
  --border-color: #334155;    /* Bordas (slate-700) */
  --border-hover: #475569;    /* Bordas hover (slate-600) */
}
```

**Cores Neutras (Light Theme - Opcional)**:
```css
.light-theme {
  --bg-primary: #FFFFFF;
  --bg-secondary: #F9FAFB;
  --bg-tertiary: #F3F4F6;

  --text-primary: #111827;
  --text-secondary: #4B5563;
  --text-muted: #9CA3AF;

  --border-color: #E5E7EB;
  --border-hover: #D1D5DB;
}
```

**Cores Semânticas**:
```css
:root {
  /* Sucesso */
  --success-500: #10B981;
  --success-600: #059669;

  /* Alerta */
  --warning-500: #F59E0B;
  --warning-600: #D97706;

  /* Erro */
  --error-500: #EF4444;
  --error-600: #DC2626;

  /* Info */
  --info-500: #3B82F6;
  --info-600: #2563EB;
}
```

### Tipografia

**Fontes**:
```css
:root {
  /* Headings - Sans-serif forte */
  --font-heading: 'Poppins', 'Montserrat', system-ui, sans-serif;

  /* Body - Sans-serif legível */
  --font-body: 'Inter', 'Roboto', system-ui, sans-serif;

  /* Monospace - Código e detalhes técnicos */
  --font-mono: 'JetBrains Mono', 'Fira Code', monospace;
}
```

**Escala Tipográfica**:
```css
:root {
  /* Headings */
  --text-h1: 2.5rem;      /* 40px */
  --text-h2: 2rem;        /* 32px */
  --text-h3: 1.5rem;      /* 24px */
  --text-h4: 1.25rem;     /* 20px */

  /* Body */
  --text-lg: 1.125rem;    /* 18px */
  --text-base: 1rem;      /* 16px */
  --text-sm: 0.875rem;    /* 14px */
  --text-xs: 0.75rem;     /* 12px */

  /* Line Heights */
  --leading-tight: 1.25;
  --leading-normal: 1.5;
  --leading-relaxed: 1.75;
}
```

**Pesos de Fonte**:
```css
:root {
  --font-normal: 400;
  --font-medium: 500;
  --font-semibold: 600;
  --font-bold: 700;
}
```

### Espaçamento e Grid

**Sistema de Espaçamento (baseado em 8px)**:
```css
:root {
  --space-1: 0.25rem;   /* 4px */
  --space-2: 0.5rem;    /* 8px */
  --space-3: 0.75rem;   /* 12px */
  --space-4: 1rem;      /* 16px */
  --space-6: 1.5rem;    /* 24px */
  --space-8: 2rem;      /* 32px */
  --space-12: 3rem;     /* 48px */
  --space-16: 4rem;     /* 64px */
  --space-24: 6rem;     /* 96px */
}
```

**Breakpoints Responsivos**:
```css
/* Mobile-first approach */
:root {
  --screen-sm: 640px;   /* Tablets */
  --screen-md: 768px;   /* Tablets landscape */
  --screen-lg: 1024px;  /* Desktop */
  --screen-xl: 1280px;  /* Desktop large */
  --screen-2xl: 1536px; /* Desktop XL */
}
```

### Bordas e Sombras

**Border Radius**:
```css
:root {
  --radius-sm: 0.25rem;   /* 4px */
  --radius-md: 0.5rem;    /* 8px */
  --radius-lg: 0.75rem;   /* 12px */
  --radius-xl: 1rem;      /* 16px */
  --radius-full: 9999px;  /* Circular */
}
```

**Sombras**:
```css
:root {
  /* Elevação sutil */
  --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);

  /* Elevação média (cards) */
  --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1),
               0 2px 4px -1px rgba(0, 0, 0, 0.06);

  /* Elevação alta (modais) */
  --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1),
               0 4px 6px -2px rgba(0, 0, 0, 0.05);

  /* Sombra colorida (CTAs) */
  --shadow-accent: 0 4px 12px rgba(250, 204, 21, 0.4);
  --shadow-primary: 0 4px 12px rgba(124, 58, 237, 0.4);
}
```

## 🏗️ Componentes de UI

### Botões

**Botão Primário** (CTAs principais):
```css
.btn-primary {
  background: linear-gradient(135deg, var(--accent-500) 0%, var(--accent-600) 100%);
  color: #000;
  padding: 12px 24px;
  border-radius: var(--radius-md);
  font-weight: var(--font-semibold);
  font-size: var(--text-base);
  border: none;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-accent);
}

.btn-primary:active {
  transform: translateY(0);
}
```

**Botão Secundário**:
```css
.btn-secondary {
  background: transparent;
  color: var(--primary-500);
  border: 2px solid var(--primary-500);
  padding: 12px 24px;
  border-radius: var(--radius-md);
  font-weight: var(--font-semibold);
  transition: background 0.2s, color 0.2s;
}

.btn-secondary:hover {
  background: var(--primary-500);
  color: #fff;
}
```

**Botão Ghost** (links discretos):
```css
.btn-ghost {
  background: transparent;
  color: var(--text-secondary);
  padding: 8px 16px;
  border: none;
  border-radius: var(--radius-md);
  transition: background 0.2s;
}

.btn-ghost:hover {
  background: var(--bg-tertiary);
  color: var(--text-primary);
}
```

### Cards

**Card de Produto**:
```css
.product-card {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  padding: var(--space-6);
  transition: transform 0.2s, box-shadow 0.2s;
}

.product-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-lg);
  border-color: var(--primary-500);
}

.product-card img {
  width: 100%;
  aspect-ratio: 1 / 1;
  object-fit: cover;
  border-radius: var(--radius-md);
}

.product-card h3 {
  font-family: var(--font-heading);
  font-size: var(--text-lg);
  font-weight: var(--font-semibold);
  color: var(--text-primary);
  margin-top: var(--space-4);
}

.product-card .price {
  font-size: var(--text-h3);
  font-weight: var(--font-bold);
  color: var(--accent-500);
  margin-top: var(--space-2);
}
```

**Card de Post**:
```css
.post-card {
  background: var(--bg-secondary);
  border-radius: var(--radius-lg);
  overflow: hidden;
  transition: transform 0.2s;
}

.post-card:hover {
  transform: scale(1.02);
}

.post-card img {
  width: 100%;
  aspect-ratio: 16 / 9;
  object-fit: cover;
}

.post-card-content {
  padding: var(--space-6);
}

.post-card-category {
  display: inline-block;
  background: var(--primary-500);
  color: #fff;
  padding: 4px 12px;
  border-radius: var(--radius-full);
  font-size: var(--text-xs);
  font-weight: var(--font-medium);
  text-transform: uppercase;
}

.post-card-title {
  font-family: var(--font-heading);
  font-size: var(--text-h3);
  font-weight: var(--font-semibold);
  color: var(--text-primary);
  margin-top: var(--space-3);
  line-height: var(--leading-tight);
}

.post-card-excerpt {
  color: var(--text-secondary);
  margin-top: var(--space-2);
  line-height: var(--leading-normal);
}
```

### Navegação

**Header**:
```css
.header {
  background: rgba(2, 6, 23, 0.8);
  backdrop-filter: blur(8px);
  border-bottom: 1px solid var(--border-color);
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-container {
  max-width: 1280px;
  margin: 0 auto;
  padding: var(--space-4) var(--space-6);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.logo {
  font-family: var(--font-heading);
  font-size: var(--text-h3);
  font-weight: var(--font-bold);
  color: var(--text-primary);
  text-decoration: none;
}

.logo span {
  color: var(--accent-500);
}

.nav-menu {
  display: flex;
  gap: var(--space-6);
  list-style: none;
}

.nav-link {
  color: var(--text-secondary);
  text-decoration: none;
  font-weight: var(--font-medium);
  transition: color 0.2s;
}

.nav-link:hover {
  color: var(--primary-500);
}

.nav-link.active {
  color: var(--accent-500);
}
```

### Formulários

**Input Field**:
```css
.input {
  background: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  color: var(--text-primary);
  padding: 12px 16px;
  border-radius: var(--radius-md);
  font-size: var(--text-base);
  width: 100%;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.input:focus {
  outline: none;
  border-color: var(--primary-500);
  box-shadow: 0 0 0 3px rgba(124, 58, 237, 0.1);
}

.input::placeholder {
  color: var(--text-muted);
}
```

## 📱 Layouts de Páginas

### Homepage (`/`)

**Estrutura**:
```
[Header - sticky]
[Hero Section - full width, gradient background]
[Featured Posts - 3 colunas desktop, 1 mobile]
[Ocasiões - grid de ícones grandes]
[Categorias/Fandoms - cards horizontais]
[Posts Recentes - lista]
[Newsletter CTA - destaque]
[Footer]
```

**Hero Section**:
```html
<section class="hero">
  <div class="hero-content">
    <h1 class="hero-title">
      Encontre o <span>presente geek</span> perfeito
    </h1>
    <p class="hero-subtitle">
      Listas, reviews e ideias criadas por geeks, para geeks
    </p>
    <div class="hero-cta">
      <a href="/presentes-natal" class="btn-primary">
        🎄 Presentes de Natal
      </a>
      <a href="/presentes-baratos" class="btn-secondary">
        💰 Até R$ 100
      </a>
    </div>
  </div>
  <div class="hero-visual">
    <!-- Ilustração ou imagem -->
  </div>
</section>
```

---

### Página de Post

**Estrutura**:
```
[Breadcrumbs]
[Título (H1) + Meta (data, categoria)]
[Imagem Destacada]
[Botões de Compartilhamento]
[Conteúdo Principal - 2 colunas desktop]
  ├─ [Artigo]
  └─ [Sidebar - produtos destacados, newsletter]
[Produtos Relacionados]
[Posts Relacionados]
[Comentários/Discussão - opcional]
```

**Layout Desktop**:
```css
.post-layout {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: var(--space-12);
  max-width: 1280px;
  margin: 0 auto;
  padding: var(--space-8) var(--space-6);
}

@media (max-width: 768px) {
  .post-layout {
    grid-template-columns: 1fr;
  }
}
```

**Tabela Comparativa em Post**:
```html
<div class="comparison-table">
  <table>
    <thead>
      <tr>
        <th>Produto</th>
        <th>Preço</th>
        <th>Avaliação</th>
        <th>Onde Comprar</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td>
          <div class="product-cell">
            <img src="produto.jpg" alt="">
            <span>Nome do Produto</span>
          </div>
        </td>
        <td>
          <span class="price">R$ 89,90</span>
        </td>
        <td>
          <div class="rating">
            ⭐⭐⭐⭐⭐
            <span>(1.2k)</span>
          </div>
        </td>
        <td>
          <a href="/goto/produto" class="btn-primary btn-sm">
            Ver Oferta
          </a>
        </td>
      </tr>
    </tbody>
  </table>
</div>
```

## ♿ Acessibilidade (a11y)

### Checklist de Acessibilidade

- [ ] **Contraste de cores** adequado (mínimo 4.5:1 para texto)
- [ ] **Alt text** em todas as imagens
- [ ] **Navegação por teclado** funcional (Tab, Enter, Esc)
- [ ] **ARIA labels** em botões e links sem texto
- [ ] **Headings hierárquicos** (H1 > H2 > H3)
- [ ] **Focus states** visíveis em todos os elementos interativos
- [ ] **Skip to content** link para pular navegação
- [ ] **Tamanho mínimo de toque**: 44x44px (mobile)
- [ ] **Textos redimensionáveis** até 200% sem quebra de layout
- [ ] **Modo escuro/claro** para preferências visuais

### Exemplos de Implementação

**Skip to Content**:
```html
<a href="#main-content" class="skip-link">
  Pular para conteúdo principal
</a>
```

```css
.skip-link {
  position: absolute;
  top: -40px;
  left: 0;
  background: var(--accent-500);
  color: #000;
  padding: 8px;
  text-decoration: none;
  z-index: 999;
}

.skip-link:focus {
  top: 0;
}
```

**ARIA Labels**:
```html
<button aria-label="Fechar modal" class="btn-close">
  <svg>...</svg>
</button>

<nav aria-label="Navegação principal">
  <ul>...</ul>
</nav>

<img src="produto.jpg" alt="Caneca térmica do Baby Yoda com capacidade de 350ml">
```

## 📱 Responsividade (Mobile-First)

### Abordagem Mobile-First

```css
/* Base: Mobile (< 640px) */
.container {
  padding: var(--space-4);
}

.grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: var(--space-4);
}

/* Tablet (≥ 640px) */
@media (min-width: 640px) {
  .container {
    padding: var(--space-6);
  }

  .grid {
    grid-template-columns: repeat(2, 1fr);
    gap: var(--space-6);
  }
}

/* Desktop (≥ 1024px) */
@media (min-width: 1024px) {
  .container {
    padding: var(--space-8);
  }

  .grid {
    grid-template-columns: repeat(3, 1fr);
    gap: var(--space-8);
  }
}
```

### Menu Mobile (Hamburguer)

```html
<button class="menu-toggle" aria-label="Abrir menu">
  <span></span>
  <span></span>
  <span></span>
</button>

<nav class="mobile-menu" aria-hidden="true">
  <ul>...</ul>
</nav>
```

```css
.menu-toggle {
  display: flex;
  flex-direction: column;
  gap: 4px;
  background: transparent;
  border: none;
  cursor: pointer;
}

.menu-toggle span {
  width: 24px;
  height: 2px;
  background: var(--text-primary);
  transition: transform 0.3s;
}

.mobile-menu {
  position: fixed;
  top: 0;
  right: -100%;
  width: 80%;
  height: 100vh;
  background: var(--bg-secondary);
  transition: right 0.3s;
}

.mobile-menu.open {
  right: 0;
}

@media (min-width: 768px) {
  .menu-toggle {
    display: none;
  }

  .mobile-menu {
    position: static;
    width: auto;
    height: auto;
  }
}
```

## 🎯 Otimização de Conversão (CRO)

### Hierarquia Visual

**Ordem de Importância**:
1. **Título** (maior, bold, cor primária)
2. **Imagem do Produto** (destaque visual)
3. **CTA Primário** (botão grande, cor contrastante)
4. **Preço** (tamanho médio-grande, cor destaque)
5. **Descrição** (tamanho normal, fácil leitura)
6. **CTAs Secundários** (menores, menos destaque)

### Princípios de Design para Conversão

**1. Contraste**:
- Botões de CTA devem contrastar fortemente com o fundo
- Amarelo/Dourado (#FACC15) sobre fundo escuro = alto contraste

**2. Espaçamento**:
- Dar "ar" ao redor de CTAs importantes
- Mínimo 24px de margem ao redor de botões principais

**3. Direção Visual**:
- Usar setas, olhares de pessoas em direção ao CTA
- Linhas guiam o olho para elementos importantes

**4. Urgência Visual**:
- Cores quentes (vermelho, laranja, amarelo) para escassez
- Badges de "Oferta Limitada", "Últimas Unidades"

**5. Confiança**:
- Mostrar avaliações (estrelas) próximo ao produto
- Logos de plataformas confiáveis (Amazon, ML)
- Selo de "Frete Grátis", "Entrega Rápida"

## 📚 Design System (Componentes Reutilizáveis)

### Badge

```html
<span class="badge badge-primary">Novo</span>
<span class="badge badge-success">Disponível</span>
<span class="badge badge-warning">Últimas unidades</span>
```

### Rating Stars

```html
<div class="rating">
  <span class="stars">⭐⭐⭐⭐⭐</span>
  <span class="rating-count">(1.234 avaliações)</span>
</div>
```

### Price Display

```html
<div class="price-display">
  <span class="price-old">R$ 149,90</span>
  <span class="price-current">R$ 89,90</span>
  <span class="price-discount">40% OFF</span>
</div>
```

### Social Share Buttons

```html
<div class="social-share">
  <button class="share-btn share-whatsapp">
    <svg>...</svg> WhatsApp
  </button>
  <button class="share-btn share-telegram">
    <svg>...</svg> Telegram
  </button>
  <button class="share-btn share-twitter">
    <svg>...</svg> X
  </button>
  <button class="share-btn share-copy">
    <svg>...</svg> Copiar Link
  </button>
</div>
```

---

**Versão**: 1.0
**Última atualização**: 2025-12-10
**Projeto**: geek.bidu.guru
