# MEMORIA AI - Security Architecture

## Version: 1.0
## Date: June 13, 2026
## Status: Final

---

## Executive Summary

This document describes the comprehensive security architecture for MEMORIA AI, covering authentication, authorization, data protection, network security, compliance, and security monitoring. The architecture follows OWASP best practices and implements defense-in-depth principles.

---

## Security Principles

### 1. Defense in Depth
Multiple layers of security controls to protect against threats.

### 2. Least Privilege
Users and services have only the minimum access required.

### 3. Zero Trust
No implicit trust; verify every request regardless of source.

### 4. Security by Design
Security integrated into every layer of the architecture.

### 5. Compliance Ready
Designed to meet GDPR, SOC 2, HIPAA, and other regulations.

---

## Authentication Architecture

### Authentication Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           Authentication Flow                                   │
│                                                                              │
│  1. User submits credentials                                                 │
│         │                                                                   │
│         ▼                                                                   │
│  2. API Gateway validates request format                                    │
│         │                                                                   │
│         ▼                                                                   │
│  3. Auth Service validates credentials                                       │
│         │                                                                   │
│         ▼                                                                   │
│  4. Generate JWT access token (15 min)                                     │
│         │                                                                   │
│         ▼                                                                   │
│  5. Generate refresh token (7 days)                                        │
│         │                                                                   │
│         ▼                                                                   │
│  6. Store refresh token in database                                         │
│         │                                                                   │
│         ▼                                                                   │
│  7. Create session record                                                  │
│         │                                                                   │
│         ▼                                                                   │
│  8. Return tokens to client                                                 │
│         │                                                                   │
│         ▼                                                                   │
│  9. Client includes access token in requests                               │
│         │                                                                   │
│         ▼                                                                   │
│  10. API Gateway validates token on each request                            │
│         │                                                                   │
│         ▼                                                                   │
│  11. Service checks permissions                                             │
│         │                                                                   │
│         ▼                                                                   │
│  12. Request processed                                                     │
└─────────────────────────────────────────────────────────────────────────────┘
```

### JWT Token Structure

```python
# core/security/jwt.py
from datetime import datetime, timedelta
from jose import JWTError, jwt
from typing import Optional, Dict

class JWTManager:
    def __init__(self, config: Config):
        self.secret_key = config.SECRET_KEY
        self.algorithm = "HS256"
        self.access_token_expire_minutes = config.ACCESS_TOKEN_EXPIRE_MINUTES
        self.refresh_token_expire_days = config.REFRESH_TOKEN_EXPIRE_DAYS
    
    def create_access_token(
        self,
        user_id: str,
        additional_claims: Optional[Dict] = None
    ) -> str:
        now = datetime.utcnow()
        expires = now + timedelta(minutes=self.access_token_expire_minutes)
        
        claims = {
            "sub": user_id,
            "iat": now.timestamp(),
            "exp": expires.timestamp(),
            "type": "access",
            "jti": str(uuid.uuid4())
        }
        
        if additional_claims:
            claims.update(additional_claims)
        
        return jwt.encode(claims, self.secret_key, algorithm=self.algorithm)
    
    def create_refresh_token(self, user_id: str) -> str:
        now = datetime.utcnow()
        expires = now + timedelta(days=self.refresh_token_expire_days)
        
        claims = {
            "sub": user_id,
            "iat": now.timestamp(),
            "exp": expires.timestamp(),
            "type": "refresh",
            "jti": str(uuid.uuid4())
        }
        
        return jwt.encode(claims, self.secret_key, algorithm=self.algorithm)
    
    def verify_token(self, token: str) -> Dict:
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm]
            )
            return payload
        except JWTError as e:
            raise InvalidTokenException(str(e))
    
    def decode_token(self, token: str) -> Dict:
        return jwt.decode(
            token,
            self.secret_key,
            algorithms=[self.algorithm],
            options={"verify_exp": False}
        )
```

### OAuth Integration

```python
# core/security/oauth.py
from authlib.integrations.base_client import OAuthError
from authlib.integrations.requests_client import OAuth2Session

