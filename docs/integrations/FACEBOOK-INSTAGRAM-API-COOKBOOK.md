# Cookbook: Configuração do Facebook App para Instagram API

> **Versão**: 1.0
> **Última atualização**: 2025-12-24
> **Projeto**: geek.bidu.guru
> **Referência vídeo**: [YouTube - Configuração Facebook App](https://www.youtube.com/watch?v=X_GcmVdTrrU)

---

## Índice

1. [Visão Geral](#visão-geral)
2. [Pré-requisitos](#pré-requisitos)
3. [Etapa 1: Criar App no Facebook Developer](#etapa-1-criar-app-no-facebook-developer)
4. [Etapa 2: Configurar Instagram Graph API](#etapa-2-configurar-instagram-graph-api)
5. [Etapa 3: Obter Token de Curto Prazo](#etapa-3-obter-token-de-curto-prazo)
6. [Etapa 4: Gerar Token de Longo Prazo](#etapa-4-gerar-token-de-longo-prazo)
7. [Etapa 5: Configurar Webhooks](#etapa-5-configurar-webhooks)
8. [Etapa 6: Configurar OAuth para n8n](#etapa-6-configurar-oauth-para-n8n)
9. [Estrutura JSON para n8n Output Parser](#estrutura-json-para-n8n-output-parser)
10. [Credenciais e Configurações](#credenciais-e-configurações)
11. [Troubleshooting](#troubleshooting)
12. [Links Úteis](#links-úteis)

---

## Visão Geral

Este cookbook documenta o processo completo de configuração de um Facebook App para acesso às APIs do Instagram, permitindo:

- **Publicar posts** automaticamente via n8n
- **Ler métricas** e insights da conta
- **Gerenciar conteúdo** via Instagram Graph API
- **Receber webhooks** de eventos

### Arquitetura da Integração

```
┌─────────────────────────────────────────────────────────────────┐
│                      FLUXO DE AUTENTICAÇÃO                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  [Facebook App]                                                 │
│       │                                                         │
│       ▼                                                         │
│  [OAuth 2.0] ──► [Token Curto Prazo] ──► [Token Longo Prazo]   │
│       │                  (1 hora)              (60 dias)        │
│       ▼                                                         │
│  [Instagram Graph API]                                          │
│       │                                                         │
│       ▼                                                         │
│  [n8n Workflows] ──► [Publicação Automática]                   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Pré-requisitos

### Contas Necessárias

- [ ] Conta Meta Business Suite
- [ ] Conta Instagram Business ou Creator (vinculada ao Facebook)
- [ ] Acesso ao Facebook Developers

### Informações para Coleta

| Item | Descrição |
|------|-----------|
| Business ID | ID do seu Business Manager |
| Instagram Account ID | ID numérico da conta Instagram |
| App ID | ID do aplicativo Facebook |
| App Secret | Chave secreta do aplicativo |

---

## Etapa 1: Criar App no Facebook Developer

### 1.1 Acessar Facebook Developers

1. Acesse: https://developers.facebook.com
2. Faça login com sua conta Meta Business
3. Clique em **"Meus Apps"** no menu superior

### 1.2 Criar Novo App

1. Clique em **"Criar App"**
2. Selecione o tipo: **"Negócios"** (recomendado) ou **"Outro"**
3. Preencha:
   - **Nome do App**: `Geek Bidu Guru - Instagram Integration`
   - **Email de contato**: seu email de administrador
   - **Business Account**: Selecione sua conta Business

### 1.3 Configurações Básicas

Após criar, acesse **Configurações > Básico** e anote:

```
┌──────────────────────────────────────────────────────────────┐
│  CONFIGURAÇÕES DO APP (Exemplo - Use seus valores reais)    │
├──────────────────────────────────────────────────────────────┤
│  App ID:          22656782605*****                          │
│  App Secret:      a6b396f452856b5a*****************         │
│  Namespace:       geek-bidu-guru                            │
│  Display Name:    Geek Bidu Guru                            │
└──────────────────────────────────────────────────────────────┘
```

---

## Etapa 2: Configurar Instagram Graph API

### 2.1 Adicionar Produtos ao App

1. No painel do app, vá em **"Adicionar Produtos"**
2. Adicione os seguintes produtos:
   - **Instagram Graph API** (ou Instagram Business)
   - **Facebook Login** (necessário para OAuth)

### 2.2 Configurar Use Cases

1. Acesse: **Use Cases > Customize**
2. Configure o caso de uso **"Instagram Business"**
3. Em **API Setup**, configure as permissões:

```
Permissões Necessárias:
├── instagram_basic
├── instagram_content_publish
├── instagram_manage_comments
├── instagram_manage_insights
├── pages_show_list
├── pages_read_engagement
└── business_management
```

### 2.3 Vincular Conta Instagram

1. Acesse Meta Business Suite: https://business.facebook.com
2. Vá em **Configurações > Contas > Contas do Instagram**
3. Vincule sua conta Instagram Business
4. Anote o **Instagram Account ID**

```
┌──────────────────────────────────────────────────────────────┐
│  CONTA INSTAGRAM (Exemplo - Use seus valores reais)         │
├──────────────────────────────────────────────────────────────┤
│  Instagram Account ID:  178414788066*****                   │
│  Username:              @geekbiduguru                       │
│  Tipo:                  Business Account                    │
└──────────────────────────────────────────────────────────────┘
```

---

## Etapa 3: Obter Token de Curto Prazo

### 3.1 Usar Graph API Explorer

1. Acesse: https://developers.facebook.com/tools/explorer/
2. Selecione seu app no menu superior
3. Configure as permissões necessárias
4. Clique em **"Generate Access Token"**
5. Autorize o acesso às contas

### 3.2 Validar Token

Use o Access Token Debugger para validar:

```
https://developers.facebook.com/tools/debug/accesstoken/
```

O token curto prazo tem validade de **1 hora**.

```
┌──────────────────────────────────────────────────────────────┐
│  TOKEN CURTO PRAZO (Exemplo - Expira em 1 hora)             │
├──────────────────────────────────────────────────────────────┤
│  Token: EAAgMn1PlZBq0BQ...                                  │
│  Tipo:  User Access Token                                   │
│  Expira: 1 hora                                             │
│  Escopo: instagram_basic, instagram_content_publish, ...    │
└──────────────────────────────────────────────────────────────┘
```

---

## Etapa 4: Gerar Token de Longo Prazo

### 4.1 Converter Token (Facebook Graph API)

Para tokens de **Facebook/Page**:

```bash
# Requisição para converter token curto em longo prazo
curl -X GET "https://graph.facebook.com/v24.0/oauth/access_token?\
grant_type=fb_exchange_token&\
client_id=SEU_APP_ID&\
client_secret=SEU_APP_SECRET&\
fb_exchange_token=SEU_TOKEN_CURTO_PRAZO"
```

**Exemplo com valores ofuscados:**

```bash
curl -X GET "https://graph.facebook.com/v24.0/oauth/access_token?\
grant_type=fb_exchange_token&\
client_id=22656782605*****&\
client_secret=a6b396f452856b5a*****************&\
fb_exchange_token=EAAgMn1PlZBq0BQ..."
```

### 4.2 Converter Token (Instagram Graph API)

Para tokens específicos do **Instagram**:

```bash
curl -X GET "https://graph.instagram.com/access_token?\
grant_type=ig_exchange_token&\
client_secret=SEU_INSTAGRAM_APP_SECRET&\
access_token=SEU_TOKEN_CURTO_PRAZO"
```

### 4.3 Response Esperada

```json
{
  "access_token": "EAAgMn1PlZBq0BQYk0igeM4w1YY...",
  "token_type": "bearer",
  "expires_in": 5183944
}
```

O token longo prazo tem validade de **60 dias** (~5.184.000 segundos).

```
┌──────────────────────────────────────────────────────────────┐
│  TOKEN LONGO PRAZO (Exemplo - Renovar a cada 60 dias)       │
├──────────────────────────────────────────────────────────────┤
│  Token: EAAgMn1PlZBq0BQYk0igeM4w...                         │
│  Tipo:  Long-Lived User Access Token                        │
│  Expira: 60 dias                                            │
│  Renova: Antes de expirar usando mesmo endpoint             │
└──────────────────────────────────────────────────────────────┘
```

### 4.4 Renovar Token Antes de Expirar

Use o mesmo endpoint com o token atual para renovar:

```bash
curl -X GET "https://graph.facebook.com/v24.0/oauth/access_token?\
grant_type=fb_exchange_token&\
client_id=SEU_APP_ID&\
client_secret=SEU_APP_SECRET&\
fb_exchange_token=SEU_TOKEN_LONGO_PRAZO_ATUAL"
```

---

## Etapa 5: Configurar Webhooks

### 5.1 Criar Webhook Verify Token

Gere um token aleatório para verificação:

```
┌──────────────────────────────────────────────────────────────┐
│  WEBHOOK VERIFY TOKEN (Exemplo)                             │
├──────────────────────────────────────────────────────────────┤
│  Token: b573961dadcb50587a*****************                 │
│  Uso:   Verificação de callback do Facebook                 │
└──────────────────────────────────────────────────────────────┘
```

### 5.2 Configurar Callback URL

No painel do app, vá em **Webhooks > Instagram**:

1. **Callback URL**: `https://n8n.bidu.guru/webhook/instagram`
2. **Verify Token**: Seu token gerado acima
3. Assine os eventos desejados:
   - `comments`
   - `mentions`
   - `story_insights`

### 5.3 Endpoint de Verificação (Backend)

O Facebook fará um GET para verificar o webhook:

```python
# app/api/v1/webhooks/instagram.py
from fastapi import APIRouter, Query, HTTPException
from app.core.config import settings

router = APIRouter()

@router.get("/webhook/instagram")
async def verify_webhook(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_verify_token: str = Query(None, alias="hub.verify_token"),
    hub_challenge: str = Query(None, alias="hub.challenge"),
):
    """
    Endpoint de verificação do webhook do Instagram/Facebook.
    Facebook envia GET com token para validar o callback.
    """
    if hub_mode == "subscribe" and hub_verify_token == settings.WEBHOOK_VERIFY_TOKEN:
        return int(hub_challenge)
    raise HTTPException(status_code=403, detail="Verification failed")
```

---

## Etapa 6: Configurar OAuth para n8n

### 6.1 Configurar Facebook Login

No painel do app, vá em **Facebook Login > Configurações**:

```
┌──────────────────────────────────────────────────────────────┐
│  FACEBOOK LOGIN - CONFIGURAÇÕES                             │
├──────────────────────────────────────────────────────────────┤
│  URIs de Redirecionamento do OAuth Válidos:                 │
│  https://n8n.bidu.guru/rest/oauth2-credential/callback      │
│                                                             │
│  Logout URLs:                                               │
│  https://n8n.bidu.guru/logout                               │
│                                                             │
│  Deauthorize Callback URL:                                  │
│  https://n8n.bidu.guru/webhook/fb-deauthorize               │
└──────────────────────────────────────────────────────────────┘
```

### 6.2 Criar Credencial no n8n

No n8n, crie uma credencial **Facebook Graph API**:

1. Vá em **Credentials > New**
2. Selecione **Facebook Graph API**
3. Preencha:
   - **App ID**: Seu App ID
   - **App Secret**: Sua App Secret
   - **Access Token**: Token longo prazo

### 6.3 Credencial Instagram no n8n

Crie também uma credencial **Instagram**:

```json
{
  "accessToken": "SEU_TOKEN_LONGO_PRAZO",
  "instagramAccountId": "SEU_INSTAGRAM_ACCOUNT_ID"
}
```

---

## Estrutura JSON para n8n Output Parser

### Modelo de Saída para Agente IA

Use este JSON schema como output parser no n8n para estruturar respostas de agentes de IA:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "InstagramPostOutput",
  "description": "Estrutura de saída para posts do Instagram gerados por IA",
  "type": "object",
  "required": ["caption", "hashtags", "media_type"],
  "properties": {
    "caption": {
      "type": "string",
      "description": "Texto principal do post (máx 2200 caracteres)",
      "maxLength": 2200
    },
    "headline": {
      "type": "string",
      "description": "Headline de impacto para template visual",
      "maxLength": 50
    },
    "title": {
      "type": "string",
      "description": "Título curto do produto/conteúdo",
      "maxLength": 100
    },
    "badge": {
      "type": "string",
      "description": "Badge/etiqueta (ex: NOVO!, OFERTA)",
      "maxLength": 30
    },
    "hashtags": {
      "type": "array",
      "description": "Lista de hashtags (sem #)",
      "items": {
        "type": "string",
        "pattern": "^[a-zA-Z0-9_]+$"
      },
      "minItems": 5,
      "maxItems": 30
    },
    "media_type": {
      "type": "string",
      "enum": ["IMAGE", "VIDEO", "CAROUSEL_ALBUM"],
      "description": "Tipo de mídia do post"
    },
    "alt_text": {
      "type": "string",
      "description": "Texto alternativo para acessibilidade",
      "maxLength": 420
    },
    "call_to_action": {
      "type": "string",
      "description": "CTA para engajamento",
      "maxLength": 150
    },
    "suggested_post_time": {
      "type": "string",
      "format": "date-time",
      "description": "Horário sugerido para publicação (ISO 8601)"
    },
    "content_category": {
      "type": "string",
      "enum": ["produto", "dica", "meme", "promocao", "engajamento", "informativo"],
      "description": "Categoria do conteúdo"
    },
    "target_audience": {
      "type": "array",
      "description": "Público-alvo do post",
      "items": {
        "type": "string"
      }
    },
    "related_products": {
      "type": "array",
      "description": "IDs de produtos relacionados",
      "items": {
        "type": "string",
        "format": "uuid"
      }
    }
  }
}
```

### Exemplo de Output Estruturado

```json
{
  "caption": "🎮 CHEGOU O PRESENTE PERFEITO!\n\nEsse kit de materiais do Mario vai fazer a escola ficar muito mais divertida! Caderno, estojo, lápis... tudo com o bigodudo mais famoso dos games!\n\n💰 Preço especial no link da bio!\n\n👆 Corre que é edição limitada!\n\n#mario #nintendo #geek #voltaasaulas #materialescolar",
  "headline": "VOLTA ÀS AULAS GEEK!",
  "title": "Kit Material Escolar Mario Bros",
  "badge": "NOVIDADE",
  "hashtags": [
    "mario",
    "nintendo",
    "geek",
    "voltaasaulas",
    "materialescolar",
    "supermario",
    "games",
    "nerd",
    "escola",
    "papelaria"
  ],
  "media_type": "IMAGE",
  "alt_text": "Kit de material escolar do Super Mario Bros contendo caderno vermelho, estojo azul e lápis coloridos com personagens do jogo",
  "call_to_action": "Link na bio para garantir o seu!",
  "suggested_post_time": "2025-12-24T18:00:00-03:00",
  "content_category": "produto",
  "target_audience": ["gamers", "estudantes", "pais", "geeks"],
  "related_products": ["550e8400-e29b-41d4-a716-446655440000"]
}
```

### Configuração no n8n - Output Parser Node

```json
{
  "nodes": [
    {
      "name": "Output Parser",
      "type": "@n8n/n8n-nodes-langchain.outputParserStructured",
      "parameters": {
        "schemaType": "fromJson",
        "jsonSchemaExample": "{{ JSON Schema acima }}"
      }
    }
  ]
}
```

---

## Credenciais e Configurações

### Tabela de Credenciais (Template)

> **IMPORTANTE**: Substitua os valores de exemplo pelos seus valores reais.
> Nunca commite credenciais reais no repositório.

```
┌────────────────────────────────────────────────────────────────────────┐
│                        CREDENCIAIS - TEMPLATE                          │
├────────────────────────────────────────────────────────────────────────┤
│                                                                        │
│  FACEBOOK APP                                                          │
│  ────────────────────────────────────────────────────────────────────  │
│  App ID:                   22656782605***** (ofuscado)                │
│  App Secret:               a6b396f452856b5a***************** (ofusc.) │
│  Namespace:                geek-bidu-guru                             │
│                                                                        │
│  INSTAGRAM APP (se separado)                                          │
│  ────────────────────────────────────────────────────────────────────  │
│  Instagram App ID:         22693563435***** (ofuscado)                │
│  Instagram App Secret:     f21e947c7489c1b5***************** (ofusc.) │
│                                                                        │
│  TOKENS                                                                │
│  ────────────────────────────────────────────────────────────────────  │
│  Access Token (Long-Lived): IGAAgP97K5n2dBZAG... (ofuscado)           │
│  Webhook Verify Token:      b573961dadcb50587a****** (ofuscado)       │
│                                                                        │
│  CONTAS                                                                │
│  ────────────────────────────────────────────────────────────────────  │
│  Instagram Account ID:      178414788066***** (ofuscado)              │
│  Business ID:               20549023419***** (ofuscado)               │
│                                                                        │
│  ADMIN                                                                 │
│  ────────────────────────────────────────────────────────────────────  │
│  Email:                     admin@geek.bidu.guru                      │
│  Senha:                     ********** (não armazenar aqui)           │
│                                                                        │
└────────────────────────────────────────────────────────────────────────┘
```

### Variáveis de Ambiente (.env)

Adicione ao seu arquivo `.env`:

```bash
# Facebook/Instagram API
FACEBOOK_APP_ID=22656782605*****
FACEBOOK_APP_SECRET=a6b396f452856b5a*****************
INSTAGRAM_APP_ID=22693563435*****
INSTAGRAM_APP_SECRET=f21e947c7489c1b5*****************
INSTAGRAM_ACCOUNT_ID=178414788066*****
INSTAGRAM_ACCESS_TOKEN=IGAAgP97K5n2dBZAG...

# Webhooks
WEBHOOK_VERIFY_TOKEN=b573961dadcb50587a******

# Business
META_BUSINESS_ID=20549023419*****
```

---

## Troubleshooting

### Erros Comuns

| Erro | Causa | Solução |
|------|-------|---------|
| `OAuthException 190` | Token expirado ou inválido | Gerar novo token longo prazo |
| `OAuthException 10` | Permissão não concedida | Verificar escopos do token |
| `Error 100` | Parâmetro inválido | Verificar formato dos IDs |
| `Error 190` (subcode 460) | Senha alterada | Refazer autenticação |
| `Error 190` (subcode 463) | Token expirado | Renovar token |

### Verificar Status do Token

```bash
curl -X GET "https://graph.facebook.com/debug_token?\
input_token=SEU_TOKEN&\
access_token=APP_ID|APP_SECRET"
```

### Testar Conexão com Instagram

```bash
# Buscar informações da conta
curl -X GET "https://graph.instagram.com/v24.0/me?\
fields=id,username,account_type&\
access_token=SEU_TOKEN"
```

### Listar Páginas Vinculadas

```bash
curl -X GET "https://graph.facebook.com/v24.0/me/accounts?\
access_token=SEU_TOKEN"
```

---

## Links Úteis

### Documentação Oficial

- [Instagram Platform Overview](https://developers.facebook.com/docs/instagram-platform)
- [Instagram API with Business Login](https://developers.facebook.com/docs/instagram-platform/instagram-api-with-instagram-login/business-login)
- [Graph API Reference](https://developers.facebook.com/docs/graph-api)
- [Content Publishing API](https://developers.facebook.com/docs/instagram-platform/content-publishing)

### Ferramentas do Facebook

- [Graph API Explorer](https://developers.facebook.com/tools/explorer/)
- [Access Token Debugger](https://developers.facebook.com/tools/debug/accesstoken/)
- [Meta Business Suite](https://business.facebook.com)
- [Facebook Developers](https://developers.facebook.com)

### Links do Projeto

| Recurso | URL |
|---------|-----|
| Business Settings | `https://business.facebook.com/latest/settings/business_users?business_id=SEU_ID` |
| App Use Cases | `https://developers.facebook.com/apps/SEU_APP_ID/use_cases/customize/` |
| Instagram Access | `https://www.instagram.com/accounts/manage_access/` |

---

## Checklist de Configuração

### Pré-Deploy

- [ ] App criado no Facebook Developers
- [ ] Instagram Graph API adicionado como produto
- [ ] Facebook Login configurado
- [ ] Conta Instagram Business vinculada
- [ ] Permissões necessárias habilitadas
- [ ] Token longo prazo gerado e salvo
- [ ] Variáveis de ambiente configuradas
- [ ] Webhook verify token gerado
- [ ] OAuth redirect URI configurado para n8n

### Validação

- [ ] Token validado no Access Token Debugger
- [ ] Teste de GET /me funciona
- [ ] Teste de publicação em modo sandbox
- [ ] Webhook recebendo eventos (se configurado)
- [ ] Credenciais salvas no n8n

### Produção

- [ ] App em modo "Live" (não Development)
- [ ] Permissões aprovadas pela Meta (se necessário)
- [ ] Monitoramento de expiração de token configurado
- [ ] Rotina de renovação de token implementada

---

## Changelog

| Versão | Data | Alterações |
|--------|------|------------|
| 1.0 | 2025-12-24 | Versão inicial do cookbook |

---

## Suporte

Para dúvidas ou problemas:
- Consultar documentação relacionada: [docs/api/INSTAGRAM-API-REFERENCE.md](../api/INSTAGRAM-API-REFERENCE.md)
- Workflow de referência: [docs/workflows/FLOW-A-POST-DIARIO.md](../workflows/FLOW-A-POST-DIARIO.md)
- Abrir issue no repositório GitHub
