# Automation Engineer (n8n) - geek.bidu.guru

## 👤 Perfil do Agente

**Nome**: Automation Engineer
**Área**: Técnica / Automação
**Especialidade**: n8n workflows, integrações com APIs, automação de processos, IA para geração de conteúdo

## 🎯 Responsabilidades

- Criação e manutenção de workflows no n8n
- Integração com APIs de afiliados (Amazon, Mercado Livre, Shopee)
- Automação de criação de posts
- Geração de conteúdo com IA (LLMs)
- Atualização automática de preços
- Disparos de compartilhamento em redes sociais
- Monitoramento de oportunidades e promoções
- Manutenção e debugging de fluxos

## 🔄 Fluxos n8n - Implementação Detalhada

### Fluxo A: Post Diário (1 Produto)

**Objetivo**: Criar automaticamente 1 post por dia com destaque para um produto.

**Gatilho**: Cron (diário às 08h00)

**Diagrama do Fluxo**:
```
[Cron: 08h] → [Get Products] → [Select Product] → [LLM: Generate Content] → [Create Post] → [Publish] → [Notify Team]
```

**Implementação Detalhada**:

1. **Node: Schedule Trigger**
   - Type: Cron
   - Expression: `0 8 * * *` (08h todos os dias)

2. **Node: HTTP Request - Get Products**
   - Method: GET
   - URL: `http://app:8000/api/v1/products`
   - Query Parameters:
     - `availability=available`
     - `limit=50`
     - `sort=random`
   - Authentication: Bearer Token (n8n user)

3. **Node: Function - Select Product**
   ```javascript
   // Selecionar produto que não foi usado recentemente
   const products = $input.all()[0].json;

   // Filtrar produtos não usados nos últimos 7 dias
   // (Assumindo que há um campo last_used_at)
   const availableProducts = products.filter(p => {
     if (!p.last_used_at) return true;
     const daysSinceUsed = (Date.now() - new Date(p.last_used_at)) / (1000 * 60 * 60 * 24);
     return daysSinceUsed > 7;
   });

   // Escolher aleatoriamente
   const selectedProduct = availableProducts[Math.floor(Math.random() * availableProducts.length)];

   return {
     json: selectedProduct
   };
   ```

4. **Node: OpenAI / LLM - Generate Content**
   - Model: GPT-4 ou equivalente
   - System Prompt:
   ```
   Você é um redator especialista em presentes geek.
   Crie um post de blog envolvente sobre o produto fornecido.
   Tom de voz: amigável, divertido, mas profissional.
   Público: pessoas procurando presentes geek.
   ```
   - User Prompt:
   ```
   Crie um post completo sobre este produto:
   Nome: {{ $json.name }}
   Descrição: {{ $json.long_description }}
   Preço: R$ {{ $json.price }}
   Plataforma: {{ $json.platform }}

   O post deve ter:
   1. Título chamativo (max 60 chars)
   2. Introdução (2-3 parágrafos explicando por que este produto é especial)
   3. Características principais (bullet points)
   4. Para quem é ideal
   5. Conclusão com call-to-action

   Formato JSON:
   {
     "title": "título aqui",
     "content": "conteúdo em markdown",
     "seo_title": "título SEO otimizado",
     "seo_description": "meta description",
     "seo_focus_keyword": "palavra-chave principal"
   }
   ```

5. **Node: Set - Prepare Post Data**
   ```javascript
   const llmOutput = $json.choices[0].message.content;
   const parsedContent = JSON.parse(llmOutput);
   const product = $('Select Product').item.json;

   return {
     json: {
       type: "product_single",
       title: parsedContent.title,
       content: parsedContent.content,
       seo_title: parsedContent.seo_title,
       seo_description: parsedContent.seo_description,
       seo_focus_keyword: parsedContent.seo_focus_keyword,
       featured_image_url: product.main_image_url,
       category_id: "uuid-da-categoria-geral",
       tags: product.tags,
       status: "published",
       products: [product.id]
     }
   };
   ```

6. **Node: HTTP Request - Create Post**
   - Method: POST
   - URL: `http://app:8000/api/v1/posts`
   - Body Type: JSON
   - Body: `{{ $json }}`
   - Authentication: Bearer Token

7. **Node: HTTP Request - Publish Post**
   - Method: POST
   - URL: `http://app:8000/api/v1/posts/{{ $json.id }}/publish`

8. **Node: Telegram - Notify Team**
   - Message:
   ```
   ✅ Post diário publicado com sucesso!

   📝 {{ $('Create Post').item.json.title }}
   🔗 https://geek.bidu.guru/blog/{{ $('Create Post').item.json.slug }}
   🛒 Produto: {{ $('Select Product').item.json.name }}
   ```

