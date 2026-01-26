from qdrant_client import QdrantClient, models
from qdrant_client.models import Distance, VectorParams, PointStruct
from config.settings import get_settings
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)
settings = get_settings()


class QdrantService:
    def __init__(self):
        self.client = QdrantClient(
            url=settings.qdrant_url,
            api_key=settings.qdrant_api_key,
            timeout=60
        )
        self.collection_name = settings.collection_name
        
    async def init_collection(self):
        """Initialize Qdrant collection with separate named vectors for text and image"""
        try:
            # Check if collection exists
            collections = self.client.get_collections().collections
            collection_exists = any(c.name == self.collection_name for c in collections)
            
            if collection_exists:
                logger.info(f"Collection '{self.collection_name}' already exists")
                return
            
            # Create collection with named vectors
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config={
                    "text": VectorParams(
                        size=settings.text_embedding_dim,
                        distance=Distance.COSINE,
                        on_disk=False
                    ),
                    "image": VectorParams(
                        size=settings.image_embedding_dim,
                        distance=Distance.COSINE,
                        on_disk=False
                    )
                },
                # Scalar quantization for both vectors
                quantization_config=models.ScalarQuantization(
                    scalar=models.ScalarQuantizationConfig(
                        type=models.ScalarType.INT8,
                        quantile=0.99,
                        always_ram=True
                    )
                ),
                # Enable indexing for faster search
                hnsw_config=models.HnswConfigDiff(
                    m=16,
                    ef_construct=100,
                    full_scan_threshold=10000
                )
            )
            
            logger.info(f"Collection '{self.collection_name}' created successfully")
            
        except Exception as e:
            logger.error(f"Error initializing collection: {e}")
            raise
    
    async def upsert_points(self, points: List[PointStruct], batch_size: int = 100):
        """Upsert points to Qdrant in batches"""
        try:
            total_points = len(points)
            
            for i in range(0, total_points, batch_size):
                batch = points[i:i + batch_size]
                self.client.upsert(
                    collection_name=self.collection_name,
                    points=batch,
                    wait=True
                )
                logger.info(f"Upserted batch {i // batch_size + 1} ({len(batch)} points)")
            
            logger.info(f"Successfully upserted {total_points} points")
            return total_points
            
        except Exception as e:
            logger.error(f"Error upserting points: {e}")
            raise
    
    async def health_check(self) -> bool:
        """Check if Qdrant is accessible"""
        try:
            self.client.get_collections()
            return True
        except Exception as e:
            logger.error(f"Qdrant health check failed: {e}")
            return False
    
    async def get_collection_info(self):
        """Get collection information"""
        try:
            return self.client.get_collection(self.collection_name)
        except Exception as e:
            logger.error(f"Error getting collection info: {e}")
            return None


# Singleton instance
qdrant_service = QdrantService()