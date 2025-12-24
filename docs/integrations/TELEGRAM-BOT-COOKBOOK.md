# Cookbook: Configuração do Bot Telegram

> **Versão**: 1.0
> **Última atualização**: 2025-12-24
> **Projeto**: geek.bidu.guru

---

## Índice

1. [Visão Geral](#visão-geral)
2. [Criar Bot no BotFather](#criar-bot-no-botfather)
3. [Configurar Webhook](#configurar-webhook)
4. [Integração com n8n](#integração-com-n8n)
5. [Credenciais](#credenciais)

---

## Visão Geral

Bot Telegram para notificações e interações automatizadas do projeto geek.bidu.guru.

### Casos de Uso

- Notificações de novos posts publicados
- Alertas de erros nos workflows
- Comandos para consultar status
- Receber sugestões de produtos

---

## Criar Bot no BotFather

### Passo a Passo

1. Abra o Telegram e busque por **@BotFather**
2. Envie o comando `/newbot`
3. Siga as instruções para nomear o bot
4. Anote o token gerado

```
┌──────────────────────────────────────────────────────────────┐
│  TOKEN DO BOT (Exemplo - Ofuscado)                          │
├──────────────────────────────────────────────────────────────┤
│  Token: 8287331470:AAGxpy73aRL40Zs*********************     │
│                                                              │
│  Use este token para acessar a HTTP API:                    │
│  https://api.telegram.org/bot<TOKEN>/METHOD_NAME            │
└──────────────────────────────────────────────────────────────┘
```

---

## Configurar Webhook

### Endpoint de Webhook

```bash
# Configurar webhook
curl -X POST "https://api.telegram.org/bot<TOKEN>/setWebhook" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://n8n.bidu.guru/webhook/telegram"}'
```

### Verificar Webhook

```bash
curl "https://api.telegram.org/bot<TOKEN>/getWebhookInfo"
```

---

## Integração com n8n

### Credencial no n8n

1. Vá em **Credentials > New**
2. Selecione **Telegram API**
3. Cole o token do bot

### Exemplo de Nó

```json
{
  "name": "Telegram Notification",
  "type": "n8n-nodes-base.telegram",
  "parameters": {
    "operation": "sendMessage",
    "chatId": "SEU_CHAT_ID",
    "text": "Novo post publicado!"
  }
}
```

---

## Credenciais

### Variáveis de Ambiente

```bash
# Telegram Bot
TELEGRAM_BOT_TOKEN=8287331470:AAGxpy73aRL40Zs*********************
TELEGRAM_CHAT_ID=SEU_CHAT_ID
```

---

## Changelog

| Versão | Data | Alterações |
|--------|------|------------|
| 1.0 | 2025-12-24 | Versão inicial |
