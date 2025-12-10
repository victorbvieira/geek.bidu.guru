# DevOps Engineer (Docker/Infrastructure) - geek.bidu.guru

## 👤 Perfil do Agente

**Nome**: DevOps Engineer
**Área**: Técnica / Infraestrutura
**Especialidade**: Docker, Docker Compose, CI/CD, deploy, monitoramento, infraestrutura

## 🎯 Responsabilidades

- Containerização com Docker
- Orquestração com Docker Compose
- Deploy e continuous deployment
- Monitoramento e observabilidade
- Gestão de logs
- Backup automatizado
- Configuração de ambientes (dev, staging, prod)
- Performance e escalabilidade da infraestrutura

## 🐳 Containerização com Docker

### Dockerfile (Python/FastAPI)

```dockerfile
# Multi-stage build para otimização

# Stage 1: Builder
FROM python:3.11-slim as builder

WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements e instalar
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim

WORKDIR /app

# Copiar dependências do builder
COPY --from=builder /root/.local /root/.local

# Adicionar ao PATH
ENV PATH=/root/.local/bin:$PATH

# Copiar código da aplicação
COPY ./app ./app
COPY ./migrations ./migrations
COPY alembic.ini .

# Criar usuário não-root para segurança
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expor porta
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Comando de inicialização
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

### docker-compose.yml (Completo)

```yaml
version: '3.8'

services:
  # PostgreSQL Database
  db:
    image: postgres:15-alpine
    container_name: geekbidu_db
    restart: unless-stopped
    environment:
      POSTGRES_DB: ${POSTGRES_DB:-geekbidu}
      POSTGRES_USER: ${POSTGRES_USER:-geekbidu}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./docker/postgres/init.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER:-geekbidu}"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - geekbidu_network

  # Redis (Cache - Opcional)
  redis:
    image: redis:7-alpine
    container_name: geekbidu_redis
    restart: unless-stopped
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - geekbidu_network

  # FastAPI Application
  app:
    build:
      context: .
      dockerfile: docker/Dockerfile
    container_name: geekbidu_app
    restart: unless-stopped
    environment:
      - DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@db:5432/${POSTGRES_DB}
      - REDIS_URL=redis://redis:6379/0
      - SECRET_KEY=${SECRET_KEY}
      - ENVIRONMENT=production
    volumes:
      - ./app:/app/app
      - ./uploads:/app/uploads
      - ./static:/app/static
    ports:
      - "8000:8000"
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    networks:
      - geekbidu_network

  # Nginx (Reverse Proxy)
  nginx:
    image: nginx:alpine
    container_name: geekbidu_nginx
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./docker/nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./docker/nginx/conf.d:/etc/nginx/conf.d:ro
      - ./static:/var/www/static:ro
      - ./certbot/conf:/etc/letsencrypt:ro
      - ./certbot/www:/var/www/certbot:ro
    depends_on:
      - app
    networks:
      - geekbidu_network

  # n8n (Automation)
  n8n:
    image: n8nio/n8n:latest
    container_name: geekbidu_n8n
    restart: unless-stopped
    environment:
      - N8N_BASIC_AUTH_ACTIVE=true
      - N8N_BASIC_AUTH_USER=${N8N_USER}
      - N8N_BASIC_AUTH_PASSWORD=${N8N_PASSWORD}
      - N8N_HOST=${N8N_HOST:-n8n.geek.bidu.guru}
      - N8N_PROTOCOL=https
      - WEBHOOK_URL=https://${N8N_HOST:-n8n.geek.bidu.guru}
      - GENERIC_TIMEZONE=America/Sao_Paulo
    volumes:
      - n8n_data:/home/node/.n8n
    ports:
      - "5678:5678"
    networks:
      - geekbidu_network

  # Certbot (SSL/TLS - Let's Encrypt)
  certbot:
    image: certbot/certbot:latest
    container_name: geekbidu_certbot
    volumes:
      - ./certbot/conf:/etc/letsencrypt
      - ./certbot/www:/var/www/certbot
    entrypoint: "/bin/sh -c 'trap exit TERM; while :; do certbot renew; sleep 12h & wait $${!}; done;'"
    networks:
      - geekbidu_network

volumes:
  postgres_data:
    driver: local
  redis_data:
    driver: local
  n8n_data:
    driver: local

networks:
  geekbidu_network:
    driver: bridge
```

---

### Configuração do Nginx

**docker/nginx/conf.d/geekbidu.conf**:
```nginx
# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name geek.bidu.guru www.geek.bidu.guru;

    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    location / {
        return 301 https://$server_name$request_uri;
    }
}

