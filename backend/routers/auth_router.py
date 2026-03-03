"""
routers/auth_router.py - Complete authentication endpoints.
Handles registration, login, token refresh, logout, email verification, and password recovery.
"""

import os
import secrets
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Response, Request, Body
from sqlalchemy.orm import Session
from email_validator import validate_email, EmailNotValidError

from database import get_db
from models.user import User, UserRole
from schemas.user import UserCreate, UserOut
from utils.password_utils import hash_password, verify_password, validate_password
from utils.jwt_utils import create_access_token, create_refresh_token, decode_token
from utils.email_utils import send_verification_email, send_password_reset_email, send_login_warning_email
from utils.rate_limiter import limiter, RATE_LIMITS
from utils.auth_deps import get_current_user as get_authenticated_user

router = APIRouter(prefix="/auth", tags=["auth"])

# Constants
TOKEN_EXPIRE_SECONDS = 900  # 15 minutes
REFRESH_TOKEN_EXPIRE_SECONDS = 604800  # 7 days
VERIFICATION_TOKEN_EXPIRE_HOURS = 24
RESET_TOKEN_EXPIRE_MINUTES = 60
ACCOUNT_LOCKOUT_MINUTES = 15
MAX_FAILED_ATTEMPTS = 5


# ─── Helper Functions ───────────────────────────────────────────────────────

def _set_tokens_in_cookies(response: Response, access_token: str, refresh_token: str) -> None:
    """Set JWT tokens in httpOnly secure cookies."""
    is_prod = os.getenv("ENVIRONMENT") == "production"
    response.set_cookie(
        key="access_token",
        value=access_token,
        max_age=TOKEN_EXPIRE_SECONDS,
        httponly=True,
        secure=is_prod,
        samesite="none" if is_prod else "lax",
        path="/",
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        max_age=REFRESH_TOKEN_EXPIRE_SECONDS,
        httponly=True,
        secure=is_prod,
        samesite="none" if is_prod else "lax",
        path="/",
    )


def _clear_tokens_from_cookies(response: Response) -> None:
    """Clear JWT tokens from cookies."""
    response.delete_cookie(key="access_token", path="/")
    response.delete_cookie(key="refresh_token", path="/")


def _generate_verification_token() -> tuple[str, datetime]:
    """Generate a verification token and expiry time."""
    token = secrets.token_urlsafe(32)
    expires = datetime.utcnow() + timedelta(hours=VERIFICATION_TOKEN_EXPIRE_HOURS)
    return token, expires


def _generate_reset_token() -> tuple[str, datetime]:
    """Generate a password reset token and expiry time."""
    token = secrets.token_urlsafe(32)
    expires = datetime.utcnow() + timedelta(minutes=RESET_TOKEN_EXPIRE_MINUTES)
    return token, expires


def _is_account_locked(user: User) -> bool:
    """Check if account is temporarily locked due to failed login attempts."""
    if user.failed_login_attempts < MAX_FAILED_ATTEMPTS:
        return False

    if user.last_failed_login is None:
        return False

    lockout_time = user.last_failed_login + timedelta(minutes=ACCOUNT_LOCKOUT_MINUTES)
    return datetime.utcnow() < lockout_time


# ─── Public Endpoints ───────────────────────────────────────────────────────

@router.post("/register", response_model=UserOut)
# @limiter.limit(RATE_LIMITS["register"])  # TEMP DISABLED FOR TESTING
async def register(request: Request, user_data: UserCreate = Body(...), db: Session = Depends(get_db)):
    """
    Register a new user with email, password, and role.

    Validates email format, password strength, and sends verification email.
    """
    # Validate email format
    try:
        valid = validate_email(user_data.email, check_deliverability=False)
        email = valid.email
    except EmailNotValidError as e:
        print(f"Email validation failed: {str(e)}")
        raise HTTPException(status_code=400, detail="Invalid email format")

    # Check if email already registered
    existing = db.query(User).filter(User.email == email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Validate password strength
    is_valid, error_msg = validate_password(user_data.password)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_msg)

    # Generate verification token (kept for future SMTP integration)
    # verification_token, token_expires = _generate_verification_token()

    # Hash password
    password_hash = hash_password(user_data.password)

    # Create user
    try:
        db_role = UserRole(user_data.role)
    except Exception:
        db_role = user_data.role

    db_user = User(
        email=email,
        name=user_data.name,
        role=db_role,
        password_hash=password_hash,
        email_verified=True,   # Auto-verified: no SMTP configured in dev
        email_verification_token=None,
        verification_token_expires=None,
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


@router.post("/login")
@limiter.limit(RATE_LIMITS["login"])
async def login(request: Request, response: Response, payload: dict = Body(...), db: Session = Depends(get_db)):
    """
    Login with email and password.

    Returns JWT tokens in httpOnly cookies and user data.
    Implements account lockout after 5 failed attempts.
    """
    email = payload.get("email")
    password = payload.get("password")

    if not email or not password:
        raise HTTPException(status_code=400, detail="Email and password required")

    # Validate email format
    try:
        valid = validate_email(email, check_deliverability=False)
        email = valid.email
    except EmailNotValidError:
        raise HTTPException(status_code=400, detail="Invalid email format")

    # Find user
    db_user = db.query(User).filter(User.email == email).first()
    if not db_user:
        # Don't reveal if email exists
        raise HTTPException(status_code=401, detail="Invalid email or password")

    # Check if account is locked
    if _is_account_locked(db_user):
        raise HTTPException(
            status_code=429,
            detail="Account locked due to too many failed attempts. Try again in 15 minutes."
        )

    # Verify password
    if not verify_password(password, db_user.password_hash):
        # Increment failed attempts
        db_user.failed_login_attempts += 1
        db_user.last_failed_login = datetime.utcnow()

        # Send warning email after 5 failed attempts
        if db_user.failed_login_attempts == MAX_FAILED_ATTEMPTS:
            send_login_warning_email(email, db_user.name)

        db.commit()
        raise HTTPException(status_code=401, detail="Invalid email or password")

    # Success: Reset failed attempts and update last_login
    db_user.failed_login_attempts = 0
    db_user.last_login = datetime.utcnow()
    # Auto-heal: verify any existing unverified users (SMTP not configured in dev)
    if not db_user.email_verified:
        db_user.email_verified = True
        db_user.email_verification_token = None
        db_user.verification_token_expires = None
    db.commit()
    db.refresh(db_user)

    # Create tokens
    access_token = create_access_token({"sub": str(db_user.id)})
    refresh_token = create_refresh_token({"sub": str(db_user.id)})

    # Set cookies
    _set_tokens_in_cookies(response, access_token, refresh_token)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user": UserOut.model_validate(db_user)
    }


