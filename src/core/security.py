
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import jwt
from passlib.context import CryptContext
from src.config import settings

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Generate password hash"""
    return pwd_context.hash(password)

def create_token(data: dict, expires_delta: timedelta) -> str:
    """Create JWT token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.ALGORITHM)
    return encoded_jwt

def create_access_token(data: Dict[str, Any]) -> str:
    """Create access token"""
    expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return create_token(data, expires_delta)

def create_refresh_token(data: Dict[str, Any]) -> str:
    """Create refresh token"""
    expires_delta = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    return create_token(data, expires_delta)

def decode_token(token: str) -> Dict[str, Any]:
    """Decode and verify JWT token"""
    return jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.ALGORITHM])

def verify_refresh_token(token: str) -> Dict[str, Any]:
    """Verify refresh token"""
    return jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.ALGORITHM])

def create_email_verification_token(email: str) -> str:
    """Create email verification token"""
    expires_delta = timedelta(minutes=settings.EMAIL_VERIFICATION_TOKEN_EXPIRE_MINUTES)
    return create_token({"sub": email}, expires_delta)

def verify_email_token(token: str) -> str:
    """Verify email verification token and return email"""
    payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.ALGORITHM])
    email: str = payload.get("sub")
    if email is None:
        raise ValueError("Invalid token")
    return email

def create_password_reset_token(email: str) -> str:
    """Create password reset token"""
    expires_delta = timedelta(minutes=settings.PASSWORD_RESET_TOKEN_EXPIRE_MINUTES)
    return create_token({"sub": email}, expires_delta)

def verify_password_reset_token(token: str) -> str:
    """Verify password reset token and return email"""
    payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.ALGORITHM])
    email: str = payload.get("sub")
    if email is None:
        raise ValueError("Invalid token")
    return email
