"""
User Repository Layer
Handles all database operations for users
This is the Repository pattern - separates data access from business logic
"""

import logging
from typing import Optional
from bson import ObjectId
from app.models.models import User, UserCreate
from app.utils.security import SecurityUtils

logger = logging.getLogger(__name__)


class UserRepository:
    """Repository for user database operations"""
    
    def __init__(self, db):
        """
        Initialize repository with database connection
        
        Args:
            db (AsyncIOMotorDatabase): Motor async MongoDB database
        """
        self.db = db
        self.collection = db["users"]
    
    async def create_user(self, user_create: UserCreate) -> Optional[User]:
        """
        Create a new user in the database
        
        Args:
            user_create (UserCreate): User creation data
            
        Returns:
            Optional[User]: Created user object, None if failed
            
        Example:
            >>> user_create = UserCreate(email="john@example.com", username="john", password="secure123")
            >>> user = await repo.create_user(user_create)
            >>> user.email
            'john@example.com'
        """
        try:
            # Check if user already exists
            existing_user = await self.collection.find_one({"email": user_create.email})
            if existing_user:
                logger.warning(f"User already exists: {user_create.email}")
                return None
            
            # Hash password
            hashed_password = SecurityUtils.hash_password(user_create.password)
            
            # Create user document
            from datetime import datetime, timezone
            now = datetime.now(timezone.utc)
            user_doc = {
                "email": user_create.email,
                "username": user_create.username,
                "hashed_password": hashed_password,
                "is_active": True,
                "created_at": now,
                "updated_at": now,
            }
            
            result = await self.collection.insert_one(user_doc)
            logger.info(f"User created: {user_create.email}")
            
            # Retrieve and return created user
            created_user = await self.collection.find_one({"_id": result.inserted_id})
            return User(**created_user) if created_user else None
            
        except Exception as e:
            logger.error(f"Error creating user: {str(e)}")
            return None
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Get user by email address
        
        Args:
            email (str): User email
            
        Returns:
            Optional[User]: User object if found, None otherwise
        """
        try:
            user_doc = await self.collection.find_one({"email": email})
            if user_doc:
                return User(**user_doc)
            return None
        except Exception as e:
            logger.error(f"Error fetching user by email: {str(e)}")
            return None
    
    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """
        Get user by user ID
        
        Args:
            user_id (str): User ID
            
        Returns:
            Optional[User]: User object if found, None otherwise
        """
        try:
            user_doc = await self.collection.find_one({"_id": ObjectId(user_id)})
            if user_doc:
                return User(**user_doc)
            return None
        except Exception as e:
            logger.error(f"Error fetching user by ID: {str(e)}")
            return None
    
    async def update_user(self, user_id: str, update_data: dict) -> Optional[User]:
        """
        Update user information
        
        Args:
            user_id (str): User ID to update
            update_data (dict): Fields to update
            
        Returns:
            Optional[User]: Updated user object, None if failed
        """
        try:
            result = await self.collection.find_one_and_update(
                {"_id": ObjectId(user_id)},
                {"$set": update_data},
                return_document=True
            )
            
            if result:
                logger.info(f"User updated: {user_id}")
                return User(**result)
            return None
            
        except Exception as e:
            logger.error(f"Error updating user: {str(e)}")
            return None
    
    async def delete_user(self, user_id: str) -> bool:
        """
        Delete a user (soft delete - mark as inactive)
        
        Args:
            user_id (str): User ID to delete
            
        Returns:
            bool: True if deleted, False otherwise
        """
        try:
            result = await self.collection.find_one_and_update(
                {"_id": ObjectId(user_id)},
                {"$set": {"is_active": False}},
                return_document=True
            )
            
            if result:
                logger.info(f"User deactivated: {user_id}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error deleting user: {str(e)}")
            return False
    
    async def verify_user_exists(self, user_id: str) -> bool:
        """
        Check if user exists and is active
        
        Args:
            user_id (str): User ID
            
        Returns:
            bool: True if user exists and is active
        """
        try:
            user = await self.collection.find_one({
                "_id": ObjectId(user_id),
                "is_active": True
            })
            return user is not None
        except Exception as e:
            logger.error(f"Error verifying user: {str(e)}")
            return False
