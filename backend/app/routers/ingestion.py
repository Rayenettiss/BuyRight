"""
Ingestion router - Product ingestion endpoints (single & bulk CSV).
"""

import csv
import io
import logging
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session

from app.dependencies import get_db, get_current_user
from app.models.user import User
from app.schemas.ingestion import ProductCreate, ProductIngestResponse, CSVIngestResponse
from app.services.product_service import create_product, get_product_by_url, update_product
from app.services.embedding_service import embedding_service
from app.services.chunking_service import chunking_service
from app.services.qdrant_service import qdrant_service
from config.settings import settings

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/ingestion",
    tags=["Ingestion"]
)


async def upsert_product_with_chunks(
    product,
    db: Session
) -> dict:
    """
    Helper function to chunk, embed, and upsert a product to Qdrant.
    
    Args:
        product: Product SQLAlchemy model instance
        db: Database session
    
    Returns:
        Dict with upsert results
    """
    try:
        print(f"\n{'='*60}")
        print(f"🔍 DEBUG: Starting upsert for product {product.id}")
        print(f"   Title: {product.title}")
        print(f"   Description length: {len(product.description) if product.description else 0}")
        print(f"   Image URL: {product.image_url}")
        print(f"{'='*60}\n")
        
        # 1. Chunk description if it exists and is long enough
        chunks = []
        if product.description and len(product.description) > 100:
            print(f"📝 Chunking description (length: {len(product.description)})")
            chunks = chunking_service.chunk_product_description(
                description=product.description,
                product_id=str(product.id),
                title=product.title,
                brand=product.brand,
                category=product.category
            )
            print(f"✅ Created {len(chunks)} chunks")
        
        # If no chunks (short or missing description), create a single chunk from title
        if not chunks:
            print(f"⚠️  No chunks from description, creating single chunk from title")
            chunks = [{
                'chunk_idx': 0,
                'text': f"{product.title}. {product.description or ''}".strip(),
                'start_char': 0,
                'end_char': len(product.title),
                'token_count': len(product.title.split()),
                'metadata': {
                    'product_id': str(product.id),
                    'title': product.title,
                    'brand': product.brand,
                    'category': product.category,
                }
            }]
            print(f"✅ Created fallback chunk: {chunks[0]['text'][:100]}...")
        
        logger.info(f"Created {len(chunks)} chunks for product {product.id}")
        
        # 2. Generate text embeddings for each chunk
        print(f"\n🔤 Generating text embeddings...")
        text_embeddings = []
        for i, chunk in enumerate(chunks):
            try:
                print(f"   Embedding chunk {i}/{len(chunks)}: {chunk['text'][:50]}...")
                embedding = embedding_service.get_text_embedding(
                    chunk['text'],
                    task_type="RETRIEVAL_DOCUMENT"
                )
                text_embeddings.append(embedding)
                print(f"   ✅ Chunk {i} embedded: {len(embedding)} dimensions")
            except Exception as e:
                print(f"   ❌ Failed to embed chunk {i}: {e}")
                logger.error(f"Failed to embed chunk {chunk['chunk_idx']}: {e}")
                # Use zero vector as fallback
                text_embeddings.append([0.0] * settings.text_embedding_dim)
                print(f"   ⚠️  Using zero vector fallback")
        
        print(f"✅ Generated {len(text_embeddings)} text embeddings\n")
        logger.info(f"Generated {len(text_embeddings)} text embeddings")
        
        # 3. Generate image embedding if image URL exists
        image_embedding = None
        if product.image_url:
            print(f"🖼️  Generating image embedding from: {product.image_url}")
            try:
                image_embedding = embedding_service.get_image_embedding(
                    product.image_url
                )
                print(f"✅ Image embedded: {len(image_embedding)} dimensions\n")
                logger.info(f"Generated image embedding for product {product.id}")
            except Exception as e:
                print(f"❌ Failed to generate image embedding: {e}\n")
                logger.warning(f"Failed to generate image embedding: {e}")
        else:
            print(f"⚠️  No image URL provided\n")
        
        # 4. Prepare product metadata for Qdrant payload
        product_metadata = {
            "title": product.title,
            "brand": product.brand,
            "category": product.category,
            "price": float(product.price) if product.price else None,
            "currency": product.currency,
            "url": product.url,
            "source": product.source,
        }
        print(f"📦 Product metadata: {product_metadata}\n")
        
        # 5. Delete old chunks (if updating)
        print(f"🗑️  Deleting old chunks for product {product.id}")
        delete_result = qdrant_service.delete_old_product_chunks(product.id)
        print(f"   Result: {delete_result}\n")
        logger.info(f"Delete old chunks result: {delete_result}")
        
        # 6. Upsert to Qdrant
        print(f"⬆️  Upserting to Qdrant...")
        print(f"   - Product ID: {product.id}")
        print(f"   - Chunks: {len(chunks)}")
        print(f"   - Text embeddings: {len(text_embeddings)}")
        print(f"   - Has image embedding: {image_embedding is not None}")
        
        upsert_result = qdrant_service.upsert_product_chunks(
            product_id=product.id,
            chunks=chunks,
            text_embeddings=text_embeddings,
            image_embedding=image_embedding,
            product_metadata=product_metadata
        )
        
        print(f"✅ Upsert result: {upsert_result}\n")
        print(f"{'='*60}\n")
        logger.info(f"Upsert result: {upsert_result}")
        
        return {
            "status": "success",
            "chunk_count": len(chunks),
            "upserted_points": upsert_result.get("chunks_upserted", 0),
            "has_image_embedding": image_embedding is not None,
            "error": None
        }
        
    except Exception as e:
        print(f"\n❌ ERROR in upsert_product_with_chunks: {e}\n")
        logger.error(f"Error in upsert_product_with_chunks: {e}")
        import traceback
        traceback.print_exc()
        return {
            "status": "error",
            "chunk_count": 0,
            "upserted_points": 0,
            "has_image_embedding": False,
            "error": str(e)
        }
