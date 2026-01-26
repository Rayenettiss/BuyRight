from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Qdrant Configuration
    qdrant_url: str
    qdrant_api_key: str
    
    # Google Cloud Configuration
    gcp_project_id: str
    gcp_location: str = "us-central1"
    vertex_ai_api_key: str
    google_application_credentials: str = ""  # Optional, can be empty if using API key
    
    # Collection Configuration
    collection_name: str = "financial_products_vertex"
    
    # Embedding Configuration
    text_embedding_model: str = "text-embedding-004"
    image_embedding_model: str = "multimodalembedding@001"
    text_embedding_dim: int = 3072
    image_embedding_dim: int = 1408
    
    # Chunking Configuration
    chunk_size: int = 2000
    chunk_overlap: int = 200
    
    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    return Settings()