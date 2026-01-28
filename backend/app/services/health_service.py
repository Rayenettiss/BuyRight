"""
Health check service - monitors system status.
"""

from typing import Dict, Any


def get_health_status() -> Dict[str, Any]:
    """
    Return simple health status.
    Can be extended to check database, Qdrant, etc.
    
    Returns:
        Dict with status and version info
    """
    return {
        "status": "ok",
        "service": "Product Recommendation API",
        "version": "1.0.0"
    }