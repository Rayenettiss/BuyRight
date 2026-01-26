"""
User Profile Router
Handles user profile management, budget configuration, payment methods
Hackathon Deliverable: User financial context management
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import uuid

from app.database import get_db
from app.models.user import User
from app.models.budget import Budget
from app.models.recommendation import PaymentMethod
from app.schemas.user import UserUpdate, UserResponse
from app.routers.auth import get_current_user
from app.utils.security import encrypt_sensitive_data, decrypt_sensitive_data, anonymize_user_id
from app.utils.logger import get_logger
from pydantic import BaseModel, Field

router = APIRouter(prefix="/user", tags=["User Profile"])
logger = get_logger(__name__)


# Pydantic schemas for this router
class BudgetCreate(BaseModel):
    category: str = Field(..., description="Budget category (e.g., 'Electronics')")
    hard_max: float = Field(..., ge=0, description="Absolute maximum - cannot exceed")
    soft_max: float = Field(..., ge=0, description="Preferred maximum - flexible")
    monthly_limit: float = Field(None, ge=0, description="Monthly recurring budget")


class BudgetResponse(BaseModel):
    budget_id: str
    category: str
    hard_max: float
    soft_max: float
    monthly_limit: float
    current_month_spent: float
    is_active: bool
    
    class Config:
        from_attributes = True


class PaymentMethodCreate(BaseModel):
    type: str = Field(..., description="Payment type: credit_card, debit_card, cash")
    limit: float = Field(None, ge=0, description="Credit/debit limit")
    interest_rate: float = Field(0.0, ge=0, description="Annual interest rate")
    preferred_for_installments: bool = False
    cashback_eligible: bool = False


class PaymentMethodResponse(BaseModel):
    method_id: str
    type: str
    interest_rate: float
    preferred_for_installments: bool
    cashback_eligible: bool
    is_active: bool
    
    class Config:
        from_attributes = True


@router.put("/profile", response_model=UserResponse)
async def update_profile(
    update_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update user profile and financial context.
    
    Hackathon: Update income, profession, price sensitivity, financial goals, etc.
    Triggers user profile vector update in Qdrant (handled separately).
    """
    try:
        # Update fields if provided
        if update_data.full_name is not None:
            current_user.full_name = update_data.full_name
        if update_data.profession is not None:
            current_user.profession = update_data.profession
        if update_data.income is not None:
            current_user.income = update_data.income
        if update_data.price_sensitivity is not None:
            current_user.price_sensitivity = update_data.price_sensitivity
        if update_data.last_payday is not None:
            current_user.last_payday = update_data.last_payday
        if update_data.preferred_categories is not None:
            current_user.preferred_categories = update_data.preferred_categories
        if update_data.financial_goals is not None:
            current_user.financial_goals = update_data.financial_goals
        
        db.commit()
        db.refresh(current_user)
        
        logger.info(
            "user_profile_updated",
            user_id=anonymize_user_id(current_user.user_id),
            updated_fields=update_data.model_dump(exclude_unset=True).keys()
        )
        
        return UserResponse(
            user_id=current_user.user_id,
            email=current_user.email,
            full_name=current_user.full_name,
            profession=current_user.profession,
            income=current_user.income,
            price_sensitivity=current_user.price_sensitivity.value if current_user.price_sensitivity else "medium",
            last_payday=current_user.last_payday,
            preferred_categories=current_user.preferred_categories,
            financial_goals=current_user.financial_goals,
            created_at=current_user.created_at,
            updated_at=current_user.updated_at
        )
    
    except Exception as e:
        db.rollback()
        logger.error("profile_update_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update profile"
        )


