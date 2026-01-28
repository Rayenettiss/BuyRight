"""
Debug router - Development endpoints for testing services.
"""

from fastapi import APIRouter, Depends
from app.services.qdrant_service import QdrantService, get_qdrant

router = APIRouter(
    prefix="/debug",
    tags=["Debug"]
)


@router.get("/qdrant/connection")
async def check_qdrant_connection(
    qdrant: QdrantService = Depends(get_qdrant)
):
    """
    Check Qdrant connection status.
    
    Returns:
        Connection status and server info
    """
    return qdrant.check_connection()


@router.get("/qdrant/collection")
async def get_collection_info(
    qdrant: QdrantService = Depends(get_qdrant)
):
    """
    Get financial products collection information.
    
    Returns:
        Collection metadata and statistics
    """
    return qdrant.get_collection_info()