@router.post("/product", response_model=ProductIngestResponse)
async def ingest_single_product(
    product_data: ProductCreate,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    """
    Ingest a single product.
    
    Flow:
    1. Check if product exists by URL
    2. Create or update product in PostgreSQL
    3. If DEBUG_UPSERT_TESTING=True: chunk, embed, and upsert to Qdrant
    
    Returns:
        ProductIngestResponse with product info and optional upsert results
    """
    try:
        # Check if product already exists
        existing_product = get_product_by_url(db, product_data.url)
        is_new = existing_product is None
        
        if existing_product:
            # Update existing product
            update_data = product_data.model_dump(exclude_unset=True)
            product = update_product(db, existing_product.id, update_data)
            message = f"Product updated: {product.title}"
        else:
            # Create new product
            product = create_product(
                db=db,
                title=product_data.title,
                url=product_data.url,
                description=product_data.description,
                brand=product_data.brand,
                category=product_data.category,
                price=product_data.price,
                currency=product_data.currency,
                image_url=product_data.image_url,
                stars=product_data.stars,
                reviews_count=product_data.reviews_count,
                source=product_data.source,
            )
            message = f"Product created: {product.title}"
        
        # Prepare response
        response = ProductIngestResponse(
            status="success",
            message=message,
            product_id=str(product.id),
            is_new=is_new
        )
        
        # If debug upsert testing is enabled, chunk/embed/upsert
        if settings.debug_upsert_testing:
            logger.info(f"DEBUG_UPSERT_TESTING enabled, upserting product {product.id}")
            upsert_result = await upsert_product_with_chunks(product, db)
            
            # Add upsert results to response
            response.chunk_count = upsert_result.get("chunk_count")
            response.upserted_points = upsert_result.get("upserted_points")
            response.has_image_embedding = upsert_result.get("has_image_embedding")
            response.upsert_error = upsert_result.get("error")
            
            if upsert_result.get("error"):
                response.message += f" (Upsert failed: {upsert_result['error']})"
            else:
                response.message += f" and upserted {upsert_result['upserted_points']} points to Qdrant"
        
        return response
        
    except Exception as e:
        logger.error(f"Error ingesting product: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to ingest product: {str(e)}"
        )


@router.post("/csv", response_model=CSVIngestResponse)
async def ingest_csv(
    file: UploadFile = File(..., description="CSV file with product data"),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    """
    Bulk ingest products from CSV file.
    
    Expected CSV columns:
    - title (required)
    - url (required)
    - description
    - price
    - currency
    - brand
    - category
    - image_url (or imageurl)
    - source
    - stars
    - reviews_count (or reviewsCount)
    
    Flow:
    1. Parse CSV
    2. Batch create/update products in PostgreSQL
    3. Batch chunk/embed/upsert to Qdrant (no debug mode in bulk)
    
    Returns:
        CSVIngestResponse with ingestion statistics
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be a CSV"
        )
    
    try:
        # Read CSV content
        contents = await file.read()
        csv_text = contents.decode('utf-8')
        csv_reader = csv.DictReader(io.StringIO(csv_text))
        
        total_rows = 0
        successful = 0
        failed = 0
        errors = []
        products_to_upsert = []
        
        for row_num, row in enumerate(csv_reader, start=2):  # Start at 2 (header is row 1)
            total_rows += 1
            
            try:
                # Map CSV columns (handle variations)
                title = row.get('title', '').strip()
                url = row.get('url', '').strip()
                
                if not title or not url:
                    raise ValueError("Missing required fields: title and url")
                
                # Parse optional fields
                price_str = row.get('price', '').strip()
                price = float(price_str) if price_str else None
                
                stars_str = row.get('stars', '').strip()
                stars = float(stars_str) if stars_str else None
                
                reviews_str = row.get('reviews_count') or row.get('reviewsCount') or row.get('reviews Count') or '0'
                reviews_count = int(reviews_str.strip()) if reviews_str.strip() else 0
                
                # Handle image_url variations
                image_url = row.get('image_url') or row.get('imageurl') or row.get('imageUrl') or None
                if image_url:
                    image_url = image_url.strip()
                
                # Create product data
                product_data = ProductCreate(
                    title=title,
                    url=url,
                    description=row.get('description', '').strip() or None,
                    price=price,
                    currency=row.get('currency', 'TND').strip() or 'TND',
                    brand=row.get('brand', '').strip() or None,
                    category=row.get('category', '').strip() or None,
                    image_url=image_url,
                    source=row.get('source', 'csv').strip() or 'csv',
                    stars=stars,
                    reviews_count=reviews_count
                )
                
                # Check if exists
                existing = get_product_by_url(db, product_data.url)
                
                if existing:
                    # Update
                    update_data = product_data.model_dump(exclude_unset=True)
                    product = update_product(db, existing.id, update_data)
                else:
                    # Create
                    product = create_product(
                        db=db,
                        title=product_data.title,
                        url=product_data.url,
                        description=product_data.description,
                        brand=product_data.brand,
                        category=product_data.category,
                        price=product_data.price,
                        currency=product_data.currency,
                        image_url=product_data.image_url,
                        stars=product_data.stars,
                        reviews_count=product_data.reviews_count,
                        source=product_data.source,
                    )
                
                # Queue for batch upsert
                products_to_upsert.append(product)
                successful += 1
                
            except Exception as e:
                failed += 1
                error_msg = f"Row {row_num}: {str(e)}"
                errors.append(error_msg)
                logger.error(error_msg)
        
        # Batch upsert to Qdrant
        logger.info(f"Starting batch upsert of {len(products_to_upsert)} products to Qdrant")
        
        for product in products_to_upsert:
            try:
                await upsert_product_with_chunks(product, db)
            except Exception as e:
                logger.error(f"Failed to upsert product {product.id}: {e}")
                # Don't fail the whole batch, just log
        
        # Determine status
        if failed == 0:
            status_text = "success"
            message = f"Successfully ingested {successful} products"
        elif successful > 0:
            status_text = "partial_success"
            message = f"Ingested {successful} products, {failed} failed"
        else:
            status_text = "error"
            message = f"All {total_rows} products failed"
        
        return CSVIngestResponse(
            status=status_text,
            message=message,
            total_rows=total_rows,
            successful=successful,
            failed=failed,
            errors=errors[:10]  # Limit to first 10 errors
        )
        
    except Exception as e:
        logger.error(f"Error processing CSV: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process CSV: {str(e)}"
        )