---

### Fluxo B: Post Semanal "Top 10"

**Objetivo**: Criar semanalmente uma lista com 10 produtos.

**Gatilho**: Cron (segundas-feiras às 09h)

**Diagrama do Fluxo**:
```
[Cron: Segunda 09h] → [Define Theme] → [Get Products] → [Select Top 10] → [LLM: Generate Listicle] → [Create Post] → [Publish] → [Trigger Share Flow]
```

**Implementação**:

1. **Node: Schedule Trigger**
   - Cron: `0 9 * * 1` (09h toda segunda)

2. **Node: Set - Define Theme**
   ```javascript
   // Temas rotativos por semana do mês
   const weekOfMonth = Math.ceil(new Date().getDate() / 7);
   const themes = [
     { name: "Presentes de Natal", tag: "natal", category: "ocasião" },
     { name: "Presentes para Gamers", tag: "gamer", category: "perfil" },
     { name: "Presentes até R$ 100", price_max: 100, category: "faixa-preço" },
     { name: "Gadgets Geek Inovadores", tag: "gadget", category: "tipo-produto" }
   ];

   const theme = themes[(weekOfMonth - 1) % themes.length];

   return {
     json: theme
   };
   ```

3. **Node: HTTP Request - Get Products**
   - URL: `http://app:8000/api/v1/products`
   - Query (dinâmico):
   ```javascript
   {
     availability: 'available',
     limit: 30,
     ...(json.tag && { tag: json.tag }),
     ...(json.price_max && { price_max: json.price_max }),
     sort: 'internal_score_desc'
   }
   ```

4. **Node: Function - Select Top 10**
   ```javascript
   const products = $input.all()[0].json;
   const theme = $('Define Theme').item.json;

   // Selecionar 10 produtos únicos
   const selected = products
     .filter((p, index, self) =>
       index === self.findIndex(t => t.platform_product_id === p.platform_product_id)
     )
     .slice(0, 10);

   return {
     json: {
       theme: theme,
       products: selected
     }
   };
   ```

5. **Node: LLM - Generate Listicle**
   - System Prompt:
   ```
   Você é um redator especialista em listas de presentes geek.
   Crie uma listicle envolvente no estilo "Top 10".
   ```
   - User Prompt:
   ```
   Crie um post "Top 10 {{ $json.theme.name }}"

   Produtos:
   {{ $json.products.map((p, i) => `${i+1}. ${p.name} - R$ ${p.price} - ${p.short_description}`).join('\n') }}

   Estrutura:
   1. Título chamativo com keyword
   2. Introdução (por que essa lista é útil)
   3. Para cada produto (1-10):
      - Nome e breve descrição
      - Por que está na lista
      - Para quem é ideal
   4. Conclusão com CTA

   Retorne JSON:
   {
     "title": "",
     "intro": "",
     "items": [
       {
         "product_index": 0,
         "description": "texto descritivo"
       }
     ],
     "conclusion": "",
     "seo_title": "",
     "seo_description": "",
     "seo_focus_keyword": ""
   }
   ```

6. **Node: Function - Build Post Content**
   ```javascript
   const llm = JSON.parse($json.choices[0].message.content);
   const data = $('Select Top 10').item.json;

   // Construir conteúdo em Markdown
   let content = `${llm.intro}\n\n`;

   llm.items.forEach((item, index) => {
     const product = data.products[item.product_index];
     content += `## ${index + 1}. ${product.name}\n\n`;
     content += `![${product.name}](${product.main_image_url})\n\n`;
     content += `${item.description}\n\n`;
     content += `**Preço**: R$ ${product.price}\n\n`;
     content += `[Ver produto](/goto/${product.affiliate_redirect_slug})\n\n`;
     content += `---\n\n`;
   });

   content += `## Conclusão\n\n${llm.conclusion}`;

   return {
     json: {
       type: "listicle",
       title: llm.title,
       content: content,
       seo_title: llm.seo_title,
       seo_description: llm.seo_description,
       seo_focus_keyword: llm.seo_focus_keyword,
       products: data.products.map(p => p.id)
     }
   };
   ```

7. **Node: HTTP Request - Create & Publish Post**

8. **Node: Webhook - Trigger Share Flow**
   - Chamar Fluxo D (compartilhamento)

---

### Fluxo C: Atualização de Preços

**Objetivo**: Atualizar preços e disponibilidade de produtos periodicamente.

**Gatilho**: Cron (diário às 02h)

**Diagrama**:
```
[Cron: 02h] → [Get Outdated Products] → [Split by Platform] → [Amazon API / ML API / Shopee API] → [Update Product] → [Log Results]
```

**Implementação**:

1. **Node: Schedule Trigger**
   - Cron: `0 2 * * *` (02h todos os dias)

2. **Node: HTTP Request - Get Outdated Products**
   - URL: `http://app:8000/api/v1/products`
   - Query:
   ```
   last_price_update_before: {{ $today.minus({ days: 3 }).toISO() }}
   limit: 100
   ```

