"""
Budget Model - PostgreSQL
Stores user budget constraints (hard/soft limits by category)
Hackathon: Core feature for constraint-aware recommendations
"""
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class Budget(Base):
    """
    Budget table - stores category-specific budget constraints.
    
    Hackathon Requirements:
    - Hard max: Absolute maximum (e.g., cannot exceed credit limit)
    - Soft max: Preferred maximum (can be flexible)
    - Monthly limit: Reset monthly for recurring budgets
    
    Examples:
    - "Electronics" hard_max=$2000 (credit limit), soft_max=$500 (prefer not to spend more)
    - "Groceries" monthly_limit=$400
    """
    __tablename__ = "budgets"
    
    # Primary Key
    budget_id = Column(String(36), primary_key=True, index=True)
    
    # Foreign Key to User
    user_id = Column(String(36), ForeignKey("users.user_id"), nullable=False, index=True)
    
    # Budget Constraints
    category = Column(String(100), nullable=False)  # "Electronics", "Groceries", etc.
    
    # Hard and Soft Limits (Hackathon: Constraint-aware search)
    hard_max = Column(Float)  # Absolute maximum - CANNOT exceed
    soft_max = Column(Float)  # Preferred maximum - can be flexible
    monthly_limit = Column(Float)  # Monthly recurring budget
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Spending tracking (updated by transactions)
    current_month_spent = Column(Float, default=0.0)
    last_reset_date = Column(DateTime, default=datetime.utcnow)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Budget(budget_id={self.budget_id}, user_id={self.user_id}, category={self.category})>"
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            "budget_id": self.budget_id,
            "user_id": self.user_id,
            "category": self.category,
            "hard_max": self.hard_max,
            "soft_max": self.soft_max,
            "monthly_limit": self.monthly_limit,
            "current_month_spent": self.current_month_spent,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
    
    def check_affordability(self, amount: float) -> dict:
        """
        Check if amount is affordable within budget constraints.
        
        Returns:
            {
                "affordable": bool,
                "within_hard_max": bool,
                "within_soft_max": bool,
                "within_monthly": bool,
                "remaining_hard": float,
                "remaining_soft": float,
                "remaining_monthly": float
            }
        """
        within_hard = True
        within_soft = True
        within_monthly = True
        
        if self.hard_max:
            within_hard = amount <= self.hard_max
        
        if self.soft_max:
            within_soft = amount <= self.soft_max
        
        if self.monthly_limit:
            remaining_monthly = self.monthly_limit - self.current_month_spent
            within_monthly = amount <= remaining_monthly
        
        return {
            "affordable": within_hard and within_monthly,  # Must meet hard constraints
            "within_hard_max": within_hard,
            "within_soft_max": within_soft,
            "within_monthly": within_monthly,
            "remaining_hard": self.hard_max - amount if self.hard_max else None,
            "remaining_soft": self.soft_max - amount if self.soft_max else None,
            "remaining_monthly": (self.monthly_limit - self.current_month_spent - amount) 
                                 if self.monthly_limit else None
        }