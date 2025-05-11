
from pydantic_settings import BaseSettings
from typing import List, Literal
import os

class Settings(BaseSettings):
    # Application settings
    APP_NAME: str = "BECHDO"
    API_V1_STR: str = "/api/v1"
    
    # MongoDB connection
    MONGODB_URL: str = "mongodb://localhost:27017"
    DB_NAME: str = "bechdo_db"
    
    # JWT settings
    JWT_SECRET: str = "CHANGE_THIS_TO_A_SECURE_SECRET"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    ALGORITHM: str = "HS256"
    
    # Storage settings
    STORAGE_MODE: Literal["s3", "local"] = "s3"
    LOCAL_STORAGE_PATH: str = "./local_storage"
    
    # AWS S3 settings
    AWS_ACCESS_KEY_ID: str = "YOUR_AWS_ACCESS_KEY"
    AWS_SECRET_ACCESS_KEY: str = "YOUR_AWS_SECRET_KEY"
    S3_BUCKET_NAME: str = "bechdo-media"
    
    # Redis settings (for Celery)
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    
    # Email settings
    SMTP_SERVER: str = "smtp.example.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = "noreply@bechdo.com"
    SMTP_PASSWORD: str = "YOUR_SMTP_PASSWORD"
    EMAIL_FROM: str = "BECHDO <noreply@bechdo.com>"
    
    # Security
    PASSWORD_RESET_TOKEN_EXPIRE_MINUTES: int = 10
    EMAIL_VERIFICATION_TOKEN_EXPIRE_MINUTES: int = 60
    RATE_LIMIT_ATTEMPTS: int = 5
    RATE_LIMIT_PERIOD_SECONDS: int = 60
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8080"]
    
    class Config:
        env_file = ".env"
        
settings = Settings()
