"""
Test script for product, embedding, and chunking services.
Run: python test_service.py
"""

import os
# Update this path to your actual service account key location
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'C:/Users/ettis/OneDrive/Desktop/BuyRight-dev/backend/buyright-485700-4d57aa7fdd7a.json'

from app.services.embedding_service import embedding_service
from app.services.chunking_service import chunking_service

def test_text_embedding():
    print("Testing text embedding...")
    text = "Apple iPhone 15 Pro Max - Premium smartphone with advanced camera"
    embedding = embedding_service.get_text_embedding(text)
    print(f"✅ Text embedding generated: {len(embedding)} dimensions")
    assert len(embedding) == 1408, f"Expected 1408 dims, got {len(embedding)}"

def test_image_embedding():
    print("\nTesting image embedding...")
    # Use a sample image URL
    image_url = "https://images.unsplash.com/photo-1575936123452-b67c3203c357?q=80&w=1740&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D"
    try:
        embedding = embedding_service.get_image_embedding(image_url)
        print(f"✅ Image embedding generated: {len(embedding)} dimensions")
        assert len(embedding) == 1408, f"Expected 1408 dims, got {len(embedding)}"
    except Exception as e:
        print(f"❌ Image embedding failed: {e}")

def test_chunking():
    print("\nTesting chunking service...")
    long_text = """
    The Apple iPhone 15 Pro Max represents the pinnacle of smartphone technology.
    It features the powerful A17 Pro chip, built on a 3-nanometer process.
    The device boasts a stunning Super Retina XDR display with ProMotion technology.
    Camera capabilities include a 48MP main sensor, ultra-wide, and telephoto lenses.
    Advanced computational photography enables stunning low-light performance.
    The titanium design makes it both durable and lightweight.
    Battery life has been significantly improved over previous generations.
    5G connectivity ensures blazing-fast download and upload speeds.
    """ * 5  # Repeat to create longer text
    
    chunks = chunking_service.chunk_text(long_text)
    print(f"✅ Chunking completed: {len(chunks)} chunks created")
    for i, chunk in enumerate(chunks[:10]):  # Show first 10 chunks
        print(f"  Chunk {i}: {len(chunk['text'])} chars, tokens: {chunk['token_count']}")

if __name__ == "__main__":
    print("=== Testing Embedding and Chunking Services ===\n")
    test_text_embedding()
    test_image_embedding()
    test_chunking()
    print("\n✅ All tests completed!")