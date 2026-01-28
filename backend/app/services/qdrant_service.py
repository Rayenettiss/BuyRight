"""
Qdrant service - CORE HACKATHON FOCUS
Handles vector database operations with named vectors and quantization.
"""

from typing import Optional, Dict, Any
from qdrant_client import QdrantClient
from qdrant_client.models import (
    VectorParams,
    Distance,
    ScalarQuantization,
    ScalarQuantizationConfig,
    CollectionInfo,
)

from config.settings import settings


class QdrantService:
    """
    Qdrant client wrapper with connection management and collection operations.
    """
    
    def __init__(self):
        self._client: Optional[QdrantClient] = None
    
    def get_client(self) -> QdrantClient:
        """
        Get or create Qdrant client instance (singleton pattern).
        
        Returns:
            QdrantClient instance
        """
        if self._client is None:
            self._client = QdrantClient(
                url=settings.qdrant_url,
                api_key=settings.qdrant_api_key,
                https=settings.qdrant_use_https,
                timeout=settings.qdrant_timeout
            )
        return self._client
    
    def check_connection(self) -> Dict[str, Any]:
        """
        Check Qdrant connection and return server info.
        
        Returns:
            Dict with connection status and server details
        """
        try:
            client = self.get_client()
            collections = client.get_collections()
            return {
                "status": "connected",
                "url": settings.qdrant_url,
                "collections_count": len(collections.collections),
                "collections": [col.name for col in collections.collections]
            }
        except Exception as e:
            return {
                "status": "error",
                "url": settings.qdrant_url,
                "error": str(e)
            }
    
    def create_financial_products_collection(self) -> Dict[str, str]:
        """
        Create financial products collection with named vectors and INT8 quantization.
        
        Named vectors:
        - text_vector: text-embedding-004 (3072-dim)
        - image_vector: multimodalembedding@001 (1408-dim)
        
        Uses scalar INT8 quantization for memory efficiency.
        
        Returns:
            Dict with creation status
        """
        client = self.get_client()
        collection_name = settings.qdrant_collection_name
        
        # Check if collection already exists
        try:
            existing = client.get_collection(collection_name)
            return {
                "status": "exists",
                "collection_name": collection_name,
                "message": f"Collection '{collection_name}' already exists"
            }
        except Exception:
            pass  # Collection doesn't exist, proceed to create
        
        # Create collection with named vectors
        client.create_collection(
            collection_name=collection_name,
            vectors_config={
                # Text embeddings from Vertex AI text-embedding-004 (3072-dim)
                "text_vector": VectorParams(
                    size=settings.text_embedding_dim,
                    distance=Distance.COSINE,
                    on_disk=False,  # Keep in memory for performance
                ),
                # Image embeddings from Vertex AI multimodalembedding@001 (1408-dim)
                "image_vector": VectorParams(
                    size=settings.image_embedding_dim,
                    distance=Distance.COSINE,
                    on_disk=False,
                ),
            },
            # INT8 Scalar Quantization for memory efficiency (HACKATHON FOCUS)
            quantization_config=ScalarQuantization(
                scalar=ScalarQuantizationConfig(
                    type="int8",
                    quantile=0.99,
                    always_ram=True,
                )
            ),
        )
        
        return {
            "status": "created",
            "collection_name": collection_name,
            "message": f"Collection '{collection_name}' created successfully",
            "vectors": {
                "text_vector": f"{settings.text_embedding_dim}-dim (COSINE)",
                "image_vector": f"{settings.image_embedding_dim}-dim (COSINE)",
            },
            "quantization": "INT8 Scalar (99th percentile)"
        }
    
    def get_collection_info(self) -> Dict[str, Any]:
        """
        Get detailed information about the financial products collection.
        
        Returns:
            Dict with collection metadata and stats
        """
        try:
            client = self.get_client()
            collection_name = settings.qdrant_collection_name
            
            # Get collection info
            info: CollectionInfo = client.get_collection(collection_name)
            
            # Count points in collection
            count_result = client.count(collection_name)
            points_count = count_result.count if hasattr(count_result, 'count') else 0
            
            return {
                "status": "ok",
                "collection_name": collection_name,
                "points_count": points_count,
                "segments_count": len(info.segments) if hasattr(info, 'segments') else 0,
                "status_info": info.status.value if hasattr(info, 'status') else "unknown",
                "optimizer_status": info.optimizer_status.value if hasattr(info, 'optimizer_status') else "unknown",
                "vectors_config": {
                    "text_vector": {
                        "size": settings.text_embedding_dim,
                        "distance": "COSINE"
                    },
                    "image_vector": {
                        "size": settings.image_embedding_dim,
                        "distance": "COSINE"
                    }
                },
                "quantization_config": {
                    "type": "INT8",
                    "quantile": 0.99,
                    "always_ram": True
                }
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }


# Global instance
qdrant_service = QdrantService()


# Dependency for FastAPI routes
def get_qdrant() -> QdrantService:
    """
    Dependency injection for Qdrant service.
    
    Usage:
        @router.get("/endpoint")
        def my_route(qdrant: QdrantService = Depends(get_qdrant)):
            ...
    """
    return qdrant_service