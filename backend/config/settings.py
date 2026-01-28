"""
Application configuration using Pydantic BaseSettings.
Loads environment variables from .env file.
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    Expanding with Qdrant and Vertex AI configuration.
    """
    
    # Database (Direct URL format)
    database_url: str
    
    # Qdrant (CORE - HACKATHON FOCUS)
    qdrant_url: str = "http://localhost:6333"
    qdrant_api_key: Optional[str] = None
    qdrant_collection_name: str = "financial_products"
    qdrant_use_https: bool = False
    qdrant_timeout: int = 30  # ✅ Added timeout setting
    
    # Vertex AI Embeddings (PRIMARY - NO FALLBACK)
    google_cloud_project: str
    google_application_credentials: str
    vertex_ai_location: str = "us-central1"
    text_embedding_model: str = "text-embedding-004"
    image_embedding_model: str = "multimodalembedding@001"
    
    # Vector Dimensions - text-embedding-004 supports up to 3072 dimensions
    text_embedding_dim: int = 3072  # Output dimension
    text_embedding_dimensions: int = 3072  # API parameter for dimensionality
    image_embedding_dim: int = 1408  # Multimodal embedding dimension
    
    # Authentication
    secret_key: str
    
    # Application
    debug: bool = False
    environment: str = "development"
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False
    }


# Global settings instance
settings = Settings()