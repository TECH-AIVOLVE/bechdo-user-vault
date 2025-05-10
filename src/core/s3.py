
import os
import boto3
from botocore.client import Config
from src.config import settings

def get_s3_client():
    """Get boto3 S3 client or use local storage"""
    if settings.STORAGE_MODE == "local":
        # For local development, we'll return None and handle differently
        return None
    
    return boto3.client(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        config=Config(signature_version='s3v4')
    )

def generate_presigned_url(file_path: str, content_type: str, expires_in: int = 3600):
    """Generate a presigned URL for S3 upload or prepare local path"""
    if settings.STORAGE_MODE == "local":
        # Create local directory if it doesn't exist
        os.makedirs(os.path.dirname(os.path.join(settings.LOCAL_STORAGE_PATH, file_path)), exist_ok=True)
        # Return a placeholder URL that will be handled by the frontend to use local upload
        return f"/api/v1/storage/local-upload/{file_path}"
    
    # Regular S3 flow
    s3_client = get_s3_client()
    
    presigned_url = s3_client.generate_presigned_url(
        'put_object',
        Params={
            'Bucket': settings.S3_BUCKET_NAME,
            'Key': file_path,
            'ContentType': content_type
        },
        ExpiresIn=expires_in
    )
    
    return presigned_url

def get_object_url(file_path: str):
    """Get the URL for an S3 object or local file"""
    if settings.STORAGE_MODE == "local":
        return f"/api/v1/storage/files/{file_path}"
    
    return f"https://{settings.S3_BUCKET_NAME}.s3.amazonaws.com/{file_path}"
