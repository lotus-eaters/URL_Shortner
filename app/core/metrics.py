"""
Performance Metrics Tracking
Monitors and tracks performance of database operations, cache, and API calls
"""

import time
import logging
from typing import Callable, Any
from functools import wraps
import asyncio

logger = logging.getLogger(__name__)


class PerformanceTracker:
    """Track performance metrics for monitoring"""
    
    def __init__(self):
        """Initialize performance tracker"""
        self.metrics = {
            'database_queries': [],
            'cache_hits': 0,
            'cache_misses': 0,
            'api_calls': []
        }
    
    def track_db_query(self, operation: str, duration_ms: float, **context):
        """
        Track database query performance
        
        Args:
            operation: Database operation (insert, find, update, delete)
            duration_ms: Query duration in milliseconds
            **context: Additional context (collection, query_type, etc.)
        """
        self.metrics['database_queries'].append({
            'operation': operation,
            'duration_ms': duration_ms,
            'timestamp': time.time(),
            **context
        })
        
        # Log slow queries
        if duration_ms > 500:
            logger.warning(
                f"Slow DB {operation}",
                extra={
                    'operation': operation,
                    'duration_ms': f"{duration_ms:.2f}",
                    **context
                }
            )
    
    def record_cache_hit(self, key: str, **context):
        """
        Record cache hit
        
        Args:
            key: Cache key
            **context: Additional context
        """
        self.metrics['cache_hits'] += 1
        logger.debug(f"Cache hit: {key}", extra={'cache_key': key, **context})
    
    def record_cache_miss(self, key: str, **context):
        """
        Record cache miss
        
        Args:
            key: Cache key
            **context: Additional context
        """
        self.metrics['cache_misses'] += 1
        logger.debug(f"Cache miss: {key}", extra={'cache_key': key, **context})
    
    def get_cache_hit_rate(self) -> float:
        """
        Calculate cache hit rate percentage
        
        Returns:
            Hit rate as percentage (0-100)
        """
        total = self.metrics['cache_hits'] + self.metrics['cache_misses']
        if total == 0:
            return 0.0
        return (self.metrics['cache_hits'] / total) * 100
    
    def get_stats(self) -> dict:
        """
        Get all performance statistics
        
        Returns:
            Dictionary with performance metrics
        """
        return {
            'cache_hit_rate': f"{self.get_cache_hit_rate():.2f}%",
            'cache_hits': self.metrics['cache_hits'],
            'cache_misses': self.metrics['cache_misses'],
            'database_queries': len(self.metrics['database_queries']),
            'api_calls': len(self.metrics['api_calls'])
        }


# Global performance tracker instance
performance_tracker = PerformanceTracker()


def track_performance(operation_name: str):
    """
    Decorator to track function performance
    
    Usage:
        @track_performance("create_user")
        async def create_user(user_data):
            ...
    
    Args:
        operation_name: Name of the operation being tracked
    """
    def decorator(func: Callable) -> Callable:
        # Handle async functions
        if asyncio.iscoroutinefunction(func):
            @wraps(func)
            async def async_wrapper(*args, **kwargs) -> Any:
                start_time = time.time()
                try:
                    result = await func(*args, **kwargs)
                    duration_ms = (time.time() - start_time) * 1000
                    
                    logger.info(
                        f"✓ {operation_name}",
                        extra={
                            'operation': operation_name,
                            'duration_ms': f"{duration_ms:.2f}",
                            'status': 'success'
                        }
                    )
                    
                    return result
                except Exception as e:
                    duration_ms = (time.time() - start_time) * 1000
                    
                    logger.error(
                        f"✗ {operation_name}",
                        extra={
                            'operation': operation_name,
                            'duration_ms': f"{duration_ms:.2f}",
                            'exception': str(e),
                            'exception_type': type(e).__name__,
                            'status': 'error'
                        }
                    )
                    
                    raise
            
            return async_wrapper
        else:
            # Handle sync functions
            @wraps(func)
            def sync_wrapper(*args, **kwargs) -> Any:
                start_time = time.time()
                try:
                    result = func(*args, **kwargs)
                    duration_ms = (time.time() - start_time) * 1000
                    
                    logger.info(
                        f"✓ {operation_name}",
                        extra={
                            'operation': operation_name,
                            'duration_ms': f"{duration_ms:.2f}",
                            'status': 'success'
                        }
                    )
                    
                    return result
                except Exception as e:
                    duration_ms = (time.time() - start_time) * 1000
                    
                    logger.error(
                        f"✗ {operation_name}",
                        extra={
                            'operation': operation_name,
                            'duration_ms': f"{duration_ms:.2f}",
                            'exception': str(e),
                            'exception_type': type(e).__name__,
                            'status': 'error'
                        }
                    )
                    
                    raise
            
            return sync_wrapper
    
    return decorator
