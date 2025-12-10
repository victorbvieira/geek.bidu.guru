# Otimização de Imagens — SEO

Versão: 1.0  
Última atualização: 2025-12-10  
Relacionado: PRD.md §7 (Performance), §12 (Layout)

---

## Checklist

- Formatos modernos: WebP (preferencial) e AVIF (opcional) com fallback JPG/PNG.  
- Lazy loading nativo: `loading="lazy"` em imagens não críticas.  
- Srcset + sizes: variações responsivas por largura (320/640/960/1280/1600).  
- ALT descritivo com keywords naturais.  
- Nomenclatura: `categoria-tema-produto-palavra-chave.webp` (sem espaços, minúsculas, hífens).  
- Dimensões explícitas (`width`/`height`) para evitar CLS.  
- Compressão automática (pipeline build ou serviço externo).  
- CDN para servir imagens com cache e HTTP/2.

---

## Exemplo HTML

```html
<img
  src="/img/presentes-geek/caneca-baby-yoda-640.webp"
  srcset="/img/presentes-geek/caneca-baby-yoda-320.webp 320w,
          /img/presentes-geek/caneca-baby-yoda-640.webp 640w,
          /img/presentes-geek/caneca-baby-yoda-960.webp 960w"
  sizes="(max-width: 640px) 100vw, 640px"
  alt="Caneca Baby Yoda presente geek até 100 reais"
  width="640" height="480" loading="lazy"
>
```

