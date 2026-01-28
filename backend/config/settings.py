"""
Application configuration using Pydantic BaseSettings.
Loads environment variables from .env file.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
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
    qdrant_timeout: int = 30
    
    # Vertex AI Embeddings (PRIMARY - NO FALLBACK)
    # Either vertex_project_id OR google_cloud_project must be provided
    vertex_project_id: Optional[str] = None
    google_cloud_project: Optional[str] = None
    google_application_credentials: str
    vertex_ai_location: str = "us-central1"
    text_embedding_model: str = "text-embedding-004"
    image_embedding_model: str = "multimodalembedding@001"
    
    # Vector Dimensions - text-embedding-004 supports up to 3072 dimensions
    text_embedding_dim: int = 3072  # Output dimension
    text_embedding_dimensions: int = 3072  # API parameter for dimensionality
    image_embedding_dim: int = 1408  # Multimodal embedding dimension
    
    # Chunking Configuration
    max_chunk_size: int = 512  # Maximum tokens per chunk
    chunk_overlap: int = 50  # Overlap between chunks
    
    # Debug & Testing
    debug_upsert_testing: bool = False  # Enable automatic upsert testing on single product ingestion
    
    # JWT Authentication
    secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440
    
    # Application
    debug: bool = False
    environment: str = "development"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"  # Ignore extra fields in .env
    )
    
    @property
    def project_id(self) -> str:
        """Get project ID (prefer vertex_project_id, fallback to google_cloud_project)."""
        project = self.vertex_project_id or self.google_cloud_project
        if not project:
            raise ValueError(
                "Either VERTEX_PROJECT_ID or GOOGLE_CLOUD_PROJECT must be set in .env"
            )
        return project


# Global settings instance
settings = Settings()