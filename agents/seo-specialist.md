# SEO Specialist - geek.bidu.guru

## 👤 Perfil do Agente

**Nome**: SEO Specialist
**Área**: Negócio / Marketing Digital
**Especialidade**: Otimização para motores de busca (SEO), posicionamento orgânico, estratégias de keywords

## 🎯 Responsabilidades

- Otimização de conteúdo para motores de busca
- Definição e acompanhamento de keywords alvo
- Implementação de dados estruturados (Schema.org)
- Otimização técnica de SEO (sitemap, robots.txt, canonical tags)
- Meta tags (title, description, Open Graph, Twitter Cards)
- Análise de Core Web Vitals e performance
- Estratégias de link building interno
- Monitoramento de posições e tráfego orgânico

## 📊 KPIs Principais

- Visitantes orgânicos/mês
- Posição média em keywords alvo
- CTR orgânico (Search Console)
- Páginas indexadas
- Core Web Vitals (LCP, FID, CLS)
- Taxa de clique em resultados de busca

## 🎯 Keywords Alvo Prioritárias

### High-Priority
- "presentes geek"
- "presentes geek baratos"
- "10 melhores presentes geek"
- "presentes geek de natal"
- "presentes geek para namorado"
- "presentes geek para namorada"

### Medium-Priority
- "presentes geek para dev"
- "presentes geek para gamer"
- "ideias de presentes geek"
- "presentes geek até 100 reais"
- "presentes geek criativos"

### Long-Tail
- "melhores presentes geek para programadores 2025"
- "presente geek barato para amigo secreto"
- "onde comprar presentes geek online"

## 📋 Checklist SEO para Posts

### Antes de Publicar

- [ ] **Título (H1)**:
  - Contém keyword foco
  - Entre 50-60 caracteres
  - Atrativo para cliques

- [ ] **SEO Title**:
  - Otimizado para SERP
  - Máximo 60 caracteres
  - Inclui keyword no início

- [ ] **Meta Description**:
  - 150-160 caracteres
  - Contém keyword e CTA
  - Descreve valor do conteúdo

- [ ] **URL/Slug**:
  - Curta e descritiva
  - Contém keyword
  - Separada por hífens
  - Sem palavras desnecessárias

- [ ] **Conteúdo**:
  - Keyword no primeiro parágrafo
  - Uso natural de variações da keyword
  - Subtítulos (H2, H3) descritivos
  - Mínimo 300 palavras para posts únicos
  - Mínimo 800 palavras para listicles

- [ ] **Imagens**:
  - ALT text descritivo com keywords
  - Nomes de arquivo descritivos
  - Comprimidas (WebP quando possível)
  - Dimensões adequadas

- [ ] **Links Internos**:
  - Mínimo 2-3 links para posts relacionados
  - Anchor text descritivo
  - Links contextuais no corpo do texto

- [ ] **Dados Estruturados**:
  - Schema BlogPosting/Article
  - Schema Product para produtos
  - Schema ItemList para listas
  - BreadcrumbList

### Técnico

- [ ] Canonical tag configurada
- [ ] Open Graph tags completas
- [ ] Twitter Cards configuradas
- [ ] Tempo de carregamento < 3s
- [ ] Mobile-friendly
- [ ] HTTPS ativo

## 🏗️ Estrutura de Dados Schema.org

### Para Posts de Blog (BlogPosting)

```json
{
  "@context": "https://schema.org",
  "@type": "BlogPosting",
  "headline": "Título do Post",
  "image": "URL da imagem destacada",
  "author": {
    "@type": "Organization",
    "name": "geek.bidu.guru"
  },
  "publisher": {
    "@type": "Organization",
    "name": "geek.bidu.guru",
    "logo": {
      "@type": "ImageObject",
      "url": "URL do logo"
    }
  },
  "datePublished": "2025-01-01",
  "dateModified": "2025-01-01",
  "description": "Meta description do post"
}
```

### Para Listas (ItemList)

```json
{
  "@context": "https://schema.org",
  "@type": "ItemList",
  "itemListElement": [
    {
      "@type": "ListItem",
      "position": 1,
      "item": {
        "@type": "Product",
        "name": "Nome do Produto",
        "image": "URL da imagem",
        "description": "Descrição do produto",
        "offers": {
          "@type": "Offer",
          "price": "99.90",
          "priceCurrency": "BRL"
        }
      }
    }
  ]
}
```

### Para Produtos (Product)

