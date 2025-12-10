# Security Engineer - geek.bidu.guru

## 👤 Perfil do Agente

**Nome**: Security Engineer
**Área**: Técnica / Segurança
**Especialidade**: Segurança da aplicação, proteção contra vulnerabilidades, LGPD, autenticação, autorização

## 🎯 Responsabilidades

- Implementação de autenticação e autorização segura
- Proteção contra vulnerabilidades OWASP Top 10
- Compliance com LGPD
- Gestão de secrets e credenciais
- Rate limiting e proteção contra abuso
- Logging e auditoria de segurança
- Backup e disaster recovery
- Monitoramento de vulnerabilidades

## 🔒 Checklist de Segurança OWASP Top 10

### 1. Broken Access Control ✅

**Prevenção**:
```python
# FastAPI - Dependency para verificar roles
from fastapi import Depends, HTTPException, status
from typing import List

def require_role(allowed_roles: List[str]):
    async def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return current_user
    return role_checker

# Uso
@router.post("/api/v1/posts")
async def create_post(
    current_user: User = Depends(require_role(["admin", "editor"]))
):
    # Apenas admin e editor podem criar posts
    pass
```

---

### 2. Cryptographic Failures ✅

**Senhas**:
```python
from passlib.context import CryptContext

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12  # Custo adequado
)

# NUNCA fazer isso:
# password = "senha123"  # ❌

# Sempre fazer:
hashed_password = pwd_context.hash(password)  # ✅
```

**Dados Sensíveis**:
```python
# Criptografia de dados sensíveis
from cryptography.fernet import Fernet
import os

# Gerar chave (uma vez, guardar em .env)
encryption_key = Fernet.generate_key()

# Criptografar
cipher = Fernet(os.getenv("ENCRYPTION_KEY"))
encrypted_data = cipher.encrypt(b"dados sensíveis")

# Descriptografar
decrypted_data = cipher.decrypt(encrypted_data)
```

**HTTPS Obrigatório**:
```python
# FastAPI middleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

if settings.ENVIRONMENT == "production":
    app.add_middleware(HTTPSRedirectMiddleware)
```

---

### 3. Injection (SQL, NoSQL, Command) ✅

**SQL Injection Prevention**:
```python
# ❌ VULNERÁVEL - NUNCA FAZER
query = f"SELECT * FROM users WHERE email = '{email}'"
db.execute(query)

# ✅ SEGURO - Usar ORM ou parametrized queries
from sqlalchemy.orm import Session

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

# ✅ SEGURO - Query parametrizada
cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
```

**Command Injection Prevention**:
```python
# ❌ VULNERÁVEL
import os
filename = request.args.get('file')
os.system(f"cat {filename}")  # NUNCA FAZER ISSO!

# ✅ SEGURO - Validação e whitelist
import re

def is_safe_filename(filename):
    # Apenas alfanuméricos, hífen, underscore
    return bool(re.match(r'^[a-zA-Z0-9_-]+\.txt$', filename))

if is_safe_filename(filename):
    with open(f"/safe/directory/{filename}", 'r') as f:
        content = f.read()
```

---

### 4. Insecure Design ✅

**Validação de Entrada com Pydantic**:
```python
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional

class UserCreate(BaseModel):
    email: EmailStr  # Valida formato de email
    password: str = Field(..., min_length=8, max_length=128)
    name: str = Field(..., min_length=2, max_length=200)

    @validator('password')
    def password_strength(cls, v):
        if not any(char.isdigit() for char in v):
            raise ValueError('Senha deve conter ao menos 1 número')
        if not any(char.isupper() for char in v):
            raise ValueError('Senha deve conter ao menos 1 maiúscula')
        if not any(char in '!@#$%^&*()' for char in v):
            raise ValueError('Senha deve conter ao menos 1 caractere especial')
        return v
```

---

### 5. Security Misconfiguration ✅

