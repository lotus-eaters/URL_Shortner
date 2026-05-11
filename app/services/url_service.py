"""
URL Service Layer
Contains business logic for URL shortening operations
Service layer sits between controller and repository
"""

import logging
from typing import Optional, Tuple, List
from app.models.models import URL, URLCreate
from app.repositories.url_repository import URLRepository
from app.utils.url_utils import URLUtils
from app.core.database import set_cache, get_cache, delete_cache
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# Default URL expiration time (in days)
DEFAULT_URL_EXPIRATION_DAYS = 30


class URLService:
    """Service for URL business logic"""
    
    def __init__(self, db):
        """
        Initialize service with database
        
        Args:
            db: Motor async MongoDB database
        """
        self.repository = URLRepository(db)
    
    async def create_shortened_url(
        self,
        user_id: str,
        original_url: str,
        custom_alias: Optional[str] = None,
        expires_at: Optional[datetime] = None
    ) -> Tuple[bool, str, Optional[dict]]:
        """
        Create a shortened URL
        
        Args:
            user_id (str): User ID
            original_url (str): Original URL to shorten
            custom_alias (str): Optional custom short code
            expires_at (datetime): Optional expiration time
            
        Returns:
            Tuple[bool, str, Optional[dict]]: (success, message, url_data)
            
        Example:
            >>> success, msg, data = await service.create_shortened_url(
            ...     user_id="123",
            ...     original_url="https://www.example.com"
            ... )
            >>> success
            True
            >>> "short_code" in data
            True
        """
        try:
            # Validate URL
            if not URLUtils.validate_url(original_url):
                logger.warning(f"Invalid URL: {original_url}")
                return False, "Invalid URL format", None
            
            # Normalize URL for consistency
            normalized_url = URLUtils.normalize_url(original_url)
            
            # Generate short code
            short_code = URLUtils.generate_short_code_md5(
                normalized_url,
                custom_alias
            )
            
            # Check for collision (another URL with same short code)
            collision_count = 0
            max_retries = 5
            
            while await self.repository.check_short_code_exists(short_code):
                collision_count += 1
                if collision_count > max_retries:
                    logger.error(f"Too many collisions for {original_url}")
                    return False, "Could not generate unique short code", None
                
                # Generate fallback short code
                short_code = URLUtils.generate_fallback_short_code(length=7)
                logger.warning(f"Collision detected, retrying with: {short_code}")
            
            # Set default expiration if not provided
            if expires_at is None:
                from datetime import datetime, timezone
                expires_at = datetime.now(timezone.utc) + timedelta(days=DEFAULT_URL_EXPIRATION_DAYS)
                logger.debug(f"No expiration provided, setting default: {expires_at}")
            
            # Create URL in database
            url_create = URLCreate(
                original_url=normalized_url,
                custom_alias=custom_alias,
                short_code=short_code,
                expires_at=expires_at
            )
            
            created_url = await self.repository.create_url(
                url_create,
                user_id
            )
            
            if not created_url:
                return False, "Failed to create URL", None
            
            # Cache the URL for quick access
            cache_key = f"url:{short_code}"
            await set_cache(cache_key, normalized_url, ttl=86400)  # 24 hours
            
            logger.info(f"URL created: {short_code} for user {user_id}")
            
            return True, "URL shortened successfully", {
                "short_code": short_code,
                "original_url": normalized_url,
                "created_at": created_url.created_at,
                "url_id": str(created_url.id) if created_url.id else None
            }
            
        except Exception as e:
            logger.error(f"Error creating shortened URL: {str(e)}")
            return False, f"Error: {str(e)}", None
    
    async def get_original_url(self, short_code: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Get original URL from short code (with caching)
        
        Args:
            short_code (str): Short code
            
        Returns:
            Tuple[bool, Optional[str], Optional[str]]: (success, original_url, error_message)
            
        Example:
            >>> success, url, msg = await service.get_original_url("abc123")
            >>> success
            True
            >>> url
            'https://www.example.com'
        """
        try:
            # Check cache first
            cache_key = f"url:{short_code}"
            cached_url = await get_cache(cache_key)
            
            if cached_url:
                logger.debug(f"URL found in cache: {short_code}")
                # Increment click count asynchronously (fire and forget)
                await self.repository.increment_click_count(short_code)
                return True, cached_url, None
            
            # Check database
            url = await self.repository.get_url_by_short_code(short_code)
            
            if not url:
                logger.warning(f"URL not found: {short_code}")
                return False, None, "URL not found"
            
            # Check if expired
            if URLUtils.is_url_expired(url.expires_at):
                logger.warning(f"URL expired: {short_code}")
                return False, None, "URL has expired"
            
            # Cache the URL
            await set_cache(cache_key, url.original_url, ttl=86400)
            
            # Increment click count
            await self.repository.increment_click_count(short_code)
            
            logger.info(f"URL retrieved: {short_code}")
            return True, url.original_url, None
            
        except Exception as e:
            logger.error(f"Error getting original URL: {str(e)}")
            return False, None, f"Error: {str(e)}"
    
    async def get_url_details(self, url_id: str, user_id: str) -> Tuple[bool, str, Optional[dict]]:
        """
        Get URL details (for user's own URLs)
        
        Args:
            url_id (str): URL ID
            user_id (str): User ID (for authorization)
            
        Returns:
            Tuple[bool, str, Optional[dict]]: (success, message, url_data)
        """
        try:
            url = await self.repository.get_url_by_id(url_id)
            
            if not url:
                return False, "URL not found", None
            
            # Check authorization
            if str(url.user_id) != user_id:
                logger.warning(f"Unauthorized access to URL {url_id} by user {user_id}")
                return False, "Not authorized to access this URL", None
            
            return True, "URL details retrieved", {
                "short_code": url.short_code,
                "original_url": url.original_url,
                "click_count": url.click_count,
                "created_at": url.created_at,
                "is_active": url.is_active
            }
            
        except Exception as e:
            logger.error(f"Error getting URL details: {str(e)}")
            return False, f"Error: {str(e)}", None
    
    async def get_user_urls(
        self,
        user_id: str,
        limit: int = 50,
        skip: int = 0
    ) -> Tuple[bool, str, Optional[dict]]:
        """
        Get all URLs for a user
        
        Args:
            user_id (str): User ID
            limit (int): Max results
            skip (int): Pagination skip
            
        Returns:
            Tuple[bool, str, Optional[dict]]: (success, message, data)
        """
        try:
            urls = await self.repository.get_urls_by_user(user_id, limit, skip)
            total_count = await self.repository.get_user_url_count(user_id)
            
            url_list = [
                {
                    "short_code": url.short_code,
                    "original_url": url.original_url,
                    "click_count": url.click_count,
                    "created_at": url.created_at
                }
                for url in urls
            ]
            
            return True, "URLs retrieved", {
                "total": total_count,
                "urls": url_list,
                "limit": limit,
                "skip": skip
            }
            
        except Exception as e:
            logger.error(f"Error getting user URLs: {str(e)}")
            return False, f"Error: {str(e)}", None
    
    async def delete_url(self, url_id: str, user_id: str) -> Tuple[bool, str]:
        """
        Delete a URL (soft delete)
        
        Args:
            url_id (str): URL ID to delete
            user_id (str): User ID (for authorization)
            
        Returns:
            Tuple[bool, str]: (success, message)
        """
        try:
            url = await self.repository.get_url_by_id(url_id)
            
            if not url:
                return False, "URL not found"
            
            # Check authorization
            if str(url.user_id) != user_id:
                logger.warning(f"Unauthorized delete attempt by user {user_id}")
                return False, "Not authorized to delete this URL"
            
            # Delete from cache
            cache_key = f"url:{url.short_code}"
            await delete_cache(cache_key)
            
            # Soft delete from database
            if await self.repository.delete_url(url_id):
                logger.info(f"URL deleted: {url_id}")
                return True, "URL deleted successfully"
            
            return False, "Failed to delete URL"
            
        except Exception as e:
            logger.error(f"Error deleting URL: {str(e)}")
            return False, f"Error: {str(e)}"
    
    async def get_url_stats(self, short_code: str) -> Tuple[bool, str, Optional[dict]]:
        """
        Get URL statistics
        
        Args:
            short_code (str): Short code
            
        Returns:
            Tuple[bool, str, Optional[dict]]: (success, message, stats)
        """
        try:
            url = await self.repository.get_url_by_short_code(short_code)
            
            if not url:
                return False, "URL not found", None
            
            return True, "Stats retrieved", {
                "short_code": short_code,
                "original_url": url.original_url,
                "click_count": url.click_count,
                "created_at": url.created_at,
                "is_active": url.is_active
            }
            
        except Exception as e:
            logger.error(f"Error getting URL stats: {str(e)}")
            return False, f"Error: {str(e)}", None
    
    async def get_user_urls(
        self,
        user_id: str,
        limit: int = 50,
        skip: int = 0
    ) -> Tuple[bool, str, Optional[dict]]:
        """
        Get all shortened URLs for a user
        
        Args:
            user_id (str): User ID
            limit (int): Number of results to return
            skip (int): Number of results to skip (for pagination)
            
        Returns:
            Tuple[bool, str, Optional[dict]]: (success, message, data_dict)
        """
        try:
            urls = await self.repository.get_urls_by_user_id(
                user_id=user_id,
                limit=limit,
                skip=skip
            )
            
            if not urls:
                return True, "No URLs found", {"urls": [], "total": 0}
            
            urls_list = [
                {
                    "_id": str(url.id),
                    "short_code": url.short_code,
                    "original_url": url.original_url,
                    "user_id": str(url.user_id),
                    "click_count": url.click_count,
                    "created_at": url.created_at,
                    "is_active": url.is_active
                }
                for url in urls
            ]
            
            return True, "URLs retrieved", {"urls": urls_list, "total": len(urls_list)}
            
        except Exception as e:
            logger.error(f"Error getting user URLs: {str(e)}")
            return False, f"Error: {str(e)}", None