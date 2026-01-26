from fastapi import APIRouter, UploadFile, File, HTTPException
from app.models.product import IngestionResponse
from app.services.qdrant import qdrant_service
from app.services.embedding import embedding_service
from app.services.utils import (
    normalize_csv_data,
    extract_source_from_filename,
    chunk_product_text,
    download_images_batch
)
from qdrant_client.models import PointStruct
import pandas as pd
import uuid
import logging
from typing import List

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/ingest", tags=["ingestion"])


@router.post("/products", response_model=IngestionResponse)
async def ingest_products(file: UploadFile = File(...)):
    """
    Ingest products from CSV or XLSX file.
    
    Processes CSV/XLSX with varying column structures, normalizes data,
    generates separate text and image embeddings, and stores in Qdrant.
    """
    errors = []
    
    try:
        # Validate file type
        if not (file.filename.endswith('.csv') or file.filename.endswith('.xlsx')):
            raise HTTPException(status_code=400, detail="Only CSV and XLSX files are accepted")
        
        # Read file based on extension
        try:
            contents = await file.read()
            
            if file.filename.endswith('.csv'):
                df = pd.read_csv(pd.io.common.BytesIO(contents))
            else:  # .xlsx
                df = pd.read_excel(pd.io.common.BytesIO(contents))
            
            logger.info(f"Loaded file with {len(df)} rows and columns: {df.columns.tolist()}")
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error reading file: {str(e)}")
        
        # Extract source from filename
        source = extract_source_from_filename(file.filename)
        
        # Normalize data
        normalized_products = normalize_csv_data(df, source)
        logger.info(f"Normalized {len(normalized_products)} products")
        
        if not normalized_products:
            raise HTTPException(status_code=400, detail="No valid products found in CSV")
        
        # Generate chunks for each product
        all_chunks = []
        product_ids = []
        
        for product in normalized_products:
            product_id = str(uuid.uuid4())
            product_ids.append(product_id)
            
            chunks = chunk_product_text(product, product_id)
            
            # If no chunks (no text content), create one chunk with metadata only
            if not chunks:
                from app.models.product import ProductChunk
                chunks = [ProductChunk(
                    product_id=product_id,
                    chunk_index=0,
                    text_content="",
                    title=product.title,
                    price=product.price,
                    currency=product.currency,
                    url=product.url,
                    image_url=product.image_url,
                    source=product.source,
                    original_id=product.original_id
                )]
            
            all_chunks.extend(chunks)
        
        logger.info(f"Created {len(all_chunks)} chunks from {len(normalized_products)} products")
        
        # Generate text embeddings (batch processing)
        text_contents = [chunk.text_content for chunk in all_chunks]
        text_embeddings = await embedding_service.embed_text_batch(text_contents)
        
        # Collect unique image URLs
        image_urls = list(set([
            chunk.image_url for chunk in all_chunks 
            if chunk.image_url and chunk.image_url.strip()
        ]))
        
        # Download images
        logger.info(f"Downloading {len(image_urls)} unique images")
        image_data = await download_images_batch(image_urls)
        
        # Generate image embeddings
        image_embeddings_map = {}
        for url, img_bytes in image_data.items():
            if img_bytes:
                embedding = await embedding_service.embed_image(img_bytes)
                if embedding:
                    image_embeddings_map[url] = embedding
        
        logger.info(f"Generated {len(image_embeddings_map)} image embeddings")
        
        # Create Qdrant points
        points = []
        points_with_text = 0
        points_with_image = 0
        
        for i, chunk in enumerate(all_chunks):
            point_id = str(uuid.uuid4())
            
            # Prepare vectors
            vectors = {}
            
            # Add text vector if available
            if text_embeddings[i]:
                vectors["text"] = text_embeddings[i]
                points_with_text += 1
            
            # Add image vector if available (only for first chunk of each product)
            if chunk.chunk_index == 0 and chunk.image_url in image_embeddings_map:
                vectors["image"] = image_embeddings_map[chunk.image_url]
                points_with_image += 1
            
            # Skip if no vectors
            if not vectors:
                errors.append(f"No embeddings for product {chunk.product_id} chunk {chunk.chunk_index}")
                continue
            
            # Create payload
            payload = {
                "product_id": chunk.product_id,
                "chunk_index": chunk.chunk_index,
                "text_content": chunk.text_content,
                "title": chunk.title,
                "price": chunk.price,
                "currency": chunk.currency,
                "url": chunk.url,
                "image_url": chunk.image_url,
                "source": chunk.source,
                "original_id": chunk.original_id,
                "brand": chunk.brand,
                "stars": chunk.stars,
                "reviews_count": chunk.reviews_count,
                "category": chunk.category
            }
            
            # Create point
            point = PointStruct(
                id=point_id,
                vector=vectors,
                payload=payload
            )
            
            points.append(point)
        
        # Upsert to Qdrant
        if points:
            await qdrant_service.upsert_points(points)
            logger.info(f"Successfully upserted {len(points)} points to Qdrant")
        else:
            raise HTTPException(status_code=400, detail="No valid points to insert")
        
        return IngestionResponse(
            status="success",
            message=f"Successfully ingested {len(normalized_products)} products",
            total_products=len(normalized_products),
            total_points=len(points),
            points_with_text=points_with_text,
            points_with_image=points_with_image,
            errors=errors
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during ingestion: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")