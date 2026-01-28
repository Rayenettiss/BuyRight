"""
Dependency injection for FastAPI routes.
Provides database sessions, authentication dependencies and other shared dependencies.
"""

from typing import Generator, Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from jose import JWTError

from config.settings import settings
from app.models.user import User
from app.services.auth_service import verify_token

# ────────────────────────────────────────────────
# Database configuration
# ────────────────────────────────────────────────

engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,           # Verify connections before using
    echo=settings.debug,          # Log SQL queries in debug mode
)

# Create SessionLocal class for database sessions
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base class for ORM models
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    Dependency that provides a database session.
    Automatically closes session after request completes.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ────────────────────────────────────────────────
# JWT Authentication dependencies
# ────────────────────────────────────────────────

# OAuth2 scheme – used by FastAPI to read Bearer token
# Points to your login endpoint (very important for Swagger UI)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Session = Depends(get_db)
) -> User:
    """
    Get current authenticated user from JWT bearer token.

    Raises:
        HTTPException 401 if:
        - no token provided
        - token invalid / expired / malformed
        - user id not present in token
        - user not found in database
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = verify_token(token)
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception

    return user


# ────────────────────────────────────────────────
# Optional version – useful for public routes that can personalize
# ────────────────────────────────────────────────

def get_optional_current_user(
    token: Annotated[str | None, Depends(oauth2_scheme)] = None,
    db: Session = Depends(get_db)
) -> User | None:
    """
    Returns current user if valid token is provided,
    otherwise returns None (no exception raised)
    """
    if token is None:
        return None

    try:
        payload = verify_token(token)
        user_id: str = payload.get("sub")
        if user_id is None:
            return None
    except JWTError:
        return None

    return db.query(User).filter(User.id == user_id).first()