3. **Node: Split In Batches**
   - Batch Size: 10
   - (Evitar rate limits das APIs)

4. **Node: Switch - By Platform**
   - Route por `platform` (amazon, mercadolivre, shopee)

5. **Node: HTTP Request - Amazon API**
   - URL: Amazon Product Advertising API
   - Endpoint: `/paapi5/getitems`
   - Authentication: AWS Signature
   - Body:
   ```json
   {
     "ItemIds": ["{{ $json.platform_product_id }}"],
     "Resources": ["Offers.Listings.Price", "Images.Primary.Large"]
   }
   ```

6. **Node: Function - Parse Amazon Response**
   ```javascript
   const response = $json.ItemsResult.Items[0];

   return {
     json: {
       product_id: $('Split In Batches').item.json.id,
       price: response.Offers.Listings[0].Price.Amount,
       availability: response.Offers.Listings[0].Availability.Type === 'Now' ? 'available' : 'unavailable',
       main_image_url: response.Images.Primary.Large.URL
     }
   };
   ```

7. **Node: HTTP Request - Update Product**
   - Method: PUT
   - URL: `http://app:8000/api/v1/products/{{ $json.product_id }}`
   - Body:
   ```json
   {
     "price": {{ $json.price }},
     "availability": "{{ $json.availability }}",
     "last_price_update": "{{ $now.toISO() }}"
   }
   ```

8. **Node: Google Sheets - Log Results** (Opcional)
   - Registrar sucesso/erro em planilha

---

### Fluxo D: Compartilhamento Automático

**Objetivo**: Ao publicar post, gerar e enviar textos para redes sociais.

**Gatilho**: Webhook do backend quando post é publicado

**Diagrama**:
```
[Webhook] → [LLM: Generate Social Text] → [Telegram] → [Email com Sugestões] → [Update Post (shared=true)]
```

**Implementação**:

1. **Node: Webhook Trigger**
   - Path: `/webhook/post-published`
   - Method: POST
   - Expected body:
   ```json
   {
     "post_id": "uuid",
     "title": "título",
     "url": "https://geek.bidu.guru/blog/slug",
     "summary": "breve resumo"
   }
   ```

2. **Node: LLM - Generate Social Media Copy**
   - Prompt:
   ```
   Crie variações de texto para divulgar este post:
   Título: {{ $json.title }}
   URL: {{ $json.url }}
   Resumo: {{ $json.summary }}

   Gere:
   1. Texto para WhatsApp/Telegram (informal, 2-3 linhas)
   2. Texto para X/Twitter (max 280 chars, com hashtags)
   3. Texto para LinkedIn (profissional, 3-4 linhas)

   Retorne JSON:
   {
     "whatsapp": "",
     "twitter": "",
     "linkedin": ""
   }
   ```

3. **Node: Telegram - Send to Channel**
   - Message:
   ```
   {{ $json.whatsapp }}

   🔗 {{ $('Webhook').item.json.url }}
   ```

4. **Node: Email - Send Suggestions**
   - To: equipe@geek.bidu.guru
   - Subject: `Novo post publicado: {{ $('Webhook').item.json.title }}`
   - Body (HTML):
   ```html
   <h2>Post publicado com sucesso!</h2>
   <p><strong>Título:</strong> {{ $('Webhook').item.json.title }}</p>
   <p><strong>URL:</strong> <a href="{{ $('Webhook').item.json.url }}">{{ $('Webhook').item.json.url }}</a></p>

   <h3>Sugestões de texto para redes sociais:</h3>

   <h4>WhatsApp/Telegram:</h4>
   <p>{{ $json.whatsapp }}</p>

   <h4>X/Twitter:</h4>
   <p>{{ $json.twitter }}</p>

   <h4>LinkedIn:</h4>
   <p>{{ $json.linkedin }}</p>
   ```

5. **Node: HTTP Request - Mark as Shared**
   - Method: PUT
   - URL: `http://app:8000/api/v1/posts/{{ $('Webhook').item.json.post_id }}`
   - Body:
   ```json
   {
     "shared": true
   }
   ```

---

### Fluxo E: Pesquisa Qualificada com IA

**Objetivo**: Permitir busca inteligente de produtos e criação automática de post.

**Gatilho**: Webhook ou formulário manual

