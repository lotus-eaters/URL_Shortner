"""
User API Routes/Controller
Handles HTTP requests and responses for user operations
"""

import logging
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import HTTPBearer
from app.core.database import get_mongodb
from app.services.user_service import UserService
from app.schemas.schemas import UserCreate, UserLogin, UserResponse, TokenResponse
from app.middleware.auth import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/auth", tags=["Authentication"])
security = HTTPBearer()


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    responses={
        201: {"description": "User registered successfully"},
        400: {"description": "Invalid input or user already exists"},
        500: {"description": "Internal server error"}
    }
)
async def register(
    user_data: UserCreate,
    db = Depends(get_mongodb)
) -> UserResponse:
    """
    Register a new user
    
    - **email**: User email address (must be unique)
    - **username**: Username for the account
    - **password**: Password (minimum 8 characters)
    
    Returns:
        UserResponse: Created user details
        
    Raises:
        HTTPException: If registration fails
    """
    try:
        service = UserService(db)
        success, message, user = await service.register_user(
            email=user_data.email,
            username=user_data.username,
            password=user_data.password
        )
        
        if not success:
            logger.warning(f"Registration failed: {message}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=message
            )
        
        logger.info(f"User registered: {user_data.email}")
        
        return UserResponse(
            id=str(user.id),
            email=user.email,
            username=user.username,
            created_at=user.created_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Login user",
    responses={
        200: {"description": "Login successful, token returned"},
        401: {"description": "Invalid credentials"},
        500: {"description": "Internal server error"}
    }
)
async def login(
    login_data: UserLogin,
    db = Depends(get_mongodb)
) -> TokenResponse:
    """
    Login user and receive JWT token
    
    - **email**: User email address
    - **password**: User password
    
    Returns:
        TokenResponse: Access token and user information
        
    Raises:
        HTTPException: If login fails
    """
    try:
        service = UserService(db)
        success, message, token_data = await service.authenticate_user(
            email=login_data.email,
            password=login_data.password
        )
        
        if not success:
            logger.warning(f"Login failed for {login_data.email}: {message}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=message
            )
        
        logger.info(f"User logged in: {login_data.email}")
        
        return TokenResponse(
            access_token=token_data["access_token"],
            token_type=token_data["token_type"],
            user=UserResponse(
                id=token_data["user_id"],
                email=token_data["email"],
                username=token_data["username"],
                created_at=token_data["created_at"]
            )
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )


@router.get(
    "/profile",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get current user profile",
    responses={
        200: {"description": "User profile retrieved"},
        401: {"description": "Not authenticated"},
        404: {"description": "User not found"}
    }
)
async def get_profile(
    current_user: dict = Depends(get_current_user),
    db = Depends(get_mongodb)
) -> UserResponse:
    """
    Get the profile of the currently authenticated user
    
    Requires: Valid JWT token in Authorization header
    
    Returns:
        UserResponse: User profile information
    """
    try:
        service = UserService(db)
        user_id = current_user["user_id"]
        
        success, message, user = await service.get_user_profile(user_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=message
            )
        
        return UserResponse(
            id=str(user.id),
            email=user.email,
            username=user.username,
            created_at=user.created_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting profile: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving profile"
        )


@router.post(
    "/change-password",
    status_code=status.HTTP_200_OK,
    summary="Change password",
    responses={
        200: {"description": "Password changed successfully"},
        401: {"description": "Not authenticated or wrong password"},
        500: {"description": "Internal server error"}
    }
)
async def change_password(
    password_data: dict,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_mongodb)
):
    """
    Change password for the current user
    
    Request body:
    - **old_password**: Current password
    - **new_password**: New password (minimum 8 characters)
    
    Requires: Valid JWT token in Authorization header
    """
    try:
        old_password = password_data.get("old_password")
        new_password = password_data.get("new_password")
        
        if not old_password or not new_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="old_password and new_password are required"
            )
        
        if len(new_password) < 8:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="New password must be at least 8 characters"
            )
        
        service = UserService(db)
        success, message = await service.change_password(
            user_id=current_user["user_id"],
            old_password=old_password,
            new_password=new_password
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=message
            )
        
        return {"message": message}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error changing password: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error changing password"
        )
