"""
Authentication utilities for tenant validation and API key management.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, Dict, Any
import hashlib
import secrets
from datetime import datetime, timedelta, timezone
import os
import bcrypt
from cryptography.fernet import Fernet
import base64

# TenantStore will be imported when needed to avoid circular imports
from .logger import get_logger
from .auth_constants import AuthConstants
from .security_constants import SecurityConstants
from .regex_constants import RegexConstants
from .message_templates import MessageTemplates

# Security scheme
security = HTTPBearer()

class AuthManager:
    """Manages authentication and authorization."""
    
    def __init__(self):
        """Initialize the AuthManager."""
        # TenantStore will be imported when needed to avoid circular imports
        self.tenant_store = None
        self.logger = get_logger("auth")
        # Initialize encryption key
        self.encryption_key = self._get_or_create_encryption_key()
        self.cipher_suite = Fernet(self.encryption_key)
        self.logger.info(AuthConstants.AUTH_MANAGER_INITIALIZED)
    
    def _get_tenant_store(self):
        """Get TenantStore instance, importing it when needed."""
        if self.tenant_store is None:
            from ..store.firestore.tenants import TenantStore
            self.tenant_store = TenantStore()
        return self.tenant_store
    
    def _get_or_create_encryption_key(self) -> bytes:
        """Get or create encryption key for API keys."""
        key = os.getenv(AuthConstants.ENCRYPTION_KEY_ENV)
        if key:
            return key.encode()
        else:
            # Generate a new key (in production, store this securely)
            new_key = Fernet.generate_key()
            print(AuthConstants.ENCRYPTION_KEY_WARNING.format(new_key.decode()))
            return new_key

    def hash_password(self, password: str) -> str:
        """Hash a password using bcrypt."""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode(SecurityConstants.ENCRYPTION_ALGORITHM), salt)
        return hashed.decode(SecurityConstants.ENCRYPTION_ALGORITHM)
    
    def verify_password(self, password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        try:
            return bcrypt.checkpw(password.encode(SecurityConstants.ENCRYPTION_ALGORITHM), 
                                 hashed_password.encode(SecurityConstants.ENCRYPTION_ALGORITHM))
        except Exception as e:
            print(AuthConstants.ERROR_VERIFYING_PASSWORD.format(e))
            return False
    
    def encrypt_api_key(self, api_key: str) -> str:
        """Encrypt an API key for storage."""
        try:
            encrypted_key = self.cipher_suite.encrypt(api_key.encode())
            return base64.b64encode(encrypted_key).decode(SecurityConstants.BASE64_ENCODING)
        except Exception as e:
            print(AuthConstants.ERROR_ENCRYPTING_API_KEY.format(e))
            return api_key  # Fallback to unencrypted
    
    def decrypt_api_key(self, encrypted_api_key: str) -> str:
        """Decrypt an API key from storage."""
        try:
            encrypted_bytes = base64.b64decode(encrypted_api_key.encode(SecurityConstants.BASE64_ENCODING))
            decrypted_key = self.cipher_suite.decrypt(encrypted_bytes)
            return decrypted_key.decode(SecurityConstants.ENCRYPTION_ALGORITHM)
        except Exception as e:
            print(AuthConstants.ERROR_DECRYPTING_API_KEY.format(e))
            return encrypted_api_key  # Fallback to encrypted value
    
    def validate_tenant_credentials(self, name: str, password: str):
        """Validate tenant credentials (name and password). Returns (tenant, error_message)."""
        try:
            self.logger.debug(AuthConstants.VALIDATING_CREDENTIALS.format(name))
            
            # Find tenant by name
            tenants = self._get_tenant_store().query(filters={"name": name})
            if not tenants:
                self.logger.warning(AuthConstants.TENANT_NOT_FOUND_LOG.format(name))
                return None, "Tenant not found. Please check the tenant name or create a new tenant."
            
            tenant = tenants[0]  # Should be unique
            stored_password = tenant.get("password")
            
            if not stored_password or not self.verify_password(password, stored_password):
                self.logger.warning(AuthConstants.INVALID_PASSWORD_LOG.format(name))
                return None, "Invalid password. Please check your password and try again."
            
            self.logger.info(AuthConstants.SUCCESSFUL_LOGIN_LOG.format(name))
            return tenant, None
        except Exception as e:
            self.logger.error(AuthConstants.ERROR_VALIDATING_CREDENTIALS.format(name, e))
            return None, "An error occurred during validation."
    
    def check_tenant_name_exists(self, name: str) -> bool:
        """Check if a tenant name already exists."""
        try:
            tenants = self._get_tenant_store().query(filters={"name": name})
            return len(tenants) > 0
        except Exception as e:
            print(AuthConstants.ERROR_CHECKING_TENANT_NAME.format(e))
            return False
    def validate_tenant_api_key(self, tenant_id: str, api_key: str) -> bool:
        """Validate a tenant's API key."""
        try:
            tenant = self._get_tenant_store().get(tenant_id)
            if not tenant:
                return False
            
            stored_api_key = tenant.get("api_key")
            if not stored_api_key:
                return False
            
            # Decrypt the stored API key and compare
            decrypted_stored_key = self.decrypt_api_key(stored_api_key)
            return decrypted_stored_key == api_key
        except Exception as e:
            print(AuthConstants.ERROR_VALIDATING_API_KEY.format(e))
            return False


    def hash_api_key(self, api_key: str) -> str:
        """Encrypt an API key for storage (renamed for compatibility)."""
        return self.encrypt_api_key(api_key)

    def generate_api_key(self) -> str:
        """Generate a new API key."""
        return secrets.token_urlsafe(AuthConstants.API_KEY_LENGTH)

    def extract_tenant_from_auth(self, credentials: HTTPAuthorizationCredentials) -> str:
        """Extract tenant ID from authorization credentials."""
        token = credentials.credentials
        
        # Parse API key format (tenant_id:api_key)
        try:
            tenant_id, api_key = token.split(AuthConstants.TOKEN_SEPARATOR, 1)
            if self.validate_tenant_api_key(tenant_id, api_key):
                return tenant_id
        except ValueError:
            pass
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=AuthConstants.INVALID_AUTH_CREDENTIALS
        )

