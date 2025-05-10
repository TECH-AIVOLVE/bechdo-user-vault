
import pytest
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi.testclient import TestClient
from bson import ObjectId
import os
import json
from datetime import datetime

from src.main import app
from src.config import settings
from src.core.security import get_password_hash, create_access_token

# Use a separate test database
TEST_MONGODB_URL = "mongodb://localhost:27017"
TEST_DB_NAME = "bechdo_test_db"

@pytest.fixture
def event_loop():
    """Create an instance of the default event loop for each test."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def client():
    """Create a test client for FastAPI app."""
    with TestClient(app) as c:
        yield c

@pytest.fixture
async def test_db():
    """Connect to test database and clean up after tests."""
    client = AsyncIOMotorClient(TEST_MONGODB_URL)
    db = client[TEST_DB_NAME]
    
    # Override the app's database settings
    app.mongodb_client = client
    app.mongodb = db
    
    # Clear the database before tests
    collections = await db.list_collection_names()
    for collection in collections:
        await db[collection].delete_many({})
    
    yield db
    
    # Clear the database after tests
    collections = await db.list_collection_names()
    for collection in collections:
        await db[collection].delete_many({})
    
    client.close()

@pytest.fixture
async def test_user(test_db):
    """Create a test user."""
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "full_name": "Test User",
        "hashed_password": get_password_hash("password123"),
        "is_active": True,
        "is_verified": True,
        "role": "basic_user",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    result = await test_db.users.insert_one(user_data)
    user_id = result.inserted_id
    
    # Create access token for the test user
    access_token = create_access_token(data={"sub": str(user_id)})
    
    return {
        "id": str(user_id),
        "access_token": access_token,
        **user_data
    }

@pytest.fixture
async def test_admin(test_db):
    """Create a test admin user."""
    admin_data = {
        "username": "admin",
        "email": "admin@example.com",
        "full_name": "Admin User",
        "hashed_password": get_password_hash("admin123"),
        "is_active": True,
        "is_verified": True,
        "role": "admin",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    result = await test_db.users.insert_one(admin_data)
    admin_id = result.inserted_id
    
    # Create access token for the test admin
    access_token = create_access_token(data={"sub": str(admin_id)})
    
    return {
        "id": str(admin_id),
        "access_token": access_token,
        **admin_data
    }
