
from fastapi import APIRouter
from src.api.endpoints import users, auth, storage

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(storage.router, prefix="/storage", tags=["storage"])
