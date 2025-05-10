
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os

from src.config import settings
from src.api.router import api_router
from src.dependencies import get_current_user

# Create local storage directory if using local storage mode
if settings.STORAGE_MODE == "local":
    os.makedirs(settings.LOCAL_STORAGE_PATH, exist_ok=True)

app = FastAPI(
    title=settings.APP_NAME + " API",
    description="Backend API for BECHDO marketplace platform",
    version="0.1.0",
    docs_url="/api/docs",  # Swagger UI
    redoc_url="/api/redoc",  # ReDoc UI
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_db_client():
    # Connect to MongoDB
    app.mongodb_client = AsyncIOMotorClient(settings.MONGODB_URL)
    app.mongodb = app.mongodb_client[settings.DB_NAME]
    
    # Create indexes for collections
    await app.mongodb.users.create_index("email", unique=True)
    await app.mongodb.users.create_index("username", unique=True)
    # Add more indexes as needed

@app.on_event("shutdown")
async def shutdown_db_client():
    app.mongodb_client.close()

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
async def root():
    return {
        "message": f"Welcome to {settings.APP_NAME} API",
        "docs": "/api/docs",
        "redoc": "/api/redoc"
    }
