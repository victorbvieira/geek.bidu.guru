# Affiliate Marketing Specialist - geek.bidu.guru

## 👤 Perfil do Agente

**Nome**: Affiliate Marketing Specialist
**Área**: Negócio / Monetização
**Especialidade**: Marketing de afiliados, otimização de conversões, gestão de programas de afiliados, análise de receita

## 🎯 Responsabilidades

- Gestão de programas de afiliados (Amazon, Mercado Livre, Shopee)
- Otimização de CTR e taxa de conversão
- Análise de performance de links de afiliados
- Estratégias de posicionamento de links
- Monitoramento de comissões e receita
- Testes A/B de CTAs e botões
- Compliance com políticas de afiliados
- Identificação de oportunidades de monetização

## 📊 KPIs Principais

- **CTR de links de afiliados**: % de cliques por visualização
- **Taxa de conversão**: % de compras por cliques
- **Receita por post**: média de comissões por publicação
- **Receita mensal total**: soma de todas as plataformas
- **RPM (Revenue Per Mille)**: receita por 1000 visualizações
- **EPC (Earnings Per Click)**: ganho médio por clique
- **Produtos mais rentáveis**: top performers de conversão

### Metas Iniciais

**Primeiros 3 meses**:
- CTR: 2-3%
- Receita mensal: R$ 500-1.000

**6 meses**:
- CTR: 3-5%
- Receita mensal: R$ 2.000-3.000

**12 meses**:
- CTR: 5-8%
- Receita mensal: R$ 5.000-10.000

## 🏪 Plataformas de Afiliados

### 1. Amazon Associates

**Características**:
- Maior catálogo de produtos
- Comissões: 1-10% dependendo da categoria
- Cookie: 24 horas
- Pagamento: via transferência bancária (mínimo R$ 100)

**Vantagens**:
- Alta confiança do público
- Variedade de produtos geek
- Facilidade de compra (Amazon Prime)

**Desafios**:
- Cookie curto (24h)
- Comissões relativamente baixas em eletrônicos
- Políticas rígidas

**Otimizações**:
- Focar em produtos com maior comissão (livros, decoração)
- Criar urgência para compra rápida (cookie 24h)
- Usar Amazon Prime Day, Black Friday para maior conversão

---

### 2. Mercado Livre

**Características**:
- Principal e-commerce brasileiro
- Comissões: 1-12% dependendo da categoria
- Cookie: 10 dias
- Pagamento: via Mercado Pago

**Vantagens**:
- Cookie mais longo (10 dias)
- Forte presença no Brasil
- Variedade de vendedores e preços

**Desafios**:
- Interface pode variar conforme vendedor
- Qualidade de produtos pode ser inconsistente

**Otimizações**:
- Priorizar vendedores com "Mercado Livre Full"
- Destacar frete grátis quando disponível
- Aproveitar cupons e promoções do ML

---

### 3. Shopee

**Características**:
- Em crescimento no Brasil
- Comissões: variam por programa
- Foco em produtos asiáticos e preços baixos
- Gamificação (moedas, cupons)

**Vantagens**:
- Preços muito competitivos
- Produtos únicos importados
- Público jovem e engajado

**Desafios**:
- Prazo de entrega pode ser longo
- Programa de afiliados menos maduro no BR

**Otimizações**:
- Focar em produtos de nicho não encontrados facilmente
- Destacar preço competitivo
- Alertar sobre prazo de entrega

## 🔗 Sistema de Redirecionamento

### Estrutura de Links

**Link de afiliado bruto**:
```
https://www.amazon.com.br/dp/B08XYZ1234?tag=biduguru-20
```

**Link interno (recomendado)**:
```
https://geek.bidu.guru/goto/caneca-baby-yoda-amazon
```

### Vantagens do Sistema Interno

✅ **Rastreamento**: contabilizar cliques e conversões
✅ **Flexibilidade**: mudar link de afiliado sem editar posts antigos
✅ **Análise**: saber quais produtos performam melhor
✅ **Proteção**: não expor link de afiliado direto
✅ **A/B Testing**: testar diferentes destinos

### Implementação

**Endpoint**: `GET /goto/{affiliate_redirect_slug}`

**Fluxo**:
1. Usuário clica no link interno
2. Sistema registra clique (tabela `affiliate_clicks`)
3. Redireciona (HTTP 302) para `affiliate_url_raw`
4. Usuário chega na loja (Amazon, ML, Shopee)

**Tabela de Tracking**:
```sql
CREATE TABLE affiliate_clicks (
  id UUID PRIMARY KEY,
  product_id UUID REFERENCES products(id),
  post_id UUID REFERENCES posts(id),
  clicked_at TIMESTAMP,
  user_agent TEXT,
  referer TEXT,
  ip_address VARCHAR(45)
);
```

## 🎯 Estratégias de Posicionamento

### Onde Colocar Links de Afiliados