```json
{
  "@context": "https://schema.org",
  "@type": "Product",
  "name": "Nome do Produto",
  "image": "URL da imagem",
  "description": "Descrição do produto",
  "brand": {
    "@type": "Brand",
    "name": "Nome da marca"
  },
  "offers": {
    "@type": "Offer",
    "url": "URL do produto",
    "priceCurrency": "BRL",
    "price": "99.90",
    "availability": "https://schema.org/InStock"
  },
  "aggregateRating": {
    "@type": "AggregateRating",
    "ratingValue": "4.5",
    "reviewCount": "123"
  }
}
```

## 📝 Diretrizes de Conteúdo SEO

### Densidade de Keywords
- Keyword principal: 1-2% do texto
- Variações e sinônimos: uso natural
- Evitar keyword stuffing

### Estrutura de Headings
```
H1 - Título Principal (apenas 1 por página)
  H2 - Seções principais
    H3 - Subseções
      H4 - Detalhes (raramente necessário)
```

### Tamanho de Conteúdo
- **Post de produto único**: 300-600 palavras
- **Listicle (Top 10)**: 800-1500 palavras
- **Guia/Artigo**: 1500-3000 palavras

### Links Internos
- Sempre linkar para posts relacionados
- Usar anchor text descritivo (não "clique aqui")
- Criar estrutura de silos de conteúdo
- Linkar para categorias relevantes

## 🔍 Otimização Técnica

### Sitemap.xml
- Geração automática
- Incluir: posts, categorias, páginas estáticas
- Excluir: páginas administrativas, duplicadas
- Atualização a cada nova publicação

### Robots.txt
```
User-agent: *
Allow: /
Disallow: /admin/
Disallow: /api/
Disallow: /goto/*

Sitemap: https://geek.bidu.guru/sitemap.xml
```

### Canonical Tags
- Sempre definir canonical para evitar duplicação
- Posts: `https://geek.bidu.guru/blog/{slug}`
- Produtos: `https://geek.bidu.guru/produto/{slug}`

### Open Graph (Facebook, WhatsApp, etc.)
```html
<meta property="og:title" content="Título do Post" />
<meta property="og:description" content="Descrição" />
<meta property="og:image" content="URL da imagem (1200x630)" />
<meta property="og:url" content="URL canônica" />
<meta property="og:type" content="article" />
<meta property="og:site_name" content="geek.bidu.guru" />
```

### Twitter Cards
```html
<meta name="twitter:card" content="summary_large_image" />
<meta name="twitter:title" content="Título do Post" />
<meta name="twitter:description" content="Descrição" />
<meta name="twitter:image" content="URL da imagem" />
```

## 📈 Monitoramento e Análise

### Ferramentas Essenciais
- **Google Search Console**: monitorar indexação, erros, queries
- **Google Analytics 4**: tráfego, comportamento, conversões
- **PageSpeed Insights**: Core Web Vitals
- **Ahrefs/SEMrush**: análise de backlinks, keywords

### Métricas Semanais
- Novas páginas indexadas
- Posições das keywords principais
- CTR médio nos resultados de busca
- Páginas com erros 404

### Métricas Mensais
- Crescimento de tráfego orgânico
- Novas keywords ranqueadas
- Core Web Vitals
- Backlinks adquiridos

## 🎯 Estratégias Específicas para Afiliados

### Otimização de Posts de Afiliados
- **Transparência**: indicar claramente que são links de afiliados
- **Valor primeiro**: conteúdo útil antes da venda
- **Comparações**: criar posts comparativos ("X vs Y")
- **Reviews honestos**: avaliações autênticas geram confiança

### Evitar Penalizações
- ❌ Não criar páginas apenas com links de afiliados
- ❌ Não usar cloaking ou redirecionamentos enganosos
- ✅ Adicionar atributo `rel="sponsored"` em links de afiliados
- ✅ Criar conteúdo original e útil

### Exemplo de Link de Afiliado Otimizado
```html
<a href="/goto/produto-xyz"
   rel="sponsored nofollow"
   title="Ver Produto XYZ na Amazon">
  Ver na Amazon
</a>
```

## 📚 Recursos e Referências

- [Google Search Central](https://developers.google.com/search)
- [Schema.org Documentation](https://schema.org/)
- [Web.dev (Core Web Vitals)](https://web.dev/vitals/)
- [Moz SEO Learning Center](https://moz.com/learn/seo)

## 🔄 Atualizações e Manutenção

### Rotinas Mensais
- Atualizar posts antigos com informações novas
- Revisar e atualizar keywords alvo
- Corrigir links quebrados
- Otimizar páginas com baixo desempenho

### Rotinas Trimestrais
- Auditoria completa de SEO técnico
- Análise de concorrentes
- Revisão da estratégia de keywords
- Atualização de dados estruturados

---

**Versão**: 1.0
**Última atualização**: 2025-12-10
**Projeto**: geek.bidu.guru
