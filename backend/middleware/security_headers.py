"""
middleware/security_headers.py - HTTP security headers middleware.

NOTE: Strict-Transport-Security (HSTS) is intentionally NOT set in dev mode.
HSTS on localhost permanently forces HTTPS, breaking all HTTP connections.
Enable it only on production HTTPS via an env variable ENVIRONMENT=production.
"""

import os
from fastapi import Request
from fastapi.responses import Response

IS_PRODUCTION = os.getenv("ENVIRONMENT", "development") == "production"


async def add_security_headers(request: Request, call_next) -> Response:
    """
    Middleware to add security headers to all HTTP responses.
    """
    response = await call_next(request)

    # Prevent clickjacking attacks
    response.headers["X-Frame-Options"] = "DENY"

    # Prevent MIME type sniffing
    response.headers["X-Content-Type-Options"] = "nosniff"

    # Enable XSS protection in browsers
    response.headers["X-XSS-Protection"] = "1; mode=block"

    # HSTS only in production (NEVER on localhost - permanently breaks HTTP)
    if IS_PRODUCTION:
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

    # Content Security Policy - allows Swagger UI CDN assets + local dev
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net; "
        "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://fonts.googleapis.com; "
        "img-src 'self' data: https:; "
        "font-src 'self' https://fonts.googleapis.com https://fonts.gstatic.com https://cdn.jsdelivr.net; "
        "connect-src 'self' http://localhost:8000 http://localhost:5173 https://api.skillsync.com"
    )

    # Referrer Policy
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

    # Prevent caching of sensitive responses
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"

    return response