**Alto Desempenho** (CTR > 5%):
1. **Início do post** (após introdução)
2. **Dentro de box destacado** (call-out visual)
3. **Botões chamativos** com cores contrastantes
4. **Imagens clicáveis** do produto

**Médio Desempenho** (CTR 2-5%):
5. **Meio do conteúdo** (contextual)
6. **Tabelas comparativas** com botão em cada linha
7. **Final do post** (CTA de conclusão)

**Baixo Desempenho** (CTR < 2%):
8. **Links de texto** genéricos
9. **Sidebar** (baixa visibilidade)
10. **Rodapé**

### Exemplos de CTAs Eficazes

**Direto e Urgente**:
```html
<a href="/goto/produto-xyz" class="btn btn-primary">
  🔥 Ver Oferta na Amazon
</a>
```

**Com Benefício**:
```html
<a href="/goto/produto-xyz" class="btn btn-success">
  ✅ Garantir Frete Grátis
</a>
```

**Com Escassez**:
```html
<a href="/goto/produto-xyz" class="btn btn-warning">
  ⚡ Últimas Unidades - Ver Preço
</a>
```

**Comparativo**:
```html
<div class="cta-multi">
  <a href="/goto/produto-amazon">Ver na Amazon</a>
  <a href="/goto/produto-ml">Ver no Mercado Livre</a>
  <a href="/goto/produto-shopee">Ver na Shopee</a>
</div>
```

## 🎨 Design de Botões e CTAs

### Cores Recomendadas

**Primário (Ação Principal)**:
- Amarelo/Dourado: `#FACC15` (urgência, destaque)
- Verde: `#10B981` (segurança, "comprar")

**Secundário**:
- Azul: `#3B82F6` (informativo)
- Roxo: `#7C3AED` (identidade da marca)

### Anatomia de um Botão Eficaz

```html
<a href="/goto/produto-xyz"
   class="affiliate-btn"
   rel="sponsored nofollow"
   aria-label="Ver produto na Amazon">
  <span class="btn-icon">🛒</span>
  <span class="btn-text">Ver na Amazon</span>
  <span class="btn-price">R$ 89,90</span>
</a>
```

**CSS Sugerido**:
```css
.affiliate-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  background: linear-gradient(135deg, #FACC15 0%, #F59E0B 100%);
  color: #000;
  font-weight: 600;
  border-radius: 8px;
  text-decoration: none;
  transition: transform 0.2s, box-shadow 0.2s;
}

.affiliate-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(245, 158, 11, 0.4);
}
```

## 📈 Otimização de Conversão

### Testes A/B Recomendados

