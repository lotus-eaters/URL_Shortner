"""
MongoDB Models
Pydantic models for database documents
"""

from pydantic import BaseModel, Field, EmailStr, field_validator
from typing import Optional
from datetime import datetime, timezone
from bson import ObjectId


class PyObjectId(ObjectId):
    """
    Custom type for BSON ObjectId
    """
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if isinstance(v, ObjectId):
            return v
        if isinstance(v, str):
            try:
                return ObjectId(v)
            except Exception:
                raise ValueError("Invalid ObjectId")
        raise TypeError("ObjectId required")


class UserBase(BaseModel):
    """Base user model"""
    email: EmailStr
    username: str


class UserCreate(UserBase):
    """User creation model"""
    password: str


class User(UserBase):
    """User model for database"""
    # Inherited from UserBase: email, username
    id: Optional[ObjectId] = Field(alias="_id", default=None)
    hashed_password: str
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_schema_extra = {
            "example": {
                "_id": "507f1f77bcf86cd799439011",
                "email": "user@example.com",
                "username": "john_doe",
                "hashed_password": "$2b$12$...",
                "is_active": True,
                "created_at": "2024-01-15T10:30:00",
                "updated_at": "2024-01-15T10:30:00"
            }
        }


class URLBase(BaseModel):
    """Base URL model"""
    original_url: str


class URLCreate(URLBase):
    """URL creation model"""
    custom_alias: Optional[str] = None
    short_code: Optional[str] = None
    expires_at: Optional[datetime] = None


class URL(URLCreate):
    """URL model for database - inherits all creation fields plus database metadata"""
    id: Optional[ObjectId] = Field(alias="_id", default=None)
    user_id: ObjectId
    click_count: int = 0
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_schema_extra = {
            "example": {
                "_id": "507f1f77bcf86cd799439012",
                "user_id": "507f1f77bcf86cd799439011",
                "original_url": "https://www.example.com/very-long-url",
                "short_code": "abc123",
                "click_count": 42,
                "is_active": True,
                "created_at": "2024-01-15T10:30:00",
                "updated_at": "2024-01-15T10:30:00",
                "expires_at": None
            }
        }