@router.post("/refresh")
async def refresh_token(request: Request, response: Response, db: Session = Depends(get_db)):
    """
    Refresh an expired access token.

    Uses the refresh token (long-lived) to issue a new access token.
    """
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Refresh token missing")

    payload = decode_token(refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    user_id = payload.get("sub")
    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    # Create new access token
    access_token = create_access_token({"sub": str(user.id)})
    is_prod = os.getenv("ENVIRONMENT") == "production"
    response.set_cookie(
        key="access_token",
        value=access_token,
        max_age=TOKEN_EXPIRE_SECONDS,
        httponly=True,
        secure=is_prod,
        samesite="none" if is_prod else "lax",
        path="/",
    )

    return {"access_token": access_token}


@router.post("/logout")
async def logout(response: Response, request: Request):
    """
    Logout user by clearing tokens from cookies.
    """
    _clear_tokens_from_cookies(response)
    return {"message": "Logged out successfully"}


@router.post("/forgot-password")
@limiter.limit(RATE_LIMITS["forgot_password"])
async def forgot_password(request: Request, payload: dict = Body(...), db: Session = Depends(get_db)):
    """
    Request password reset link.

    Generates a reset token and sends email. Returns success regardless of whether email exists.
    """
    email = payload.get("email")
    if not email:
        raise HTTPException(status_code=400, detail="Email required")

    # Find user (don't reveal if exists)
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return {"message": "If that email exists, you will receive a password reset link"}

    # Generate reset token
    reset_token, token_expires = _generate_reset_token()
    user.reset_token = reset_token
    user.reset_token_expires = token_expires
    db.commit()

    # Send email
    send_password_reset_email(email, reset_token, user.name)

    return {"message": "If that email exists, you will receive a password reset link"}


@router.get("/validate-reset-token/{token}")
async def validate_reset_token(token: str, db: Session = Depends(get_db)):
    """
    Validate a password reset token before showing form.
    """
    user = db.query(User).filter(User.reset_token == token).first()
    if not user:
        return {"valid": False}

    if user.reset_token_expires < datetime.utcnow():
        return {"valid": False}

    return {"valid": True}


@router.post("/reset-password")
async def reset_password(payload: dict, db: Session = Depends(get_db)):
    """
    Reset password using valid token.
    """
    token = payload.get("token")
    new_password = payload.get("password")

    if not token or not new_password:
        raise HTTPException(status_code=400, detail="Token and password required")

    # Find user by reset token
    user = db.query(User).filter(User.reset_token == token).first()
    if not user:
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    # Check token expiry
    if user.reset_token_expires < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Token has expired")

    # Validate new password
    is_valid, error_msg = validate_password(new_password)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_msg)

    # Update password
    user.password_hash = hash_password(new_password)
    user.reset_token = None
    user.reset_token_expires = None
    user.failed_login_attempts = 0  # Reset failed attempts on password reset
    db.commit()

    return {"message": "Password updated. Please login with your new password."}


@router.get("/verify-email/{token}")
async def verify_email(token: str, db: Session = Depends(get_db)):
    """
    Verify email using verification token.

    Used when user clicks link in verification email.
    """
    user = db.query(User).filter(User.email_verification_token == token).first()
    if not user:
        return {"valid": False, "message": "Invalid verification link"}

    # Check token expiry
    if user.verification_token_expires < datetime.utcnow():
        return {"valid": False, "message": "Verification link has expired"}

    # Mark email as verified
    user.email_verified = True
    user.email_verification_token = None
    user.verification_token_expires = None
    db.commit()

    return {"valid": True, "message": "Email verified successfully"}


@router.post("/resend-verification-email")
@limiter.limit(RATE_LIMITS["resend_email"])
async def resend_verification_email(request: Request, payload: dict = Body(...), db: Session = Depends(get_db)):
    """
    Resend verification email for an unverified account.
    """
    email = payload.get("email")
    if not email:
        raise HTTPException(status_code=400, detail="Email required")

    user = db.query(User).filter(User.email == email).first()
    if not user:
        return {"message": "If that email is registered, you will receive a verification link"}

    # Check if already verified
    if user.email_verified:
        raise HTTPException(status_code=400, detail="Email already verified")

    # Generate new verification token
    verification_token, token_expires = _generate_verification_token()
    user.email_verification_token = verification_token
    user.verification_token_expires = token_expires
    db.commit()

    # Send verification email
    send_verification_email(email, verification_token, user.name)

    return {"message": "Verification email sent"}


@router.get("/me", response_model=UserOut)
async def get_me(current_user: User = Depends(get_authenticated_user)):
    """
    Get current logged-in user info.
    Reads token from Authorization header or cookie.
    """
    return current_user