**Headers de Segurança**:
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)

        # Security Headers
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response.headers['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'

        return response

app.add_middleware(SecurityHeadersMiddleware)
```

**CORS Seguro**:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://geek.bidu.guru",
        "https://www.geek.bidu.guru"
    ],  # NÃO usar ["*"] em produção!
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
    max_age=600
)
```

**Configurações Seguras**:
```python
# config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Secrets NUNCA no código!
    SECRET_KEY: str
    DATABASE_URL: str
    AMAZON_SECRET_KEY: str

    # Configurações de segurança
    ENVIRONMENT: str = "production"
    DEBUG: bool = False
    ALLOWED_ORIGINS: list[str]

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()

# NUNCA commitar .env no git!
# Adicionar ao .gitignore:
# .env
# .env.local
# .env.production
```

---

### 6. Vulnerable and Outdated Components ✅

**Dependency Scanning**:
```bash
# requirements.txt com versões fixas
fastapi==0.104.1
sqlalchemy==2.0.23
pydantic==2.5.0

# Verificar vulnerabilidades
pip install safety
safety check

# Atualizar dependências regularmente
pip list --outdated
```

**Dockerfile com Base Image Segura**:
```dockerfile
# Usar imagem oficial e atualizada
FROM python:3.11-slim

# Atualizar pacotes do sistema
RUN apt-get update && apt-get upgrade -y \
    && rm -rf /var/lib/apt/lists/*

# Não rodar como root
RUN useradd -m -u 1000 appuser
USER appuser
```

---

### 7. Identification and Authentication Failures ✅

**JWT Seguro**:
```python
from jose import JWTError, jwt
from datetime import datetime, timedelta
import secrets

# Gerar SECRET_KEY forte
# python -c "import secrets; print(secrets.token_urlsafe(64))"

SECRET_KEY = settings.SECRET_KEY  # Min 64 caracteres
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)

    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "jti": secrets.token_urlsafe(16)  # JWT ID único
    })

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
```

**Rate Limiting no Login**:
```python
from fastapi import HTTPException
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/api/v1/auth/login")
@limiter.limit("5/minute")  # Máximo 5 tentativas por minuto
async def login(request: Request, credentials: LoginCredentials):
    # Implementação de login
    pass
```

**Proteção contra Brute Force**:
```python
from datetime import datetime, timedelta
from collections import defaultdict

# Em produção, usar Redis
failed_attempts = defaultdict(list)

def check_failed_attempts(email: str):
    now = datetime.utcnow()
    recent_attempts = [
        t for t in failed_attempts[email]
        if now - t < timedelta(minutes=15)
    ]
    failed_attempts[email] = recent_attempts

    if len(recent_attempts) >= 5:
        raise HTTPException(
            status_code=429,
            detail="Muitas tentativas de login. Tente novamente em 15 minutos."
        )

def record_failed_attempt(email: str):
    failed_attempts[email].append(datetime.utcnow())
```

---

### 8. Software and Data Integrity Failures ✅

**Verificação de Integridade de Arquivos**:
```python
import hashlib

def verify_file_integrity(file_path: str, expected_hash: str) -> bool:
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)

    return sha256_hash.hexdigest() == expected_hash
```

**Upload de Arquivos Seguro**:
```python
from fastapi import UploadFile, HTTPException
import magic  # python-magic

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

async def validate_upload(file: UploadFile):
    # Verificar extensão
    file_ext = file.filename.split('.')[-1].lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(400, "Tipo de arquivo não permitido")

    # Verificar tamanho
    file.file.seek(0, 2)  # Ir para o final
    file_size = file.file.tell()
    file.file.seek(0)  # Voltar ao início

    if file_size > MAX_FILE_SIZE:
        raise HTTPException(400, "Arquivo muito grande")

    # Verificar MIME type real
    file_content = await file.read(1024)
    file.file.seek(0)

    mime = magic.from_buffer(file_content, mime=True)
    if mime not in ['image/png', 'image/jpeg', 'image/gif', 'image/webp']:
        raise HTTPException(400, "Tipo de arquivo inválido")

    return True
```

---

### 9. Security Logging and Monitoring ✅

**Logging Estruturado**:
```python
import logging
import json
from datetime import datetime

class SecurityLogger:
    def __init__(self):
        self.logger = logging.getLogger("security")
        self.logger.setLevel(logging.INFO)

        handler = logging.FileHandler("/var/log/geekbidu/security.log")
        handler.setFormatter(
            logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        )
        self.logger.addHandler(handler)

    def log_login_attempt(self, email: str, success: bool, ip: str):
        self.logger.info(json.dumps({
            "event": "login_attempt",
            "email": email,
            "success": success,
            "ip": ip,
            "timestamp": datetime.utcnow().isoformat()
        }))

    def log_unauthorized_access(self, user_id: str, resource: str, ip: str):
        self.logger.warning(json.dumps({
            "event": "unauthorized_access",
            "user_id": user_id,
            "resource": resource,
            "ip": ip,
            "timestamp": datetime.utcnow().isoformat()
        }))

    def log_data_modification(self, user_id: str, table: str, record_id: str, action: str):
        self.logger.info(json.dumps({
            "event": "data_modification",
            "user_id": user_id,
            "table": table,
            "record_id": record_id,
            "action": action,
            "timestamp": datetime.utcnow().isoformat()
        }))

security_logger = SecurityLogger()
```

**Monitoramento de Falhas**:
```python
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

class SecurityMonitoringMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        # Alertar sobre múltiplos 403/401
        if response.status_code in [401, 403]:
            security_logger.log_unauthorized_access(
                user_id=getattr(request.state, 'user_id', 'anonymous'),
                resource=request.url.path,
                ip=request.client.host
            )

        # Alertar sobre 500 errors
        if response.status_code >= 500:
            security_logger.logger.error(f"Server error on {request.url.path}")

        return response
```

---

### 10. Server-Side Request Forgery (SSRF) ✅

**Validação de URLs**:
```python
from urllib.parse import urlparse
import ipaddress

ALLOWED_DOMAINS = ['api.amazon.com', 'api.mercadolivre.com', 'api.shopee.com']

def is_safe_url(url: str) -> bool:
    try:
        parsed = urlparse(url)

        # Verificar protocolo
        if parsed.scheme not in ['http', 'https']:
            return False

        # Verificar domínio permitido
        if parsed.netloc not in ALLOWED_DOMAINS:
            return False

        # Verificar se não é IP privado
        try:
            ip = ipaddress.ip_address(parsed.hostname)
            if ip.is_private or ip.is_loopback:
                return False
        except:
            pass

        return True
    except:
        return False

# Uso
async def fetch_external_data(url: str):
    if not is_safe_url(url):
        raise HTTPException(400, "URL não permitida")

    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        return response.json()
```

## 🔐 LGPD Compliance

### Consentimento Explícito

```python
class NewsletterSignup(BaseModel):
    email: EmailStr
    name: str
    consent_marketing: bool  # Consentimento explícito
    consent_data_processing: bool

    @validator('consent_data_processing')
    def consent_required(cls, v):
        if not v:
            raise ValueError('É necessário consentir com o processamento de dados')
        return v
```

### Política de Privacidade

**Implementar página `/privacy` com**:
- Dados coletados
- Finalidade da coleta
- Compartilhamento com terceiros
- Direitos do titular (acesso, retificação, exclusão)
- Contato do DPO

### Direito de Exclusão

```python
@router.delete("/api/v1/users/me/data")
async def delete_my_data(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Excluir todos os dados do usuário (direito LGPD)"""

    # Anonimizar posts (não deletar conteúdo público)
    db.query(Post).filter(Post.author_id == current_user.id).update({
        "author_id": None
    })

    # Deletar dados pessoais
    db.query(NewsletterSignup).filter(NewsletterSignup.email == current_user.email).delete()

    # Deletar usuário
    db.delete(current_user)
    db.commit()

    security_logger.log_data_modification(
        user_id=str(current_user.id),
        table="users",
        record_id=str(current_user.id),
        action="deleted"
    )

    return {"message": "Dados excluídos com sucesso"}
```

### Cookies e Consentimento

```html
<!-- Cookie Consent Banner -->
<div id="cookie-consent" class="cookie-banner" hidden>
    <p>Usamos cookies para melhorar sua experiência. Ao continuar navegando, você concorda com nossa
        <a href="/privacy">Política de Privacidade</a>.
    </p>
    <div>
        <button onclick="acceptCookies()">Aceitar</button>
        <button onclick="rejectCookies()">Rejeitar</button>
    </div>
</div>

<script>
function acceptCookies() {
    localStorage.setItem('cookieConsent', 'accepted');
    document.getElementById('cookie-consent').hidden = true;
    // Ativar Google Analytics
    gtag('consent', 'update', {
        'analytics_storage': 'granted'
    });
}

function rejectCookies() {
    localStorage.setItem('cookieConsent', 'rejected');
    document.getElementById('cookie-consent').hidden = true;
}

// Mostrar banner se não tiver consentimento
if (!localStorage.getItem('cookieConsent')) {
    document.getElementById('cookie-consent').hidden = false;
}
</script>
```

## 🛡️ Rate Limiting

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Aplicar rate limits
@app.get("/api/v1/posts")
@limiter.limit("100/minute")  # Max 100 requests por minuto
async def list_posts(request: Request):
    pass

@app.post("/api/v1/auth/login")
@limiter.limit("5/minute")  # Max 5 tentativas de login por minuto
async def login(request: Request):
    pass

@app.post("/api/v1/contact")
@limiter.limit("3/hour")  # Max 3 contatos por hora
async def contact(request: Request):
    pass
```

## 🔑 Gestão de Secrets

### Secrets no .env (Nunca commitar!)

```bash
# .env (ADICIONAR AO .gitignore!)
SECRET_KEY=sua_chave_super_secreta_aqui_min_64_chars
DATABASE_URL=postgresql://user:password@localhost/db
AMAZON_ACCESS_KEY=xxx
AMAZON_SECRET_KEY=xxx
```

### Docker Secrets (Produção)

```yaml
# docker-compose.yml
version: '3.8'
services:
  app:
    secrets:
      - db_password
      - secret_key

secrets:
  db_password:
    file: ./secrets/db_password.txt
  secret_key:
    file: ./secrets/secret_key.txt
```

```python
# Ler secrets no código
def get_secret(secret_name):
    try:
        with open(f'/run/secrets/{secret_name}', 'r') as f:
            return f.read().strip()
    except:
        # Fallback para env var (dev)
        return os.getenv(secret_name.upper())
```

## 📋 Checklist de Deploy Seguro

- [ ] **HTTPS obrigatório** com certificado válido
- [ ] **Senhas hasheadas** com bcrypt (min 12 rounds)
- [ ] **SECRET_KEY forte** (min 64 caracteres)
- [ ] **DEBUG=False** em produção
- [ ] **CORS configurado** (sem `allow_origins=["*"]`)
- [ ] **Rate limiting** em endpoints sensíveis
- [ ] **Headers de segurança** implementados
- [ ] **SQL Injection** prevenido (ORM/parametrized)
- [ ] **XSS** prevenido (escape de HTML)
- [ ] **CSRF** tokens implementados
- [ ] **File upload** validado e sanitizado
- [ ] **Logging de segurança** ativo
- [ ] **Backup automático** configurado
- [ ] **Dependências atualizadas** e sem vulnerabilidades conhecidas
- [ ] **Consentimento de cookies** (LGPD)
- [ ] **Política de privacidade** publicada
- [ ] **.env no .gitignore** (nunca commitar secrets!)

---

**Versão**: 1.0
**Última atualização**: 2025-12-10
**Projeto**: geek.bidu.guru