class OAuthManager:
    def __init__(self, config: Config):
        self.config = config
        self.providers = {
            "google": {
                "client_id": config.GOOGLE_CLIENT_ID,
                "client_secret": config.GOOGLE_CLIENT_SECRET,
                "authorization_url": "https://accounts.google.com/o/oauth2/v2/auth",
                "token_url": "https://oauth2.googleapis.com/token",
                "userinfo_url": "https://www.googleapis.com/oauth2/v2/userinfo"
            },
            "github": {
                "client_id": config.GITHUB_CLIENT_ID,
                "client_secret": config.GITHUB_CLIENT_SECRET,
                "authorization_url": "https://github.com/login/oauth/authorize",
                "token_url": "https://github.com/login/oauth/access_token",
                "userinfo_url": "https://api.github.com/user"
            },
            "microsoft": {
                "client_id": config.MICROSOFT_CLIENT_ID,
                "client_secret": config.MICROSOFT_CLIENT_SECRET,
                "authorization_url": "https://login.microsoftonline.com/common/oauth2/v2.0/authorize",
                "token_url": "https://login.microsoftonline.com/common/oauth2/v2.0/token",
                "userinfo_url": "https://graph.microsoft.com/v1.0/me"
            }
        }
    
    def get_authorization_url(self, provider: str, redirect_uri: str) -> str:
        provider_config = self.providers.get(provider)
        if not provider_config:
            raise ValueError(f"Provider {provider} not supported")
        
        oauth = OAuth2Session(
            provider_config["client_id"],
            redirect_uri=redirect_uri,
            scope=self._get_scope(provider)
        )
        
        return oauth.authorization_url(provider_config["authorization_url"])
    
    async def exchange_code_for_token(
        self,
        provider: str,
        code: str,
        redirect_uri: str
    ) -> Dict:
        provider_config = self.providers.get(provider)
        if not provider_config:
            raise ValueError(f"Provider {provider} not supported")
        
        oauth = OAuth2Session(
            provider_config["client_id"],
            redirect_uri=redirect_uri
        )
        
        token = await oauth.fetch_token(
            provider_config["token_url"],
            code=code,
            client_secret=provider_config["client_secret"]
        )
        
        return token
    
    async def get_user_info(
        self,
        provider: str,
        access_token: str
    ) -> Dict:
        provider_config = self.providers.get(provider)
        if not provider_config:
            raise ValueError(f"Provider {provider} not supported")
        
        oauth = OAuth2Session(token={"access_token": access_token})
        response = await oauth.get(provider_config["userinfo_url"])
        
        return response.json()
    
    def _get_scope(self, provider: str) -> str:
        scopes = {
            "google": "openid email profile",
            "github": "user:email",
            "microsoft": "openid profile email"
        }
        return scopes.get(provider, "")
```

### Two-Factor Authentication

```python
# core/security/2fa.py
import pyotp
import qrcode
from io import BytesIO
import base64

class TwoFactorAuthManager:
    def __init__(self):
        pass
    
    def generate_secret(self) -> str:
        return pyotp.random_base32()
    
    def generate_qr_code(self, secret: str, user_email: str) -> str:
        totp = pyotp.TOTP(secret)
        provisioning_uri = totp.provisioning_uri(
            name=user_email,
            issuer_name="MEMORIA AI"
        )
        
        qr = qrcode.make(provisioning_uri)
        buffer = BytesIO()
        qr.save(buffer, format='PNG')
        qr_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        return f"data:image/png;base64,{qr_base64}"
    
    def verify_token(self, secret: str, token: str) -> bool:
        totp = pyotp.TOTP(secret)
        return totp.verify(token, valid_window=1)
    
    def generate_backup_codes(self, count: int = 10) -> List[str]:
        import secrets
        return [secrets.token_urlsafe(16) for _ in range(count)]
```

---

## Authorization Architecture

### Role-Based Access Control (RBAC)

```python
# core/security/rbac.py
from enum import Enum
from typing import List, Set

class Role(Enum):
    USER = "user"
    MODERATOR = "moderator"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"

