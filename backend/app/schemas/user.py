# app/schemas/user.py
"""
Pydantic schemas for users.
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Dict, Any
from uuid import UUID
from datetime import datetime

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)

class UserOut(BaseModel):
    id: UUID
    email: EmailStr
    preferences: Dict[str, Any] = {}
    created_at: datetime

    class Config:
        from_attributes = True  # For SQLAlchemy ORM