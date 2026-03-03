"""
utils/rate_limiter.py - Rate limiting using slowapi.
Prevents brute force attacks on authentication endpoints.
"""

from slowapi import Limiter
from slowapi.util import get_remote_address

# Initialize rate limiter using IP address as the key
limiter = Limiter(key_func=get_remote_address)

# Rate limit configurations
RATE_LIMITS = {
    "register": "5/hour",           # 5 registrations per hour per IP
    "login": "10/hour",             # 10 login attempts per hour per IP
    "forgot_password": "3/hour",    # 3 password reset requests per hour per IP
    "resend_email": "3/hour",       # 3 verification email resends per hour per IP
    "api_general": "100/minute",    # 100 API calls per minute per IP
}
