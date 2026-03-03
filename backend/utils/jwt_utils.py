"""
utils/jwt_utils.py - JWT token creation, verification, and decoding.
Handles both access tokens (short-lived) and refresh tokens (long-lived).
"""

import os
from datetime import datetime, timedelta
from typing import Optional, Dict
import jwt

# Config from environment
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 15))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 7))


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a short-lived JWT access token (default 15 minutes).

    Args:
        data: Dictionary of claims to encode (typically {"sub": user_id})
        expires_delta: Custom expiration time, defaults to ACCESS_TOKEN_EXPIRE_MINUTES

    Returns:
        Encoded JWT token as string
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire, "type": "access"})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a long-lived JWT refresh token (default 7 days).

    Args:
        data: Dictionary of claims to encode (typically {"sub": user_id})
        expires_delta: Custom expiration time, defaults to REFRESH_TOKEN_EXPIRE_DAYS

    Returns:
        Encoded JWT token as string
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

    to_encode.update({"exp": expire, "type": "refresh"})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> Optional[Dict]:
    """
    Decode and verify a JWT token.

    Args:
        token: JWT token string to decode

    Returns:
        Decoded token payload (dictionary) if valid, None if invalid/expired
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None  # Token has expired
    except jwt.InvalidTokenError:
        return None  # Token is invalid


def verify_token_expiry(payload: dict) -> bool:
    """
    Check if a token payload is expired.

    Args:
        payload: Decoded JWT payload dictionary

    Returns:
        True if token is still valid, False if expired
    """
    if "exp" not in payload:
        return False

    exp_timestamp = payload["exp"]
    current_timestamp = datetime.utcnow().timestamp()

    return current_timestamp <= exp_timestamp
