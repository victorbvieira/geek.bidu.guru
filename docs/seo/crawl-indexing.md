# Crawl & Indexing — SEO Técnico

Versão: 1.0  
Última atualização: 2025-12-10  
Relacionado: PRD.md §6.3, §7, agents/seo-specialist.md

---

## robots.txt (base)

```
User-agent: *
Allow: /
Disallow: /admin/
Disallow: /api/
Disallow: /goto/*

Sitemap: https://geek.bidu.guru/sitemap.xml
```

---

## Meta Robots

- `noindex,follow` para páginas administrativas, resultados de busca interna, páginas de filtro.  
- `index,follow` para posts, hubs, categorias, ocasiões.

---

## Sitemaps

- Usar index: `/sitemap.xml` apontando para:  
  - `/sitemap-posts.xml`  
  - `/sitemap-categories.xml`  
  - `/sitemap-hubs.xml`  
  - `/sitemap-static.xml`
- Incluir `lastmod`, `changefreq` e `priority` indicativas (não garantem comportamento, mas ajudam).

---

## Erros & Redirecionamentos

- 404 para inexistentes; 410 para removidos permanentes.  
- 301 para mudanças de slug/estrutura.  
- Monitorar via Search Console (erros de cobertura).

