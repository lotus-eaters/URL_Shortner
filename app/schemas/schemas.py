"""
Pydantic schemas for request/response validation
These are what FastAPI uses to validate and serialize data
"""

from pydantic import BaseModel, HttpUrl, Field
from datetime import datetime
from typing import Optional, List


# ============= User Schemas =============

class UserCreate(BaseModel):
    """Schema for user registration"""
    email: str = Field(..., description="User email address")
    username: str = Field(..., description="Username for the account")
    password: str = Field(..., min_length=8, description="User password (min 8 chars)")


class UserLogin(BaseModel):
    """Schema for user login"""
    email: str = Field(..., description="User email address")
    password: str = Field(..., description="User password")


class UserResponse(BaseModel):
    """Schema for user response"""
    id: str = Field(..., alias="_id", description="User ID")
    email: str
    username: str
    created_at: datetime
    
    class Config:
        populate_by_name = True


# ============= Token Schemas =============

class TokenResponse(BaseModel):
    """Schema for JWT token response"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# ============= URL Schemas =============

class URLCreate(BaseModel):
    """Schema for creating a shortened URL"""
    original_url: str = Field(..., description="Original URL to shorten")
    custom_alias: Optional[str] = Field(None, description="Optional custom short code")
    short_code: Optional[str] = Field(None, description="Generated short code")
    expires_at: Optional[datetime] = Field(None, description="Optional URL expiration time")
    
    class Config:
        json_schema_extra = {
            "example": {
                "original_url": "https://www.geeksforgeeks.org/system-design/system-design-url-shortening-service/",
                "custom_code": None,
                "expires_at": None
            }
        }


class URLResponse(BaseModel):
    """Schema for shortened URL response - used by POST /shorten"""
    short_code: str = Field(..., description="Generated short code")
    original_url: str = Field(..., description="Original URL")
    created_at: datetime = Field(..., description="Creation timestamp")
    url_id: str = Field(..., description="Unique URL identifier")
    
    class Config:
        json_schema_extra = {
            "example": {
                "short_code": "abc123",
                "original_url": "https://www.example.com/very/long/path",
                "created_at": "2024-01-15T10:30:00",
                "url_id": "507f1f77bcf86cd799439012"
            }
        }


class URLStatsResponse(BaseModel):
    """Schema for URL statistics response - used by GET /stats/{short_code}"""
    short_code: str = Field(..., description="Short code")
    original_url: str = Field(..., description="Original URL")
    click_count: int = Field(default=0, description="Number of clicks/redirects")
    created_at: datetime = Field(..., description="Creation timestamp")
    is_active: bool = Field(default=True, description="Whether URL is active")
    
    class Config:
        json_schema_extra = {
            "example": {
                "short_code": "abc123",
                "original_url": "https://www.example.com",
                "click_count": 42,
                "created_at": "2024-01-15T10:30:00",
                "is_active": True
            }
        }


class URLDetailResponse(BaseModel):
    """Schema for full URL details - used in list responses"""
    id: str = Field(..., alias="_id", description="URL ID")
    short_code: str = Field(..., description="Short code")
    original_url: str = Field(..., description="Original URL")
    user_id: str = Field(..., description="User ID who created this URL")
    click_count: int = Field(default=0, description="Number of clicks/redirects")
    created_at: datetime = Field(..., description="Creation timestamp")
    is_active: bool = Field(default=True, description="Whether URL is active")
    
    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "_id": "507f1f77bcf86cd799439012",
                "short_code": "abc123",
                "original_url": "https://www.example.com",
                "user_id": "507f1f77bcf86cd799439011",
                "click_count": 42,
                "created_at": "2024-01-15T10:30:00",
                "is_active": True
            }
        }


class URLListResponse(BaseModel):
    """Schema for URL list response - used by GET /user/list"""
    total: int = Field(..., description="Total number of URLs")
    urls: List[URLDetailResponse] = Field(..., description="List of URLs")
    
    class Config:
        json_schema_extra = {
            "example": {
                "total": 5,
                "urls": [
                    {
                        "_id": "507f1f77bcf86cd799439012",
                        "short_code": "abc123",
                        "original_url": "https://example.com/1",
                        "user_id": "507f1f77bcf86cd799439011",
                        "click_count": 10,
                        "created_at": "2024-01-15T10:30:00",
                        "is_active": True
                    }
                ]
            }
        }


class MessageResponse(BaseModel):
    """Generic message response - used by DELETE and other operations"""
    message: str = Field(..., description="Response message")
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "URL deleted successfully"
            }
        }
