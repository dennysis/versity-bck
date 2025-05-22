import os
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from fastapi import HTTPException, status
from pydantic import EmailStr
import jwt
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# Email configuration - should be moved to environment variables in production
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME", "your-email@gmail.com")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "your-app-password")
EMAIL_FROM = os.getenv("EMAIL_FROM", "Versity <noreply@versity.org>")
BASE_URL = os.getenv("BASE_URL", "http://localhost:3000")

# JWT configuration for password reset tokens
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")
ALGORITHM = "HS256"
PASSWORD_RESET_EXPIRE_MINUTES = 30


def send_email(to_email: EmailStr, subject: str, html_content: str, text_content: str) -> bool:
    """
    Send an email with both HTML and plain text versions.
    
    Args:
        to_email: Recipient email address
        subject: Email subject
        html_content: HTML version of the email body
        text_content: Plain text version of the email body
        
    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    try:
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = EMAIL_FROM
        message["To"] = to_email
        
        # Attach plain text and HTML versions
        part1 = MIMEText(text_content, "plain")
        part2 = MIMEText(html_content, "html")
        message.attach(part1)
        message.attach(part2)
        
        # Connect to SMTP server and send email
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.sendmail(SMTP_USERNAME, to_email, message.as_string())
            
        logger.info(f"Email sent successfully to {to_email}")
        return True
    
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {str(e)}")
        return False


def send_welcome_email(username: str, email: EmailStr) -> bool:
    """
    Send a welcome email to a newly registered user.
    
    Args:
        username: The user's username
        email: The user's email address
        
    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    subject = "Welcome to Versity!"
    
    html_content = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            h1 {{ color: #4a6fa5; }}
            .button {{ display: inline-block; background-color: #4a6fa5; color: white; 
                      padding: 10px 20px; text-decoration: none; border-radius: 5px; }}
            .footer {{ margin-top: 30px; font-size: 12px; color: #777; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Welcome to Versity!</h1>
            <p>Hello {username},</p>
            <p>Thank you for registering with Versity. We're excited to have you join our community of volunteers and organizations making a difference!</p>
            <p>With your new account, you can:</p>
            <ul>
                <li>Browse volunteer opportunities</li>
                <li>Apply for positions that match your skills</li>
                <li>Track your volunteer hours</li>
                <li>Connect with organizations making a difference</li>
            </ul>
            <p>
                <a href="{BASE_URL}/login" class="button">Log In Now</a>
            </p>
            <p>If you have any questions or need assistance, please don't hesitate to contact our support team.</p>
            <p>Best regards,<br>The Versity Team</p>
            <div class="footer">
                <p>This email was sent to {email}. If you didn't create this account, please ignore this email.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    text_content = f"""
    Welcome to Versity!
    
    Hello {username},
    
    Thank you for registering with Versity. We're excited to have you join our community of volunteers and organizations making a difference!
    
    With your new account, you can:
    - Browse volunteer opportunities
    - Apply for positions that match your skills
    - Track your volunteer hours
    - Connect with organizations making a difference
    
    Log in now: {BASE_URL}/login
    
    If you have any questions or need assistance, please don't hesitate to contact our support team.
    
    Best regards,
    The Versity Team
    
    This email was sent to {email}. If you didn't create this account, please ignore this email.
    """
    
    return send_email(email, subject, html_content, text_content)


def create_password_reset_token(email: str) -> str:
    """
    Create a JWT token for password reset.
    
    Args:
        email: The user's email address
        
    Returns:
        str: JWT token
    """
    expire = datetime.utcnow() + timedelta(minutes=PASSWORD_RESET_EXPIRE_MINUTES)
    to_encode = {"sub": email, "exp": expire}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_password_reset_token(token: str) -> Optional[str]:
    """
    Verify a password reset token and return the email if valid.
    
    Args:
        token: JWT token
        
    Returns:
        Optional[str]: Email address if token is valid, None otherwise
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        return email
    except jwt.PyJWTError:
        return None


def send_password_reset_email(email: EmailStr, token: str) -> bool:
    """
    Send a password reset email with a reset link.
    
    Args:
        email: The user's email address
        token: Password reset token
        
    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    reset_link = f"{BASE_URL}/reset-password?token={token}"
    subject = "Reset Your Versity Password"
    
    html_content = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            h1 {{ color: #4a6fa5; }}
            .button {{ display: inline-block; background-color: #4a6fa5; color: white; 
                      padding: 10px 20px; text-decoration: none; border-radius: 5px; }}
            .warning {{ color: #e74c3c; }}
            .footer {{ margin-top: 30px; font-size: 12px; color: #777; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Reset Your Password</h1>
            <p>We received a request to reset your password for your Versity account.</p>
            <p>Click the button below to reset your password:</p>
            <p>
                <a href="{reset_link}" class="button">Reset Password</a>
            </p>
            <p>If the button doesn't work, you can copy and paste this link into your browser:</p>
            <p>{reset_link}</p>
            <p class="warning">This link will expire in {PASSWORD_RESET_EXPIRE_MINUTES} minutes.</p>
            <p>If you didn't request a password reset, you can safely ignore this email. Your password will not be changed.</p>
            <p>Best regards,<br>The Versity Team</p>
            <div class="footer">
                <p>This email was sent to {email}.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    text_content = f"""
    Reset Your Password
    
    We received a request to reset your password for your Versity account.
    
    Click the link below to reset your password:
    {reset_link}
    
    This link will expire in {PASSWORD_RESET_EXPIRE_MINUTES} minutes.
    
    If you didn't request a password reset, you can safely ignore this email. Your password will not be changed.
    
    Best regards,
    The Versity Team
    
    This email was sent to {email}.
    """
    
    return send_email(email, subject, html_content, text_content)


def request_password_reset(email: EmailStr, db) -> bool:
    """
    Handle a password reset request.
    
    Args:
        email: The user's email address
        db: Database session
        
    Returns:
        bool: True if reset email was sent, False otherwise
        
    Raises:
        HTTPException: If user with email doesn't exist
    """
    from app.models.user import User
    
    user = db.query(User).filter(User.email == email).first()
    if not user:
        # Don't reveal that the user doesn't exist for security reasons
        logger.warning(f"Password reset requested for non-existent email: {email}")
        return True
    
    token = create_password_reset_token(email)
    return send_password_reset_email(email, token)


def send_match_notification_email(user_email: EmailStr, username: str, opportunity_title: str) -> bool:
    """
    Send a notification email when a user applies for an opportunity.
    
    Args:
        user_email: The user's email address
        username: The user's username
        opportunity_title: The title of the opportunity
        
    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    subject = f"Application Submitted: {opportunity_title}"
    
    html_content = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            h1 {{ color: #4a6fa5; }}
            .button {{ display: inline-block; background-color: #4a6fa5; color: white; 
                      padding: 10px 20px; text-decoration: none; border-radius: 5px; }}
            .footer {{ margin-top: 30px; font-size: 12px; color: #777; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Application Submitted</h1>
            <p>Hello {username},</p>
            <p>Your application for <strong>{opportunity_title}</strong> has been successfully submitted!</p>
            <p>The organization will review your application and get back to you soon.</p>
            <p>
                <a href="{BASE_URL}/dashboard" class="button">View Your Applications</a>
            </p>
            <p>Thank you for your interest in volunteering!</p>
            <p>Best regards,<br>The Versity Team</p>
            <div class="footer">
                <p>This email was sent to {user_email}.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    text_content = f"""
    Application Submitted
    
    Hello {username},
    
    Your application for {opportunity_title} has been successfully submitted!
    
    The organization will review your application and get back to you soon.
    
    View your applications: {BASE_URL}/dashboard
    
    Thank you for your interest in volunteering!
    
    Best regards,
    The Versity Team
    
    This email was sent to {user_email}.
    """
    
    return send_email(user_email, subject, html_content, text_content)
