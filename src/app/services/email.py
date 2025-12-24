"""
Servico de envio de emails via Amazon SES.

Utiliza aioboto3 para envio assincrono de emails transacionais,
como confirmacao de newsletter e notificacoes.
"""

import logging
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional

import aioboto3

from app.config import settings

logger = logging.getLogger(__name__)


class EmailService:
    """
    Servico de email usando Amazon SES.

    Suporta envio de emails em HTML e texto plano.
    Configurado para uso assincrono com FastAPI.
    """

    def __init__(self) -> None:
        """Inicializa o servico com as credenciais AWS."""
        self.session = aioboto3.Session(
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key,
            region_name=settings.aws_region,
        )
        self.from_address = settings.email_from_address
        self.from_name = settings.email_from_name

    def _format_sender(self) -> str:
        """Formata o remetente no padrao 'Nome <email>'."""
        return f"{self.from_name} <{self.from_address}>"

    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_body: str,
        text_body: Optional[str] = None,
    ) -> bool:
        """
        Envia um email via Amazon SES.

        Args:
            to_email: Email do destinatario
            subject: Assunto do email
            html_body: Corpo do email em HTML
            text_body: Corpo do email em texto plano (opcional, fallback)

        Returns:
            True se enviado com sucesso, False caso contrario

        Note:
            Se text_body nao for fornecido, sera gerado uma versao
            simplificada do HTML removendo as tags.
        """
        # Se nao tiver credenciais configuradas, loga warning e retorna
        if not settings.aws_access_key_id or not settings.aws_secret_access_key:
            logger.warning(
                "Credenciais AWS nao configuradas. Email nao enviado para %s",
                to_email,
            )
            return False

        # Gera texto plano se nao fornecido
        if text_body is None:
            # Remove tags HTML basicas para fallback
            import re
            text_body = re.sub(r"<[^>]+>", "", html_body)
            text_body = re.sub(r"\s+", " ", text_body).strip()

        try:
            async with self.session.client("ses") as ses:
                response = await ses.send_email(
                    Source=self._format_sender(),
                    Destination={
                        "ToAddresses": [to_email],
                    },
                    Message={
                        "Subject": {
                            "Data": subject,
                            "Charset": "UTF-8",
                        },
                        "Body": {
                            "Text": {
                                "Data": text_body,
                                "Charset": "UTF-8",
                            },
                            "Html": {
                                "Data": html_body,
                                "Charset": "UTF-8",
                            },
                        },
                    },
                )

                message_id = response.get("MessageId", "unknown")
                logger.info(
                    "Email enviado com sucesso. MessageId: %s, Destinatario: %s",
                    message_id,
                    to_email,
                )
                return True

        except Exception as e:
            logger.error(
                "Falha ao enviar email para %s: %s",
                to_email,
                str(e),
            )
            return False

    async def send_verification_email(
        self,
        to_email: str,
        verification_url: str,
    ) -> bool:
        """
        Envia email de verificacao/confirmacao de newsletter.

        Args:
            to_email: Email do inscrito
            verification_url: URL para confirmar inscricao

        Returns:
            True se enviado com sucesso, False caso contrario
        """
        # Saudacao generica (sem nome, pois so capturamos o email)
        greeting = "Oi!"
        current_year = datetime.now().year

        # URL de descadastro com email pre-preenchido
        from urllib.parse import quote
        unsubscribe_url = f"{settings.app_url}/newsletter/descadastro?email={quote(to_email)}"

        html_body = f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Confirme sua inscricao - geek.bidu.guru</title>
</head>
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
    <div style="background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%); padding: 30px; border-radius: 12px 12px 0 0; text-align: center;">
        <h1 style="color: white; margin: 0; font-size: 28px;">🎮 geek.bidu.guru</h1>
        <p style="color: rgba(255,255,255,0.9); margin: 10px 0 0 0;">Presentes Geek com Curadoria</p>
    </div>

    <div style="background: #f9fafb; padding: 30px; border-radius: 0 0 12px 12px;">
        <h2 style="color: #1f2937; margin-top: 0;">{greeting}</h2>

        <p>Que legal que voce quer receber nossas dicas de presentes geek! 🚀</p>

        <p>Para confirmar sua inscricao na nossa newsletter, clique no botao abaixo:</p>

        <div style="text-align: center; margin: 30px 0;">
            <a href="{verification_url}"
               style="display: inline-block; background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%); color: white; text-decoration: none; padding: 14px 32px; border-radius: 8px; font-weight: 600; font-size: 16px;">
                Confirmar Inscricao
            </a>
        </div>

        <p style="color: #6b7280; font-size: 14px;">
            Se o botao nao funcionar, copie e cole este link no seu navegador:<br>
            <a href="{verification_url}" style="color: #6366f1; word-break: break-all;">{verification_url}</a>
        </p>

        <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 30px 0;">

        <p style="color: #6b7280; font-size: 13px; margin-bottom: 0;">
            Se voce nao solicitou essa inscricao, pode ignorar este email com seguranca.
            Este link expira em {settings.email_verification_expire_hours} horas.
        </p>
    </div>

    <div style="text-align: center; padding: 20px; color: #9ca3af; font-size: 12px;">
        <p>&copy; {current_year} geek.bidu.guru - Todos os direitos reservados</p>
        <p style="margin-top: 8px;">
            <a href="{unsubscribe_url}" style="color: #9ca3af; text-decoration: underline;">Cancelar inscricao</a>
        </p>
    </div>
