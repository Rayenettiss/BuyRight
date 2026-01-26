"""
Security Utilities
Hackathon Deliverable: Non-Functional - Security/Privacy
Hash passwords, encrypt financial data, anonymize sensitive information
"""
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
from typing import Optional
import hashlib
from app.config import settings


# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Fernet encryption for sensitive financial data
cipher_suite = Fernet(settings.ENCRYPTION_KEY.encode() if len(settings.ENCRYPTION_KEY) == 44 
                      else Fernet.generate_key())


def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create JWT access token for authentication.
    Hackathon: Secure user sessions for demo.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access"
    })
    
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """Decode and validate JWT token"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None


def encrypt_sensitive_data(data: str) -> str:
    """
    Encrypt sensitive financial data (credit limits, account numbers).
    Hackathon: Privacy requirement - protect financial information.
    """
    return cipher_suite.encrypt(data.encode()).decode()


def decrypt_sensitive_data(encrypted_data: str) -> str:
    """Decrypt sensitive financial data"""
    return cipher_suite.decrypt(encrypted_data.encode()).decode()


def anonymize_user_id(user_id: str) -> str:
    """
    Hash user ID with salt for anonymization in logs.
    Hackathon: Privacy - mask sensitive data in observability logs.
    """
    if not settings.MASK_SENSITIVE_DATA:
        return user_id
    
    salted = f"{user_id}{settings.HASH_SALT}"
    return hashlib.sha256(salted.encode()).hexdigest()[:16]


def mask_financial_amount(amount: float) -> str:
    """
    Mask financial amounts for logging (keep order of magnitude).
    Example: $1,234.56 -> "$1,2XX.XX"
    """
    if not settings.MASK_SENSITIVE_DATA:
        return str(amount)
    
    amount_str = f"{amount:.2f}"
    if len(amount_str) > 4:
        # Mask all but first 2 digits
        return f"${amount_str[:2]}XX.XX"
    return "$XX.XX"


def validate_token_payload(payload: dict, required_fields: list) -> bool:
    """Validate JWT payload has required fields"""
    return all(field in payload for field in required_fields)


class SecurityException(Exception):
    """Custom exception for security-related errors"""
    pass