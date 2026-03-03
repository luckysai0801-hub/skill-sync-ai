"""
utils/password_utils.py - Password hashing, verification, and validation.
Uses bcrypt for secure password hashing with high salt rounds.
"""

import bcrypt
import re

def hash_password(password: str) -> str:
    """
    Hash a plain-text password using bcrypt.

    Args:
        password: Plain-text password to hash

    Returns:
        Bcrypt hashed password string
    """
    salt = bcrypt.gensalt(12)
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain-text password against its bcrypt hash.
    Uses constant-time comparison to prevent timing attacks.

    Args:
        plain_password: Plain-text password from user input
        hashed_password: Bcrypt hash stored in database

    Returns:
        True if password matches, False otherwise
    """
    try:
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    except Exception:
        return False


def validate_password(password: str) -> tuple[bool, str]:
    """
    Validate password meets security requirements:
    - Minimum 8 characters
    - At least 1 uppercase letter
    - At least 1 lowercase letter
    - At least 1 digit
    - At least 1 special character (!@#$%^&*)

    Args:
        password: Password string to validate

    Returns:
        Tuple of (is_valid: bool, error_message: str)
        If valid, returns (True, "")
        If invalid, returns (False, "Error message")
    """
    error_message = ""

    # Check minimum length
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"

    # Check for uppercase letter
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"

    # Check for lowercase letter
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"

    # Check for digit
    if not re.search(r'\d', password):
        return False, "Password must contain at least one digit"

    # Check for special character
    if not re.search(r'[!@#$%^&*]', password):
        return False, "Password must contain at least one special character (!@#$%^&*)"

    return True, ""


def get_password_strength(password: str) -> dict:
    """
    Evaluate password strength and return detailed feedback.

    Args:
        password: Password to evaluate

    Returns:
        Dictionary with strength score (0-5) and feedback list
    """
    feedback = []
    score = 0

    # Length score
    if len(password) >= 8:
        score += 1
        if len(password) >= 12:
            score += 1

    # Character variety
    has_upper = bool(re.search(r'[A-Z]', password))
    has_lower = bool(re.search(r'[a-z]', password))
    has_digit = bool(re.search(r'\d', password))
    has_special = bool(re.search(r'[!@#$%^&*]', password))

    if has_upper:
        score += 1
    else:
        feedback.append("Add uppercase letters")

    if has_lower:
        score += 1
    else:
        feedback.append("Add lowercase letters")

    if has_digit:
        score += 1
    else:
        feedback.append("Add numbers")

    if has_special:
        score += 1
    else:
        feedback.append("Add special characters (!@#$%^&*)")

    # Normalize score to 0-5
    strength_score = min(5, score)

    return {
        "score": strength_score,  # 0-5 scale
        "feedback": feedback,
        "is_strong": strength_score >= 4
    }