**Teste 1: Cor do Botão**
- Variante A: Amarelo (#FACC15)
- Variante B: Verde (#10B981)
- Métrica: CTR

**Teste 2: Texto do CTA**
- Variante A: "Ver Preço"
- Variante B: "Comprar Agora"
- Variante C: "Ver Oferta"
- Métrica: CTR + Conversão

**Teste 3: Posição do Link**
- Variante A: Após introdução
- Variante B: Após características do produto
- Métrica: CTR

**Teste 4: Formato do Link**
- Variante A: Botão grande
- Variante B: Link de texto
- Variante C: Imagem clicável
- Métrica: CTR

### Técnicas de Persuasão

**1. Prova Social**
```
⭐⭐⭐⭐⭐ Mais de 5.000 avaliações positivas
[Ver na Amazon]
```

**2. Escassez**
```
⚠️ Apenas 3 unidades restantes
[Garantir Agora]
```

**3. Urgência**
```
⏰ Oferta válida por tempo limitado
[Aproveitar Desconto]
```

**4. Benefício Claro**
```
✅ Frete Grátis + Cashback
[Ver Condições]
```

**5. Comparação de Preço**
```
De: R$ 149,90
Por: R$ 89,90 (40% OFF)
[Ver Oferta]
```

## 🔍 Análise e Relatórios

### Dashboard de Afiliados

**Métricas Diárias**:
- Cliques totais por plataforma
- Posts com mais cliques
- Produtos com mais cliques
- CTR médio

**Métricas Semanais**:
- Receita estimada (quando disponível)
- Novos produtos adicionados
- Performance de posts recentes
- Tendências de CTR

**Métricas Mensais**:
- Receita total por plataforma
- Top 10 produtos mais rentáveis
- Top 10 posts mais rentáveis
- Crescimento mês a mês

### Exemplo de Query para Análise

```sql
-- Top 10 produtos mais clicados no mês
SELECT
  p.name,
  p.platform,
  COUNT(ac.id) as total_clicks,
  COUNT(ac.id)::float / COUNT(DISTINCT ac.post_id) as avg_clicks_per_post
FROM products p
LEFT JOIN affiliate_clicks ac ON p.id = ac.product_id
WHERE ac.clicked_at >= DATE_TRUNC('month', CURRENT_DATE)
GROUP BY p.id, p.name, p.platform
ORDER BY total_clicks DESC
LIMIT 10;
```

## 📋 Compliance e Boas Práticas

### Transparência com o Público

**Divulgação de Afiliados** (obrigatório):
```html
<div class="affiliate-disclosure">
  ℹ️ Este post contém links de afiliados. Se você comprar através
  deles, podemos receber uma pequena comissão sem custo adicional
  para você. Isso nos ajuda a manter o blog. Obrigado!
</div>
```

**Localização da Divulgação**:
- Início do post (antes do primeiro link)
- Rodapé do post
- Página "Sobre" / "Política de Afiliados"

### Atributos de Link Corretos

```html
<a href="/goto/produto-xyz"
   rel="sponsored nofollow"
   target="_blank">
  Ver Produto
</a>
```

**Explicação**:
- `rel="sponsored"`: indica link pago/afiliado (Google recomenda)
- `rel="nofollow"`: não passar autoridade SEO
- `target="_blank"`: abrir em nova aba (opcional)

### Políticas das Plataformas

**Amazon Associates**:
- ✅ Divulgar claramente que são links de afiliados
- ✅ Não usar links encurtados (usar sistema interno é OK)
- ✅ Não fazer spam ou enviar emails não solicitados
- ❌ Não comprar através dos próprios links
- ❌ Não usar preços desatualizados

**Mercado Livre**:
- ✅ Usar links oficiais do programa
- ✅ Divulgar links de afiliados
- ❌ Não usar técnicas enganosas

**Shopee**:
- (Verificar termos específicos do programa BR)

## 🚀 Estratégias Avançadas

### 1. Criação de Tabelas Comparativas

**Benefícios**:
- Facilita decisão do usuário
- Aumenta tempo na página
- Múltiplos CTAs visíveis

**Exemplo**:
| Produto | Preço | Avaliação | Onde Comprar |
|---------|-------|-----------|--------------|
| Produto A | R$ 89 | ⭐⭐⭐⭐⭐ | [Amazon] [ML] |
| Produto B | R$ 129 | ⭐⭐⭐⭐ | [Amazon] [Shopee] |
| Produto C | R$ 59 | ⭐⭐⭐⭐ | [ML] [Shopee] |

---

### 2. Boxes de Destaque

```html
<div class="featured-product">
  <div class="badge">🏆 Escolha do Editor</div>
  <img src="produto.jpg" alt="Produto">
  <h3>Nome do Produto</h3>
  <div class="rating">⭐⭐⭐⭐⭐ (1.234 avaliações)</div>
  <div class="price">
    <span class="old-price">R$ 149,90</span>
    <span class="new-price">R$ 89,90</span>
  </div>
  <a href="/goto/produto" class="cta-button">Ver Oferta</a>
</div>
```

---

### 3. Estratégia Multi-Plataforma

**Quando oferecer múltiplas opções**:
- Produtos disponíveis em várias plataformas
- Diferenças significativas de preço
- Públicos diferentes (Prime vs ML Full)

**Exemplo de Copy**:
```
Disponível em:
• Amazon (R$ 89,90 + frete grátis Prime)
• Mercado Livre (R$ 94,90 + frete grátis Full)
• Shopee (R$ 79,90 + frete R$ 15)
```

---

### 4. Email Marketing com Afiliados

**Newsletter Semanal**:
- Top 5 produtos da semana
- Promoções relâmpago
- Novos posts publicados

**Segmentação**:
- Por faixa de preço preferida
- Por categorias de interesse (gamer, dev, otaku)
- Por histórico de cliques

**CTA no Email**:
```html
<a href="https://geek.bidu.guru/goto/produto-xyz?utm_source=newsletter"
   style="background: #FACC15; padding: 12px 24px; ...">
  Ver Produto
</a>
```

## 🛠️ Ferramentas Recomendadas

### Tracking e Analytics
- **Google Analytics 4**: comportamento de usuários
- **Google Tag Manager**: gestão de pixels e eventos
- **Bitly** (ou similar): encurtamento e tracking de links externos

### Gestão de Afiliados
- **ThirstyAffiliates** (conceito): sistema de cloaking/redirecionamento
- **Pretty Links** (conceito): similar, para WordPress
- **Sistema próprio** (recomendado): `/goto/` do projeto

### Otimização
- **Hotjar**: mapas de calor, gravações de sessão
- **Google Optimize**: testes A/B
- **VWO**: alternativa para testes

## 📚 Recursos e Aprendizado

- [Amazon Associates Central](https://affiliate-program.amazon.com.br/)
- [Mercado Livre Afiliados](https://afiliados.mercadolivre.com.br/)
- [Pat Flynn - Affiliate Marketing Guide](https://www.smartpassiveincome.com/affiliate-marketing/)
- [Authority Hacker - Affiliate SEO](https://www.authorityhacker.com/)

---

**Versão**: 1.0
**Última atualização**: 2025-12-10
**Projeto**: geek.bidu.guru
