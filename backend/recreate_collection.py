from app.services.qdrant_service import qdrant_service
from config.settings import settings
import sys

def recreate():
    try:
        client = qdrant_service.get_client()
        collection_name = settings.qdrant_collection_name
        
        print(f"Deleting collection: {collection_name}...")
        try:
            client.delete_collection(collection_name)
            print("Deleted.")
        except Exception as e:
            print(f"Delete failed (might not exist): {e}")
            
        print(f"Creating collection: {collection_name}...")
        result = qdrant_service.create_financial_products_collection()
        print(f"Result: {result}")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    recreate()
