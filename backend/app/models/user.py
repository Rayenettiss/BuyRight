"""
User Model - PostgreSQL
Stores user profile, financial context, and preferences
Hackathon: Financial context includes income, profession, goals, price sensitivity
"""
from sqlalchemy import Column, String, Float, DateTime, JSON, Text, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import ARRAY
from datetime import datetime
import enum
from app.database import Base


class PriceSensitivity(str, enum.Enum):
    """User's price sensitivity level"""
    LOW = "low"  # Premium buyer, less price-conscious
    MEDIUM = "medium"  # Balanced
    HIGH = "high"  # Budget-conscious, very price-sensitive


class User(Base):
    """
    User table - stores authenticated users and their financial context.
    
    Hackathon Requirements:
    - Financial context: income, profession, price sensitivity
    - Preferences: categories, goals (saving, specific purchases)
    - Temporal: last_payday for post-payday timing recommendations
    """
    __tablename__ = "users"
    
    # Primary Key - anonymized in logs
    user_id = Column(String(36), primary_key=True, index=True)
    
    # Authentication
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    
    # Personal Information
    full_name = Column(String(255), nullable=False)
    profession = Column(String(100))  # For profession-based recommendations (e.g., "developer")
    
    # Financial Context (Hackathon: Core Feature)
    income = Column(Float)  # Monthly income - encrypted in sensitive scenarios
    price_sensitivity = Column(SQLEnum(PriceSensitivity), default=PriceSensitivity.MEDIUM)
    last_payday = Column(DateTime)  # For post-payday timing recs
    
    # Preferences
    preferred_categories = Column(ARRAY(String))  # ["Electronics", "Gaming", "Software"]
    financial_goals = Column(JSON)  # {"saving_target": 500, "purpose": "emergency fund"}
    
    # User Profile Vector (stored in Qdrant, this is metadata)
    profile_vector_version = Column(String(50))  # Track embedding model version
    profile_last_updated = Column(DateTime, default=datetime.utcnow)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<User(user_id={self.user_id}, email={self.email})>"
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            "user_id": self.user_id,
            "email": self.email,
            "full_name": self.full_name,
            "profession": self.profession,
            "income": self.income,
            "price_sensitivity": self.price_sensitivity.value if self.price_sensitivity else None,
            "last_payday": self.last_payday.isoformat() if self.last_payday else None,
            "preferred_categories": self.preferred_categories,
            "financial_goals": self.financial_goals,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }