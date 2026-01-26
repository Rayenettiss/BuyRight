from google.cloud import aiplatform
from vertexai.vision_models import MultiModalEmbeddingModel, Image
from vertexai.language_models import TextEmbeddingModel
from config.settings import get_settings
from typing import List, Optional
import logging
import base64
import os

logger = logging.getLogger(__name__)
settings = get_settings()


class EmbeddingService:
    def __init__(self):
        # Set credentials if service account JSON is provided
        if settings.google_application_credentials and os.path.exists(settings.google_application_credentials):
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = settings.google_application_credentials
        
        # Initialize Vertex AI with API key
        aiplatform.init(
            project=settings.gcp_project_id,
            location=settings.gcp_location,
            api_key=settings.vertex_ai_api_key if hasattr(settings, 'vertex_ai_api_key') else None
        )
        
        # Initialize models
        self.text_model = TextEmbeddingModel.from_pretrained(settings.text_embedding_model)
        self.image_model = MultiModalEmbeddingModel.from_pretrained(settings.image_embedding_model)
        
        logger.info(f"Initialized embedding models: {settings.text_embedding_model}, {settings.image_embedding_model}")
    
    async def embed_text(self, text: str) -> Optional[List[float]]:
        """Generate text embedding using Vertex AI"""
        try:
            if not text or not text.strip():
                return None
            
            # Truncate if too long (max 20,000 chars for text-embedding-004)
            text = text[:20000]
            
            embeddings = self.text_model.get_embeddings([text])
            
            if embeddings and len(embeddings) > 0:
                return embeddings[0].values
            
            return None
            
        except Exception as e:
            logger.error(f"Error generating text embedding: {e}")
            return None
    
    async def embed_text_batch(self, texts: List[str]) -> List[Optional[List[float]]]:
        """Generate text embeddings for multiple texts"""
        try:
            # Filter out empty texts
            valid_texts = [(i, text[:20000]) for i, text in enumerate(texts) if text and text.strip()]
            
            if not valid_texts:
                return [None] * len(texts)
            
            # Extract just the texts for embedding
            texts_to_embed = [text for _, text in valid_texts]
            
            # Get embeddings (batch size max 5 for Vertex AI)
            batch_size = 5
            all_embeddings = []
            
            for i in range(0, len(texts_to_embed), batch_size):
                batch = texts_to_embed[i:i + batch_size]
                embeddings = self.text_model.get_embeddings(batch)
                all_embeddings.extend([emb.values if emb else None for emb in embeddings])
            
            # Map back to original indices
            result = [None] * len(texts)
            for (original_idx, _), embedding in zip(valid_texts, all_embeddings):
                result[original_idx] = embedding
            
            return result
            
        except Exception as e:
            logger.error(f"Error generating text embeddings batch: {e}")
            return [None] * len(texts)
    
    async def embed_image(self, image_bytes: bytes) -> Optional[List[float]]:
        """Generate image embedding using Vertex AI multimodal model"""
        try:
            if not image_bytes:
                return None
            
            # Create Image object from bytes
            image = Image(image_bytes=image_bytes)
            
            # Get embeddings (image only, no text)
            embeddings = self.image_model.get_embeddings(
                image=image,
                contextual_text=None
            )
            
            if embeddings and embeddings.image_embedding:
                return embeddings.image_embedding
            
            return None
            
        except Exception as e:
            logger.error(f"Error generating image embedding: {e}")
            return None
    
    async def embed_image_from_base64(self, base64_str: str) -> Optional[List[float]]:
        """Generate image embedding from base64 string"""
        try:
            # Decode base64
            image_bytes = base64.b64decode(base64_str)
            return await self.embed_image(image_bytes)
            
        except Exception as e:
            logger.error(f"Error generating image embedding from base64: {e}")
            return None


# Singleton instance
embedding_service = EmbeddingService()