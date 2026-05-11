"""
URL API Routes/Controller
Handles HTTP requests and responses for URL operations
"""

import logging
from fastapi import APIRouter, HTTPException, status, Depends, Query
from fastapi.responses import RedirectResponse
from app.core.database import get_mongodb
from app.services.url_service import URLService
from app.schemas.schemas import (
    URLCreate, 
    URLResponse, 
    URLStatsResponse,
    URLDetailResponse,
    URLListResponse,
    MessageResponse
)
from app.middleware.auth import get_current_user
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/urls", tags=["URL Shortening"])


@router.post(
    "/shorten",
    response_model=URLResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create shortened URL",
    responses={
        201: {"description": "URL shortened successfully"},
        400: {"description": "Invalid input"},
        401: {"description": "Not authenticated"},
        500: {"description": "Internal server error"}
    }
)
async def shorten_url(
    url_data: URLCreate,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_mongodb)
) -> URLResponse:
    """
    Create a shortened URL
    
    - **original_url**: URL to shorten (must be valid HTTP/HTTPS)
    - **custom_code**: Optional custom short code (must be unique)
    - **expires_at**: Optional expiration time for the URL
    
    Returns:
        URLResponse: Shortened URL details with short_code
        
    Raises:
        HTTPException: If URL is invalid or short code already exists
        
    Example:
        Request:
        {
          "original_url": "https://www.example.com/very/long/path"
        }
        
        Response (201):
        {
          "short_code": "abc123",
          "original_url": "https://www.example.com/very/long/path",
          "created_at": "2024-01-15T10:30:00",
          "url_id": "507f1f77bcf86cd799439012"
        }
    """
    try:
        service = URLService(db)
        user_id = current_user["user_id"]
        
        # Get custom_alias from request if provided
        custom_alias = url_data.custom_alias
        
        success, message, url_data_result = await service.create_shortened_url(
            user_id=user_id,
            original_url=url_data.original_url,
            custom_alias=custom_alias,
            expires_at=url_data.expires_at
        )
        
        if not success:
            logger.warning(f"Failed to shorten URL: {message}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=message
            )
        
        logger.info(f"URL shortened for user {user_id}: {url_data_result['short_code']}")
        
        return URLResponse(
            short_code=url_data_result["short_code"],
            original_url=url_data_result["original_url"],
            created_at=url_data_result["created_at"],
            url_id=url_data_result["url_id"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error shortening URL: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to shorten URL"
        )


@router.get(
    "/{short_code}",
    status_code=status.HTTP_307_TEMPORARY_REDIRECT,
    summary="Redirect to original URL",
    responses={
        307: {"description": "Redirect to original URL"},
        404: {"description": "Short code not found"},
        410: {"description": "URL has expired"}
    }
)
async def redirect_to_url(
    short_code: str,
    db = Depends(get_mongodb)
) -> RedirectResponse:
    """
    Redirect to the original URL
    
    - **short_code**: Short code to redirect from
    
    Returns:
        HTTP 307 Temporary Redirect to original URL
        
    Raises:
        HTTPException: If short code not found or URL expired
        
    Example:
        GET /api/urls/abc123
        → Redirects to https://www.example.com/very/long/path
    """
    try:
        service = URLService(db)
        
        success, original_url, error_msg = await service.get_original_url(short_code)
        
        if not success:
            logger.warning(f"Redirect failed for {short_code}: {error_msg}")
            
            if error_msg == "URL has expired":
                raise HTTPException(
                    status_code=status.HTTP_410_GONE,
                    detail="This URL has expired"
                )
            
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Short code not found"
            )
        
        logger.info(f"Redirecting {short_code}")
        return RedirectResponse(url=original_url, status_code=307)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error redirecting: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to redirect"
        )


