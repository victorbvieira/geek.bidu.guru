# Content Recycling — Sistema 1 → 24

Versão: 1.0  
Última atualização: 2025-12-10  
Relacionado: PRD.md §6.12, docs/content/editorial-calendar.md

---

## Objetivo

Multiplicar o alcance de cada peça principal (pilar) transformando‑a em múltiplos formatos reutilizáveis para blog, redes e email — mantendo consistência de tom e SEO.

---

## Mapeamento 1 → 24 (exemplo: Listicle Top 10)

Entrada: "Top 10 Presentes para Gamers"

- 10 posts individuais (produto único)  
- 1 infográfico (Pinterest)  
- 10 posts para Instagram (carrossel/estático)  
- 1 vídeo YouTube (roundup)  
- 1 newsletter (resumo)  
- 1 thread X/Twitter (10 itens)

Opcional: shorts/reels (3–5 cortes) a partir do vídeo principal.

---

## Diretrizes por Formato

- Blog (produto único): 400–600 palavras, 3 CTAs, 2–3 links internos, Schema Product.  
- Blog (infográfico): imagem otimizada com ALT, embed + resumo; link para listicle pilar.  
- Instagram: carrossel 5–7 cards com benefício/CTA discreto; link na bio/Linktree.  
- YouTube: 6–8 min, roteiro direto, CTAs de afiliado na descrição; capítulos por item.  
- Newsletter: 3–5 destaques, 1 CTA principal, UTMs dedicados.  
- X/Twitter: thread com 1 insight por item + link curto; hashtag temática.

---

## Processo

1) Seleção: escolher 1 pilar/semana (listicle ou guia).  
2) Planejamento: definir quais 24 saídas serão geradas (nem sempre todas).  
3) Produção: usar templates/copy base do pilar; adaptar por canal (ver style‑guide).  
4) QA: links, UTMs, imagens, ALT, consistência de tom.  
5) Agendamento: social/email (Buffer/Meta/Telegram/GA4).  
6) Medição: CTR, sessões, receita por UTM/canal.

---

## Nomenclatura & UTMs

- Campanhas: `utm_campaign=recycling_{slug_pilar}_{yyyy-mm}`  
- Origem/Meio: `utm_source=instagram|youtube|newsletter|twitter`, `utm_medium=social|email|video`  
- Padrão de arquivos: `recycling/{yyyy}/{mm}/{slug_pilar}-{canal}-{versao}.md` (se aplicável).

---

## Responsabilidades

- Editor: escolhe pilar, revisa e aprova.  
- Redator/IA: adapta copy por canal (seguir `docs/content/style-guide.md`).  
- Designer: carrosséis, infográfico, thumbs.  
- Social/Email: agendamento e performance.

---

## Sinais de Qualidade

- Consistência entre pilar e derivados.  
- CTAs contextuais, não agressivos.  
- 2–3 links internos nos derivados de blog.  
- Aderência a SEO/Schema quando aplicável.

