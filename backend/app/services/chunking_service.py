"""
Chunking service - Semantic text chunking using Chonkie.
Splits long product descriptions into manageable chunks.
"""

from typing import List, Dict, Any, Optional  # ✅ Added Optional import
from chonkie import SemanticChunker

from config.settings import settings


class ChunkingService:
    """
    Service for chunking long text into smaller semantic pieces.
    Uses Chonkie for intelligent text splitting.
    """
    
    def __init__(self):
        # Initialize Chonkie semantic chunker
        self.chunker = SemanticChunker(
            chunk_size=settings.max_chunk_size,
            chunk_overlap=settings.chunk_overlap,
        )
    
    def chunk_text(
        self,
        text: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Chunk text into smaller semantic pieces.
        
        Args:
            text: Text to chunk (e.g., product description)
            metadata: Optional metadata to attach to each chunk
        
        Returns:
            List of chunk dictionaries with format:
            [
                {
                    'chunk_idx': 0,
                    'text': 'chunk text...',
                    'start_char': 0,
                    'end_char': 100,
                    'metadata': {...}
                },
                ...
            ]
        """
        if not text or not text.strip():
            return []
        
        # Use Chonkie to create semantic chunks
        chunks = self.chunker.chunk(text.strip())
        
        # Format chunks with metadata
        formatted_chunks = []
        for idx, chunk in enumerate(chunks):
            chunk_dict = {
                'chunk_idx': idx,
                'text': chunk.text,
                'start_char': chunk.start_index,
                'end_char': chunk.end_index,
                'token_count': len(chunk.text.split()),  # Approximate token count
            }
            
            # Add metadata if provided
            if metadata:
                chunk_dict['metadata'] = metadata
            
            formatted_chunks.append(chunk_dict)
        
        return formatted_chunks
    
    def chunk_product_description(
        self,
        description: str,
        product_id: str,
        title: str,
        brand: Optional[str] = None,
        category: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Chunk product description with product metadata.
        
        Args:
            description: Product description text
            product_id: Product UUID
            title: Product title
            brand: Product brand
            category: Product category
        
        Returns:
            List of chunks with product metadata
        """
        metadata = {
            'product_id': str(product_id),
            'title': title,
            'brand': brand,
            'category': category,
        }
        
        chunks = self.chunk_text(description, metadata)
        
        # Add title as context to first chunk if exists
        if chunks and title:
            chunks[0]['context'] = f"Product: {title}"
        
        return chunks


# Global instance
chunking_service = ChunkingService()