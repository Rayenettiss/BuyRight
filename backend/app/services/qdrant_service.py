"""
Qdrant service - CORE HACKATHON FOCUS
Handles vector database operations with named vectors and quantization.
"""

from typing import Optional, Dict, Any, List
from uuid import UUID
from qdrant_client import QdrantClient
from qdrant_client.models import (
    VectorParams,
    Distance,
    ScalarQuantization,
    ScalarQuantizationConfig,
    ScalarType,
    CollectionInfo,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
    PayloadSchemaType,
)
from uuid import UUID, uuid5, NAMESPACE_DNS

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
                timeout=30
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
        - text_vector: multimodalembedding@001 (1408-dim)
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

        # Correct ScalarQuantization usage
        quantization_config = ScalarQuantization(
            scalar=ScalarQuantizationConfig(
                type=ScalarType.INT8,
                quantile=0.99,
                always_ram=True
            )
        )

        # Create collection with named vectors
        client.create_collection(
            collection_name=collection_name,
            vectors_config={
                "text_vector": VectorParams(
                    size=settings.text_embedding_dim,
                    distance=Distance.COSINE,
                    on_disk=False,
                ),
                "image_vector": VectorParams(
                    size=settings.image_embedding_dim,
                    distance=Distance.COSINE,
                    on_disk=False,
                ),
            },
            quantization_config=quantization_config,
        )
        
        # Create payload index for product_id
        client.create_payload_index(
            collection_name=collection_name,
            field_name="product_id",
            field_schema=PayloadSchemaType.KEYWORD,
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

            info: CollectionInfo = client.get_collection(collection_name)
            points_count = client.count(collection_name).count

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

    def delete_old_product_chunks(self, product_id: UUID) -> Dict[str, Any]:
        """
        Delete all existing chunks for a product before re-upserting.

        Args:
            product_id: Product UUID

        Returns:
            Dict with deletion status
        """
        try:
            client = self.get_client()
            collection_name = settings.qdrant_collection_name

            client.delete(
                collection_name=collection_name,
                points_selector=Filter(
                    must=[
                        FieldCondition(
                            key="product_id",
                            match=MatchValue(value=str(product_id))
                        )
                    ]
                )
            )

            return {
                "status": "success",
                "product_id": str(product_id),
                "message": f"Deleted all chunks for product {product_id}"
            }
        except Exception as e:
            return {
                "status": "error",
                "product_id": str(product_id),
                "error": str(e)
            }

    def upsert_product_chunks(
        self,
        product_id: UUID,
        chunks: List[Dict[str, Any]],
        text_embeddings: List[List[float]],
        image_embedding: Optional[List[float]] = None,
        product_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Upsert product chunks with text and optional image embeddings.

        Args:
            product_id: Product UUID
            chunks: List of chunk dictionaries from chunking_service
            text_embeddings: List of text embeddings (one per chunk)
            image_embedding: Optional image embedding (shared across chunks)
            product_metadata: Additional product metadata (price, brand, etc.)

        Returns:
            Dict with upsert status
        """
        if len(chunks) != len(text_embeddings):
            raise ValueError("Number of chunks must match number of text embeddings")

        try:
            client = self.get_client()
            collection_name = settings.qdrant_collection_name
            points = []

            for chunk, text_emb in zip(chunks, text_embeddings):
                # Use deterministic UUID for chunks
                point_id = str(uuid5(NAMESPACE_DNS, f"{product_id}_chunk_{chunk['chunk_idx']}"))
                payload = {
                    "product_id": str(product_id),
                    "chunk_idx": chunk['chunk_idx'],
                    "text": chunk['text'],
                    "start_char": chunk['start_char'],
                    "end_char": chunk['end_char'],
                }
                if product_metadata:
                    payload.update(product_metadata)
                if 'metadata' in chunk:
                    payload.update(chunk['metadata'])

                vectors = {"text_vector": text_emb}
                if image_embedding:
                    vectors["image_vector"] = image_embedding

                points.append(PointStruct(id=point_id, vector=vectors, payload=payload))

            client.upsert(collection_name=collection_name, points=points)

            return {
                "status": "success",
                "product_id": str(product_id),
                "chunks_upserted": len(points),
                "has_image_embedding": image_embedding is not None
            }

        except Exception as e:
            return {
                "status": "error",
                "product_id": str(product_id),
                "error": str(e)
            }


# Global instance
qdrant_service = QdrantService()


# Dependency for FastAPI routes
def get_qdrant() -> QdrantService:
    """
    Dependency injection for Qdrant service.
    """
    return qdrant_service
