# Frontend Developer (Jinja2/SSR) - geek.bidu.guru

## 👤 Perfil do Agente

**Nome**: Frontend Developer
**Área**: Técnica / Frontend
**Especialidade**: Jinja2 templates, HTML/CSS, JavaScript, Server-Side Rendering (SSR), responsividade

## 🎯 Responsabilidades

- Desenvolvimento de templates Jinja2
- HTML semântico e acessível
- CSS/Styling (seguindo guia visual)
- JavaScript para interatividade
- Otimização de performance frontend
- Responsividade mobile-first
- Implementação de componentes reutilizáveis
- Integração com backend FastAPI

## 🎨 Identidade Visual do Logo

O texto do logo "GEEK BIDU GURU" utiliza a fonte **Bungee** (Google Fonts).

```css
/* Variável CSS para o logo */
--font-logo: 'Bungee', 'Impact', system-ui, sans-serif;

/* Classe do logo */
.logo-text {
  font-family: var(--font-logo);
  color: #F5B81C;
  font-weight: 400;
}
```

**Importação da fonte:**
```html
<link href="https://fonts.googleapis.com/css2?family=Bungee&display=swap" rel="stylesheet">
```

**Documentação completa:** `docs/branding/LOGO-GUIDE.md`

## 📁 Estrutura de Templates

```
app/templates/
├── base.html                   # Template base
├── home.html                   # Homepage
├── post.html                   # Página de post
├── category.html               # Página de categoria
├── search.html                 # Página de busca
├── static/                     # Páginas estáticas
│   ├── about.html
│   ├── contact.html
│   └── privacy.html
└── components/                 # Componentes reutilizáveis
    ├── header.html
    ├── footer.html
    ├── post_card.html
    ├── product_card.html
    ├── newsletter_form.html
    └── social_share.html
```

## 🎨 Templates Principais

### 1. base.html - Template Base

```html
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">

    <!-- SEO Meta Tags -->
    <title>{% block title %}{{ seo.title | default('geek.bidu.guru - Presentes Geek') }}{% endblock %}</title>
    <meta name="description" content="{% block description %}{{ seo.description | default('Encontre os melhores presentes geek') }}{% endblock %}">
    <meta name="keywords" content="{% block keywords %}{{ seo.keywords | default('presentes geek, presentes nerd') }}{% endblock %}">

    <!-- Canonical -->
    <link rel="canonical" href="{{ request.url }}">

    <!-- Open Graph -->
    <meta property="og:title" content="{{ seo.title | default('geek.bidu.guru') }}">
    <meta property="og:description" content="{{ seo.description }}">
    <meta property="og:image" content="{{ seo.image | default(url_for('static', path='images/og-default.jpg')) }}">
    <meta property="og:url" content="{{ request.url }}">
    <meta property="og:type" content="{% block og_type %}website{% endblock %}">
    <meta property="og:site_name" content="geek.bidu.guru">

    <!-- Twitter Cards -->
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{{ seo.title }}">
    <meta name="twitter:description" content="{{ seo.description }}">
    <meta name="twitter:image" content="{{ seo.image }}">

    <!-- Favicon -->
    <link rel="icon" type="image/png" href="{{ url_for('static', path='images/favicon.png') }}">

    <!-- CSS -->
    <link rel="stylesheet" href="{{ url_for('static', path='css/main.css') }}">
    {% block extra_css %}{% endblock %}

    <!-- Google Analytics -->
    {% if config.GA_MEASUREMENT_ID %}
    <script async src="https://www.googletagmanager.com/gtag/js?id={{ config.GA_MEASUREMENT_ID }}"></script>
    <script>
        window.dataLayer = window.dataLayer || [];
        function gtag(){dataLayer.push(arguments);}
        gtag('js', new Date());
        gtag('config', '{{ config.GA_MEASUREMENT_ID }}');
    </script>
    {% endif %}

    <!-- Structured Data (JSON-LD) -->
    {% block structured_data %}{% endblock %}
</head>
<body class="dark-theme">
    <!-- Skip to Content (Acessibilidade) -->
    <a href="#main-content" class="skip-link">Pular para conteúdo principal</a>

    <!-- Header -->
    {% include 'components/header.html' %}

    <!-- Main Content -->
    <main id="main-content">
        {% block content %}{% endblock %}
    </main>

    <!-- Footer -->
    {% include 'components/footer.html' %}

    <!-- JavaScript -->
    <script src="{{ url_for('static', path='js/main.js') }}" defer></script>
    {% block extra_js %}{% endblock %}
</body>
</html>
```

