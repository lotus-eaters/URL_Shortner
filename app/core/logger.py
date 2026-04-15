"""
Logging configuration for the application
Provides structured logging with proper formatting and levels
"""

import logging
import logging.config
import os
from app.core.config import get_settings

settings = get_settings()

# Ensure logs directory exists
os.makedirs("logs", exist_ok=True)

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        },
        "detailed": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "detailed",
            "stream": "ext://sys.stdout",
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "INFO",
            "formatter": "detailed",
            "filename": "logs/app.log",
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5,
        },
        "error_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "ERROR",
            "formatter": "detailed",
            "filename": "logs/error.log",
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5,
        },
    },
    "root": {
        "level": settings.log_level,
        "handlers": ["console", "file", "error_file"],
    },
}


def setup_logging():
    """Setup logging configuration"""
    logging.config.dictConfig(LOGGING_CONFIG)
    return logging.getLogger(__name__)


class StructuredLogger:
    """Helper class for structured logging with context"""
    
    def __init__(self, name: str):
        """
        Initialize structured logger
        
        Args:
            name: Logger name (usually __name__)
        """
        self.logger = logging.getLogger(name)
    
    def info(self, message: str, **context):
        """
        Log info with context
        
        Args:
            message: Log message
            **context: Additional context data
        """
        context_str = " | ".join([f"{k}={v}" for k, v in context.items()])
        if context_str:
            self.logger.info(f"{message} | {context_str}")
        else:
            self.logger.info(message)
    
    def error(self, message: str, exception: Exception = None, **context):
        """
        Log error with context and exception info
        
        Args:
            message: Log message
            exception: Exception object
            **context: Additional context data
        """
        context_str = " | ".join([f"{k}={v}" for k, v in context.items()])
        if exception:
            message = f"{message} - {type(exception).__name__}: {str(exception)}"
        if context_str:
            self.logger.error(f"{message} | {context_str}")
        else:
            self.logger.error(message)
    
    def warning(self, message: str, **context):
        """
        Log warning with context
        
        Args:
            message: Log message
            **context: Additional context data
        """
        context_str = " | ".join([f"{k}={v}" for k, v in context.items()])
        if context_str:
            self.logger.warning(f"{message} | {context_str}")
        else:
            self.logger.warning(message)
    
    def debug(self, message: str, **context):
        """
        Log debug with context
        
        Args:
            message: Log message
            **context: Additional context data
        """
        context_str = " | ".join([f"{k}={v}" for k, v in context.items()])
        if context_str:
            self.logger.debug(f"{message} | {context_str}")
        else:
            self.logger.debug(message)
    
    def performance(self, operation: str, duration_ms: float, **context):
        """
        Log performance metric
        
        Args:
            operation: Operation name
            duration_ms: Duration in milliseconds
            **context: Additional context data
        """
        is_slow = duration_ms > 1000
        
        context['duration_ms'] = f"{duration_ms:.2f}"
        context['slow'] = is_slow
        context_str = " | ".join([f"{k}={v}" for k, v in context.items()])
        
        message = f"Performance: {operation} | {context_str}"
        
        if is_slow:
            self.logger.warning(message)
        else:
            self.logger.debug(message)


logger = setup_logging()
