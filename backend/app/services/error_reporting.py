"""
Error Reporting Service for Vocalysis
Integrates with Sentry for production error tracking
"""

import os
import logging
from typing import Optional, Dict, Any
from functools import wraps
import traceback

logger = logging.getLogger(__name__)

# Sentry configuration
SENTRY_DSN = os.getenv("SENTRY_DSN", "")
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

# Initialize Sentry if DSN is provided
_sentry_initialized = False

def init_sentry():
    """Initialize Sentry SDK for error reporting"""
    global _sentry_initialized
    
    if _sentry_initialized:
        return
    
    if not SENTRY_DSN:
        logger.info("Sentry DSN not configured, error reporting disabled")
        return
    
    try:
        import sentry_sdk
        from sentry_sdk.integrations.fastapi import FastApiIntegration
        from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
        from sentry_sdk.integrations.logging import LoggingIntegration
        
        sentry_sdk.init(
            dsn=SENTRY_DSN,
            environment=ENVIRONMENT,
            traces_sample_rate=0.1,  # 10% of transactions for performance monitoring
            profiles_sample_rate=0.1,  # 10% of transactions for profiling
            integrations=[
                FastApiIntegration(transaction_style="endpoint"),
                SqlalchemyIntegration(),
                LoggingIntegration(
                    level=logging.INFO,
                    event_level=logging.ERROR
                ),
            ],
            # Filter out sensitive data
            before_send=filter_sensitive_data,
            # Set release version
            release=f"vocalysis-backend@1.0.0",
            # Additional context
            server_name="vocalysis-api",
        )
        
        _sentry_initialized = True
        logger.info(f"Sentry initialized for environment: {ENVIRONMENT}")
        
    except ImportError:
        logger.warning("Sentry SDK not installed, error reporting disabled")
    except Exception as e:
        logger.error(f"Failed to initialize Sentry: {e}")


def filter_sensitive_data(event: Dict, hint: Dict) -> Optional[Dict]:
    """Filter sensitive data before sending to Sentry"""
    
    # Remove sensitive headers
    if "request" in event and "headers" in event["request"]:
        headers = event["request"]["headers"]
        sensitive_headers = ["authorization", "cookie", "x-api-key"]
        for header in sensitive_headers:
            if header in headers:
                headers[header] = "[FILTERED]"
    
    # Remove sensitive data from request body
    if "request" in event and "data" in event["request"]:
        data = event["request"]["data"]
        if isinstance(data, dict):
            sensitive_fields = ["password", "token", "secret", "api_key", "credit_card"]
            for field in sensitive_fields:
                if field in data:
                    data[field] = "[FILTERED]"
    
    return event


def capture_exception(error: Exception, context: Optional[Dict[str, Any]] = None):
    """Capture and report an exception to Sentry"""
    try:
        import sentry_sdk
        
        if context:
            with sentry_sdk.push_scope() as scope:
                for key, value in context.items():
                    scope.set_extra(key, value)
                sentry_sdk.capture_exception(error)
        else:
            sentry_sdk.capture_exception(error)
            
    except ImportError:
        # Sentry not installed, log locally
        logger.error(f"Exception: {error}\n{traceback.format_exc()}")
    except Exception as e:
        logger.error(f"Failed to capture exception: {e}")


def capture_message(message: str, level: str = "info", context: Optional[Dict[str, Any]] = None):
    """Capture and report a message to Sentry"""
    try:
        import sentry_sdk
        
        if context:
            with sentry_sdk.push_scope() as scope:
                for key, value in context.items():
                    scope.set_extra(key, value)
                sentry_sdk.capture_message(message, level=level)
        else:
            sentry_sdk.capture_message(message, level=level)
            
    except ImportError:
        # Sentry not installed, log locally
        log_func = getattr(logger, level, logger.info)
        log_func(message)
    except Exception as e:
        logger.error(f"Failed to capture message: {e}")


def set_user_context(user_id: str, email: Optional[str] = None, role: Optional[str] = None):
    """Set user context for Sentry"""
    try:
        import sentry_sdk
        
        sentry_sdk.set_user({
            "id": user_id,
            "email": email,
            "role": role
        })
    except ImportError:
        pass
    except Exception as e:
        logger.error(f"Failed to set user context: {e}")


def add_breadcrumb(message: str, category: str = "custom", level: str = "info", data: Optional[Dict] = None):
    """Add a breadcrumb for debugging"""
    try:
        import sentry_sdk
        
        sentry_sdk.add_breadcrumb(
            message=message,
            category=category,
            level=level,
            data=data or {}
        )
    except ImportError:
        pass
    except Exception as e:
        logger.error(f"Failed to add breadcrumb: {e}")


def error_handler(func):
    """Decorator to automatically capture exceptions"""
    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            capture_exception(e, context={
                "function": func.__name__,
                "args": str(args)[:200],
                "kwargs": str(kwargs)[:200]
            })
            raise
    
    @wraps(func)
    def sync_wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            capture_exception(e, context={
                "function": func.__name__,
                "args": str(args)[:200],
                "kwargs": str(kwargs)[:200]
            })
            raise
    
    import asyncio
    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    return sync_wrapper


class ErrorReporter:
    """Error reporting utility class"""
    
    def __init__(self):
        init_sentry()
    
    def report_error(self, error: Exception, context: Optional[Dict] = None):
        """Report an error"""
        capture_exception(error, context)
    
    def report_warning(self, message: str, context: Optional[Dict] = None):
        """Report a warning"""
        capture_message(message, level="warning", context=context)
    
    def report_info(self, message: str, context: Optional[Dict] = None):
        """Report an info message"""
        capture_message(message, level="info", context=context)
    
    def set_user(self, user_id: str, email: Optional[str] = None, role: Optional[str] = None):
        """Set user context"""
        set_user_context(user_id, email, role)
    
    def add_context(self, message: str, category: str = "custom", data: Optional[Dict] = None):
        """Add context breadcrumb"""
        add_breadcrumb(message, category, data=data)


# Global error reporter instance
error_reporter = ErrorReporter()
