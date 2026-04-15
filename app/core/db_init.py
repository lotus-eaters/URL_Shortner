"""
Database Initialization and Seeding
Creates indexes and sample data for testing
"""

import logging
from app.core.config import get_settings
from app.models.models import User, URL
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from datetime import datetime
from bson import ObjectId
import hashlib

logger = logging.getLogger(__name__)


async def create_indexes(db) -> None:
    """
    Create database indexes for optimal query performance
    
    Args:
        db (AsyncIOMotorDatabase): MongoDB database instance
    """
    try:
        # Users collection indexes
        users_collection = db["users"]
        await users_collection.create_index("email", unique=True)
        await users_collection.create_index("username", unique=True)
        logger.info(" Users collection indexes created")
        
        # URLs collection indexes
        urls_collection = db["urls"]
        await urls_collection.create_index("user_id")
        await urls_collection.create_index("short_code", unique=True)
        await urls_collection.create_index("created_at")
        await urls_collection.create_index("expires_at")
        logger.info(" URLs collection indexes created")
        
    except Exception as e:
        logger.error(f" Error creating indexes: {str(e)}")
        raise


async def seed_database(db: AsyncIOMotorDatabase) -> None:
    """
    Seed database with sample data for testing
    
    Args:
        db (AsyncIOMotorDatabase): MongoDB database instance
    """
    try:
        users_collection = db["users"]
        urls_collection = db["urls"]
        
        # Check if data already exists
        user_count = await users_collection.count_documents({})
        if user_count > 0:
            logger.info("Database already seeded, skipping...")
            return
        
        # Create sample user
        sample_user = {
            "_id": ObjectId(),
            "email": "demo@example.com",
            "username": "demo_user",
            "hashed_password": "$2b$12$example_hash_here",
            "is_active": True,
            "created_at": datetime.now(datetime.timezone.utc),
            "updated_at": datetime.now(datetime.timezone.utc)
        }
        
        result = await users_collection.insert_one(sample_user)
        user_id = result.inserted_id
        logger.info(f" Sample user created: {user_id}")
        
        # Create sample URLs
        sample_urls = [
            {
                "_id": ObjectId(),
                "user_id": user_id,
                "original_url": "https://www.geeksforgeeks.org/system-design-url-shortening-service/",
                "short_code": "gfg_design",
                "click_count": 0,
                "is_active": True,
                "created_at": datetime.now(datetime.timezone.utc),
                "updated_at": datetime.now(datetime.timezone.utc),
                "expires_at": None
            },
            {
                "_id": ObjectId(),
                "user_id": user_id,
                "original_url": "https://github.com/",
                "short_code": "gh",
                "click_count": 0,
                "is_active": True,
                "created_at": datetime.now(datetime.timezone.utc),
                "updated_at": datetime.now(datetime.timezone.utc),
                "expires_at": None
            }
        ]
        
        result = await urls_collection.insert_many(sample_urls)
        logger.info(f" Sample URLs created: {len(result.inserted_ids)} documents")
        
    except Exception as e:
        logger.error(f" Error seeding database: {str(e)}")
        raise


async def drop_database(db: AsyncIOMotorDatabase) -> None:
    """
    Drop all collections (use with caution!)
    
    Args:
        db (AsyncIOMotorDatabase): MongoDB database instance
    """
    try:
        await db.drop_collection("users")
        await db.drop_collection("urls")
        logger.warning("  Database collections dropped")
    except Exception as e:
        logger.error(f" Error dropping database: {str(e)}")
        raise


async def init_database() -> None:
    """
    Initialize database with indexes and seed data
    Gets database instance from centralized manager
    """
    from app.core.database import get_mongodb
    
    logger.info(" Initializing database...")
    
    # Get database instance from centralized manager
    db = get_mongodb()
    
    # Create indexes
    await create_indexes(db)
    
    # Seed data
    await seed_database(db)
    
    logger.info(" Database initialization complete")