---

### 2. components/header.html

```html
<header class="header">
    <div class="container">
        <div class="header-content">
            <!-- Logo -->
            <a href="/" class="logo">
                <span class="logo-text">geek.</span><span class="logo-accent">bidu.guru</span>
            </a>

            <!-- Desktop Navigation -->
            <nav class="nav-desktop" aria-label="Navegação principal">
                <ul class="nav-menu">
                    <li><a href="/presentes-natal" class="nav-link">Natal</a></li>
                    <li><a href="/presentes-baratos" class="nav-link">Até R$ 100</a></li>
                    <li><a href="/categoria/gamer" class="nav-link">Gamers</a></li>
                    <li><a href="/categoria/dev" class="nav-link">Devs</a></li>
                    <li><a href="/sobre" class="nav-link">Sobre</a></li>
                </ul>
            </nav>

            <!-- Search Icon -->
            <button class="search-toggle" aria-label="Abrir busca">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <circle cx="11" cy="11" r="8"></circle>
                    <path d="m21 21-4.35-4.35"></path>
                </svg>
            </button>

            <!-- Mobile Menu Toggle -->
            <button class="menu-toggle" aria-label="Abrir menu" aria-expanded="false">
                <span></span>
                <span></span>
                <span></span>
            </button>
        </div>
    </div>

    <!-- Mobile Navigation -->
    <nav class="nav-mobile" aria-label="Navegação mobile" hidden>
        <ul class="nav-menu-mobile">
            <li><a href="/presentes-natal">🎄 Natal</a></li>
            <li><a href="/presentes-baratos">💰 Até R$ 100</a></li>
            <li><a href="/categoria/gamer">🎮 Gamers</a></li>
            <li><a href="/categoria/dev">💻 Devs</a></li>
            <li><a href="/sobre">ℹ️ Sobre</a></li>
        </ul>
    </nav>

    <!-- Search Overlay -->
    <div class="search-overlay" hidden>
        <div class="search-container">
            <input type="search" id="search-input" placeholder="Buscar presentes geek..." aria-label="Campo de busca">
            <div id="search-results"></div>
        </div>
    </div>
</header>
```

---

### 3. home.html - Homepage

```html
{% extends "base.html" %}

{% block content %}
<!-- Hero Section -->
<section class="hero">
    <div class="container">
        <div class="hero-content">
            <h1 class="hero-title">
                Encontre o <span class="accent">presente geek</span> perfeito
            </h1>
            <p class="hero-subtitle">
                Listas, reviews e ideias criadas por geeks, para geeks – com os melhores achados da Amazon, Mercado Livre e Shopee
            </p>
            <div class="hero-cta">
                <a href="/presentes-natal" class="btn btn-primary">
                    🎄 Presentes de Natal
                </a>
                <a href="/presentes-baratos" class="btn btn-secondary">
                    💰 Até R$ 100
                </a>
            </div>
        </div>
    </div>
</section>

<!-- Featured Posts -->
<section class="featured-posts">
    <div class="container">
        <h2 class="section-title">Destaques da Semana</h2>
        <div class="posts-grid">
            {% for post in featured_posts %}
                {% include 'components/post_card.html' %}
            {% endfor %}
        </div>
    </div>
</section>

<!-- Ocasiões -->
<section class="occasions">
    <div class="container">
        <h2 class="section-title">Navegue por Ocasião</h2>
        <div class="occasions-grid">
            <a href="/ocasiao/natal" class="occasion-card">
                <span class="occasion-icon">🎄</span>
                <span class="occasion-name">Natal</span>
            </a>
            <a href="/ocasiao/aniversario" class="occasion-card">
                <span class="occasion-icon">🎂</span>
                <span class="occasion-name">Aniversário</span>
            </a>
            <a href="/ocasiao/dia-dos-namorados" class="occasion-card">
                <span class="occasion-icon">❤️</span>
                <span class="occasion-name">Namorados</span>
            </a>
            <a href="/ocasiao/amigo-secreto" class="occasion-card">
                <span class="occasion-icon">🎁</span>
                <span class="occasion-name">Amigo Secreto</span>
            </a>
        </div>
    </div>
</section>

<!-- Categorias por Perfil -->
<section class="categories">
    <div class="container">
        <h2 class="section-title">Presentes por Perfil</h2>
        <div class="categories-grid">
            {% for category in categories %}
            <a href="/categoria/{{ category.slug }}" class="category-card">
                <div class="category-icon">{{ category.emoji }}</div>
                <h3 class="category-name">{{ category.name }}</h3>
                <p class="category-count">{{ category.post_count }} posts</p>
            </a>
            {% endfor %}
        </div>
    </div>
</section>

<!-- Newsletter -->
{% include 'components/newsletter_form.html' %}

<!-- Recent Posts -->
<section class="recent-posts">
    <div class="container">
        <h2 class="section-title">Posts Recentes</h2>
        <div class="posts-list">
            {% for post in recent_posts %}
                {% include 'components/post_card.html' %}
            {% endfor %}
        </div>
    </div>
</section>
{% endblock %}
```

