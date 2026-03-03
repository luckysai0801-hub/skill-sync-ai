"""
utils/auth_deps.py - Dependency functions for route protection.
Reads JWT from Authorization: Bearer header first, then falls back to cookie.
"""

from fastapi import Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from database import get_db
from models.user import User, UserRole
from utils.jwt_utils import decode_token


async def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    """
    Get current authenticated user.
    Reads token from Authorization: Bearer header first, then falls back to cookie.
    """
    # Try Authorization header first (reliable in dev, avoids cookie issues)
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        access_token = auth_header[7:]
    else:
        access_token = request.cookies.get("access_token")

    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = decode_token(access_token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired or invalid",
        )

    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token missing user ID",
        )

    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled",
        )

    return user


async def get_current_verified_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Ensure user is authenticated AND email is verified."""
    if not current_user.email_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Please verify your email to access this feature",
        )
    return current_user


async def require_candidate(
    current_user: User = Depends(get_current_verified_user),
) -> User:
    """Ensure user is a CANDIDATE."""
    if current_user.role != UserRole.candidate:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This action requires a candidate account",
        )
    return current_user


async def require_employer(
    current_user: User = Depends(get_current_verified_user),
) -> User:
    """Ensure user is an EMPLOYER."""
    if current_user.role != UserRole.employer:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This action requires an employer account",
        )
    return current_user
