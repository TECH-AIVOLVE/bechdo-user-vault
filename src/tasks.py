
from src.celery_config import celery_app
from src.core.email import send_verification_email, send_password_reset_email

@celery_app.task
def send_verification_email_task(to_email: str, name: str, token: str):
    """Background task to send verification email"""
    return send_verification_email(to_email, name, token)

@celery_app.task
def send_password_reset_email_task(to_email: str, name: str, token: str):
    """Background task to send password reset email"""
    return send_password_reset_email(to_email, name, token)
