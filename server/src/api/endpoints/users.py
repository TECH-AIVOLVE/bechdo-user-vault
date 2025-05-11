
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from bson import ObjectId
from pydantic import EmailStr

from src.core.security import get_password_hash
from src.dependencies import get_current_user, get_current_admin, get_db
from src.models.user import User, UserUpdate, UserInDB, UserAdminUpdate
from src.core.s3 import generate_presigned_url

router = APIRouter()

@router.get("/me", response_model=User)
async def read_current_user(current_user: User = Depends(get_current_user)):
    """Get current user profile"""
    return current_user

@router.patch("/me", response_model=User)
async def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db = Depends(get_db)
):
    """Update current user profile"""
    update_data = user_update.model_dump(exclude_unset=True)
    
    # Don't allow direct role updates through this endpoint
    if "role" in update_data:
        del update_data["role"]
    
    if update_data.get("password"):
        update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
    
    update_data["updated_at"] = datetime.utcnow()
    
    await db.users.update_one(
        {"_id": ObjectId(current_user["id"])},
        {"$set": update_data}
    )
    
    updated_user = await db.users.find_one({"_id": ObjectId(current_user["id"])})
    updated_user["id"] = str(updated_user.pop("_id"))
    
    return UserInDB(**updated_user).model_dump(exclude={"hashed_password"})

@router.get("/profile/{user_id}", response_model=User)
async def read_user_profile(
    user_id: str = Path(..., title="The ID of the user to get"),
    db = Depends(get_db)
):
    """Get public user profile by ID"""
    user = await db.users.find_one({"_id": ObjectId(user_id)})
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # For public profile, only return safe fields
    user["id"] = str(user.pop("_id"))
    
    # Use Pydantic for data validation and field filtering
    return UserInDB(**user).model_dump(exclude={
        "hashed_password", 
        "email",  # Keep email private
        "is_active", 
        "is_verified",
        "created_at",
        "updated_at"
    })

@router.get("/avatar-upload-url")
async def get_avatar_upload_url(
    filename: str,
    current_user: User = Depends(get_current_user)
):
    """Generate a presigned URL for avatar upload to S3"""
    content_type = "image/jpeg"  # Adjust based on allowed file types
    
    # Generate a unique file path for the user's avatar
    file_path = f"avatars/{current_user['id']}/{filename}"
    
    # Get presigned URL from S3
    presigned_url = generate_presigned_url(
        file_path=file_path, 
        content_type=content_type,
        expires_in=300  # URL expires in 5 minutes
    )
    
    return {
        "upload_url": presigned_url,
        "file_key": file_path
    }

# Admin endpoints
@router.get("/", response_model=List[User])
async def read_users(
    skip: int = 0,
    limit: int = 100,
    role: Optional[str] = None,
    is_active: Optional[bool] = None,
    current_admin: User = Depends(get_current_admin),
    db = Depends(get_db)
):
    """
    Get all users (admin only)
    """
    query = {}
    
    # Apply filters if provided
    if role:
        query["role"] = role
    if is_active is not None:
        query["is_active"] = is_active
    
    users = []
    async for user in db.users.find(query).skip(skip).limit(limit):
        user["id"] = str(user.pop("_id"))
        users.append(UserInDB(**user).model_dump(exclude={"hashed_password"}))
    
    return users

@router.patch("/{user_id}", response_model=User)
async def admin_update_user(
    user_update: UserAdminUpdate,
    user_id: str = Path(..., title="The ID of the user to update"),
    current_admin: User = Depends(get_current_admin),
    db = Depends(get_db)
):
    """
    Update a user (admin only)
    """
    update_data = user_update.model_dump(exclude_unset=True)
    
    if update_data.get("password"):
        update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
    
    update_data["updated_at"] = datetime.utcnow()
    
    # Record audit log for admin action
    audit_log = {
        "action": "user_update",
        "user_id": ObjectId(user_id),
        "admin_id": ObjectId(current_admin["id"]),
        "timestamp": datetime.utcnow(),
        "details": {k: v for k, v in update_data.items() if k != "hashed_password"}
    }
    
    await db.audit_logs.insert_one(audit_log)
    
    result = await db.users.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    updated_user = await db.users.find_one({"_id": ObjectId(user_id)})
    updated_user["id"] = str(updated_user.pop("_id"))
    
    return UserInDB(**updated_user).model_dump(exclude={"hashed_password"})

@router.get("/audit-logs", response_model=List[dict])
async def get_audit_logs(
    skip: int = 0,
    limit: int = 100,
    user_id: Optional[str] = None,
    action: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_admin: User = Depends(get_current_admin),
    db = Depends(get_db)
):
    """
    Get audit logs (admin only)
    """
    query = {}
    
    # Apply filters if provided
    if user_id:
        query["user_id"] = ObjectId(user_id)
    if action:
        query["action"] = action
    
    # Date range filter
    date_filter = {}
    if start_date:
        date_filter["$gte"] = start_date
    if end_date:
        date_filter["$lte"] = end_date
    if date_filter:
        query["timestamp"] = date_filter
    
    logs = []
    async for log in db.audit_logs.find(query).sort("timestamp", -1).skip(skip).limit(limit):
        # Convert ObjectId to string for each log entry
        log["_id"] = str(log["_id"])
        log["user_id"] = str(log["user_id"])
        log["admin_id"] = str(log["admin_id"])
        logs.append(log)
    
    return logs
