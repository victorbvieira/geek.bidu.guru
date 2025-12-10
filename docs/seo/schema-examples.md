# Schema.org — Exemplos Avançados

Versão: 1.0  
Última atualização: 2025-12-10  
Relacionado: PRD.md §6.3, agents/seo-specialist.md

---

## Graph Base (Organization + WebSite)

```json
{
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "Organization",
      "name": "geek.bidu.guru",
      "url": "https://geek.bidu.guru",
      "logo": "https://geek.bidu.guru/static/images/logo.png",
      "sameAs": [
        "https://instagram.com/geekbiduguru",
        "https://facebook.com/geekbiduguru"
      ]
    },
    {
      "@type": "WebSite",
      "name": "geek.bidu.guru",
      "url": "https://geek.bidu.guru",
      "potentialAction": {
        "@type": "SearchAction",
        "target": "https://geek.bidu.guru/search?q={search_term_string}",
        "query-input": "required name=search_term_string"
      }
    }
  ]
}
```

---

## BreadcrumbList

```json
{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [
    {"@type": "ListItem", "position": 1, "name": "Home", "item": "https://geek.bidu.guru/"},
    {"@type": "ListItem", "position": 2, "name": "Natal", "item": "https://geek.bidu.guru/ocasiao/natal"},
    {"@type": "ListItem", "position": 3, "name": "Top 10 Presentes de Natal", "item": "https://geek.bidu.guru/blog/presentes-geek-natal-2025"}
  ]
}
```

---

## FAQPage

```json
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [{
    "@type": "Question",
    "name": "O que são presentes geek?",
    "acceptedAnswer": {"@type": "Answer", "text": "Presentes geek são itens relacionados à cultura nerd com foco em filmes, séries, jogos e tecnologia."}
  }]
}
```

---

## HowTo (para guias aplicáveis)

```json
{
  "@context": "https://schema.org",
  "@type": "HowTo",
  "name": "Como escolher o presente geek perfeito",
  "step": [
    {"@type": "HowToStep", "name": "Defina o perfil", "text": "Gamer, dev, otaku..."},
    {"@type": "HowToStep", "name": "Estabeleça orçamento", "text": "Até R$ 100, R$ 200..."}
  ]
}
```

---

## AggregateRating (quando aplicável)

```json
{
  "@context": "https://schema.org",
  "@type": "Product",
  "name": "Caneca Baby Yoda",
  "aggregateRating": {
    "@type": "AggregateRating",
    "ratingValue": "4.7",
    "reviewCount": "1234"
  }
}
```

---

## VideoObject (Video SEO)

```json
{
  "@context": "https://schema.org",
  "@type": "VideoObject",
  "name": "Top 5 Presentes para Devs",
  "thumbnailUrl": ["https://geek.bidu.guru/thumbs/top5-devs.jpg"],
  "uploadDate": "2025-12-10",
  "contentUrl": "https://geek.bidu.guru/videos/top5-devs.mp4",
  "embedUrl": "https://www.youtube.com/embed/VIDEO_ID",
  "description": "Os melhores presentes para desenvolvedores em 2025."
}
```

---

## Speakable (Voice Search) — opcional

```json
{
  "@context": "https://schema.org",
  "@type": "WebPage",
  "speakable": {
    "@type": "SpeakableSpecification",
    "xpath": ["/html/head/title", "/html/body//h1"]
  }
}
```

