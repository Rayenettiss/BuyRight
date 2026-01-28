"""
API route handlers.
"""

from app.routers import health, debug, auth, ingestion

__all__ = [
    "health",
    "debug",
    "auth",
    "ingestion",
]