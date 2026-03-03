"""
utils/email_utils.py - Email sending utilities using SMTP.
Handles verification emails and password reset emails.
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional

# Email configuration from environment
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
FROM_EMAIL = os.getenv("FROM_EMAIL", "noreply@skillsync.com")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")


def send_verification_email(email: str, token: str, name: str) -> bool:
    """
    Send email verification link to user.

    Args:
        email: User's email address
        token: Verification token to include in link
        name: User's name for personalization

    Returns:
        True if email sent successfully, False otherwise
    """
    if not SMTP_USERNAME or not SMTP_PASSWORD:
        print("⚠️  SMTP credentials not configured. Skipping email send.")
        print(f"   Verification link: {FRONTEND_URL}/verify-email?token={token}")
        return True  # Don't fail, but log the token

    subject = "Verify Your SkillSync Email"
    verification_link = f"{FRONTEND_URL}/verify-email?token={token}"

    html_body = f"""
    <html>
        <body style="font-family: Arial, sans-serif; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2>Welcome to SkillSync, {name}!</h2>
                <p>Please verify your email address to get started:</p>

                <a href="{verification_link}" style="display: inline-block; padding: 12px 24px; background-color: #6366f1; color: white; text-decoration: none; border-radius: 6px; margin: 20px 0;">
                    Verify Email Address
                </a>

                <p>Or copy this link:</p>
                <p style="word-break: break-all; background-color: #f5f5f5; padding: 10px;">{verification_link}</p>

                <p style="color: #999; font-size: 12px; margin-top: 30px;">
                    This link expires in 24 hours.
                </p>
            </div>
        </body>
    </html>
    """

    return _send_email(email, subject, html_body)


def send_password_reset_email(email: str, token: str, name: str) -> bool:
    """
    Send password reset link to user.

    Args:
        email: User's email address
        token: Reset token to include in link
        name: User's name for personalization

    Returns:
        True if email sent successfully, False otherwise
    """
    if not SMTP_USERNAME or not SMTP_PASSWORD:
        print("⚠️  SMTP credentials not configured. Skipping email send.")
        print(f"   Password reset link: {FRONTEND_URL}/reset-password?token={token}")
        return True  # Don't fail, but log the token

    subject = "Reset Your SkillSync Password"
    reset_link = f"{FRONTEND_URL}/reset-password?token={token}"

    html_body = f"""
    <html>
        <body style="font-family: Arial, sans-serif; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2>Password Reset Request</h2>
                <p>Hi {name},</p>
                <p>We received a request to reset your password. Click the link below to set a new password:</p>

                <a href="{reset_link}" style="display: inline-block; padding: 12px 24px; background-color: #6366f1; color: white; text-decoration: none; border-radius: 6px; margin: 20px 0;">
                    Reset Password
                </a>

                <p>Or copy this link:</p>
                <p style="word-break: break-all; background-color: #f5f5f5; padding: 10px;">{reset_link}</p>

                <p style="color: #999; font-size: 12px; margin-top: 30px;">
                    This link expires in 1 hour.<br>
                    If you didn't request a password reset, ignore this email.
                </p>
            </div>
        </body>
    </html>
    """

    return _send_email(email, subject, html_body)


def send_login_warning_email(email: str, name: str) -> bool:
    """
    Send warning email after multiple failed login attempts.

    Args:
        email: User's email address
        name: User's name for personalization

    Returns:
        True if email sent successfully, False otherwise
    """
    if not SMTP_USERNAME or not SMTP_PASSWORD:
        print(f"⚠️  SMTP credentials not configured. Skipping warning email to {email}")
        return True

    subject = "SkillSync - Multiple Failed Login Attempts"

    html_body = f"""
    <html>
        <body style="font-family: Arial, sans-serif; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #ef4444;">Security Alert</h2>
                <p>Hi {name},</p>
                <p>We detected multiple failed login attempts on your SkillSync account.</p>

                <p style="background-color: #fef2f2; padding: 15px; border-left: 4px solid #ef4444; border-radius: 4px;">
                    <strong>Your account is temporarily locked for security.</strong><br>
                    You can try logging in again in 15 minutes.
                </p>

                <p>If you didn't try to login, <a href="{FRONTEND_URL}/forgot-password" style="color: #6366f1; text-decoration: none;">reset your password immediately</a>.</p>

                <p style="color: #999; font-size: 12px; margin-top: 30px;">
                    Need help? Contact our support team.
                </p>
            </div>
        </body>
    </html>
    """

    return _send_email(email, subject, html_body)


def _send_email(to_email: str, subject: str, html_body: str) -> bool:
    """
    Internal method to send email via SMTP.

    Args:
        to_email: Recipient email address
        subject: Email subject line
        html_body: HTML email body

    Returns:
        True if sent successfully, False otherwise
    """
    try:
        # Create message
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = FROM_EMAIL
        message["To"] = to_email

        # Attach HTML content
        message.attach(MIMEText(html_body, "html"))

        # Send email via SMTP
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=10) as server:
            server.starttls()  # Upgrade connection to TLS
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(message)

        print(f"✓ Email sent to {to_email}")
        return True

    except smtplib.SMTPException as e:
        print(f"✗ SMTP error sending email to {to_email}: {e}")
        return False
    except Exception as e:
        print(f"✗ Error sending email to {to_email}: {e}")
        return False