# Global auth manager instance
auth_manager = AuthManager()

async def get_current_tenant(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """Dependency to get current tenant from authorization header."""
    return auth_manager.extract_tenant_from_auth(credentials)

async def validate_tenant_access(tenant_id: str, current_tenant: str = Depends(get_current_tenant)) -> str:
    """Validate that the current tenant has access to the requested tenant."""
    if current_tenant != tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=AuthConstants.ACCESS_DENIED_INVALID_TENANT
        )
    
    # Verify tenant exists
    tenant = auth_manager.tenant_store.get(tenant_id)
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=AuthConstants.TENANT_NOT_FOUND
        )
    
    return tenant_id

async def get_tenant_info(tenant_id: str = Depends(validate_tenant_access)) -> Dict[str, Any]:
    """Get tenant information for the current tenant."""
    tenant = auth_manager.tenant_store.get(tenant_id)
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=AuthConstants.TENANT_NOT_FOUND
        )
    
    return tenant

def require_admin_access(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """Require admin access (for tenant management operations)."""
    token = credentials.credentials
    
    try:
        tenant_id, api_key = token.split(":", 1)
        if auth_manager.validate_tenant_api_key(tenant_id, api_key):
            # For now, all authenticated tenants can access admin functions
            # In production, you might want to add role-based access control
            return tenant_id
    except ValueError:
        pass
    
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=AuthConstants.INVALID_ADMIN_CREDENTIALS
        )


def validate_api_key_format(api_key: str) -> bool:
    """Validate API key format."""
    if not api_key or len(api_key) < AuthConstants.API_KEY_MIN_LENGTH:
        return False
    
    # Check for basic format requirements
    return True

def sanitize_tenant_id(tenant_id: str) -> str:
    """Sanitize tenant ID to prevent injection attacks."""
    # Remove any non-alphanumeric characters except hyphens and underscores
    import re
    sanitized = re.sub(RegexConstants.TENANT_ID_SANITIZE_PATTERN, '', tenant_id)
    return sanitized[:AuthConstants.TENANT_ID_MAX_LENGTH]  # Limit length

def log_auth_event(tenant_id: str, event_type: str, details: Dict[str, Any], 
                   ip_address: str = "", user_agent: str = ""):
    """Log authentication events."""
    logger = get_logger("auth")
    logger.log_auth_event(event_type, tenant_id, details)

class RateLimiter:
    """Simple rate limiter for API endpoints."""
    
    def __init__(self):
        self.requests = {}  # tenant_id -> list of timestamps
        self.max_requests = AuthConstants.DEFAULT_MAX_REQUESTS  # per minute
        self.window_minutes = AuthConstants.DEFAULT_WINDOW_MINUTES

    def is_rate_limited(self, tenant_id: str) -> bool:
        """Check if tenant is rate limited."""
        now = datetime.now(timezone.utc)
        window_start = now - timedelta(minutes=self.window_minutes)
        
        if tenant_id not in self.requests:
            self.requests[tenant_id] = []
        
        # Remove old requests
        self.requests[tenant_id] = [
            req_time for req_time in self.requests[tenant_id] 
            if req_time > window_start
        ]
        
        # Check if limit exceeded
        if len(self.requests[tenant_id]) >= self.max_requests:
            return True
        
        # Add current request
        self.requests[tenant_id].append(now)
        return False

# Global rate limiter
rate_limiter = RateLimiter()

def check_rate_limit(tenant_id: str):
    """Check rate limit for a tenant."""
    if rate_limiter.is_rate_limited(tenant_id):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=AuthConstants.RATE_LIMIT_EXCEEDED
        )
