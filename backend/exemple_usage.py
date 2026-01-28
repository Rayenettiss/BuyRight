"""
Example: Complete flow from product creation to Qdrant upsert.
"""

from uuid import uuid4
from app.services.product_service import create_product
from app.services.embedding_service import embedding_service
from app.services.chunking_service import chunking_service
from app.services.qdrant_service import qdrant_service
from app.dependencies import SessionLocal

def ingest_product_example():
    """
    Example workflow: Create product → Chunk → Embed → Upsert to Qdrant
    """
    db = SessionLocal()
    
    try:
        # 1. Create product in PostgreSQL
        product = create_product(
            db=db,
            title="Apple iPhone 15 Pro Max 256GB",
            url="https://example.com/iphone-15-pro-max-",
            brand="Apple",
            category="Electronics",
            price=1199.99,
            currency="USD",
            description="""The Apple iPhone 15 Pro Max represents the pinnacle of smartphone technology.
            It features the powerful A17 Pro chip, built on a 3-nanometer process.
            The device boasts a stunning Super Retina XDR display with ProMotion technology.
            Camera capabilities include a 48MP main sensor, ultra-wide, and telephoto lenses.
            Advanced computational photography enables stunning low-light performance.
            The titanium design makes it both durable and lightweight.
            Battery life has been significantly improved over previous generations.
            5G connectivity ensures blazing-fast download and upload speeds.
            """ * 5,
            image_url="https://example.com/images/iphone-15.jpg",
            stars=4.8,
            reviews_count=1523,
            source="amazon"
        )
        print(f"✅ Product created: {product.id}")
        
        # 2. Chunk description
        chunks = chunking_service.chunk_product_description(
            description=product.description,
            product_id=str(product.id),
            title=product.title,
            brand=product.brand,
            category=product.category
        )
        print(f"✅ Created {len(chunks)} chunks")
        
        # 3. Generate text embeddings for each chunk
        text_embeddings = []
        for chunk in chunks:
            embedding = embedding_service.get_text_embedding(chunk['text'])
            text_embeddings.append(embedding)
        print(f"✅ Generated {len(text_embeddings)} text embeddings")
        
        # 4. Generate image embedding (optional)
        image_embedding = None
        if product.image_url:
            try:
                image_embedding = embedding_service.get_image_embedding(product.image_url)
                print(f"✅ Generated image embedding")
            except Exception as e:
                print(f"⚠️  Image embedding failed: {e}")
        
        # 5. Prepare product metadata for Qdrant payload
        product_metadata = {
            "title": product.title,
            "brand": product.brand,
            "category": product.category,
            "price": float(product.price) if product.price else None,
            "currency": product.currency,
            "url": product.url,
            "source": product.source,
        }
        
        # 6. Upsert to Qdrant
        result = qdrant_service.upsert_product_chunks(
            product_id=product.id,
            chunks=chunks,
            text_embeddings=text_embeddings,
            image_embedding=image_embedding,
            product_metadata=product_metadata
        )
        print(f"✅ Upserted to Qdrant: {result}")
        
    finally:
        db.close()

if __name__ == "__main__":
    ingest_product_example()