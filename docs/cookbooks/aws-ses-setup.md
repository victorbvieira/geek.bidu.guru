# Cookbook: Configuracao AWS SES para Newsletter

Este guia detalha o passo a passo para configurar o Amazon SES (Simple Email Service)
para envio de emails de verificacao da newsletter do geek.bidu.guru.

## Pre-requisitos

- Conta AWS ativa
- Dominio `bidu.guru` ja verificado no SES (us-west-2)
- Acesso ao console AWS IAM

---

## 1. Criar Usuario IAM para a Aplicacao

### 1.1 Acessar o Console IAM

1. Acesse [AWS IAM Console](https://console.aws.amazon.com/iam/)
2. No menu lateral, clique em **Users**
3. Clique no botao **Create user**

### 1.2 Configurar o Usuario

1. **User name**: `geek-bidu-guru-ses`
2. Clique em **Next**

### 1.3 Definir Permissoes

1. Selecione **Attach policies directly**
2. Clique em **Create policy** (abre nova aba)

### 1.4 Criar Policy Customizada (Principio do Menor Privilegio)

Na nova aba, selecione a aba **JSON** e cole:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "AllowSendEmail",
            "Effect": "Allow",
            "Action": [
                "ses:SendEmail",
                "ses:SendRawEmail"
            ],
            "Resource": "*",
            "Condition": {
                "StringEquals": {
                    "ses:FromAddress": "contato-geek@bidu.guru"
                }
            }
        },
        {
            "Sid": "AllowGetSendQuota",
            "Effect": "Allow",
            "Action": [
                "ses:GetSendQuota",
                "ses:GetSendStatistics"
            ],
            "Resource": "*"
        }
    ]
}
```

**Explicacao da Policy:**
- `SendEmail` e `SendRawEmail`: Permite enviar emails
- `Condition`: Restringe envio APENAS do email `contato-geek@bidu.guru`
- `GetSendQuota/Statistics`: Permite monitorar limites e estatisticas

5. Clique em **Next**
6. **Policy name**: `geek-bidu-guru-ses-send-policy`
7. **Description**: `Permite envio de emails via SES apenas do endereco contato-geek@bidu.guru`
8. Clique em **Create policy**

### 1.5 Associar Policy ao Usuario

1. Volte para a aba de criacao do usuario
2. Clique no botao de refresh na lista de policies
3. Busque por `geek-bidu-guru-ses-send-policy`
4. Marque a checkbox da policy
5. Clique em **Next**
6. Revise e clique em **Create user**

---

## 2. Gerar Access Key e Secret

### 2.1 Acessar o Usuario Criado

1. Na lista de usuarios, clique em `geek-bidu-guru-ses`
2. Va para a aba **Security credentials**

### 2.2 Criar Access Key

1. Na secao **Access keys**, clique em **Create access key**
2. Selecione **Application running outside AWS**
3. Clique em **Next**
4. **Description tag** (opcional): `geek-bidu-guru-production`
5. Clique em **Create access key**

### 2.3 Salvar as Credenciais (IMPORTANTE!)

**ATENCAO**: Esta e a UNICA vez que voce vera o Secret Access Key!

1. Copie o **Access key ID** (ex: `AKIAIOSFODNN7EXAMPLE`)
2. Copie o **Secret access key** (ex: `wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY`)
3. Guarde em local seguro (gerenciador de senhas)
4. Clique em **Done**

---

## 3. Verificar Email de Envio (Se Necessario)

Se o dominio `bidu.guru` ja esta verificado, o email `contato-geek@bidu.guru`
pode ser usado automaticamente. Caso contrario:

### 3.1 Verificar Identidade de Email

1. Acesse [SES Console](https://console.aws.amazon.com/ses/) na regiao **us-west-2**
2. No menu lateral, clique em **Verified identities**
3. Clique em **Create identity**
4. Selecione **Email address**
5. Digite: `contato-geek@bidu.guru`
6. Clique em **Create identity**
7. Acesse o email e clique no link de verificacao

---

## 4. Configurar o Projeto

### 4.1 Atualizar o arquivo `.env`

```env
# Amazon SES (Email para Newsletter)
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
AWS_REGION=us-west-2