**Diagrama**:
```
[Webhook/Form] → [LLM: Parse Theme] → [Search Amazon API] → [Search ML API] → [LLM: Select Best] → [Create Products] → [LLM: Generate Post] → [Create Post]
```

**Implementação**:

1. **Node: Webhook Trigger**
   - Path: `/webhook/ai-product-search`
   - Expected body:
   ```json
   {
     "tema": "presentes geek até 100 reais para devs",
     "quantidade_itens": 10,
     "faixa_preco": 100,
     "ocasiao": "aniversário"
   }
   ```

2. **Node: LLM - Parse Theme**
   - Prompt:
   ```
   Extraia informações estruturadas deste tema de post:
   "{{ $json.tema }}"

   Retorne JSON:
   {
     "keywords": ["palavra1", "palavra2"],
     "target_audience": "perfil do público",
     "max_price": número,
     "platforms_priority": ["amazon", "mercadolivre"],
     "product_categories": ["categoria1", "categoria2"]
   }
   ```

3. **Node: HTTP Request - Search Amazon**
   - URL: Amazon API Search
   - Query: keywords do LLM
   - Filter: price <= max_price

4. **Node: HTTP Request - Search Mercado Livre**
   - Similar ao Amazon

5. **Node: Function - Aggregate Results**
   ```javascript
   const amazonResults = $('Search Amazon').item.json;
   const mlResults = $('Search ML').item.json;

   const allProducts = [...amazonResults, ...mlResults];

   return {
     json: {
       products: allProducts,
       theme: $('Parse Theme').item.json
     }
   };
   ```

6. **Node: LLM - Select Best Products**
   - Prompt:
   ```
   Dos produtos abaixo, selecione os 10 melhores para o tema "{{ $json.theme.target_audience }}":

   {{ $json.products.map(p => `- ${p.name} (R$ ${p.price})`).join('\n') }}

   Critérios:
   - Relevância para o tema
   - Custo-benefício
   - Diversidade
   - Avaliações

   Retorne JSON com array de índices: [0, 3, 5, ...]
   ```

7. **Node: Loop - Create Products**
   - Para cada produto selecionado:
     - HTTP Request POST `/api/v1/products`

8. **Node: LLM - Generate Listicle**
   - (Similar ao Fluxo B)

9. **Node: HTTP Request - Create Post**

---

### Fluxo F: Monitoramento de Oportunidades

**Objetivo**: Monitorar promoções e criar posts rapidamente.

**Gatilho**: Cron (a cada 30 min)

**Implementação**:

1. **Node: Schedule Trigger**
   - Cron: `*/30 * * * *`

2. **Node: HTTP Request - Pelando/Promobit API** (ou scraping)
   - Buscar promoções com keywords geek

3. **Node: Function - Filter Geek Products**
   ```javascript
   const deals = $json;
   const geekKeywords = ['geek', 'nerd', 'lego', 'funko', 'marvel', 'star wars', 'gaming'];

   return deals.filter(deal =>
     geekKeywords.some(kw => deal.title.toLowerCase().includes(kw))
   );
   ```

4. **Node: HTTP Request - Get Affiliate Link**
   - Gerar link de afiliado para a oferta

5. **Node: LLM - Generate Quick Post**
   - Prompt:
   ```
   Crie um post rápido sobre esta promoção:
   Produto: {{ $json.title }}
   Preço: R$ {{ $json.price }}
   Desconto: {{ $json.discount }}%

   Tom: urgente, chamativo
   Foco: promoção limitada
   ```

6. **Node: HTTP Request - Create Post**
   - Type: `product_single`
   - Status: `published`

7. **Node: Trigger Share Flow**

---

## 🛠️ Melhores Práticas n8n

### 1. Error Handling

```javascript
// Node: Function com try-catch
try {
  const data = $json.some_field;
  // processamento...
  return { json: result };
} catch (error) {
  return {
    json: {
      error: true,
      message: error.message,
      original_data: $json
    }
  };
}
```

### 2. Retry Logic

- Configurar retry em HTTP Requests:
  - Max Attempts: 3
  - Wait Between: 2000ms (exponential backoff)

### 3. Rate Limiting

```javascript
// Node: Function antes de API calls
const delay = ms => new Promise(resolve => setTimeout(resolve, ms));
await delay(1000); // 1 segundo entre requests
return { json: $json };
```

### 4. Logging

- Sempre adicionar nodes "Set" com timestamp e status antes de operações críticas

### 5. Testing

- Usar "Execute Workflow" manualmente antes de ativar
- Testar com dados reais e de mock

---

**Versão**: 1.0
**Última atualização**: 2025-12-10
**Projeto**: geek.bidu.guru
