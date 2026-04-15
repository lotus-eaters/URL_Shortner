"""
Security utilities for password hashing and JWT token management
Handles password encryption and JWT token generation/verification
"""

import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# Password hashing context (using bcrypt)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class SecurityUtils:
    """Utility class for security operations"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash a password using bcrypt
        
        Args:
            password (str): Plain text password
            
        Returns:
            str: Hashed password
            
        Example:
            >>> hashed = SecurityUtils.hash_password("my_secure_password")
            >>> len(hashed) > 20  # bcrypt hashes are long
            True
        """
        try:
            return pwd_context.hash(password)
        except Exception as e:
            logger.error(f"Password hashing failed: {str(e)}")
            raise
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """
        Verify a plain password against a hashed password
        
        Args:
            plain_password (str): Plain text password from user
            hashed_password (str): Hashed password from database
            
        Returns:
            bool: True if password matches, False otherwise
            
        Example:
            >>> hashed = SecurityUtils.hash_password("password123")
            >>> SecurityUtils.verify_password("password123", hashed)
            True
            >>> SecurityUtils.verify_password("wrongpassword", hashed)
            False
        """
        try:
            return pwd_context.verify(plain_password, hashed_password)
        except Exception as e:
            logger.error(f"Password verification failed: {str(e)}")
            return False
    
    @staticmethod
    def create_access_token(
        data: Dict[str, Any],
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Create a JWT access token
        
        Args:
            data (Dict[str, Any]): Data to encode in token (typically user_id, email)
            expires_delta (Optional[timedelta]): Custom expiration time
            
        Returns:
            str: Encoded JWT token
            
        Example:
            >>> token = SecurityUtils.create_access_token({"user_id": "123"})
            >>> len(token) > 20  # JWT tokens are long
            True
        """
        try:
            to_encode = data.copy()
            
            if expires_delta:
                expire = datetime.utcnow() + expires_delta
            else:
                expire = datetime.utcnow() + timedelta(
                    hours=settings.jwt_expiration_hours
                )
            
            to_encode.update({"exp": expire})
            
            encoded_jwt = jwt.encode(
                to_encode,
                settings.jwt_secret_key,
                algorithm=settings.jwt_algorithm
            )
            
            logger.debug(f"Access token created for user: {data.get('user_id')}")
            return encoded_jwt
            
        except Exception as e:
            logger.error(f"Token creation failed: {str(e)}")
            raise
    
    @staticmethod
    def verify_token(token: str) -> Optional[Dict[str, Any]]:
        """
        Verify and decode a JWT token
        
        Args:
            token (str): JWT token to verify
            
        Returns:
            Optional[Dict[str, Any]]: Decoded token payload if valid, None otherwise
            
        Example:
            >>> token = SecurityUtils.create_access_token({"user_id": "123"})
            >>> payload = SecurityUtils.verify_token(token)
            >>> payload["user_id"]
            '123'
        """
        try:
            payload = jwt.decode(
                token,
                settings.jwt_secret_key,
                algorithms=[settings.jwt_algorithm]
            )
            return payload
            
        except JWTError as e:
            logger.warning(f"Token verification failed: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error during token verification: {str(e)}")
            return None
    
    @staticmethod
    def get_user_id_from_token(token: str) -> Optional[str]:
        """
        Extract user_id from a JWT token
        
        Args:
            token (str): JWT token
            
        Returns:
            Optional[str]: User ID if token is valid, None otherwise
        """
        payload = SecurityUtils.verify_token(token)
        if payload:
            return payload.get("user_id")
        return None
