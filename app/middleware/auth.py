"""
Authentication middleware for JWT verification
Middleware to check and validate JWT tokens in requests
"""

import logging
from typing import Optional
from fastapi import HTTPException, status, Request, Depends
from fastapi.security import HTTPBearer
from app.utils.security import SecurityUtils

logger = logging.getLogger(__name__)

# HTTP Bearer scheme for JWT
security = HTTPBearer()


async def get_current_user(credentials = Depends(HTTPBearer())) -> dict:
    """
    Dependency to extract and verify current user from JWT token
    
    Args:
        credentials: Bearer token from request
        
    Returns:
        dict: User data from token payload
        
    Raises:
        HTTPException: If token is invalid or expired
        
    Example:
        In a route:
        @app.get("/profile")
        async def get_profile(current_user: dict = Depends(get_current_user)):
            return current_user
    """
    token = credentials.credentials
    
    payload = SecurityUtils.verify_token(token)
    
    if payload is None:
        logger.warning(f"Invalid token attempted from IP")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = payload.get("user_id")
    if not user_id:
        logger.warning("Token missing user_id")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return {"user_id": user_id, "payload": payload}


async def get_current_user_optional(
    request: Request
) -> Optional[dict]:
    """
    Optional dependency for routes that work with or without authentication
    
    Args:
        request (Request): FastAPI request object
        
    Returns:
        Optional[dict]: User data if token is valid, None otherwise
    """
    auth_header = request.headers.get("Authorization")
    
    if not auth_header or not auth_header.startswith("Bearer "):
        return None
    
    token = auth_header.replace("Bearer ", "")
    payload = SecurityUtils.verify_token(token)
    
    if payload is None:
        return None
    
    user_id = payload.get("user_id")
    if user_id:
        return {"user_id": user_id, "payload": payload}
    
    return None
