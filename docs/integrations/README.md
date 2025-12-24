# Integrações - Documentação

> Cookbooks e guias de configuração para integrações externas do projeto geek.bidu.guru

---

## Índice de Integrações

| Integração | Documento | Descrição |
|------------|-----------|-----------|
| Facebook/Instagram API | [FACEBOOK-INSTAGRAM-API-COOKBOOK.md](./FACEBOOK-INSTAGRAM-API-COOKBOOK.md) | Configuração completa do app Facebook para acesso às APIs do Instagram |
| Telegram Bot | [TELEGRAM-BOT-COOKBOOK.md](./TELEGRAM-BOT-COOKBOOK.md) | Configuração do bot Telegram para notificações |

---

## Documentação Relacionada

- [API Reference - Instagram](../api/INSTAGRAM-API-REFERENCE.md) - Endpoints da nossa API interna
- [N8N Integration](../N8N-INTEGRATION.md) - Integração geral com n8n
- [Flow A - Post Diário](../workflows/FLOW-A-POST-DIARIO.md) - Workflow de publicação automática

---

## Segurança

**IMPORTANTE**: Nunca commite credenciais reais. Todos os tokens e secrets devem ser:

1. Armazenados em variáveis de ambiente (`.env`)
2. Ofuscados na documentação
3. Rotacionados periodicamente
4. Limitados ao escopo mínimo necessário

---

**Última atualização**: 2025-12-24