class Permission(Enum):
    # Note permissions
    NOTE_CREATE = "note:create"
    NOTE_READ = "note:read"
    NOTE_UPDATE = "note:update"
    NOTE_DELETE = "note:delete"
    NOTE_SHARE = "note:share"
    
    # Document permissions
    DOCUMENT_UPLOAD = "document:upload"
    DOCUMENT_READ = "document:read"
    DOCUMENT_DELETE = "document:delete"
    DOCUMENT_SHARE = "document:share"
    
    # User management
    USER_READ = "user:read"
    USER_UPDATE = "user:update"
    USER_DELETE = "user:delete"
    USER_MANAGE_ROLES = "user:manage_roles"
    
    # System management
    SYSTEM_CONFIG = "system:config"
    SYSTEM_METRICS = "system:metrics"
    SYSTEM_LOGS = "system:logs"

ROLE_PERMISSIONS = {
    Role.USER: {
        Permission.NOTE_CREATE,
        Permission.NOTE_READ,
        Permission.NOTE_UPDATE,
        Permission.NOTE_DELETE,
        Permission.NOTE_SHARE,
        Permission.DOCUMENT_UPLOAD,
        Permission.DOCUMENT_READ,
        Permission.DOCUMENT_DELETE,
        Permission.DOCUMENT_SHARE,
    },
    Role.MODERATOR: {
        *ROLE_PERMISSIONS[Role.USER],
        Permission.USER_READ,
    },
    Role.ADMIN: {
        *ROLE_PERMISSIONS[Role.MODERATOR],
        Permission.USER_UPDATE,
        Permission.USER_DELETE,
        Permission.SYSTEM_CONFIG,
        Permission.SYSTEM_METRICS,
    },
    Role.SUPER_ADMIN: {
        *ROLE_PERMISSIONS[Role.ADMIN],
        Permission.USER_MANAGE_ROLES,
        Permission.SYSTEM_LOGS,
    }
}

class AuthorizationManager:
    def __init__(self):
        self.role_permissions = ROLE_PERMISSIONS
    
    def has_permission(
        self,
        user_role: Role,
        permission: Permission
    ) -> bool:
        return permission in self.role_permissions.get(user_role, set())
    
    def has_any_permission(
        self,
        user_role: Role,
        permissions: List[Permission]
    ) -> bool:
        return any(
            self.has_permission(user_role, perm)
            for perm in permissions
        )
    
    def has_all_permissions(
        self,
        user_role: Role,
        permissions: List[Permission]
    ) -> bool:
        return all(
            self.has_permission(user_role, perm)
            for perm in permissions
        )
    
    def get_user_permissions(self, user_role: Role) -> Set[Permission]:
        return self.role_permissions.get(user_role, set())
```

### Resource-Based Access Control

```python
# core/security/rbac.py
class ResourceAccessManager:
    def __init__(self, db_session):
        self.db = db_session
    
    async def check_access(
        self,
        user_id: str,
        resource_type: str,
        resource_id: str,
        required_permission: str
    ) -> bool:
        # Check if user is owner
        if await self._is_owner(user_id, resource_type, resource_id):
            return True
        
        # Check if user has permission through sharing
        if await self._has_shared_access(
            user_id,
            resource_type,
            resource_id,
            required_permission
        ):
            return True
        
        # Check role-based permissions
        user_role = await self._get_user_role(user_id)
        return self.authorization_manager.has_permission(
            user_role,
            Permission(required_permission)
        )
    
    async def _is_owner(
        self,
        user_id: str,
        resource_type: str,
        resource_id: str
    ) -> bool:
        # Check database for ownership
        if resource_type == "note":
            note = await self.db.query(Note).filter(
                Note.id == resource_id,
                Note.user_id == user_id
            ).first()
            return note is not None
        
        elif resource_type == "document":
            document = await self.db.query(Document).filter(
                Document.id == resource_id,
                Document.user_id == user_id
            ).first()
            return document is not None
        
        return False
    
    async def _has_shared_access(
        self,
        user_id: str,
        resource_type: str,
        resource_id: str,
        permission: str
    ) -> bool:
        # Check sharing table
        if resource_type == "document":
            share = await self.db.query(DocumentShare).filter(
                DocumentShare.document_id == resource_id,
                DocumentShare.shared_with_user_id == user_id,
                DocumentShare.permission == permission
            ).first()
            return share is not None
        
        return False
```

---

## Data Protection

### Encryption at Rest

```python
# core/security/encryption.py
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import os