# HTTPS Server
server {
    listen 443 ssl http2;
    server_name geek.bidu.guru www.geek.bidu.guru;

    # SSL Certificates
    ssl_certificate /etc/letsencrypt/live/geek.bidu.guru/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/geek.bidu.guru/privkey.pem;

    # SSL Configuration (Mozilla Intermediate)
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384';
    ssl_prefer_server_ciphers off;

    # Security Headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    # Gzip Compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/json application/xml+rss image/svg+xml;

    # Static Files
    location /static/ {
        alias /var/www/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Proxy to FastAPI
    location / {
        proxy_pass http://app:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;

        # Buffering
        proxy_buffering on;
        proxy_buffer_size 4k;
        proxy_buffers 8 4k;
    }

    # Rate Limiting (API endpoints)
    location /api/ {
        limit_req zone=api_limit burst=20 nodelay;

        proxy_pass http://app:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# Rate Limit Zone
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
```

---

### .env.example

```bash
# Database
POSTGRES_DB=geekbidu
POSTGRES_USER=geekbidu
POSTGRES_PASSWORD=sua_senha_super_segura_aqui

# Application
SECRET_KEY=sua_secret_key_jwt_aqui_64_chars
ENVIRONMENT=production
ALLOWED_ORIGINS=https://geek.bidu.guru,https://www.geek.bidu.guru

# n8n
N8N_USER=admin
N8N_PASSWORD=senha_n8n_segura
N8N_HOST=n8n.geek.bidu.guru

# Affiliate APIs
AMAZON_ACCESS_KEY=
AMAZON_SECRET_KEY=
AMAZON_ASSOCIATE_TAG=biduguru-20

MERCADOLIVRE_CLIENT_ID=
MERCADOLIVRE_CLIENT_SECRET=

SHOPEE_PARTNER_ID=
SHOPEE_PARTNER_KEY=

# Email (Opcional para notificações)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=seu_email@gmail.com
SMTP_PASSWORD=sua_senha_app

# Telegram (Alertas)
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=
```

## 🚀 Deploy e CI/CD

### Script de Deploy Inicial

**scripts/deploy.sh**:
```bash
#!/bin/bash
set -e

echo "🚀 Iniciando deploy do geek.bidu.guru..."

# 1. Pull do repositório
echo "📦 Atualizando código..."
git pull origin main

# 2. Copiar .env se não existir
if [ ! -f .env ]; then
    echo "⚠️  Arquivo .env não encontrado. Copiando .env.example..."
    cp .env.example .env
    echo "⚠️  ATENÇÃO: Configure o arquivo .env antes de continuar!"
    exit 1
fi

# 3. Build das imagens Docker
echo "🐳 Building Docker images..."
docker-compose build --no-cache

# 4. Parar containers antigos
echo "🛑 Parando containers antigos..."
docker-compose down

# 5. Executar migrations
echo "🗄️  Executando migrations..."
docker-compose run --rm app alembic upgrade head

# 6. Subir containers
echo "🚀 Iniciando containers..."
docker-compose up -d

# 7. Health check
echo "🏥 Verificando health dos serviços..."
sleep 10
docker-compose ps

echo "✅ Deploy concluído com sucesso!"
echo "🌐 Acesse: https://geek.bidu.guru"
```

---

### GitHub Actions (CI/CD)

**.github/workflows/deploy.yml**:
```yaml
name: Deploy to Production

on:
  push:
    branches:
      - main

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Setup SSH
        uses: webfactory/ssh-agent@v0.7.0
        with:
          ssh-private-key: ${{ secrets.SSH_PRIVATE_KEY }}

      - name: Deploy to VPS
        run: |
          ssh -o StrictHostKeyChecking=no ${{ secrets.SSH_USER }}@${{ secrets.SSH_HOST }} << 'EOF'
            cd /var/www/geek.bidu.guru
            git pull origin main
            docker-compose build
            docker-compose down
            docker-compose run --rm app alembic upgrade head
            docker-compose up -d
            docker-compose ps
          EOF

      - name: Notify Telegram
        if: success()
        run: |
          curl -X POST "https://api.telegram.org/bot${{ secrets.TELEGRAM_BOT_TOKEN }}/sendMessage" \
            -d chat_id="${{ secrets.TELEGRAM_CHAT_ID }}" \
            -d text="✅ Deploy realizado com sucesso em geek.bidu.guru"
```

---

### Makefile (Comandos Úteis)

**Makefile**:
```makefile
.PHONY: help build up down restart logs migrate test clean

help: ## Mostrar ajuda
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

build: ## Build das imagens Docker
	docker-compose build

up: ## Subir containers
	docker-compose up -d

down: ## Parar containers
	docker-compose down

restart: down up ## Reiniciar containers

logs: ## Ver logs (use: make logs SERVICE=app)
	@if [ -z "$(SERVICE)" ]; then \
		docker-compose logs -f; \
	else \
		docker-compose logs -f $(SERVICE); \
	fi

migrate: ## Executar migrations
	docker-compose run --rm app alembic upgrade head

migrate-create: ## Criar nova migration (use: make migrate-create MESSAGE="add_field")
	docker-compose run --rm app alembic revision -m "$(MESSAGE)"

shell: ## Shell do container app
	docker-compose exec app /bin/bash

db-shell: ## Shell do PostgreSQL
	docker-compose exec db psql -U geekbidu -d geekbidu

test: ## Executar testes
	docker-compose run --rm app pytest

clean: ## Limpar containers, volumes e imagens
	docker-compose down -v
	docker system prune -f

backup-db: ## Backup do banco de dados
	docker-compose exec db pg_dump -U geekbidu geekbidu > backup_$(shell date +%Y%m%d_%H%M%S).sql

restore-db: ## Restaurar banco (use: make restore-db FILE=backup.sql)
	cat $(FILE) | docker-compose exec -T db psql -U geekbidu -d geekbidu
```

## 📊 Monitoramento e Logging

### Docker Compose com Prometheus + Grafana (Opcional)

```yaml
  # Prometheus
  prometheus:
    image: prom/prometheus:latest
    container_name: geekbidu_prometheus
    restart: unless-stopped
    volumes:
      - ./docker/prometheus/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
    ports:
      - "9090:9090"
    networks:
      - geekbidu_network

  # Grafana
  grafana:
    image: grafana/grafana:latest
    container_name: geekbidu_grafana
    restart: unless-stopped
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD}
    volumes:
      - grafana_data:/var/lib/grafana
    ports:
      - "3000:3000"
    depends_on:
      - prometheus
    networks:
      - geekbidu_network

  # Node Exporter (Métricas de sistema)
  node_exporter:
    image: prom/node-exporter:latest
    container_name: geekbidu_node_exporter
    restart: unless-stopped
    ports:
      - "9100:9100"
    networks:
      - geekbidu_network
```

**docker/prometheus/prometheus.yml**:
```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'node_exporter'
    static_configs:
      - targets: ['node_exporter:9100']

  - job_name: 'fastapi'
    static_configs:
      - targets: ['app:8000']
```

---

### Logging Centralizado

**app/main.py** (Configuração de Logging):
```python
import logging
import sys
from pythonjsonlogger import jsonlogger

# Configurar logging estruturado (JSON)
logger = logging.getLogger()
logger.setLevel(logging.INFO)

logHandler = logging.StreamHandler(sys.stdout)
formatter = jsonlogger.JsonFormatter(
    '%(asctime)s %(name)s %(levelname)s %(message)s'
)
logHandler.setFormatter(formatter)
logger.addHandler(logHandler)

# Middleware para log de requests
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time

    logger.info({
        "method": request.method,
        "path": request.url.path,
        "status_code": response.status_code,
        "process_time": round(process_time, 3),
        "client_ip": request.client.host
    })

    return response
```

## 🔒 Segurança

### 1. Certbot para SSL (Let's Encrypt)

```bash
# Obter certificado inicial
docker-compose run --rm certbot certonly \
  --webroot \
  --webroot-path=/var/www/certbot \
  --email seu@email.com \
  --agree-tos \
  --no-eff-email \
  -d geek.bidu.guru \
  -d www.geek.bidu.guru
```

---

### 2. Firewall (UFW)

```bash
# Permitir apenas portas necessárias
sudo ufw allow 22/tcp   # SSH
sudo ufw allow 80/tcp   # HTTP
sudo ufw allow 443/tcp  # HTTPS
sudo ufw enable
```

---

### 3. Fail2Ban (Proteção contra brute force)

```bash
# Instalar
sudo apt install fail2ban

# Configurar para nginx
sudo nano /etc/fail2ban/jail.local
```

**jail.local**:
```ini
[nginx-http-auth]
enabled = true
port = http,https
logpath = /var/log/nginx/error.log

[nginx-noscript]
enabled = true
port = http,https
logpath = /var/log/nginx/access.log
```

## 📦 Backup Automatizado

**scripts/backup.sh**:
```bash
#!/bin/bash

BACKUP_DIR="/backup/geekbidu"
DATE=$(date +%Y%m%d_%H%M%S)

# Criar diretório de backup
mkdir -p $BACKUP_DIR

# Backup do banco de dados
docker-compose exec -T db pg_dump -U geekbidu geekbidu | gzip > $BACKUP_DIR/db_$DATE.sql.gz

# Backup de uploads
tar -czf $BACKUP_DIR/uploads_$DATE.tar.gz ./uploads

# Manter apenas últimos 7 dias
find $BACKUP_DIR -name "*.gz" -mtime +7 -delete

echo "✅ Backup concluído: $DATE"
```

**Crontab (executar diariamente às 3h)**:
```bash
0 3 * * * /var/www/geek.bidu.guru/scripts/backup.sh >> /var/log/geekbidu_backup.log 2>&1
```

---

**Versão**: 1.0
**Última atualização**: 2025-12-10
**Projeto**: geek.bidu.guru
