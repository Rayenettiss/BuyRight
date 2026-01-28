"""
Ingestion schemas - Pydantic models for product ingestion.
"""

from typing import Optional
from pydantic import BaseModel, Field, HttpUrl, field_validator
from decimal import Decimal


class ProductCreate(BaseModel):
    """
    Schema for creating a new product.
    Used for both single product ingestion and CSV parsing.
    """
    title: str = Field(..., min_length=1, max_length=500, description="Product title")
    url: str = Field(..., description="Product URL (must be unique)")
    description: Optional[str] = Field(None, description="Product description")
    price: Optional[Decimal] = Field(None, ge=0, description="Product price")
    currency: str = Field(default="TND", max_length=3, description="Currency code (TND, USD, EUR)")
    brand: Optional[str] = Field(None, max_length=200, description="Brand name")
    category: Optional[str] = Field(None, max_length=200, description="Product category")
    image_url: Optional[str] = Field(None, description="Image URL")
    source: str = Field(default="manual", max_length=50, description="Source platform")
    stars: Optional[Decimal] = Field(None, ge=0, le=5, description="Rating (0-5)")
    reviews_count: Optional[int] = Field(default=0, ge=0, description="Number of reviews")
    
    @field_validator('url')
    @classmethod
    def validate_url(cls, v: str) -> str:
        """Ensure URL is not empty and has reasonable length."""
        if not v or not v.strip():
            raise ValueError("URL cannot be empty")
        if len(v) > 1000:
            raise ValueError("URL too long (max 1000 characters)")
        return v.strip()
    
    @field_validator('currency')
    @classmethod
    def validate_currency(cls, v: str) -> str:
        """Ensure currency is uppercase."""
        return v.upper()
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "Apple iPhone 15 Pro Max 256GB",
                "url": "https://example.com/products/iphone-15-pro-max",
                "description": "Latest iPhone with titanium design and A17 Pro chip",
                "price": 1199.99,
                "currency": "USD",
                "brand": "Apple",
                "category": "Electronics",
                "image_url": "https://example.com/images/iphone-15.jpg",
                "source": "amazon",
                "stars": 4.8,
                "reviews_count": 1523
            }
        }


class ProductIngestResponse(BaseModel):
    """
    Response schema for product ingestion.
    """
    status: str = Field(..., description="success or error")
    message: str = Field(..., description="Human-readable message")
    product_id: Optional[str] = Field(None, description="UUID of created/updated product")
    is_new: bool = Field(default=True, description="True if created, False if updated")
    
    # Debug upsert testing fields (only present if DEBUG_UPSERT_TESTING=True)
    chunk_count: Optional[int] = Field(None, description="Number of chunks created")
    upserted_points: Optional[int] = Field(None, description="Number of points upserted to Qdrant")
    has_image_embedding: Optional[bool] = Field(None, description="Whether image was embedded")
    upsert_error: Optional[str] = Field(None, description="Error during upsert (if any)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "message": "Product created and upserted to Qdrant",
                "product_id": "123e4567-e89b-12d3-a456-426614174000",
                "is_new": True,
                "chunk_count": 3,
                "upserted_points": 3,
                "has_image_embedding": True,
                "upsert_error": None
            }
        }


class CSVIngestResponse(BaseModel):
    """
    Response schema for CSV bulk ingestion.
    """
    status: str = Field(..., description="success or partial_success or error")
    message: str = Field(..., description="Human-readable message")
    total_rows: int = Field(..., description="Total rows in CSV")
    successful: int = Field(..., description="Successfully ingested products")
    failed: int = Field(..., description="Failed products")
    errors: list[str] = Field(default_factory=list, description="Error messages")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "message": "Bulk ingestion completed",
                "total_rows": 100,
                "successful": 98,
                "failed": 2,
                "errors": ["Row 15: Invalid URL", "Row 47: Missing title"]
            }
        }