# Remetente dos emails
EMAIL_FROM_ADDRESS=contato-geek@bidu.guru
EMAIL_FROM_NAME=geek.bidu.guru

# Tempo de expiracao do token de validacao (horas)
EMAIL_VERIFICATION_EXPIRE_HOURS=48
```

### 4.2 Para Producao (Easypanel)

No Easypanel, adicione as variaveis de ambiente no servico `app`:

1. Acesse o projeto no Easypanel
2. Va em **Environment**
3. Adicione cada variavel:
   - `AWS_ACCESS_KEY_ID`
   - `AWS_SECRET_ACCESS_KEY`
   - `AWS_REGION`
   - `EMAIL_FROM_ADDRESS`
   - `EMAIL_FROM_NAME`

---

## 5. Testar o Envio

### 5.1 Teste via Python (Local)

```python
import asyncio
from app.services.email import email_service

async def test_email():
    result = await email_service.send_verification_email(
        to_email="seu-email@exemplo.com",
        verification_url="https://geek.bidu.guru/api/v1/newsletter/verify/test-token",
        name="Teste"
    )
    print(f"Email enviado: {result}")

asyncio.run(test_email())
```

### 5.2 Teste via API

```bash
curl -X POST "http://localhost:8001/api/v1/newsletter/subscribe" \
  -H "Content-Type: application/json" \
  -d '{"email": "seu-email@exemplo.com", "name": "Teste"}'
```

---

## 6. Monitoramento e Limites

### 6.1 Limites do SES (Sandbox vs Production)

| Modo       | Limite Diario | Limite por Segundo |
|------------|---------------|-------------------|
| Sandbox    | 200 emails    | 1 email/s         |
| Production | 50.000+       | 14+ emails/s      |

### 6.2 Sair do Sandbox (Producao)

Para enviar para qualquer email (nao apenas verificados):

1. Acesse [SES Console](https://console.aws.amazon.com/ses/)
2. No menu lateral, clique em **Account dashboard**
3. Na secao **Sending statistics**, clique em **Request production access**
4. Preencha o formulario explicando o uso:
   - **Mail type**: Transactional
   - **Website URL**: https://geek.bidu.guru
   - **Use case description**:
     ```
     Email de verificacao de inscricao em newsletter.
     Double opt-in para confirmar cadastro de usuarios.
     Estimativa: 100-500 emails/mes inicialmente.
     ```
5. Aguarde aprovacao (geralmente 24-48h)

### 6.3 Configurar Alertas de Bounce/Complaint

1. No SES Console, va em **Configuration sets**
2. Crie um configuration set: `geek-bidu-guru-config`
3. Adicione um **Event destination** para SNS
4. Configure topicos SNS para:
   - Bounces (emails invalidos)
   - Complaints (marcados como spam)

---

## 7. Custos Estimados

| Volume Mensal | Custo Aproximado |
|---------------|------------------|
| 1.000 emails  | $0.10            |
| 10.000 emails | $1.00            |
| 50.000 emails | $5.00            |

*Precos em USD, regiao us-west-2, dezembro 2024*

---

## 8. Troubleshooting

### Erro: "Email address is not verified"

**Causa**: Conta ainda em Sandbox mode
**Solucao**: Verifique o email do destinatario OU solicite producao

### Erro: "Access Denied"

**Causa**: Policy IAM incorreta ou credenciais erradas
**Solucao**: Verifique a policy e as credenciais no .env

### Erro: "Throttling"

**Causa**: Limite de envio excedido
**Solucao**: Implemente retry com backoff exponencial

### Emails nao chegam

1. Verifique pasta de spam
2. Confirme que o dominio tem SPF/DKIM configurados
3. Verifique logs no CloudWatch

---

## 9. Checklist de Seguranca

- [ ] Access Key armazenada em gerenciador de senhas
- [ ] Secret Key NUNCA commitada no Git
- [ ] Policy IAM com principio do menor privilegio
- [ ] Condition restringindo email de origem
- [ ] Monitoramento de bounces configurado
- [ ] Rate limiting implementado na aplicacao

---

## Referencias

- [AWS SES Developer Guide](https://docs.aws.amazon.com/ses/latest/dg/)
- [boto3 SES Documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ses.html)
- [IAM Best Practices](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html)
