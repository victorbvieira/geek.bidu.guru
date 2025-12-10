# Estrutura de URLs & Canonicals — SEO

Versão: 1.0  
Última atualização: 2025-12-10  
Relacionado: PRD.md §6.16, agents/seo-specialist.md

---

## Padrões de URL

- Posts: `/blog/{slug}`  
- Categorias: `/categoria/{slug}`  
- Ocasões: `/ocasiao/{slug}`  
- Tags: `/tag/{slug}`  
- Produtos (opcional): `/produto/{slug}`  
- Redirecionamento afiliado: `/goto/{slug}`

Regras: minúsculas, hífens, sem acentos, sem stop-words desnecessárias, sem parâmetros na URL de conteúdo.

Trailing slash: consistente (recomendado sem barra final para páginas); redirecionar 301 variações.

---

## Canonical

- Sempre `<link rel="canonical" href="URL absoluta">`.  
- Duplicatas (UTM, paginação) devem apontar para a versão canônica.  
- Páginas com filtros devem ser `noindex,follow` e canonical para base.

---

## Redirecionamentos

- 301 em mudanças de slug/estrutura.  
- 410 para remoções permanentes quando adequado.  
- Manter mapa de redirects no repositório (ex.: YAML/JSON).

