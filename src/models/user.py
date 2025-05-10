
from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional
from datetime import datetime
from enum import Enum

class UserRole(str, Enum):
    BASIC_USER = "basic_user"
    SELLER = "seller"
    ADMIN = "admin"
    MODERATOR = "moderator"

class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: str

class UserCreate(UserBase):
    password: str
    
    @validator('password')
    def password_min_length(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        return v
    
    @validator('username')
    def username_format(cls, v):
        if not v.isalnum() and '_' not in v:
            raise ValueError('Username can only contain letters, numbers, and underscore')
        if len(v) < 3:
            raise ValueError('Username must be at least 3 characters')
        return v

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    password: Optional[str] = None
    phone: Optional[str] = None
    profile_picture_url: Optional[str] = None
    location: Optional[dict] = None
    
    @validator('password')
    def password_min_length(cls, v):
        if v is not None and len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        return v

class UserAdminUpdate(UserUpdate):
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None
    role: Optional[UserRole] = None

class UserInDB(UserBase):
    id: str = Field(..., alias="id")
    hashed_password: str
    is_active: bool
    is_verified: bool
    role: UserRole
    phone: Optional[str] = None
    profile_picture_url: Optional[str] = None
    location: Optional[dict] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        populate_by_name = True
        json_encoders = {
            datetime: lambda dt: dt.isoformat()
        }

class User(UserBase):
    id: str
    is_active: bool
    is_verified: bool
    role: UserRole
    phone: Optional[str] = None
    profile_picture_url: Optional[str] = None
    location: Optional[dict] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        json_encoders = {
            datetime: lambda dt: dt.isoformat()
        }
