"""
User Service Layer
Contains business logic for user operations
Service layer sits between controller and repository
"""

import logging
from typing import Optional, Tuple
from app.models.models import User, UserCreate
from app.repositories.user_repository import UserRepository
from app.utils.security import SecurityUtils
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class UserService:
    """Service for user business logic"""
    
    def __init__(self, db):
        """
        Initialize service with database
        
        Args:
            db (AsyncIOMotorDatabase): Motor async MongoDB database
        """
        self.repository = UserRepository(db)
    
    async def register_user(
        self,
        email: str,
        username: str,
        password: str
    ) -> Tuple[bool, str, Optional[User]]:
        """
        Register a new user
        
        Args:
            email (str): User email
            username (str): Username
            password (str): Plain password
            
        Returns:
            Tuple[bool, str, Optional[User]]: (success, message, user)
            
        Example:
            >>> success, msg, user = await service.register_user(
            ...     "john@example.com", "john", "secure123"
            ... )
            >>> success
            True
            >>> user.email
            'john@example.com'
        """
        try:
            # Validate inputs
            if not email or not username or not password:
                return False, "Email, username, and password are required", None
            
            if len(password) < 8:
                return False, "Password must be at least 8 characters", None
            
            # Check if user already exists
            existing_user = await self.repository.get_user_by_email(email)
            if existing_user:
                logger.warning(f"Registration attempt with existing email: {email}")
                return False, "Email already registered", None
            
            # Create user
            user_create = UserCreate(
                email=email,
                username=username,
                password=password,
                created_at=datetime.now(datetime.timezone.utc),
                updated_at=datetime.now(datetime.timezone.utc)
            )
            
            created_user = await self.repository.create_user(user_create)
            
            if created_user:
                logger.info(f"User registered successfully: {email}")
                return True, "User registered successfully", created_user
            else:
                return False, "Failed to create user", None
                
        except Exception as e:
            logger.error(f"Registration error: {str(e)}")
            return False, f"Registration failed: {str(e)}", None
    
    async def authenticate_user(
        self,
        email: str,
        password: str
    ) -> Tuple[bool, str, Optional[dict]]:
        """
        Authenticate user and return JWT token
        
        Args:
            email (str): User email
            password (str): Plain password
            
        Returns:
            Tuple[bool, str, Optional[dict]]: (success, message, token_data)
            
        Example:
            >>> success, msg, token_data = await service.authenticate_user(
            ...     "john@example.com", "secure123"
            ... )
            >>> success
            True
            >>> "access_token" in token_data
            True
        """
        try:
            # Find user by email
            user = await self.repository.get_user_by_email(email)
            
            if not user:
                logger.warning(f"Login attempt with non-existent email: {email}")
                return False, "Invalid email or password", None
            
            # Verify password
            if not SecurityUtils.verify_password(password, user.hashed_password):
                logger.warning(f"Failed login attempt for user: {email}")
                return False, "Invalid email or password", None
            
            # Check if user is active
            if not user.is_active:
                logger.warning(f"Login attempt by inactive user: {email}")
                return False, "User account is inactive", None
            
            # Create access token
            token = SecurityUtils.create_access_token(
                data={"user_id": str(user.id), "email": user.email}
            )
            
            logger.info(f"User authenticated successfully: {email}")
            
            return True, "Authentication successful", {
                "access_token": token,
                "token_type": "bearer",
                "user_id": str(user.id),
                "email": user.email
            }
            
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            return False, f"Authentication failed: {str(e)}", None
    
    async def get_user_profile(self, user_id: str) -> Tuple[bool, str, Optional[User]]:
        """
        Get user profile information
        
        Args:
            user_id (str): User ID
            
        Returns:
            Tuple[bool, str, Optional[User]]: (success, message, user)
        """
        try:
            user = await self.repository.get_user_by_id(user_id)
            
            if not user:
                return False, "User not found", None
            
            if not user.is_active:
                return False, "User is inactive", None
            
            return True, "User profile retrieved", user
            
        except Exception as e:
            logger.error(f"Error getting user profile: {str(e)}")
            return False, f"Error retrieving profile: {str(e)}", None
    
    async def change_password(
        self,
        user_id: str,
        old_password: str,
        new_password: str
    ) -> Tuple[bool, str]:
        """
        Change user password
        
        Args:
            user_id (str): User ID
            old_password (str): Current password
            new_password (str): New password
            
        Returns:
            Tuple[bool, str]: (success, message)
        """
        try:
            # Get user
            user = await self.repository.get_user_by_id(user_id)
            if not user:
                return False, "User not found"
            
            # Verify old password
            if not SecurityUtils.verify_password(old_password, user.hashed_password):
                logger.warning(f"Failed password change attempt for user: {user_id}")
                return False, "Current password is incorrect"
            
            # Hash new password
            new_hashed_password = SecurityUtils.hash_password(new_password)
            
            # Update password
            updated = await self.repository.update_user(
                user_id,
                {"hashed_password": new_hashed_password, "updated_at": datetime.utcnow()}
            )
            
            if updated:
                logger.info(f"Password changed for user: {user_id}")
                return True, "Password changed successfully"
            else:
                return False, "Failed to change password"
                
        except Exception as e:
            logger.error(f"Error changing password: {str(e)}")
            return False, f"Error changing password: {str(e)}"
