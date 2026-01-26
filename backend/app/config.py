"""
Configuration Management for BuyRight Backend
Hackathon Deliverable: Non-Functional Requirements - Security, Observability
"""
from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """
    Centralized configuration using Pydantic for type safety and validation.
    Loads from environment variables with .env file support.
    """
    
    # Application
    APP_NAME: str = "BuyRight FinCommerce Intelligence Engine"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "production"
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Database - PostgreSQL (Source of Truth)
    DATABASE_URL: str
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 10
    
    # Qdrant Vector Database (Mandatory for Hackathon)
    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6333
    QDRANT_API_KEY: str = ""
    QDRANT_COLLECTION_PRODUCTS: str = "products"
    QDRANT_COLLECTION_USER_PROFILES: str = "user_profiles"
    QDRANT_USE_HTTPS: bool = False
    
    # Vector Dimensions
    TEXT_EMBEDDING_DIM: int = 768  # text-embedding-004
    IMAGE_EMBEDDING_DIM: int = 768  # multimodalembedding@001
    USER_PROFILE_EMBEDDING_DIM: int = 512  # Aggregated user preferences
    
    # Google Cloud - Vertex AI (Multimodal Embeddings)
    GOOGLE_CLOUD_PROJECT: str
    GOOGLE_APPLICATION_CREDENTIALS: str
    VERTEX_AI_LOCATION: str = "us-central1"
    TEXT_EMBEDDING_MODEL: str = "text-embedding-004"
    IMAGE_EMBEDDING_MODEL: str = "multimodalembedding@001"
    
    # Security (Hackathon: Privacy/Security Requirements)
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080  # 7 days for hackathon demo
    ENCRYPTION_KEY: str  # Fernet key for sensitive financial data
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # Data Processing
    CHUNK_SIZE: int = 512  # Text chunking with chonkie
    CHUNK_OVERLAP: int = 50
    BATCH_SIZE: int = 100  # Batch processing for Qdrant upserts
    MAX_UPLOAD_SIZE_MB: int = 50
    
    # Search Configuration
    DEFAULT_SEARCH_LIMIT: int = 20
    MAX_SEARCH_LIMIT: int = 100
    SIMILARITY_THRESHOLD: float = 0.7
    
    # Logging (Hackathon: Observability)
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    
    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "chrome-extension://*"
    ]
    
    # Privacy & Anonymization (Hackathon: Security/Privacy)
    HASH_SALT: str
    MASK_SENSITIVE_DATA: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = True
    
    @property
    def qdrant_url(self) -> str:
        """Construct Qdrant URL"""
        protocol = "https" if self.QDRANT_USE_HTTPS else "http"
        return f"{protocol}://{self.QDRANT_HOST}:{self.QDRANT_PORT}"
    
    @property
    def database_url_async(self) -> str:
        """Convert sync PostgreSQL URL to async (asyncpg)"""
        if self.DATABASE_URL.startswith("postgresql://"):
            return self.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
        return self.DATABASE_URL


# Global settings instance
settings = Settings()