@router.get(
    "/user/list",
    response_model=URLListResponse,
    status_code=status.HTTP_200_OK,
    summary="List user's shortened URLs",
    responses={
        200: {"description": "URLs listed successfully"},
        401: {"description": "Not authenticated"},
        500: {"description": "Internal server error"}
    }
)
async def list_user_urls(
    current_user: dict = Depends(get_current_user),
    db = Depends(get_mongodb),
    limit: int = Query(50, ge=1, le=100),
    skip: int = Query(0, ge=0)
) -> URLListResponse:
    """
    List all shortened URLs for the current user
    
    - **limit**: Number of results to return (default: 50, max: 100)
    - **skip**: Number of results to skip (default: 0)
    
    Returns:
        URLListResponse: List of user's shortened URLs
        
    Raises:
        HTTPException: If user not authenticated
        
    Example:
        GET /api/urls/user/list?limit=50&skip=0
        
        Response:
        {
          "urls": [
            {
              "short_code": "abc123",
              "original_url": "https://www.example.com",
              "click_count": 5,
              "created_at": "2024-01-15T10:30:00",
              "is_active": true
            }
          ],
          "total": 10,
          "limit": 50,
          "skip": 0
        }
    """
    try:
        service = URLService(db)
        user_id = current_user["user_id"]
        
        success, message, data = await service.get_user_urls(
            user_id=user_id,
            limit=limit,
            skip=skip
        )
        
        if not success:
            logger.warning(f"Failed to list URLs for user {user_id}: {message}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=message
            )
        
        urls_list = data.get("urls", [])
        total = data.get("total", 0)
        
        logger.info(f"Listed {len(urls_list)} URLs for user {user_id}")
        
        return URLListResponse(
            urls=urls_list,
            total=total
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing URLs: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list URLs"
        )


@router.get(
    "/stats/{short_code}",
    response_model=URLStatsResponse,
    status_code=status.HTTP_200_OK,
    summary="Get URL statistics",
    responses={
        200: {"description": "URL statistics retrieved"},
        404: {"description": "Short code not found"}
    }
)
async def get_url_stats(
    short_code: str,
    db = Depends(get_mongodb)
) -> URLStatsResponse:
    """
    Get statistics for a shortened URL
    
    - **short_code**: Short code to get stats for
    
    Returns:
        URLStatsResponse: URL statistics including click count
        
    Raises:
        HTTPException: If short code not found
        
    Example:
        GET /api/urls/stats/abc123
        
        Response:
        {
          "short_code": "abc123",
          "original_url": "https://www.example.com",
          "click_count": 42,
          "created_at": "2024-01-15T10:30:00",
          "is_active": true
        }
    """
    try:
        service = URLService(db)
        
        success, message, stats = await service.get_url_stats(short_code)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=message
            )
        
        return URLStatsResponse(
            short_code=stats["short_code"],
            original_url=stats["original_url"],
            click_count=stats["click_count"],
            created_at=stats["created_at"],
            is_active=stats["is_active"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get statistics"
        )


@router.delete(
    "/{url_id}",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Delete shortened URL",
    responses={
        200: {"description": "URL deleted"},
        401: {"description": "Not authenticated"},
        403: {"description": "Not authorized"},
        404: {"description": "URL not found"}
    }
)
async def delete_url(
    url_id: str,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_mongodb)
) -> MessageResponse:
    """
    Delete (deactivate) a shortened URL
    
    - **url_id**: ID of the URL to delete
    
    Returns:
        MessageResponse: Confirmation message
        
    Raises:
        HTTPException: If not authorized or URL not found
        
    Example:
        DELETE /api/urls/507f1f77bcf86cd799439012
        
        Response:
        {
          "message": "URL deleted successfully"
        }
    """
    try:
        service = URLService(db)
        user_id = current_user["user_id"]
        
        success, message = await service.delete_url(url_id, user_id)
        
        if not success:
            if "Not authorized" in message:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=message
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=message
                )
        
        logger.info(f"URL deleted by user {user_id}: {url_id}")
        
        return MessageResponse(message=message)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting URL: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete URL"
        )
