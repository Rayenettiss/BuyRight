"""
Health check router - provides system status endpoint.
"""

from fastapi import APIRouter
from app.services.health_service import get_health_status

router = APIRouter(
    prefix="/health",
    tags=["Health"]
)


@router.get("")
async def health_check():
    """
    Health check endpoint.
    
    Returns:
        System health status
    """
    return get_health_status()