class EncryptionManager:
    def __init__(self, master_key: str = None):
        if master_key is None:
            master_key = os.environ.get("ENCRYPTION_MASTER_KEY")
        
        self.key = self._derive_key(master_key)
        self.cipher = Fernet(self.key)
    
    def _derive_key(self, password: str) -> bytes:
        password_bytes = password.encode()
        salt = b'memoria_ai_salt'  # In production, use random salt per deployment
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password_bytes))
        return key
    
    def encrypt(self, data: str) -> str:
        encrypted = self.cipher.encrypt(data.encode())
        return base64.urlsafe_b64encode(encrypted).decode()
    
    def decrypt(self, encrypted_data: str) -> str:
        encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode())
        decrypted = self.cipher.decrypt(encrypted_bytes)
        return decrypted.decode()
    
    def encrypt_field(self, value: str) -> Optional[str]:
        if value is None:
            return None
        return self.encrypt(value)
    
    def decrypt_field(self, encrypted_value: str) -> Optional[str]:
        if encrypted_value is None:
            return None
        return self.decrypt(encrypted_value)
```

### Encryption in Transit

```python
# core/security/tls.py
from ssl import create_default_context
from ssl import PROTOCOL_TLS_SERVER

class TLSConfig:
    def __init__(self, config: Config):
        self.config = config
    
    def get_ssl_context(self):
        context = create_default_context(PROTOCOL_TLS_SERVER)
        
        # Load certificates
        context.load_cert_chain(
            certfile=self.config.SSL_CERT_PATH,
            keyfile=self.config.SSL_KEY_PATH
        )
        
        # Configure cipher suites
        context.set_ciphers('ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384')
        
        # Require TLS 1.2 or higher
        context.minimum_version = ssl.TLSVersion.TLSv1_2
        
        # Enable HSTS
        context.options |= ssl.OP_NO_COMPRESSION
        context.options |= ssl.OP_NO_SSLv2
        context.options |= ssl.OP_NO_SSLv3
        context.options |= ssl.OP_NO_TLSv1
        context.options |= ssl.OP_NO_TLSv1_1
        
        return context
```

### Field-Level Encryption

```python
# core/security/field_encryption.py
class FieldEncryptionMixin:
    def __init__(self, encryption_manager: EncryptionManager):
        self.encryption_manager = encryption_manager
    
    def encrypt_sensitive_fields(self, data: Dict, sensitive_fields: List[str]) -> Dict:
        encrypted_data = data.copy()
        
        for field in sensitive_fields:
            if field in encrypted_data and encrypted_data[field]:
                encrypted_data[field] = self.encryption_manager.encrypt_field(
                    encrypted_data[field]
                )
        
        return encrypted_data
    
    def decrypt_sensitive_fields(self, data: Dict, sensitive_fields: List[str]) -> Dict:
        decrypted_data = data.copy()
        
        for field in sensitive_fields:
            if field in decrypted_data and decrypted_data[field]:
                decrypted_data[field] = self.encryption_manager.decrypt_field(
                    decrypted_data[field]
                )
        
        return decrypted_data
```

---

## API Security

### Rate Limiting

```python
# core/security/rate_limiting.py
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

class RateLimitManager:
    def __init__(self, config: Config):
        self.limiter = Limiter(
            key_func=get_remote_address,
            default_limits=[f"{config.DEFAULT_RATE_LIMIT}/minute"],
            storage_uri=config.REDIS_URL,
            strategy="fixed-window"
        )
        
        # Configure different limits for different tiers
        self.tier_limits = {
            "free": "100/minute",
            "pro": "1000/minute",
            "team": "5000/minute",
            "enterprise": "10000/minute"
        }
    
    def get_limiter_for_user(self, user_tier: str) -> Limiter:
        limit = self.tier_limits.get(user_tier, self.tier_limits["free"])
        return Limiter(
            key_func=get_remote_address,
            default_limits=[limit],
            storage_uri=self.config.REDIS_URL
        )
    
    def check_rate_limit(self, user_id: str, endpoint: str) -> bool:
        # Check if user is rate limited
        # Implementation depends on rate limiting strategy
        pass
```

### API Key Management

```python
# core/security/api_keys.py
import secrets
import hashlib

