# Financial Product Search - Ingestion Service

AI-powered product ingestion service with separate text and image embeddings using Qdrant and Google Vertex AI.

## Features

- ✅ CSV ingestion with automatic column normalization
- ✅ Separate text and image embeddings (NOT unified multimodal)
- ✅ Text chunking using chonkie library
- ✅ Scalar INT8 quantization for performance
- ✅ Batch processing for embeddings and images
- ✅ Production-ready error handling
- ✅ FastAPI with async support

## Architecture

### Vector Storage Strategy
- **Text Embeddings**: 3072 dimensions (text-embedding-004)
- **Image Embeddings**: 1408 dimensions (multimodalembedding@001)
- **Separate Named Vectors**: No multimodal fusion
- **Quantization**: INT8 scalar quantization (quantile=0.99)

### Data Flow
1. CSV Upload → Normalization → Chunking
2. Text Embedding (Vertex AI text-embedding-004)
3. Image Download → Image Embedding (multimodalembedding@001)
4. Qdrant Upsert with separate vectors

## Setup Instructions

### 1. Prerequisites
- Python 3.9+
- Qdrant Cloud account
- Google Cloud Platform account with Vertex AI enabled

### 2. Install Dependencies

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Environment

Create a `.env` file based on `.env.example`:

```bash
cp .env.example .env
```

Edit `.env` with your credentials:
- Qdrant URL and API key from your cluster
- GCP Project ID and location
- Path to your service account JSON key

### 4. Run the Service

```bash
# Development mode with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production mode
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## API Endpoints

### Health Check
```bash
GET /health
```

### Ingest Products
```bash
POST /ingest/products
Content-Type: multipart/form-data

file: <CSV file>
```

**Example using curl:**
```bash
curl -X POST "http://localhost:8000/ingest/products" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@products.csv"
```

**Response:**
```json
{
  "status": "success",
  "message": "Successfully ingested 100 products",
  "total_products": 100,
  "total_points": 150,
  "points_with_text": 150,
  "points_with_image": 95,
  "errors": []
}
```

### Collection Info
```bash
GET /collection/info
```

## CSV Format

The service automatically normalizes CSV columns. Supported variations:

| Standard Field | Accepted Columns |
|---------------|------------------|
| title | title, product_name, name, product_title, titre, nom |
| description | description, desc, product_description, details, about |
| price | price, prix, cost, amount, product_price |
| url | url, link, product_url, product_link, lien |
| image_url | image_url, image, img_url, picture, photo, image_link |
| id | id, product_id, item_id, sku, asin |

**Example CSV:**
```csv
title,description,price,url,image_url
"Laptop",long description here,999.99,https://example.com/product,https://example.com/image.jpg
```

## Testing

### Sample CSV for Testing

Create `test_products.csv`:
```csv
product_name,desc,prix,product_link,image
"iPhone 15 Pro","Latest Apple smartphone with A17 chip",1199.99,https://example.com/iphone,https://picsum.photos/400/400
"Samsung Galaxy S24","Flagship Android phone",999.99,https://example.com/samsung,https://picsum.photos/400/401
"MacBook Pro","Professional laptop for developers",2499.99,https://example.com/macbook,https://picsum.photos/400/402
```

### Test the Ingestion
```bash
curl -X POST "http://localhost:8000/ingest/products" \
  -F "file=@test_products.csv"
```

## Performance Considerations

- **Batch Processing**: Text embeddings processed in batches of 5
- **Concurrent Downloads**: Images downloaded concurrently using aiohttp
- **Quantization**: INT8 reduces memory by ~4x with <1% accuracy loss
- **Chunking**: Long descriptions split into 2000-char chunks

## Troubleshooting

### Common Issues

1. **"Qdrant connection failed"**
   - Verify QDRANT_URL and QDRANT_API_KEY in .env
   - Check Qdrant cluster is running

2. **"Vertex AI authentication failed"**
   - Verify GOOGLE_APPLICATION_CREDENTIALS path
   - Ensure service account has aiplatform.user role

3. **"Image download timeout"**
   - Some image URLs may be slow/broken
   - Service continues with text-only embeddings

4. **"No valid products found"**
   - Check CSV column names match mappings
   - Verify CSV is not empty

## Next Steps

This is the **ingestion-only** service. For search functionality:
1. Implement search endpoints (text, image, hybrid)
2. Add filtering by source, price range
3. Implement ranking/reranking logic
4. Build Next.js frontend with search UI

## License

MIT