@router.post("/budgets", response_model=BudgetResponse, status_code=status.HTTP_201_CREATED)
async def create_budget(
    budget_data: BudgetCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a budget constraint for a category.
    
    Hackathon: Core feature - budget constraints for affordability filtering.
    Example: Electronics hard_max=$2000, soft_max=$500
    """
    # Check if budget already exists for this category
    existing = db.query(Budget).filter(
        Budget.user_id == current_user.user_id,
        Budget.category == budget_data.category,
        Budget.is_active == True
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Active budget already exists for category: {budget_data.category}"
        )
    
    try:
        budget = Budget(
            budget_id=str(uuid.uuid4()),
            user_id=current_user.user_id,
            category=budget_data.category,
            hard_max=budget_data.hard_max,
            soft_max=budget_data.soft_max,
            monthly_limit=budget_data.monthly_limit
        )
        
        db.add(budget)
        db.commit()
        db.refresh(budget)
        
        logger.info(
            "budget_created",
            user_id=anonymize_user_id(current_user.user_id),
            category=budget_data.category,
            hard_max=budget_data.hard_max
        )
        
        return BudgetResponse(
            budget_id=budget.budget_id,
            category=budget.category,
            hard_max=budget.hard_max,
            soft_max=budget.soft_max,
            monthly_limit=budget.monthly_limit,
            current_month_spent=budget.current_month_spent,
            is_active=budget.is_active
        )
    
    except Exception as e:
        db.rollback()
        logger.error("budget_creation_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create budget"
        )


@router.get("/budgets", response_model=List[BudgetResponse])
async def get_budgets(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all active budgets for current user.
    
    Hackathon: Used for constraint-aware recommendations.
    """
    budgets = db.query(Budget).filter(
        Budget.user_id == current_user.user_id,
        Budget.is_active == True
    ).all()
    
    return [
        BudgetResponse(
            budget_id=b.budget_id,
            category=b.category,
            hard_max=b.hard_max,
            soft_max=b.soft_max,
            monthly_limit=b.monthly_limit,
            current_month_spent=b.current_month_spent,
            is_active=b.is_active
        )
        for b in budgets
    ]


@router.post("/payment-methods", response_model=PaymentMethodResponse, status_code=status.HTTP_201_CREATED)
async def add_payment_method(
    payment_data: PaymentMethodCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Add a payment method with encrypted limit.
    
    Hackathon: Security - encrypt sensitive financial data (credit limits).
    Used for installment matching and cashback recommendations.
    """
    try:
        # Encrypt credit limit if provided
        limit_encrypted = None
        if payment_data.limit is not None:
            limit_encrypted = encrypt_sensitive_data(str(payment_data.limit))
        
        payment_method = PaymentMethod(
            method_id=str(uuid.uuid4()),
            user_id=current_user.user_id,
            type=payment_data.type,
            limit_encrypted=limit_encrypted,
            interest_rate=payment_data.interest_rate,
            preferred_for_installments=payment_data.preferred_for_installments,
            cashback_eligible=payment_data.cashback_eligible
        )
        
        db.add(payment_method)
        db.commit()
        db.refresh(payment_method)
        
        logger.info(
            "payment_method_added",
            user_id=anonymize_user_id(current_user.user_id),
            type=payment_data.type,
            cashback_eligible=payment_data.cashback_eligible
        )
        
        return PaymentMethodResponse(
            method_id=payment_method.method_id,
            type=payment_method.type,
            interest_rate=payment_method.interest_rate,
            preferred_for_installments=payment_method.preferred_for_installments,
            cashback_eligible=payment_method.cashback_eligible,
            is_active=payment_method.is_active
        )
    
    except Exception as e:
        db.rollback()
        logger.error("payment_method_creation_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add payment method"
        )


@router.get("/payment-methods", response_model=List[PaymentMethodResponse])
async def get_payment_methods(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all active payment methods for current user.
    
    Hackathon: Used for payment-aware recommendations (installments, cashback).
    """
    methods = db.query(PaymentMethod).filter(
        PaymentMethod.user_id == current_user.user_id,
        PaymentMethod.is_active == True
    ).all()
    
    return [
        PaymentMethodResponse(
            method_id=m.method_id,
            type=m.type,
            interest_rate=m.interest_rate,
            preferred_for_installments=m.preferred_for_installments,
            cashback_eligible=m.cashback_eligible,
            is_active=m.is_active
        )
        for m in methods
    ]