"""
User Pydantic Schemas
Request/Response validation for user endpoints
"""
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List, Dict
from datetime import datetime
from enum import Enum


class PriceSensitivity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class UserRegister(BaseModel):
    """Schema for user registration"""
    email: EmailStr
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters")
    full_name: str = Field(..., min_length=2, max_length=255)
    profession: Optional[str] = None
    income: Optional[float] = Field(None, ge=0)
    price_sensitivity: PriceSensitivity = PriceSensitivity.MEDIUM
    preferred_categories: Optional[List[str]] = []
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        return v


class UserLogin(BaseModel):
    """Schema for user login"""
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    """Schema for updating user profile"""
    full_name: Optional[str] = None
    profession: Optional[str] = None
    income: Optional[float] = Field(None, ge=0)
    price_sensitivity: Optional[PriceSensitivity] = None
    last_payday: Optional[datetime] = None
    preferred_categories: Optional[List[str]] = None
    financial_goals: Optional[Dict] = None


class UserResponse(BaseModel):
    """Schema for user response"""
    user_id: str
    email: str
    full_name: str
    profession: Optional[str]
    income: Optional[float]
    price_sensitivity: str
    last_payday: Optional[datetime]
    preferred_categories: Optional[List[str]]
    financial_goals: Optional[Dict]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """Schema for authentication token response"""
    access_token: str
    token_type: str = "bearer"
    user_id: str
    expires_in: int  # seconds


class UserProfileVector(BaseModel):
    """
    Schema for user profile embedding in Qdrant.
    Aggregates preferences, purchase history, financial context.
    """
    user_id: str
    preferred_categories: List[str]
    financial_goals: Optional[Dict]
    price_sensitivity: str
    recent_interactions: Optional[List[str]] = []  # Recent product IDs
    
    class Config:
        from_attributes = True