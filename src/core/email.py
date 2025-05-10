
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from src.config import settings

async def send_email(to_email: str, subject: str, html_content: str):
    """Send email using SMTP"""
    message = MIMEMultipart("alternative")
    message["From"] = settings.EMAIL_FROM
    message["To"] = to_email
    message["Subject"] = subject
    
    # Add HTML content
    html_part = MIMEText(html_content, "html")
    message.attach(html_part)
    
    # Connect to SMTP server and send email
    try:
        await aiosmtplib.send(
            message,
            hostname=settings.SMTP_SERVER,
            port=settings.SMTP_PORT,
            username=settings.SMTP_USERNAME,
            password=settings.SMTP_PASSWORD,
            use_tls=True
        )
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

async def send_verification_email(to_email: str, name: str, token: str):
    """Send email verification email"""
    subject = "Verify your email address for BECHDO"
    
    # In production, you would use a proper template system
    verification_url = f"https://yourdomain.com/verify-email?token={token}"
    
    html_content = f"""
    <html>
        <body>
            <h2>Welcome to BECHDO, {name}!</h2>
            <p>Thank you for signing up. Please click the link below to verify your email address:</p>
            <p><a href="{verification_url}">Verify Email Address</a></p>
            <p>This link will expire in {settings.EMAIL_VERIFICATION_TOKEN_EXPIRE_MINUTES} minutes.</p>
            <p>If you did not sign up for BECHDO, you can safely ignore this email.</p>
            <p>Best regards,<br/>BECHDO Team</p>
        </body>
    </html>
    """
    
    await send_email(to_email, subject, html_content)

async def send_password_reset_email(to_email: str, name: str, token: str):
    """Send password reset email"""
    subject = "Reset your BECHDO password"
    
    # In production, you would use a proper template system
    reset_url = f"https://yourdomain.com/reset-password?token={token}"
    
    html_content = f"""
    <html>
        <body>
            <h2>Hello {name},</h2>
            <p>We received a request to reset your password. Click the link below to set a new password:</p>
            <p><a href="{reset_url}">Reset Password</a></p>
            <p>This link will expire in {settings.PASSWORD_RESET_TOKEN_EXPIRE_MINUTES} minutes.</p>
            <p>If you did not request a password reset, you can safely ignore this email.</p>
            <p>Best regards,<br/>BECHDO Team</p>
        </body>
    </html>
    """
    
    await send_email(to_email, subject, html_content)