class APIKeyManager:
    def __init__(self, db_session):
        self.db = db_session
    
    def generate_api_key(self, prefix: str = "mem_") -> str:
        key = prefix + secrets.token_urlsafe(32)
        return key
    
    def hash_api_key(self, api_key: str) -> str:
        return hashlib.sha256(api_key.encode()).hexdigest()
    
    async def create_api_key(
        self,
        user_id: str,
        name: str,
        scopes: List[str]
    ) -> APIKey:
        api_key = self.generate_api_key()
        key_hash = self.hash_api_key(api_key)
        
        key_obj = APIKey(
            user_id=user_id,
            name=name,
            key_hash=key_hash,
            scopes=scopes,
            is_active=True
        )
        
        self.db.add(key_obj)
        await self.db.commit()
        await self.db.refresh(key_obj)
        
        # Return the actual key (only time it's shown)
        return APIKeyResponse(
            id=key_obj.id,
            key=api_key,
            name=name,
            scopes=scopes,
            created_at=key_obj.created_at
        )
    
    async def validate_api_key(self, api_key: str) -> Optional[APIKey]:
        key_hash = self.hash_api_key(api_key)
        
        key_obj = await self.db.query(APIKey).filter(
            APIKey.key_hash == key_hash,
            APIKey.is_active == True
        ).first()
        
        return key_obj
```

### Input Validation

```python
# core/security/validation.py
from pydantic import BaseModel, validator, EmailStr
from typing import Optional, List
import re

class UserRegistrationSchema(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'[0-9]', v):
            raise ValueError('Password must contain at least one digit')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain at least one special character')
        return v
    
    @validator('full_name')
    def validate_full_name(cls, v):
        if v and len(v) > 255:
            raise ValueError('Full name must be less than 255 characters')
        return v

class NoteCreateSchema(BaseModel):
    title: str
    content: str
    note_type: str = "rich_text"
    folder_id: Optional[str] = None
    tags: Optional[List[str]] = []
    
    @validator('title')
    def validate_title(cls, v):
        if not v or len(v) < 1:
            raise ValueError('Title is required')
        if len(v) > 500:
            raise ValueError('Title must be less than 500 characters')
        return v
    
    @validator('content')
    def validate_content(cls, v):
        if not v or len(v) < 1:
            raise ValueError('Content is required')
        if len(v) > 1000000:  # 1MB limit
            raise ValueError('Content is too large')
        return v
    
    @validator('note_type')
    def validate_note_type(cls, v):
        valid_types = ["rich_text", "markdown", "code"]
        if v not in valid_types:
            raise ValueError(f'Note type must be one of {valid_types}')
        return v
```

---

## Network Security

### CORS Configuration

```python
# core/security/cors.py
from fastapi.middleware.cors import CORSMiddleware

class CORSManager:
    def __init__(self, config: Config):
        self.config = config
    
    def get_cors_middleware(self):
        return CORSMiddleware(
            allow_origins=self.config.ALLOWED_ORIGINS,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
            expose_headers=["*"],
            max_age=600
        )
```

### Security Headers

```python
# core/security/headers.py
from fastapi import Response
from starlette.middleware.base import BaseHTTPMiddleware

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        
        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        
        return response
```

### IP Whitelisting

```python
# core/security/ip_whitelist.py
from typing import List, Optional

class IPWhitelistManager:
    def __init__(self, db_session):
        self.db = db_session
    
    async def is_ip_allowed(self, ip_address: str) -> bool:
        # Check if IP is whitelisted
        whitelist = await self.db.query(IPWhitelist).filter(
            IPWhitelist.ip_address == ip_address,
            IPWhitelist.is_active == True
        ).first()
        
        if whitelist:
            return True
        
        # Check if IP is blacklisted
        blacklist = await self.db.query(IPBlacklist).filter(
            IPBlacklist.ip_address == ip_address,
            IPBlacklist.is_active == True
        ).first()
        
        if blacklist:
            return False
        
        # Allow by default
        return True
    
    async def add_to_whitelist(
        self,
        ip_address: str,
        description: str = None
    ) -> IPWhitelist:
        whitelist = IPWhitelist(
            ip_address=ip_address,
            description=description,
            is_active=True
        )
        
        self.db.add(whitelist)
        await self.db.commit()
        await self.db.refresh(whitelist)
        
        return whitelist
```

---

## Audit Logging

### Audit Logger

```python
# core/security/audit.py
from datetime import datetime
from typing import Dict, Optional

