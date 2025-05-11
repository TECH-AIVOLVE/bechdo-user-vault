
from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, status, Path
from fastapi.responses import FileResponse
import os
import shutil
from typing import List
import uuid

from src.dependencies import get_current_user
from src.config import settings

router = APIRouter()

@router.post("/upload", response_model=dict)
async def upload_file(
    file: UploadFile = File(...),
    folder: str = "uploads",
    current_user = Depends(get_current_user)
):
    """Upload a file to storage (S3 or local)"""
    if settings.STORAGE_MODE == "local":
        return await _upload_local(file, folder, current_user["id"])
    else:
        # S3 upload would be implemented here
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="S3 upload not implemented in this demo"
        )

@router.get("/files/{path:path}", response_class=FileResponse)
async def get_file(path: str):
    """Get a file from local storage"""
    if settings.STORAGE_MODE == "local":
        file_path = os.path.join(settings.LOCAL_STORAGE_PATH, path)
        if not os.path.exists(file_path):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found"
            )
        return FileResponse(file_path)
    else:
        # S3 file access would be implemented here
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="S3 file access not implemented in this demo"
        )

@router.post("/local-upload/{path:path}", response_model=dict)
async def local_upload(
    path: str,
    file: UploadFile = File(...),
    current_user = Depends(get_current_user)
):
    """Endpoint for local file uploads when using local storage mode"""
    if settings.STORAGE_MODE != "local":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Local upload is only available when STORAGE_MODE is set to local"
        )
    
    file_path = os.path.join(settings.LOCAL_STORAGE_PATH, path)
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    # Save file
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    
    return {
        "filename": file.filename,
        "path": path,
        "url": f"/api/v1/storage/files/{path}"
    }

async def _upload_local(file: UploadFile, folder: str, user_id: str) -> dict:
    """Helper function for local file upload"""
    # Generate a unique filename
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    
    # Create path
    relative_path = os.path.join(folder, user_id, unique_filename)
    absolute_path = os.path.join(settings.LOCAL_STORAGE_PATH, relative_path)
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(absolute_path), exist_ok=True)
    
    # Save file
    with open(absolute_path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    
    return {
        "filename": file.filename,
        "path": relative_path,
        "url": f"/api/v1/storage/files/{relative_path}"
    }
