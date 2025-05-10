
import boto3
from botocore.client import Config
from src.config import settings

def get_s3_client():
    """Get boto3 S3 client"""
    return boto3.client(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        config=Config(signature_version='s3v4')
    )

def generate_presigned_url(file_path: str, content_type: str, expires_in: int = 3600):
    """Generate a presigned URL for S3 upload"""
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
    """Get the URL for an S3 object"""
    return f"https://{settings.S3_BUCKET_NAME}.s3.amazonaws.com/{file_path}"