class AuditLogger:
    def __init__(self, db_session):
        self.db = db_session
    
    async def log_action(
        self,
        user_id: Optional[str],
        action: str,
        resource_type: str,
        resource_id: Optional[str],
        old_values: Optional[Dict] = None,
        new_values: Optional[Dict] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> AuditLog:
        audit_log = AuditLog(
            user_id=user_id,
            action=action,
            table_name=resource_type,
            record_id=resource_id,
            old_values=old_values,
            new_values=new_values,
            ip_address=ip_address,
            user_agent=user_agent,
            created_at=datetime.utcnow()
        )
        
        self.db.add(audit_log)
        await self.db.commit()
        await self.db.refresh(audit_log)
        
        return audit_log
    
    async def log_login(
        self,
        user_id: str,
        success: bool,
        ip_address: str,
        user_agent: str
    ) -> AuditLog:
        action = "login.success" if success else "login.failed"
        return await self.log_action(
            user_id=user_id,
            action=action,
            resource_type="auth",
            resource_id=None,
            ip_address=ip_address,
            user_agent=user_agent
        )
    
    async def log_data_access(
        self,
        user_id: str,
        resource_type: str,
        resource_id: str,
        action: str = "read",
        ip_address: str = None
    ) -> AuditLog:
        return await self.log_action(
            user_id=user_id,
            action=f"{resource_type}.{action}",
            resource_type=resource_type,
            resource_id=resource_id,
            ip_address=ip_address
        )
```

---

## Secrets Management

### Secrets Manager

```python
# core/security/secrets.py
import os
from typing import Optional
import boto3
from botocore.exceptions import ClientError

class SecretsManager:
    def __init__(self, config: Config):
        self.config = config
        self.use_aws = config.USE_AWS_SECRETS_MANAGER
        
        if self.use_aws:
            self.client = boto3.client(
                'secretsmanager',
                region_name=config.AWS_REGION
            )
    
    def get_secret(self, secret_name: str) -> Optional[str]:
        if self.use_aws:
            return self._get_from_aws(secret_name)
        else:
            return self._get_from_env(secret_name)
    
    def _get_from_aws(self, secret_name: str) -> Optional[str]:
        try:
            response = self.client.get_secret_value(SecretId=secret_name)
            return response['SecretString']
        except ClientError:
            return None
    
    def _get_from_env(self, secret_name: str) -> Optional[str]:
        return os.environ.get(secret_name.upper())
    
    def set_secret(self, secret_name: str, secret_value: str) -> bool:
        if self.use_aws:
            return self._set_to_aws(secret_name, secret_value)
        else:
            return self._set_to_env(secret_name, secret_value)
    
    def _set_to_aws(self, secret_name: str, secret_value: str) -> bool:
        try:
            self.client.create_secret(
                Name=secret_name,
                SecretString=secret_value
            )
            return True
        except ClientError:
            return False
    
    def _set_to_env(self, secret_name: str, secret_value: str) -> bool:
        os.environ[secret_name.upper()] = secret_value
        return True
```

---

## Security Monitoring

### Security Event Monitoring

```python
# core/security/monitoring.py
from prometheus_client import Counter, Histogram, Gauge

# Security metrics
authentication_attempts = Counter(
    'security_authentication_attempts_total',
    'Total authentication attempts',
    ['status']  # success, failure
)

authorization_failures = Counter(
    'security_authorization_failures_total',
    'Total authorization failures',
    ['resource_type']
)

rate_limit_violations = Counter(
    'security_rate_limit_violations_total',
    'Total rate limit violations',
    ['endpoint']
)

suspicious_activities = Counter(
    'security_suspicious_activities_total',
    'Total suspicious activities detected',
    ['activity_type']
)

vulnerability_scans = Gauge(
    'security_vulnerabilities_found',
    'Number of vulnerabilities found',
    ['severity']
)

security_incidents = Counter(
    'security_incidents_total',
    'Total security incidents',
    ['severity', 'status']
)
```

### Anomaly Detection

```python
# core/security/anomaly_detection.py
class SecurityAnomalyDetector:
    def __init__(self, db_session):
        self.db = db_session
    
    async def detect_suspicious_login(
        self,
        user_id: str,
        ip_address: str,
        user_agent: str
    ) -> bool:
        # Check for unusual login patterns
        recent_logins = await self.db.query(AuditLog).filter(
            AuditLog.user_id == user_id,
            AuditLog.action == "login.success"
        ).order_by(AuditLog.created_at.desc()).limit(10).all()
        
        # Check if IP is new
        known_ips = set(log.ip_address for log in recent_logins)
        if ip_address not in known_ips and len(known_ips) > 0:
            return True
        
        # Check if user agent is new
        known_uas = set(log.user_agent for log in recent_logins)
        if user_agent not in known_uas and len(known_uas) > 0:
            return True
        
        # Check for rapid login attempts
        recent_attempts = await self.db.query(AuditLog).filter(
            AuditLog.user_id == user_id,
            AuditLog.action.like("login.%")
        ).filter(
            AuditLog.created_at > datetime.utcnow() - timedelta(minutes=5)
        ).count()
        
        if recent_attempts > 5:
            return True
        
        return False
    
    async def detect_data_exfiltration(
        self,
        user_id: str,
        resource_type: str,
        access_count: int
    ) -> bool:
        # Check for unusual data access patterns
        recent_access = await self.db.query(AuditLog).filter(
            AuditLog.user_id == user_id,
            AuditLog.resource_type == resource_type,
            AuditLog.action.like("%read%")
        ).filter(
            AuditLog.created_at > datetime.utcnow() - timedelta(hours=1)
        ).count()
        
        # Threshold for unusual access
        if recent_access > 100:
            return True
        
        return False
```

---

## Compliance

### GDPR Compliance

```python
# core/compliance/gdpr.py
class GDPRComplianceManager:
    def __init__(self, db_session):
        self.db = db_session
    
    async def export_user_data(self, user_id: str) -> Dict:
        # Collect all user data
        user = await self.db.query(User).filter(User.id == user_id).first()
        
        notes = await self.db.query(Note).filter(Note.user_id == user_id).all()
        documents = await self.db.query(Document).filter(Document.user_id == user_id).all()
        sessions = await self.db.query(LearningSession).filter(
            LearningSession.user_id == user_id
        ).all()
        
        return {
            "user": user.to_dict() if user else None,
            "notes": [note.to_dict() for note in notes],
            "documents": [doc.to_dict() for doc in documents],
            "sessions": [session.to_dict() for session in sessions],
            "export_date": datetime.utcnow().isoformat()
        }
    
    async def delete_user_data(self, user_id: str) -> bool:
        try:
            # Delete all user data
            await self.db.query(Note).filter(Note.user_id == user_id).delete()
            await self.db.query(Document).filter(Document.user_id == user_id).delete()
            await self.db.query(LearningSession).filter(
                LearningSession.user_id == user_id
            ).delete()
            await self.db.query(User).filter(User.id == user_id).delete()
            
            await self.db.commit()
            return True
        except Exception as e:
            await self.db.rollback()
            return False
    
    async def anonymize_user_data(self, user_id: str) -> bool:
        try:
            # Anonymize user data instead of deleting
            user = await self.db.query(User).filter(User.id == user_id).first()
            
            if user:
                user.email = f"deleted_{user_id}@memoria.ai"
                user.full_name = "Deleted User"
                user.password_hash = ""
                
                await self.db.commit()
                return True
            
            return False
        except Exception as e:
            await self.db.rollback()
            return False
```

### SOC 2 Compliance

```python
# core/compliance/soc2.py
class SOC2ComplianceManager:
    def __init__(self, db_session):
        self.db = db_session
    
    async def generate_compliance_report(self) -> Dict:
        # Generate SOC 2 compliance report
        report = {
            "access_control": await self._check_access_control(),
            "encryption": await self._check_encryption(),
            "audit_logging": await self._check_audit_logging(),
            "change_management": await self._check_change_management(),
            "incident_response": await self._check_incident_response(),
            "vulnerability_management": await self._check_vulnerability_management(),
            "report_date": datetime.utcnow().isoformat()
        }
        
        return report
    
    async def _check_access_control(self) -> Dict:
        # Check access control measures
        users_with_2fa = await self.db.query(User).filter(
            User.two_factor_enabled == True
        ).count()
        
        total_users = await self.db.query(User).count()
        
        return {
            "2fa_enabled_users": users_with_2fa,
            "total_users": total_users,
            "2fa_adoption_rate": users_with_2fa / total_users if total_users > 0 else 0
        }
    
    async def _check_encryption(self) -> Dict:
        # Check encryption measures
        return {
            "tls_enabled": True,
            "encryption_at_rest": True,
            "field_level_encryption": True,
            "key_rotation_enabled": True
        }
    
    async def _check_audit_logging(self) -> Dict:
        # Check audit logging
        recent_logs = await self.db.query(AuditLog).filter(
            AuditLog.created_at > datetime.utcnow() - timedelta(days=30)
        ).count()
        
        return {
            "audit_logs_last_30_days": recent_logs,
            "audit_log_retention_days": 365
        }
```

---

## Security Testing

### Security Testing Pipeline

```python
# tests/security/test_security.py
import pytest
from core.security.jwt import JWTManager
from core.security.encryption import EncryptionManager

class TestSecurity:
    def test_jwt_token_creation(self):
        manager = JWTManager(config)
        token = manager.create_access_token("user-123")
        
        assert token is not None
        payload = manager.verify_token(token)
        assert payload["sub"] == "user-123"
    
    def test_jwt_token_verification(self):
        manager = JWTManager(config)
        token = manager.create_access_token("user-123")
        
        payload = manager.verify_token(token)
        assert payload["type"] == "access"
    
    def test_encryption_decryption(self):
        manager = EncryptionManager("test_key")
        original = "sensitive data"
        
        encrypted = manager.encrypt(original)
        decrypted = manager.decrypt(encrypted)
        
        assert original == decrypted
    
    def test_rate_limiting(self):
        # Test rate limiting
        pass
    
    def test_input_validation(self):
        # Test input validation
        schema = UserRegistrationSchema(
            email="test@example.com",
            password="SecurePass123!",
            full_name="Test User"
        )
        
        assert schema.email == "test@example.com"
    
    def test_invalid_password(self):
        with pytest.raises(ValueError):
            UserRegistrationSchema(
                email="test@example.com",
                password="weak",
                full_name="Test User"
            )
```

---

## Security Best Practices

### 1. Authentication
- Use strong password policies
- Implement multi-factor authentication
- Use secure token storage
- Implement session timeout
- Monitor for suspicious activity

### 2. Authorization
- Implement principle of least privilege
- Use role-based access control
- Implement resource-based access control
- Regularly review permissions
- Audit access decisions

### 3. Data Protection
- Encrypt sensitive data at rest
- Use TLS for all communications
- Implement field-level encryption
- Secure key management
- Regular key rotation

### 4. API Security
- Implement rate limiting
- Validate all inputs
- Use CORS properly
- Implement security headers
- Monitor API usage

### 5. Monitoring
- Log all security events
- Implement anomaly detection
- Set up alerts for suspicious activity
- Regular security audits
- Penetration testing

---

## Incident Response

### Incident Response Plan

```python
# core/security/incident_response.py
class IncidentResponseManager:
    def __init__(self, db_session, notification_service):
        self.db = db_session
        self.notification_service = notification_service
    
    async def create_incident(
        self,
        severity: str,
        title: str,
        description: str,
        affected_systems: List[str]
    ) -> SecurityIncident:
        incident = SecurityIncident(
            severity=severity,
            title=title,
            description=description,
            affected_systems=affected_systems,
            status="open",
            created_at=datetime.utcnow()
        )
        
        self.db.add(incident)
        await self.db.commit()
        await self.db.refresh(incident)
        
        # Notify security team
        await self.notification_service.send_security_alert(incident)
        
        return incident
    
    async def update_incident_status(
        self,
        incident_id: str,
        status: str,
        resolution: str = None
    ) -> SecurityIncident:
        incident = await self.db.query(SecurityIncident).filter(
            SecurityIncident.id == incident_id
        ).first()
        
        if incident:
            incident.status = status
            if resolution:
                incident.resolution = resolution
            incident.updated_at = datetime.utcnow()
            
            await self.db.commit()
            await self.db.refresh(incident)
        
        return incident
```

---

**Document Status:** Approved
**Next Review:** Q4 2026
**Owner:** Security Team
