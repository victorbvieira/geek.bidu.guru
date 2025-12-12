#!/usr/bin/env python3
"""
Webhook Server - geek.bidu.guru
Recebe webhooks do GitHub e dispara deploy automatico.

Instalacao:
  1. Copie para /opt/scripts/webhook-server.py na VPS
  2. Siga o passo a passo em docs/DEPLOY.md secao "Deploy Automatico"
"""

import hashlib
import hmac
import json
import os
import subprocess
from http.server import HTTPServer, BaseHTTPRequestHandler

# Configuracoes (definidas via variavel de ambiente)
WEBHOOK_SECRET = os.environ.get('WEBHOOK_SECRET', '')
DEPLOY_SCRIPT = '/opt/scripts/deploy-geek.sh'
PORT = 9000


class WebhookHandler(BaseHTTPRequestHandler):
    """Handler para requisicoes de webhook do GitHub."""

    def do_POST(self):
        """Processa POST do webhook."""
        # Verificar endpoint
        if self.path != '/webhook/geek-bidu':
            self.send_response(404)
            self.end_headers()
            return

        # Ler payload
        content_length = int(self.headers.get('Content-Length', 0))
        payload = self.rfile.read(content_length)

        # Verificar assinatura do GitHub (se secret configurado)
        if WEBHOOK_SECRET:
            signature = self.headers.get('X-Hub-Signature-256', '')
            if not self._verify_signature(payload, signature):
                print(f"[ERRO] Assinatura invalida")
                self.send_response(401)
                self.end_headers()
                self.wfile.write(b'Invalid signature')
                return

        # Parsear payload
        try:
            data = json.loads(payload.decode('utf-8'))
        except json.JSONDecodeError:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b'Invalid JSON')
            return

        # Verificar se e push na branch main
        ref = data.get('ref', '')
        if ref != 'refs/heads/main':
            print(f"[INFO] Ignorando push para {ref}")
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'Ignored (not main)')
            return

        # Extrair info do commit
        commits = data.get('commits', [])
        commit_msg = commits[0].get('message', 'N/A') if commits else 'N/A'
        pusher = data.get('pusher', {}).get('name', 'unknown')

        print(f"[INFO] Push na main por {pusher}: {commit_msg[:50]}")
        print(f"[INFO] Iniciando deploy...")

        # Responder imediatamente
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'Deploy started')

        # Executar script de deploy em background
        subprocess.Popen(
            [DEPLOY_SCRIPT],
            stdout=open('/var/log/geek-deploy.log', 'a'),
            stderr=subprocess.STDOUT,
            start_new_session=True
        )

    def do_GET(self):
        """Health check do webhook server."""
        if self.path == '/health':
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'OK')
        else:
            self.send_response(404)
            self.end_headers()

    def _verify_signature(self, payload: bytes, signature: str) -> bool:
        """Verifica assinatura HMAC-SHA256 do GitHub."""
        if not signature:
            return False
        expected = 'sha256=' + hmac.new(
            WEBHOOK_SECRET.encode('utf-8'),
            payload,
            hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(expected, signature)

    def log_message(self, format, *args):
        """Customiza formato de log."""
        print(f"[{self.log_date_time_string()}] {args[0]}")


def main():
    """Inicia o servidor webhook."""
    server = HTTPServer(('0.0.0.0', PORT), WebhookHandler)
    print(f"=" * 50)
    print(f"Webhook Server - geek.bidu.guru")
    print(f"=" * 50)
    print(f"Porta: {PORT}")
    print(f"Endpoint: http://0.0.0.0:{PORT}/webhook/geek-bidu")
    print(f"Secret: {'Configurado' if WEBHOOK_SECRET else 'NAO CONFIGURADO'}")
    print(f"=" * 50)
    server.serve_forever()


if __name__ == '__main__':
    main()