---

### 4. post.html - Página de Post

```html
{% extends "base.html" %}

{% block title %}{{ post.seo_title | default(post.title) }}{% endblock %}
{% block description %}{{ post.seo_description }}{% endblock %}

{% block og_type %}article{% endblock %}

{% block structured_data %}
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "BlogPosting",
  "headline": "{{ post.title }}",
  "image": "{{ post.featured_image_url }}",
  "datePublished": "{{ post.publish_at.isoformat() }}",
  "dateModified": "{{ post.updated_at.isoformat() }}",
  "author": {
    "@type": "Organization",
    "name": "geek.bidu.guru"
  },
  "publisher": {
    "@type": "Organization",
    "name": "geek.bidu.guru",
    "logo": {
      "@type": "ImageObject",
      "url": "{{ url_for('static', path='images/logo.png') }}"
    }
  },
  "description": "{{ post.seo_description }}"
}
</script>

{% if post.type == 'listicle' %}
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "ItemList",
  "itemListElement": [
    {% for product in post.products %}
    {
      "@type": "ListItem",
      "position": {{ loop.index }},
      "item": {
        "@type": "Product",
        "name": "{{ product.name }}",
        "image": "{{ product.main_image_url }}",
        "description": "{{ product.short_description }}",
        "offers": {
          "@type": "Offer",
          "price": "{{ product.price }}",
          "priceCurrency": "BRL"
        }
      }
    }{% if not loop.last %},{% endif %}
    {% endfor %}
  ]
}
</script>
{% endif %}
{% endblock %}

{% block content %}
<article class="post-page">
    <div class="container">
        <!-- Breadcrumbs -->
        <nav aria-label="Breadcrumb" class="breadcrumbs">
            <ol>
                <li><a href="/">Home</a></li>
                <li><a href="/categoria/{{ post.category.slug }}">{{ post.category.name }}</a></li>
                <li aria-current="page">{{ post.title }}</li>
            </ol>
        </nav>

        <div class="post-layout">
            <!-- Main Content -->
            <div class="post-main">
                <!-- Header -->
                <header class="post-header">
                    <div class="post-meta">
                        <span class="post-category">{{ post.category.name }}</span>
                        <time datetime="{{ post.publish_at.isoformat() }}">
                            {{ post.publish_at.strftime('%d/%m/%Y') }}
                        </time>
                    </div>

                    <h1 class="post-title">{{ post.title }}</h1>

                    {% if post.subtitle %}
                    <p class="post-subtitle">{{ post.subtitle }}</p>
                    {% endif %}

                    <!-- Social Share Buttons -->
                    {% include 'components/social_share.html' %}
                </header>

                <!-- Featured Image -->
                {% if post.featured_image_url %}
                <figure class="post-featured-image">
                    <img src="{{ post.featured_image_url }}" alt="{{ post.title }}">
                </figure>
                {% endif %}

                <!-- Content -->
                <div class="post-content">
                    {{ post.content | markdown | safe }}
                </div>

                <!-- Tags -->
                {% if post.tags %}
                <div class="post-tags">
                    <span class="tags-label">Tags:</span>
                    {% for tag in post.tags %}
                    <a href="/tag/{{ tag }}" class="tag">#{{ tag }}</a>
                    {% endfor %}
                </div>
                {% endif %}

                <!-- Related Posts -->
                {% if related_posts %}
                <section class="related-posts">
                    <h2>Posts Relacionados</h2>
                    <div class="posts-grid">
                        {% for post in related_posts %}
                            {% include 'components/post_card.html' %}
                        {% endfor %}
                    </div>
                </section>
                {% endif %}
            </div>

            <!-- Sidebar -->
            <aside class="post-sidebar">
                <!-- Featured Products -->
                <div class="sidebar-section">
                    <h3>Produtos em Destaque</h3>
                    {% for product in post.products[:3] %}
                        {% include 'components/product_card.html' %}
                    {% endfor %}
                </div>

                <!-- Newsletter -->
                <div class="sidebar-section">
                    {% include 'components/newsletter_form.html' %}
                </div>
            </aside>
        </div>
    </div>
</article>
{% endblock %}

{% block extra_js %}
<script>
    // Track time on page
    let startTime = Date.now();

    window.addEventListener('beforeunload', function() {
        let timeOnPage = Math.floor((Date.now() - startTime) / 1000);

        // Send to analytics
        if (window.gtag) {
            gtag('event', 'timing_complete', {
                'name': 'time_on_post',
                'value': timeOnPage,
                'event_category': 'engagement'
            });
        }
    });

    // Track scroll depth
    let maxScroll = 0;
    window.addEventListener('scroll', function() {
        let scrollPercent = (window.scrollY / (document.body.scrollHeight - window.innerHeight)) * 100;
        if (scrollPercent > maxScroll) {
            maxScroll = Math.floor(scrollPercent);

            if (maxScroll >= 25 && maxScroll < 30) {
                gtag && gtag('event', 'scroll', { percent_scrolled: 25 });
            } else if (maxScroll >= 50 && maxScroll < 55) {
                gtag && gtag('event', 'scroll', { percent_scrolled: 50 });
            } else if (maxScroll >= 75 && maxScroll < 80) {
                gtag && gtag('event', 'scroll', { percent_scrolled: 75 });
            } else if (maxScroll >= 90) {
                gtag && gtag('event', 'scroll', { percent_scrolled: 100 });
            }
        }
    });
</script>
{% endblock %}
```

