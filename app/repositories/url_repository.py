"""
URL Repository Layer
Handles all database operations for URLs
Repository pattern separates data access from business logic
"""

import logging
from typing import Optional, List
from bson import ObjectId
from app.models.models import URL, URLCreate
from datetime import datetime

logger = logging.getLogger(__name__)


class URLRepository:
    """Repository for URL database operations"""
    
    def __init__(self, db):
        """
        Initialize repository with database connection
        
        Args:
            db (AsyncIOMotorDatabase): Motor async MongoDB database
        """
        self.db = db
        self.collection = db["urls"]
    
    async def create_url(self, url_create: URLCreate, user_id: str) -> Optional[URL]:
        """
        Create a new shortened URL in the database
        
        Args:
            url_create (URLCreate): URL creation data (includes short_code)
            user_id (str): User ID who created the URL
            
        Returns:
            Optional[URL]: Created URL object, None if failed
            
        Example:
            >>> url_create = URLCreate(
            ...     original_url="https://example.com",
            ...     short_code="abc123"
            ... )
            >>> url = await repo.create_url(url_create, user_id)
            >>> url.short_code
            'abc123'
        """
        try:
            # Validate that short_code is provided
            if not url_create.short_code:
                raise ValueError("short_code must be provided in URLCreate")
            
            # Check if short code already exists (collision)
            existing = await self.collection.find_one({"short_code": url_create.short_code})
            if existing:
                logger.warning(f"Short code collision: {url_create.short_code}")
                return None
            
            # Create URL document
            # Ensure user_id is ObjectId
            if isinstance(user_id, str):
                user_id = ObjectId(user_id)
            
            from datetime import datetime, timezone
            now = datetime.now(timezone.utc)
            url_doc = {
                "user_id": user_id,
                "original_url": url_create.original_url,
                "short_code": url_create.short_code,
                "click_count": 0,
                "is_active": True,
                "created_at": now,
                "updated_at": now,
                "expires_at": url_create.expires_at
            }
            
            result = await self.collection.insert_one(url_doc)
            logger.info(f"URL created: {url_create.short_code} -> {url_create.original_url}")
            
            # Retrieve and return created URL
            created_url = await self.collection.find_one({"_id": result.inserted_id})
            return URL(**created_url) if created_url else None
            
        except Exception as e:
            logger.error(f"Error creating URL: {str(e)}")
            return None
    
    async def get_url_by_short_code(self, short_code: str) -> Optional[URL]:
        """
        Get URL by short code
        
        Args:
            short_code (str): Short code
            
        Returns:
            Optional[URL]: URL object if found and active, None otherwise
        """
        try:
            url_doc = await self.collection.find_one({
                "short_code": short_code,
                "is_active": True
            })
            if url_doc:
                return URL(**url_doc)
            return None
        except Exception as e:
            logger.error(f"Error fetching URL by short code: {str(e)}")
            return None
    
    async def get_url_by_id(self, url_id: str) -> Optional[URL]:
        """
        Get URL by ID
        
        Args:
            url_id (str): URL ID
            
        Returns:
            Optional[URL]: URL object if found, None otherwise
        """
        try:
            url_doc = await self.collection.find_one({"_id": ObjectId(url_id)})
            if url_doc:
                return URL(**url_doc)
            return None
        except Exception as e:
            logger.error(f"Error fetching URL by ID: {str(e)}")
            return None
    
    async def get_urls_by_user(self, user_id: str, limit: int = 100, skip: int = 0) -> List[URL]:
        """
        Get all URLs created by a user
        
        Args:
            user_id (str): User ID
            limit (int): Maximum number of results
            skip (int): Number of results to skip (for pagination)
            
        Returns:
            List[URL]: List of URL objects
        """
        try:
            cursor = self.collection.find(
                {"user_id": ObjectId(user_id), "is_active": True}
            ).limit(limit).skip(skip)
            
            urls = []
            async for url_doc in cursor:
                urls.append(URL(**url_doc))
            
            logger.debug(f"Retrieved {len(urls)} URLs for user {user_id}")
            return urls
        except Exception as e:
            logger.error(f"Error fetching URLs by user: {str(e)}")
            return []
    
    async def increment_click_count(self, short_code: str) -> bool:
        """
        Increment click count for a URL (tracks redirects)
        
        Args:
            short_code (str): Short code to increment
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            result = await self.collection.update_one(
                {"short_code": short_code},
                {"$inc": {"click_count": 1}}
            )
            
            if result.modified_count > 0:
                logger.debug(f"Click count incremented for {short_code}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error incrementing click count: {str(e)}")
            return False
    
    async def update_url(self, url_id: str, update_data: dict) -> Optional[URL]:
        """
        Update URL information
        
        Args:
            url_id (str): URL ID to update
            update_data (dict): Fields to update
            
        Returns:
            Optional[URL]: Updated URL object, None if failed
        """
        try:
            # Always update the updated_at timestamp
            from datetime import datetime, timezone
            update_data["updated_at"] = datetime.now(timezone.utc)
            
            result = await self.collection.find_one_and_update(
                {"_id": ObjectId(url_id)},
                {"$set": update_data},
                return_document=True
            )
            
            if result:
                logger.info(f"URL updated: {url_id}")
                return URL(**result)
            return None
            
        except Exception as e:
            logger.error(f"Error updating URL: {str(e)}")
            return None
    
    async def delete_url(self, url_id: str) -> bool:
        """
        Delete a URL (soft delete - mark as inactive)
        
        Args:
            url_id (str): URL ID to delete
            
        Returns:
            bool: True if deleted, False otherwise
        """
        try:
            from datetime import datetime, timezone
            result = await self.collection.find_one_and_update(
                {"_id": ObjectId(url_id)},
                {"$set": {"is_active": False, "updated_at": datetime.now(timezone.utc)}},
                return_document=True
            )
            
            if result:
                logger.info(f"URL deactivated: {url_id}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error deleting URL: {str(e)}")
            return False
    
    async def check_short_code_exists(self, short_code: str) -> bool:
        """
        Check if a short code already exists
        
        Args:
            short_code (str): Short code to check
            
        Returns:
            bool: True if exists, False otherwise
        """
        try:
            url = await self.collection.find_one({"short_code": short_code})
            return url is not None
        except Exception as e:
            logger.error(f"Error checking short code: {str(e)}")
            return False
    
    async def get_user_url_count(self, user_id: str) -> int:
        """
        Get total number of URLs created by a user
        
        Args:
            user_id (str): User ID
            
        Returns:
            int: Number of active URLs
        """
        try:
            count = await self.collection.count_documents({
                "user_id": ObjectId(user_id),
                "is_active": True
            })
            return count
        except Exception as e:
            logger.error(f"Error counting user URLs: {str(e)}")
            return 0
