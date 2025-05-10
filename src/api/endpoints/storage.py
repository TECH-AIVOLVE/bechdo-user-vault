
import os
import shutil
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from src.config import settings

router = APIRouter()

@router.post("/local-upload/{file_path:path}")
async def local_upload(file_path: str, file: UploadFile = File(...)):
    """Handle local file uploads for development"""
    if settings.STORAGE_MODE != "local":
        raise HTTPException(status_code=400, detail="Local storage mode is not enabled")
    
    file_location = os.path.join(settings.LOCAL_STORAGE_PATH, file_path)
    os.makedirs(os.path.dirname(file_location), exist_ok=True)
    
    try:
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        return {"filename": file_path, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not upload file: {str(e)}")

@router.get("/files/{file_path:path}")
async def get_local_file(file_path: str):
    """Serve local files for development"""
    if settings.STORAGE_MODE != "local":
        raise HTTPException(status_code=400, detail="Local storage mode is not enabled")
    
    file_location = os.path.join(settings.LOCAL_STORAGE_PATH, file_path)
    if not os.path.isfile(file_location):
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(file_location)