---

### 5. components/product_card.html

```html
<div class="product-card">
    <a href="/goto/{{ product.affiliate_redirect_slug }}"
       class="product-link"
       rel="sponsored nofollow"
       onclick="trackAffiliateClick('{{ product.id }}', '{{ post.id if post else '' }}')">

        <!-- Image -->
        <div class="product-image">
            <img src="{{ product.main_image_url }}"
                 alt="{{ product.name }}"
                 loading="lazy">

            <!-- Platform Badge -->
            <span class="product-platform {{ product.platform }}">
                {% if product.platform == 'amazon' %}Amazon{% endif %}
                {% if product.platform == 'mercadolivre' %}Mercado Livre{% endif %}
                {% if product.platform == 'shopee' %}Shopee{% endif %}
            </span>
        </div>

        <!-- Info -->
        <div class="product-info">
            <h3 class="product-name">{{ product.name }}</h3>

            {% if product.short_description %}
            <p class="product-description">{{ product.short_description }}</p>
            {% endif %}

            <!-- Rating -->
            {% if product.rating %}
            <div class="product-rating">
                <span class="stars">
                    {% set full_stars = product.rating | int %}
                    {% for i in range(full_stars) %}⭐{% endfor %}
                </span>
                <span class="rating-count">({{ product.review_count }})</span>
            </div>
            {% endif %}

            <!-- Price -->
            <div class="product-price">
                <span class="price">R$ {{ "%.2f" | format(product.price) }}</span>
            </div>

            <!-- CTA -->
            <button class="btn btn-primary btn-block">
                Ver Oferta
            </button>
        </div>
    </a>
</div>
```

---

### 6. components/social_share.html

