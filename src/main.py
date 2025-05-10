
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient

from src.config import settings
from src.api.router import api_router
from src.dependencies import get_current_user

app = FastAPI(
    title="BECHDO API",
    description="Backend API for BECHDO marketplace platform",
    version="0.1.0",
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_db_client():
    app.mongodb_client = AsyncIOMotorClient(settings.MONGODB_URL)
    app.mongodb = app.mongodb_client[settings.DB_NAME]
    
    # Create indexes for collections
    await app.mongodb.users.create_index("email", unique=True)
    await app.mongodb.users.create_index("username", unique=True)
    # Add more indexes as needed

@app.on_event("shutdown")
async def shutdown_db_client():
    app.mongodb_client.close()

app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "Welcome to BECHDO API"}
