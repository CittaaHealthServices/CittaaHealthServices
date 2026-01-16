"""
Security middleware for Vocalysis API
Implements healthcare-grade security measures
"""

from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from datetime import datetime, timedelta
from typing import Dict, Tuple
import hashlib
import re
import logging

logger = logging.getLogger(__name__)

# Rate limiting storage (in production, use Redis)
rate_limit_storage: Dict[str, list] = {}

# Security configuration
RATE_LIMIT_WINDOW = 60  # seconds
RATE_LIMITS = {
    "/api/v1/auth/login": (5, 60),  # 5 attempts per minute
    "/api/v1/auth/register": (3, 60),  # 3 registrations per minute
    "/api/v1/auth/forgot-password": (3, 300),  # 3 attempts per 5 minutes
    "default": (100, 60)  # 100 requests per minute for other endpoints
}

# Blocked patterns for NoSQL injection prevention
NOSQL_INJECTION_PATTERNS = [
    r'\$where',
    r'\$gt',
    r'\$lt',
    r'\$ne',
    r'\$in',
    r'\$nin',
    r'\$or',
    r'\$and',
    r'\$not',
    r'\$nor',
    r'\$exists',
    r'\$type',
    r'\$mod',
    r'\$regex',
    r'\$text',
    r'{\s*\$',
]

# XSS patterns
XSS_PATTERNS = [
    r'<script[^>]*>',
    r'javascript:',
    r'on\w+\s*=',
    r'<iframe',
    r'<object',
    r'<embed',
]


def get_client_ip(request: Request) -> str:
    """Get client IP from request, handling proxies"""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def check_rate_limit(client_ip: str, endpoint: str) -> Tuple[bool, int]:
    """
    Check if client has exceeded rate limit
    Returns (is_allowed, retry_after_seconds)
    """
    # Get rate limit for endpoint
    limit, window = RATE_LIMITS.get(endpoint, RATE_LIMITS["default"])
    
    # Create unique key
    key = f"{client_ip}:{endpoint}"
    
    now = datetime.utcnow()
    window_start = now - timedelta(seconds=window)
    
    # Clean old entries and count recent requests
    if key in rate_limit_storage:
        rate_limit_storage[key] = [
            ts for ts in rate_limit_storage[key]
            if ts > window_start
        ]
    else:
        rate_limit_storage[key] = []
    
    # Check if limit exceeded
    if len(rate_limit_storage[key]) >= limit:
        oldest = min(rate_limit_storage[key])
        retry_after = int((oldest + timedelta(seconds=window) - now).total_seconds())
        return False, max(retry_after, 1)
    
    # Add current request
    rate_limit_storage[key].append(now)
    return True, 0


def sanitize_input(value: str) -> str:
    """Sanitize input to prevent injection attacks"""
    if not isinstance(value, str):
        return value
    
    # Check for NoSQL injection patterns
    for pattern in NOSQL_INJECTION_PATTERNS:
        if re.search(pattern, value, re.IGNORECASE):
            raise ValueError(f"Potentially malicious input detected")
    
    # Check for XSS patterns
    for pattern in XSS_PATTERNS:
        if re.search(pattern, value, re.IGNORECASE):
            raise ValueError(f"Potentially malicious input detected")
    
    return value


def validate_password_strength(password: str) -> Tuple[bool, str]:
    """
    Validate password meets security requirements
    Returns (is_valid, error_message)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    
    if not re.search(r'\d', password):
        return False, "Password must contain at least one digit"
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Password must contain at least one special character"
    
    # Check for common weak passwords
    weak_passwords = ['password', '12345678', 'qwerty', 'admin123', 'letmein']
    if password.lower() in weak_passwords:
        return False, "Password is too common. Please choose a stronger password"
    
    return True, ""


class SecurityMiddleware(BaseHTTPMiddleware):
    """
    Security middleware implementing:
    - Rate limiting
    - Input sanitization
    - Security headers
    - Request logging
    """
    
    async def dispatch(self, request: Request, call_next):
        client_ip = get_client_ip(request)
        endpoint = request.url.path
        
        # Skip rate limiting for health checks
        if endpoint in ["/health", "/", "/api/docs", "/api/redoc", "/openapi.json"]:
            response = await call_next(request)
            return self.add_security_headers(response)
        
        # Check rate limit
        is_allowed, retry_after = check_rate_limit(client_ip, endpoint)
        if not is_allowed:
            logger.warning(f"Rate limit exceeded for {client_ip} on {endpoint}")
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "detail": "Too many requests. Please try again later.",
                    "retry_after": retry_after
                },
                headers={"Retry-After": str(retry_after)}
            )
        
        # Log request (for audit trail)
        logger.info(f"Request: {request.method} {endpoint} from {client_ip}")
        
        try:
            response = await call_next(request)
            return self.add_security_headers(response)
        except Exception as e:
            logger.error(f"Error processing request: {e}")
            raise
    
    def add_security_headers(self, response):
        """Add security headers to response"""
        # Prevent clickjacking
        response.headers["X-Frame-Options"] = "DENY"
        
        # Prevent MIME type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"
        
        # Enable XSS filter
        response.headers["X-XSS-Protection"] = "1; mode=block"
        
        # Strict Transport Security (HTTPS only)
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        # Referrer Policy
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Permissions Policy
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(self), camera=()"
        
        return response


def hash_sensitive_data(data: str) -> str:
    """Hash sensitive data for logging (never log raw sensitive data)"""
    return hashlib.sha256(data.encode()).hexdigest()[:16]


def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_phone(phone: str) -> bool:
    """Validate phone number format (Indian format)"""
    if not phone:
        return True  # Phone is optional
    pattern = r'^(\+91)?[6-9]\d{9}$'
    return bool(re.match(pattern, phone.replace(" ", "").replace("-", "")))