```html
<div class="social-share">
    <span class="share-label">Compartilhar:</span>
    <div class="share-buttons">
        <!-- WhatsApp -->
        <a href="https://api.whatsapp.com/send?text={{ post.title | urlencode }}%20{{ request.url | urlencode }}"
           target="_blank"
           rel="noopener"
           class="share-btn whatsapp"
           aria-label="Compartilhar no WhatsApp">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
                <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413Z"/>
            </svg>
        </a>

        <!-- Telegram -->
        <a href="https://t.me/share/url?url={{ request.url | urlencode }}&text={{ post.title | urlencode }}"
           target="_blank"
           rel="noopener"
           class="share-btn telegram"
           aria-label="Compartilhar no Telegram">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
                <path d="m12 0c-6.627 0-12 5.373-12 12s5.373 12 12 12 12-5.373 12-12-5.373-12-12-12zm5.894 8.221-1.97 9.28c-.145.658-.537.818-1.084.508l-3-2.21-1.446 1.394c-.14.18-.357.295-.6.295-.002 0-.003 0-.005 0l.213-3.054 5.56-5.022c.24-.213-.054-.334-.373-.121l-6.869 4.326-2.96-.924c-.64-.203-.658-.64.135-.954l11.566-4.458c.538-.196 1.006.128.832.941z"/>
            </svg>
        </a>

        <!-- X/Twitter -->
        <a href="https://twitter.com/intent/tweet?url={{ request.url | urlencode }}&text={{ post.title | urlencode }}"
           target="_blank"
           rel="noopener"
           class="share-btn twitter"
           aria-label="Compartilhar no X">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
                <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/>
            </svg>
        </a>

        <!-- Copy Link -->
        <button class="share-btn copy-link"
                aria-label="Copiar link"
                onclick="copyToClipboard('{{ request.url }}')">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"></path>
                <path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"></path>
            </svg>
        </button>
    </div>
</div>

<script>
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        alert('Link copiado!');
    });
}
</script>
```

## 📱 JavaScript (main.js)

```javascript
// Mobile Menu Toggle
const menuToggle = document.querySelector('.menu-toggle');
const navMobile = document.querySelector('.nav-mobile');

menuToggle?.addEventListener('click', () => {
    const isExpanded = menuToggle.getAttribute('aria-expanded') === 'true';
    menuToggle.setAttribute('aria-expanded', !isExpanded);
    navMobile.hidden = isExpanded;
    document.body.classList.toggle('menu-open');
});

// Search Toggle
const searchToggle = document.querySelector('.search-toggle');
const searchOverlay = document.querySelector('.search-overlay');

searchToggle?.addEventListener('click', () => {
    searchOverlay.hidden = !searchOverlay.hidden;
    if (!searchOverlay.hidden) {
        document.getElementById('search-input')?.focus();
    }
});

// Search Functionality
let searchTimeout;
const searchInput = document.getElementById('search-input');
const searchResults = document.getElementById('search-results');

searchInput?.addEventListener('input', (e) => {
    clearTimeout(searchTimeout);
    const query = e.target.value;

    if (query.length < 3) {
        searchResults.innerHTML = '';
        return;
    }

    searchTimeout = setTimeout(async () => {
        try {
            const response = await fetch(`/api/v1/search?q=${encodeURIComponent(query)}`);
            const results = await response.json();

            if (results.length === 0) {
                searchResults.innerHTML = '<p>Nenhum resultado encontrado</p>';
                return;
            }

            searchResults.innerHTML = results.map(post => `
                <a href="/blog/${post.slug}" class="search-result-item">
                    <img src="${post.featured_image_url}" alt="${post.title}">
                    <div>
                        <h4>${post.title}</h4>
                        <p>${post.subtitle || ''}</p>
                    </div>
                </a>
            `).join('');
        } catch (error) {
            console.error('Search error:', error);
        }
    }, 300);
});

// Track Affiliate Click
window.trackAffiliateClick = (productId, postId) => {
    fetch('/api/v1/track/click', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            product_id: productId,
            post_id: postId || null
        })
    });

    // Google Analytics
    if (window.gtag) {
        gtag('event', 'affiliate_click', {
            product_id: productId,
            post_id: postId
        });
    }
};

// Lazy Loading Images
if ('IntersectionObserver' in window) {
    const imageObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.classList.add('loaded');
                imageObserver.unobserve(img);
            }
        });
    });

    document.querySelectorAll('img[data-src]').forEach(img => imageObserver.observe(img));
}
```

---

**Versão**: 1.0
**Última atualização**: 2025-12-10
**Projeto**: geek.bidu.guru