</body>
</html>
"""

        text_body = f"""
{greeting}

Que legal que voce quer receber nossas dicas de presentes geek!

Para confirmar sua inscricao na nossa newsletter, acesse o link abaixo:

{verification_url}

Se voce nao solicitou essa inscricao, pode ignorar este email com seguranca.
Este link expira em {settings.email_verification_expire_hours} horas.

---
(c) {current_year} geek.bidu.guru - Presentes Geek com Curadoria

Para cancelar sua inscricao, acesse: {unsubscribe_url}
"""

        return await self.send_email(
            to_email=to_email,
            subject="Confirme sua inscricao na newsletter - geek.bidu.guru",
            html_body=html_body,
            text_body=text_body,
        )


    async def send_newsletter_email(
        self,
        to_email: str,
        subject: str,
        heading: str,
        content_html: str,
        preview_text: Optional[str] = None,
        cta_text: Optional[str] = None,
        cta_url: Optional[str] = None,
    ) -> bool:
        """
        Envia email de newsletter para um destinatario.

        Args:
            to_email: Email do destinatario
            subject: Assunto do email
            heading: Titulo principal do email (H1)
            content_html: Conteudo do email em HTML (ja convertido de Markdown)
            preview_text: Texto de preview (aparece ao lado do assunto)
            cta_text: Texto do botao de acao (opcional)
            cta_url: URL do botao de acao (opcional)

        Returns:
            True se enviado com sucesso, False caso contrario
        """
        current_year = datetime.now().year

        # URL de descadastro com email pre-preenchido
        from urllib.parse import quote
        unsubscribe_url = f"{settings.app_url}/newsletter/descadastro?email={quote(to_email)}"

        # Monta o botao CTA se fornecido
        cta_html = ""
        cta_text_plain = ""
        if cta_text and cta_url:
            cta_html = f"""
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{cta_url}"
                       style="display: inline-block; background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%); color: white; text-decoration: none; padding: 14px 32px; border-radius: 8px; font-weight: 600; font-size: 16px;">
                        {cta_text}
                    </a>
                </div>
            """
            cta_text_plain = f"\n\n{cta_text}: {cta_url}\n"

        # Preview text oculto (aparece no preview do email mas nao no corpo)
        preview_html = ""
        if preview_text:
            preview_html = f"""
                <div style="display: none; max-height: 0px; overflow: hidden;">
                    {preview_text}
                </div>
            """

        html_body = f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{subject}</title>
</head>
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px; background-color: #f9fafb;">
    {preview_html}

    <div style="background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
        <!-- Header -->
        <div style="background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%); padding: 30px; text-align: center;">
            <h1 style="color: white; margin: 0; font-size: 28px;">geek.bidu.guru</h1>
            <p style="color: rgba(255,255,255,0.9); margin: 10px 0 0 0;">Presentes Geek com Curadoria</p>
        </div>

        <!-- Content -->
        <div style="padding: 30px;">
            <h2 style="color: #1f2937; margin-top: 0; font-size: 24px;">{heading}</h2>

            <div style="color: #4b5563; line-height: 1.8;">
                {content_html}
            </div>

            {cta_html}
        </div>

        <!-- Footer -->
        <div style="text-align: center; padding: 20px; background: #f9fafb; color: #9ca3af; font-size: 12px;">
            <p style="margin: 0;">&copy; {current_year} geek.bidu.guru - Todos os direitos reservados</p>
            <p style="margin-top: 8px;">
                <a href="{unsubscribe_url}" style="color: #9ca3af; text-decoration: underline;">Cancelar inscricao</a>
            </p>
        </div>
    </div>
</body>
</html>
"""

        # Versao texto plano (remove tags HTML do conteudo)
        import re
        content_plain = re.sub(r"<[^>]+>", "", content_html)
        content_plain = re.sub(r"\s+", " ", content_plain).strip()

        text_body = f"""
{heading}

{content_plain}
{cta_text_plain}
---
(c) {current_year} geek.bidu.guru - Presentes Geek com Curadoria

Para cancelar sua inscricao, acesse: {unsubscribe_url}
"""

        return await self.send_email(
            to_email=to_email,
            subject=subject,
            html_body=html_body,
            text_body=text_body,
        )


# Instancia global do servico
email_service = EmailService()
