"""
Authentication Router
Handles user registration, login, token management
Hackathon Deliverable: Security - JWT-based authentication
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from datetime import timedelta
import uuid

from app.database import get_db
from app.models.user import User, PriceSensitivity
from app.schemas.user import UserRegister, UserLogin, TokenResponse, UserResponse
from app.utils.security import (
    hash_password, 
    verify_password, 
    create_access_token,
    decode_access_token,
    anonymize_user_id
)
from app.utils.logger import get_logger
from app.config import settings

router = APIRouter(prefix="/auth", tags=["Authentication"])
security = HTTPBearer()
logger = get_logger(__name__)


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserRegister, db: Session = Depends(get_db)):
    """
    Register a new user.
    
    Hackathon: Creates user profile with financial context (income, profession, price sensitivity).
    Returns JWT token for immediate authentication.
    """
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        logger.warning("registration_failed_duplicate_email", email=user_data.email)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    user_id = str(uuid.uuid4())
    hashed_pwd = hash_password(user_data.password)
    
    new_user = User(
        user_id=user_id,
        email=user_data.email,
        hashed_password=hashed_pwd,
        full_name=user_data.full_name,
        profession=user_data.profession,
        income=user_data.income,
        price_sensitivity=PriceSensitivity(user_data.price_sensitivity.value),
        preferred_categories=user_data.preferred_categories or []
    )
    
    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        # Create access token
        access_token = create_access_token(
            data={"sub": user_id, "email": user_data.email},
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        
        logger.info(
            "user_registered",
            user_id=anonymize_user_id(user_id),
            email=user_data.email,
            profession=user_data.profession
        )
        
        return TokenResponse(
            access_token=access_token,
            user_id=user_id,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
    
    except Exception as e:
        db.rollback()
        logger.error("user_registration_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to register user"
        )


@router.post("/login", response_model=TokenResponse)
async def login_user(credentials: UserLogin, db: Session = Depends(get_db)):
    """
    Authenticate user and return JWT token.
    
    Hackathon: Secure authentication for demo.
    """
    # Find user by email
    user = db.query(User).filter(User.email == credentials.email).first()
    
    if not user:
        logger.warning("login_failed_user_not_found", email=credentials.email)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Verify password
    if not verify_password(credentials.password, user.hashed_password):
        logger.warning("login_failed_invalid_password", user_id=anonymize_user_id(user.user_id))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Create access token
    access_token = create_access_token(
        data={"sub": user.user_id, "email": user.email},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    logger.info("user_logged_in", user_id=anonymize_user_id(user.user_id))
    
    return TokenResponse(
        access_token=access_token,
        user_id=user.user_id,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency to get current authenticated user from JWT token.
    
    Usage in protected routes:
        @router.get("/protected")
        async def protected_route(current_user: User = Depends(get_current_user)):
            ...
    """
    token = credentials.credentials
    
    # Decode token
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )
    
    # Get user from database
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return user


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    Get current authenticated user's information.
    
    Hackathon: Returns user profile including financial context.
    """
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


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(current_user: User = Depends(get_current_user)):
    """
    Refresh JWT token.
    
    Returns new token with extended expiration.
    """
    access_token = create_access_token(
        data={"sub": current_user.user_id, "email": current_user.email},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    logger.info("token_refreshed", user_id=anonymize_user_id(current_user.user_id))
    
    return TokenResponse(
        access_token=access_token,
        user_id=current_user.user_id,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )