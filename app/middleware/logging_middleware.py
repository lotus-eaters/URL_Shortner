"""
Logging Middleware
Tracks HTTP requests, responses, and performance metrics
"""

import time
import uuid
import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for logging HTTP requests and responses
    
    Features:
    - Generates unique request ID for tracking
    - Logs incoming requests with method, path, client IP
    - Tracks response time and status code
    - Logs errors with context
    - Adds request ID to response headers
    """
    
    async def dispatch(self, request: Request, call_next) -> Response:
        """
        Process request and response with logging
        
        Args:
            request: HTTP request
            call_next: Next middleware in chain
            
        Returns:
            Response with added request ID header
        """
        
        # Generate unique request ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # Extract request info
        method = request.method
        path = request.url.path
        query = request.url.query
        client_ip = request.client.host if request.client else "unknown"
        
        # Start timer
        start_time = time.time()
        
        # Log incoming request
        logger.info(
            f"→ {method} {path}",
            extra={
                'request_id': request_id,
                'method': method,
                'path': path,
                'query': query if query else 'none',
                'client_ip': client_ip,
                'event': 'request_start'
            }
        )
        
        try:
            # Process request
            response = await call_next(request)
            
            # Calculate response time
            duration_ms = (time.time() - start_time) * 1000
            
            # Determine log level based on status code
            if response.status_code >= 500:
                log_func = logger.error
            elif response.status_code >= 400:
                log_func = logger.warning
            else:
                log_func = logger.info
            
            # Log response
            log_func(
                f"← {response.status_code} {method} {path}",
                extra={
                    'request_id': request_id,
                    'method': method,
                    'path': path,
                    'status_code': response.status_code,
                    'duration_ms': f"{duration_ms:.2f}",
                    'slow': duration_ms > 1000,
                    'event': 'request_complete'
                }
            )
            
            # Add request ID to response headers for tracing
            response.headers["X-Request-ID"] = request_id
            
            return response
            
        except Exception as e:
            # Calculate error time
            duration_ms = (time.time() - start_time) * 1000
            
            # Log error
            logger.error(
                f"✗ {method} {path} failed: {type(e).__name__}",
                extra={
                    'request_id': request_id,
                    'method': method,
                    'path': path,
                    'duration_ms': f"{duration_ms:.2f}",
                    'exception': str(e),
                    'exception_type': type(e).__name__,
                    'event': 'request_error'
                }
            )
            
            raise
