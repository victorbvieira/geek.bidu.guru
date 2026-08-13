# Protótipo, Redesign da Home (Loja + TCG)

**Arquivo**: `home-redesign.html`, protótipo estático autocontido (fonte e imagens embutidas).
Basta abrir no navegador, não precisa de servidor.

## Diagnóstico do layout atual

Análise da home em produção (`src/app/templates/home.html` + `static/css/main.css`):

1. **Hero genérico**, texto centralizado sobre gradiente, sem nenhum elemento visual.
   O mascote (guaxinim mago), o maior ativo de identidade da marca, aparece só com
   40px no header. Nenhuma prova de valor (por que confiar na curadoria?).
2. **Três carrosséis idênticos em sequência**, "Últimos Artigos", "Listas" e "Guias"
   têm exatamente o mesmo card e o mesmo layout. A página fica longa, repetitiva e
   monótona; o usuário não distingue as seções.
3. **Card de produto sem hierarquia de conversão**, nome truncado em 50 caracteres,
   preço pequeno, sem preço "de/por", sem desconto, sem avaliação, sem microcopy de
   confiança. Para um site de afiliados, o card é o principal ponto de conversão.
4. **Categorias com emoji de fallback** (📦), passa sensação de site incompleto.
5. **Identidade tipográfica desperdiçada**, as fontes `Bungee` e `Press Start 2P`
   existem em `static/fonts/` mas nunca são usadas; os headings usam Poppins, que
   não tem personalidade geek.
6. **~440 linhas de CSS inline** no `home.html` (bloco `extra_css`), difícil de manter.
7. **Nada preparado para TCG**, nenhum conceito de condição de carta, raridade,
   pré-venda ou produto selado no modelo visual.

> ⚠️ **Bug encontrado**: `static/fonts/PressStart2P-Regular.ttf` está corrompido -
> é um documento HTML salvo com extensão .ttf (download que falhou). Precisa ser
> baixado novamente se for usado.

## Decisões do protótipo

| Decisão | Racional |
|---|---|
| **Bungee como fonte display** | Já está no repositório; dá identidade geek instantânea a títulos e logo sem perder legibilidade (uso restrito a headings). Corpo continua Inter. |
| **Hero com mascote + cartas flutuantes** | O mascote vira protagonista; as cartas flutuantes já anunciam o TCG. CTA amarelo mantido (token `--color-accent-500`). |
| **Barra de confiança no hero** | "Preços comparados em 3 lojas", "Curadoria humana", "Alerta de preço", responde "por que comprar por aqui?" na primeira dobra. |
| **Card de produto refeito** | Badge de plataforma + badge de desconto/pré-venda, categoria, título em 2 linhas, estrelas, preço "de/por" grande em verde, microcopy ("menor preço em 30 dias") e CTA amarelo de largura total. |
| **Seção "Arena TCG"** | Prepara o lançamento: leque de cartas (Pokémon/Magic/One Piece), tiles de Singles (condição NM/SP/MP), Selados, Pré-vendas e Alerta de preço, com CTA de lista de espera para capturar leads antes do lançamento. |
| **Um único "Grimório do Bidu" com abas** | Substitui os 3 carrosséis repetidos por uma seção só com filtro Listas/Guias/Reviews. |
| **Categorias como "Escolha sua classe"** | Rail horizontal de chips com vocabulário gamer; TCG entra com selo "Novo". |
| **Newsletter como "Guilda"** | Card horizontal com mascote, promessa concreta (achados + quedas de preço + lançamentos TCG) e microcopy anti-spam. |
| **Barra de anúncio no topo** | Comunica o lançamento do TCG em todas as páginas e alimenta a lista de espera. |

## O que o TCG muda no produto (resposta à dúvida)

Sim, muda, principalmente no modelo de dados e no card de produto:

- **Novos atributos de produto**: condição (NM/SP/MP/HP), raridade, set/coleção,
  idioma da carta, tipo (single vs. selado).
- **Pré-venda**: estado novo de produto com data de envio (badge ciano no protótipo).
- **Preço volátil**: singles mudam de preço muito mais rápido que produtos comuns -
  o histórico de preços (`price_history`) e os alertas viram diferencial central.
- **Navegação**: TCG merece item próprio no menu e franquias como sub-categorias.
- **Conteúdo**: guias "por onde começar" convertem muito bem nesse nicho (exemplo
  incluído no Grimório).

## Próximos passos sugeridos

1. Validar a direção visual com este protótipo.
2. Extrair os tokens novos para `main.css` (manter compatibilidade com aliases existentes).
3. Migrar o card de produto (componente Jinja reutilizável, sem CSS inline).
4. Refazer hero + seções da home nos templates.
5. Corrigir a fonte Press Start 2P corrompida (ou removê-la).
6. Criar migration para os campos TCG quando o catálogo começar.
