from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID


class NormalizedProduct(BaseModel):
    """Normalized product schema"""
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    currency: Optional[str] = "USD"
    url: Optional[str] = None
    image_url: Optional[str] = None
    source: str
    original_id: Optional[str] = None
    brand: Optional[str] = None
    stars: Optional[float] = None
    reviews_count: Optional[int] = None
    category: Optional[str] = None


class ProductChunk(BaseModel):
    """Chunked product data for embedding"""
    product_id: str
    chunk_index: int
    text_content: str
    title: Optional[str] = None
    price: Optional[float] = None
    currency: Optional[str] = None
    url: Optional[str] = None
    image_url: Optional[str] = None
    source: str
    original_id: Optional[str] = None
    brand: Optional[str] = None
    stars: Optional[float] = None
    reviews_count: Optional[int] = None
    category: Optional[str] = None


class IngestionResponse(BaseModel):
    """Response model for ingestion endpoint"""
    status: str
    message: str
    total_products: int
    total_points: int
    points_with_text: int
    points_with_image: int
    errors: List[str] = Field(default_factory=list)


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    qdrant_connected: bool
    vertex_ai_configured: bool