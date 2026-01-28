"""
API route handlers.
"""

from app.routers import health, debug

__all__ = [
    "health",
    "debug",
    "auth",
]