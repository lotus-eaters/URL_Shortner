"""
Database connection and initialization module
Centralized manager for MongoDB and Redis connections
Handles connection lifecycle and provides dependency injection
"""

import logging
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from redis.asyncio import Redis
from typing import Optional
from contextlib import asynccontextmanager

from app.core.config import get_settings

logger = logging.getLogger(__name__)

# Global database instances
mongodb_client: Optional[AsyncIOMotorClient] = None
mongodb_db = None
redis_client: Optional[Redis] = None


async def connect_db():
    """
    Connect to MongoDB and Redis
    Called on application startup
    
    Raises:
        Exception: If connection to either database fails
    """
    global mongodb_client, mongodb_db, redis_client
    
    settings = get_settings()
    
    try:
        # ============ MongoDB Connection ============
        logger.info(f"Connecting to MongoDB: {settings.mongodb_url}")
        mongodb_client = AsyncIOMotorClient(settings.mongodb_url)
        
        # Verify MongoDB connection
        await mongodb_client.admin.command("ping")
        logger.info(" MongoDB connected successfully")
        
        # Get database instance
        mongodb_db = mongodb_client[settings.mongodb_db_name]
        logger.info(f" Database selected: {settings.mongodb_db_name}")
        
        # ============ Redis Connection ============
        logger.info(f" Connecting to Redis: {settings.redis_url}")
        redis_client = Redis.from_url(
            settings.redis_url,
            encoding="utf8",
            decode_responses=True,
            socket_connect_timeout=5,
            socket_keepalive=True,
            health_check_interval=30
        )
        
        # Verify Redis connection
        await redis_client.ping()
        logger.info("Redis connected successfully")
        
        logger.info(" All database connections established")
        
    except Exception as e:
        logger.error(f" Database connection failed: {str(e)}")
        # Cleanup partial connections
        await close_db()
        raise


async def close_db():
    """
    Close database connections gracefully
    Called on application shutdown
    
    Logs warnings but doesn't raise exceptions
    """
    global mongodb_client, redis_client
    
    try:
        if mongodb_client:
            mongodb_client.close()
            logger.info(" MongoDB connection closed")
        
        if redis_client:
            await redis_client.close()
            logger.info(" Redis connection closed")
            
    except Exception as e:
        logger.error(f"  Error closing database connections: {str(e)}")


def get_mongodb():
    """
    Get MongoDB database instance
    
    Returns:
        Motor async database instance
        
    Raises:
        RuntimeError: If database not initialized
    """
    if mongodb_db is None:
        raise RuntimeError("MongoDB not initialized. Call connect_db() first.")
    return mongodb_db


def get_redis() -> Redis:
    """
    Get Redis client instance
    
    Returns:
        Redis: Redis async client instance
        
    Raises:
        RuntimeError: If Redis not initialized
    """
    if redis_client is None:
        raise RuntimeError("Redis not initialized. Call connect_db() first.")
    return redis_client


# ============ Cache Operations (kept in main database.py) ============

async def set_cache(key: str, value: str, ttl: int = 3600) -> None:
    """
    Set value in Redis cache with TTL
    
    Args:
        key (str): Cache key
        value (str): Value to cache
        ttl (int): Time to live in seconds (default: 1 hour)
    """
    try:
        client = get_redis()
        await client.setex(key, ttl, value)
        logger.debug(f" Cache set: {key}")
    except Exception as e:
        logger.warning(f" Cache set failed for {key}: {str(e)}")


async def get_cache(key: str) -> Optional[str]:
    """
    Get value from Redis cache
    
    Args:
        key (str): Cache key
        
    Returns:
        Optional[str]: Cached value or None if not found/expired
    """
    try:
        client = get_redis()
        value = await client.get(key)
        if value:
            logger.debug(f" Cache hit: {key}")
        else:
            logger.debug(f" Cache miss: {key}")
        return value
    except Exception as e:
        logger.warning(f"  Cache get failed for {key}: {str(e)}")
        return None


async def delete_cache(key: str) -> None:
    """
    Delete value from Redis cache
    
    Args:
        key (str): Cache key
    """
    try:
        client = get_redis()
        await client.delete(key)
        logger.debug(f"Cache deleted: {key}")
    except Exception as e:
        logger.warning(f"  Cache delete failed for {key}: {str(e)}")


async def clear_cache(pattern: str = "*") -> None:
    """
    Clear multiple cache keys matching pattern
    
    Args:
        pattern (str): Key pattern (e.g., "url:*" or "*")
    """
    try:
        client = get_redis()
        keys = await client.keys(pattern)
        if keys:
            await client.delete(*keys)
            logger.info(f" Cleared {len(keys)} cache entries matching '{pattern}'")
        else:
            logger.debug(f"No cache entries found matching '{pattern}'")
    except Exception as e:
        logger.warning(f" Cache clear failed for pattern '{pattern}': {str(e)}")
