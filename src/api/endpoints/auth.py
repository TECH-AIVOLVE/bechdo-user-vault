
from datetime import datetime, timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Request
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import EmailStr
from pymongo.errors import DuplicateKeyError

from src.core.security import (
    create_access_token,
    create_refresh_token,
    verify_password,
    get_password_hash,
    create_email_verification_token,
    verify_email_token,
    create_password_reset_token,
    verify_password_reset_token,
)
from src.core.rate_limit import rate_limited
from src.models.user import UserCreate, User, UserInDB
from src.models.token import Token, RefreshToken
from src.dependencies import get_current_user, get_db
from src.core.email import send_verification_email, send_password_reset_email
from src.config import settings

router = APIRouter()

@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_in: UserCreate,
    background_tasks: BackgroundTasks,
    db = Depends(get_db)
):
    """Register a new user and send verification email"""
    # Check if user already exists
    existing_user = await db.users.find_one({"email": user_in.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )
    
    # Create new user
    hashed_password = get_password_hash(user_in.password)
    
    # Generate verification token
    verification_token = create_email_verification_token(user_in.email)
    
    user_doc = {
        "email": user_in.email,
        "username": user_in.username,
        "hashed_password": hashed_password,
        "full_name": user_in.full_name,
        "role": "basic_user",
        "is_active": False,
        "is_verified": False,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }
    
    try:
        result = await db.users.insert_one(user_doc)
    except DuplicateKeyError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )
    
    # Send verification email as background task
    background_tasks.add_task(
        send_verification_email, 
        user_in.email, 
        user_in.full_name, 
        verification_token
    )
    
    user_doc["id"] = str(result.inserted_id)
    return UserInDB(**user_doc).model_dump(exclude={"hashed_password"})

@router.post("/verify-email")
async def verify_email(token: str, db = Depends(get_db)):
    """Verify user email with token"""
    try:
        email = verify_email_token(token)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification token"
        )
    
    # Activate user account
    result = await db.users.update_one(
        {"email": email},
        {"$set": {"is_verified": True, "is_active": True, "updated_at": datetime.utcnow()}}
    )
    
    if result.modified_count == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User not found or already verified"
        )
        
    return {"message": "Email successfully verified"}

@router.post("/login", response_model=Token)
@rate_limited()
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    request: Request = None,
    db = Depends(get_db)
):
    """User login with username/email and password"""
    # Find user by email or username
    user = await db.users.find_one({
        "$or": [
            {"email": form_data.username},
            {"username": form_data.username}
        ]
    })
    
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email/username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user["is_active"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User account is inactive"
        )
    
    # Record login history
    login_history = {
        "user_id": user["_id"],
        "ip_address": request.client.host if request else None,
        "user_agent": request.headers.get("User-Agent") if request else None,
        "timestamp": datetime.utcnow()
    }
    await db.login_history.insert_one(login_history)
    
    # Generate tokens
    access_token = create_access_token(data={"sub": str(user["_id"])})
    refresh_token = create_refresh_token(data={"sub": str(user["_id"])})
    
    # Store refresh token in db
    await db.refresh_tokens.insert_one({
        "user_id": user["_id"],
        "token": refresh_token,
        "expires_at": datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        "created_at": datetime.utcnow()
    })
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.post("/refresh", response_model=Token)
async def refresh_token(refresh_token: RefreshToken, db = Depends(get_db)):
    """Get new access token using refresh token"""
    try:
        payload = verify_refresh_token(refresh_token.refresh_token)
        user_id = payload.get("sub")
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if token exists and is not blacklisted
    token_entry = await db.refresh_tokens.find_one({
        "token": refresh_token.refresh_token,
        "is_blacklisted": {"$ne": True}
    })
    
    if not token_entry:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token not found or blacklisted",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Generate new tokens
    new_access_token = create_access_token(data={"sub": user_id})
    new_refresh_token = create_refresh_token(data={"sub": user_id})
    
    # Blacklist old token and save new one
    await db.refresh_tokens.update_one(
        {"token": refresh_token.refresh_token},
        {"$set": {"is_blacklisted": True}}
    )
    
    await db.refresh_tokens.insert_one({
        "user_id": token_entry["user_id"],
        "token": new_refresh_token,
        "expires_at": datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        "created_at": datetime.utcnow()
    })
    
    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer"
    }

@router.post("/logout")
async def logout(
    refresh_token: RefreshToken,
    current_user: User = Depends(get_current_user),
    db = Depends(get_db)
):
    """Logout user by blacklisting refresh token"""
    result = await db.refresh_tokens.update_one(
        {
            "token": refresh_token.refresh_token,
            "user_id": current_user["_id"]
        },
        {"$set": {"is_blacklisted": True}}
    )
    
    if result.modified_count == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token not found or already blacklisted"
        )
    
    return {"message": "Successfully logged out"}

@router.post("/forgot-password")
@rate_limited()
async def forgot_password(
    email: EmailStr,
    background_tasks: BackgroundTasks,
    db = Depends(get_db)
):
    """Send password reset email"""
    # Check if user exists
    user = await db.users.find_one({"email": email})
    if not user:
        # Don't reveal whether email exists for security
        return {"message": "If this email exists, a password reset link has been sent"}
    
    # Generate reset token
    reset_token = create_password_reset_token(email)
    
    # Send password reset email
    background_tasks.add_task(
        send_password_reset_email,
        email,
        user["full_name"],
        reset_token
    )
    
    return {"message": "Password reset email sent"}

@router.post("/reset-password")
@rate_limited()
async def reset_password(
    token: str,
    new_password: str,
    db = Depends(get_db)
):
    """Reset password with token"""
    try:
        email = verify_password_reset_token(token)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    
    # Update user password
    hashed_password = get_password_hash(new_password)
    result = await db.users.update_one(
        {"email": email},
        {"$set": {"hashed_password": hashed_password, "updated_at": datetime.utcnow()}}
    )
    
    if result.modified_count == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User not found"
        )
    
    # Invalidate all refresh tokens
    await db.refresh_tokens.update_many(
        {"user_id": result.upserted_id},
        {"$set": {"is_blacklisted": True}}
    )
    
    return {"message": "Password has been reset successfully"}
