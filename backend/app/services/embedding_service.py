"""
Embedding service - Vertex AI embeddings for text and images.
Uses multimodalembedding@001 for both text and images.
"""

from typing import List, Union, Optional
import os
from google.cloud import aiplatform
from vertexai.vision_models import MultiModalEmbeddingModel, Image
import requests
from io import BytesIO
from PIL import Image as PILImage

from config.settings import settings


# Initialize Vertex AI
aiplatform.init(
    project=settings.project_id,
    location=settings.vertex_ai_location,
)


class EmbeddingService:
    """
    Vertex AI embedding service for text and images using multimodalembedding@001.
    """
    
    def __init__(self):
        self.multimodal_model = None
    
    def _get_multimodal_model(self) -> MultiModalEmbeddingModel:
        """Get or initialize multimodal embedding model."""
        if self.multimodal_model is None:
            self.multimodal_model = MultiModalEmbeddingModel.from_pretrained(
                settings.text_embedding_model  # Now using multimodalembedding@001
            )
        return self.multimodal_model
    
    def get_text_embedding(
        self,
        text: str,
        task_type: str = "RETRIEVAL_DOCUMENT"
    ) -> List[float]:
        """
        Generate text embedding using Vertex AI multimodalembedding@001.
        
        Args:
            text: Text to embed
            task_type: Task type for embedding (not used by multimodal model)
        
        Returns:
            List of floats (1408-dimensional vector)
        
        Raises:
            Exception: If embedding generation fails
        """
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")
        
        model = self._get_multimodal_model()
        
        # Get embeddings using the multimodal model
        # Note: multimodalembedding@001 uses contextual_text parameter
        embeddings = model.get_embeddings(
            contextual_text=text.strip(),
            dimension=settings.text_embedding_dimensions
        )
        
        if not embeddings or not embeddings.text_embedding:
            raise ValueError("Failed to generate text embedding")
        
        return embeddings.text_embedding
    
    def get_image_embedding(
        self,
        image_source: Union[str, bytes],
        contextual_text: Optional[str] = None
    ) -> List[float]:
        """
        Generate image embedding using Vertex AI multimodalembedding@001.
        
        Args:
            image_source: Either:
                - URL string (http:// or https://)
                - Local file path
                - Bytes (image data)
            contextual_text: Optional text context for the image
        
        Returns:
            List of floats (1408-dimensional vector)
        
        Raises:
            Exception: If embedding generation fails
        """
        model = self._get_multimodal_model()
        
        # Load image based on source type
        if isinstance(image_source, bytes):
            # Image bytes provided
            image = Image(image_bytes=image_source)
        elif isinstance(image_source, str):
            if image_source.startswith(('http://', 'https://')):
                # Download image from URL
                try:
                    response = requests.get(image_source, timeout=10)
                    response.raise_for_status()
                    image = Image(image_bytes=response.content)
                except Exception as e:
                    raise ValueError(f"Failed to download image from URL: {e}")
            else:
                # Load from local file
                if not os.path.exists(image_source):
                    raise ValueError(f"Image file not found: {image_source}")
                image = Image.load_from_file(image_source)
        else:
            raise ValueError("image_source must be URL string, file path, or bytes")
        
        # Get embeddings
        embeddings = model.get_embeddings(
            image=image,
            contextual_text=contextual_text,
            dimension=settings.image_embedding_dim
        )
        
        if not embeddings or not embeddings.image_embedding:
            raise ValueError("Failed to generate image embedding")
        
        return embeddings.image_embedding
    
    def get_combined_text_embedding(
        self,
        title: str,
        description: Optional[str] = None,
        brand: Optional[str] = None,
        category: Optional[str] = None
    ) -> List[float]:
        """
        Generate embedding for combined product text fields.
        
        Args:
            title: Product title
            description: Product description
            brand: Product brand
            category: Product category
        
        Returns:
            List of floats (1408-dimensional vector)
        """
        # Combine text fields
        text_parts = []
        
        if title:
            text_parts.append(f"Title: {title}")
        
        if brand:
            text_parts.append(f"Brand: {brand}")
        
        if category:
            text_parts.append(f"Category: {category}")
        
        if description:
            text_parts.append(f"Description: {description}")
        
        combined_text = "\n".join(text_parts)
        
        return self.get_text_embedding(
            combined_text,
            task_type="RETRIEVAL_DOCUMENT"
        )


# Global instance
embedding_service = EmbeddingService()