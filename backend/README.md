# Product Recommendation Backend

> **Hackathon Project**: Qdrant-powered personalized financial/product recommendation system

A FastAPI backend that suggests cheaper/better product alternatives based on user budgets, leveraging Qdrant vector database for intelligent content-based recommendations.

---

## 🎯 Project Overview

### Core Features
- **Qdrant Vector Search**: High-performance ANN search with filters and INT8 quantization
- **Budget-Aware Recommendations**: Suggests products within user's financial constraints
- **Multi-Source Product Ingestion**: CSV bulk import + real-time browser extension scraping
- **Smart Re-ranking**: Content-based filtering with user behavior and preference learning
- **AI-Powered Explanations**: Gemini-generated recommendation justifications

### Tech Stack
- **Backend**: FastAPI + PostgreSQL + Qdrant
- **Embeddings**: Google Vertex AI (multimodalembedding@001)
- **Chunking**: Chonkie for semantic text splitting
- **AI/ML**: LangGraph agents for recommendation workflow
- **Clients**: Browser extension, Next.js web app, Ionic mobile app

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- PostgreSQL 14+
- Qdrant (local or cloud)
- Google Cloud Project with Vertex AI enabled

### Installation

**Note**: If you've already installed FastAPI and Uvicorn globally:
```bash
pip install fastapi uvicorn
```

**1. Clone the repository**
```bash
git clone <repository-url>
cd product-recommendation-backend
```

**2. Create virtual environment (recommended)**
```bash
python -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Set up Google Cloud credentials**
```bash
# 1. Create a service account in Google Cloud Console
# 2. Enable Vertex AI API
# 3. Download service account JSON key
# 4. Set the path in .env
```

**5. Configure environment variables**
```bash
# Copy example env file
cp .env.example .env

# Edit .env and add your credentials
nano .env  # or use your preferred editor
```

**Required environment variables:**
```bash
# PostgreSQL
DATABASE_URL=postgresql://user:password@localhost:5432/product_recommendation_db

# Qdrant
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=
QDRANT_COLLECTION_NAME=financial_products

# Google Cloud / Vertex AI
VERTEX_PROJECT_ID=your-gcp-project-id
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json
VERTEX_AI_LOCATION=us-central1

# Embedding Models (multimodal@001 for both)
TEXT_EMBEDDING_MODEL=multimodalembedding@001
IMAGE_EMBEDDING_MODEL=multimodalembedding@001

# Vector Dimensions (multimodal@001 uses 1408)
TEXT_EMBEDDING_DIM=1408
TEXT_EMBEDDING_DIMENSIONS=1408
IMAGE_EMBEDDING_DIM=1408

# Security
SECRET_KEY=your-super-secret-key-min-32-chars
```

**Generate a secure SECRET_KEY:**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

**6. Set up the database**
```bash
# Create PostgreSQL database (if not exists)
createdb product_recommendation_db

# Or using psql:
psql -U postgres -c "CREATE DATABASE product_recommendation_db;"

# Apply migrations
alembic upgrade head
```

**7. Start Qdrant (if running locally)**
```bash
# Using Docker
docker run -p 6333:6333 qdrant/qdrant

# Or download from https://qdrant.tech/documentation/quick-start/
```

### Running the Server

**Method 1: Using main.py**
```bash
python app/main.py
```

**Method 2: Using Uvicorn CLI**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Expected startup output:**
```
🚀 Starting up...
📦 Qdrant Collection: created - Collection 'financial_products' created successfully
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Server will start on:** `http://localhost:8000`

---

## 📚 API Documentation

Once the server is running:

- **Swagger UI (Interactive)**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc (Alternative)**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

### Available Endpoints

| Method | Endpoint | Description | Status |
|--------|----------|-------------|--------|
| GET | `/` | Root health check | ✅ |
| GET | `/health` | Detailed health status | ✅ |
| GET | `/debug/qdrant/connection` | Check Qdrant connection | ✅ |
| GET | `/debug/qdrant/collection` | Get collection info | ✅ |

### Quick Health Check
```bash
# Root endpoint
curl http://localhost:8000/

# Health endpoint
curl http://localhost:8000/health

# Qdrant connection check
curl http://localhost:8000/debug/qdrant/connection

# Collection info
curl http://localhost:8000/debug/qdrant/collection
```

**Expected response from `/debug/qdrant/collection`:**
```json
{
  "status": "ok",
  "collection_name": "financial_products",
  "points_count": 0,
  "segments_count": 1,
  "status_info": "green",
  "optimizer_status": "ok",
  "vectors_config": {
    "text_vector": {
      "size": 1408,
      "distance": "COSINE"
    },
    "image_vector": {
      "size": 1408,
      "distance": "COSINE"
    }
  },
  "quantization_config": {
    "type": "INT8",
    "quantile": 0.99,
    "always_ram": true
  }
}
```

---

## 📁 Project Structure
```
product-recommendation-backend/
├── app/
│   ├── __init__.py
│   ├── main.py                      # ✅ FastAPI app with lifespan events
│   ├── dependencies.py              # ✅ Database session & DI
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── health.py                # ✅ Health check endpoints
│   │   └── debug.py                 # ✅ Debug/testing endpoints
│   ├── services/
│   │   ├── __init__.py
│   │   ├── health_service.py        # ✅ Health check logic
│   │   ├── embedding_service.py     # ✅ Vertex AI embeddings
│   │   ├── chunking_service.py      # ✅ Semantic text chunking
│   │   ├── product_service.py       # ✅ Product CRUD operations
│   │   └── qdrant_service.py        # ✅ ⭐ CORE: Qdrant operations
│   ├── agents/
│   │   └── recommendation_agent.py  # 🔜 LangGraph agent
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py                  # ✅ User model with JSONB prefs
│   │   └── product.py               # ✅ Product model (CSV fields)
│   ├── schemas/
│   │   └── __init__.py
│   └── utils/
│       └── __init__.py
├── config/
│   ├── __init__.py
│   └── settings.py                  # ✅ Pydantic settings with Vertex AI
├── migrations/                      # ✅ Alembic migrations
│   ├── __init__.py
│   ├── env.py                       # ✅ Configured for auto-detection
│   ├── script.py.mako
│   └── versions/
│       ├── xxxx_add_users_table.py      # ✅ Users table
│       └── xxxx_add_products_table.py   # ✅ Products table
├── tests/
│   └── __init__.py
├── test_service.py                  # ✅ Test for embedding/chunking
├── exemple_usage.py                # ✅ End-to-end ingestion example
├── requirements.txt                 # ✅ All dependencies
├── alembic.ini                      # ✅ Alembic configuration
├── .env                             # Environment variables (not in git)
├── .env.example                     # Environment template
├── .gitignore                       # ✅ Git ignore rules
└── README.md                        # This file
```

---

## 🗄️ Database Schema

### PostgreSQL Tables

#### ✅ **users** (Implemented)
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    preferences JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP
);
```

**Preferences JSONB structure:**
```json
{
  "brands": ["Apple", "Samsung"],
  "categories": ["electronics"],
  "price_sensitivity": 0.8,
  "ignored_sources": ["jumia"]
}
```

#### ✅ **products** (Implemented)
```sql
CREATE TABLE products (
    id UUID PRIMARY KEY,
    external_id VARCHAR(100),
    title VARCHAR(500) NOT NULL,
    description TEXT,
    brand VARCHAR(200),
    category VARCHAR(200),
    price NUMERIC(12,2),
    currency VARCHAR(3) DEFAULT 'TND',
    url VARCHAR(1000) UNIQUE NOT NULL,
    image_url VARCHAR(1000),
    stars NUMERIC(3,2),
    reviews_count INTEGER DEFAULT 0,
    source VARCHAR(50) DEFAULT 'manual',
    created_at TIMESTAMP DEFAULT NOW(),
    scraped_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

**CSV field mapping:**
- `title` → title
- `brand` → brand
- `stars` → stars
- `reviews_count` → reviews Count
- `image_url` → imageurl
- `category` → category
- `description` → description
- `currency` → currency
- `price` → price
- `url` → url

#### 🔜 **wishlists** (Coming Soon)
Many-to-many relationship between users and products

#### 🔜 **budgets** (Coming Soon)
User budget limits with category_limits (JSONB)

#### 🔜 **behavior_events** (Coming Soon)
User interaction logs (clicks, views, ignores, etc.)

#### 🔜 **feedback** (Coming Soon)
User ratings and comments on recommendations

---

### Qdrant Collection

#### ✅ **financial_products** (Implemented)

**Configuration:**
- **Collection Name**: `financial_products`
- **Quantization**: INT8 Scalar (99th percentile, always in RAM)
- **Distance Metric**: COSINE

**Named Vectors:**

| Vector Name | Model | Dimensions | Purpose |
|-------------|-------|------------|---------|
| `text_vector` | multimodalembedding@001 | 1408 | Product title + chunked description |
| `image_vector` | multimodalembedding@001 | 1408 | Product image embeddings |

**Payload Schema:**
```json
{
  "product_id": "uuid",
  "title": "string",
  "price": 99.99,
  "currency": "TND",
  "brand": "string",
  "category": "string",
  "source": "amazon",
  "url": "string",
  "image_url": "string"
}
```

**Filters Available:**
- Price range: `price >= min AND price <= max`
- Brand matching: `brand IN [...]`
- Category filtering: `category = "..."`
- Source exclusion: `source NOT IN [...]`

---

## 🛠️ Development

### Database Migrations
```bash
# Create a new migration after model changes
alembic revision --autogenerate -m "description of changes"

# Apply all pending migrations
alembic upgrade head

# Rollback last migration
alembic downgrade -1

# View migration history
alembic history

# View current version
alembic current
```

### Verify Database Schema
```bash
# Connect to PostgreSQL
psql -U postgres -d product_recommendation_db

# List all tables
\dt

# Describe users table
\d users

# Describe products table
\d products

# View data
SELECT * FROM users;
SELECT * FROM products LIMIT 10;

# Exit psql
\q
```

### Verify Qdrant Collection
```bash
# Check collection exists
curl http://localhost:8000/debug/qdrant/connection

# Get collection details
curl http://localhost:8000/debug/qdrant/collection

# Or use Qdrant UI (if running locally)
# Open browser: http://localhost:6333/dashboard
```

### Running Quick Tests
```bash
# Test Embedding and Chunking services
python test_service.py

# Test Complete Flow (SQL -> Chonkie -> Vertex -> Qdrant)
python exemple_usage.py
```

### Verify Qdrant Collection
```bash
# Install dev dependencies
pip install black isort flake8

# Format code
black app/
isort app/

# Lint
flake8 app/
```

---

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `DATABASE_URL` | PostgreSQL connection string | - | ✅ |
| `QDRANT_URL` | Qdrant server URL | `http://localhost:6333` | ✅ |
| `QDRANT_API_KEY` | Qdrant API key | - | ❌ |
| `QDRANT_COLLECTION_NAME` | Collection name | `financial_products` | ❌ |
| `GOOGLE_CLOUD_PROJECT` | GCP project ID | - | ✅ |
| `GOOGLE_APPLICATION_CREDENTIALS` | Path to service account JSON | - | ✅ |
| `TEXT_EMBEDDING_MODEL` | Vertex AI text model | `text-embedding-004` | ❌ |
| `IMAGE_EMBEDDING_MODEL` | Vertex AI image model | `multimodalembedding@001` | ❌ |
| `TEXT_EMBEDDING_DIM` | Text vector dimensions | `3072` | ❌ |
| `IMAGE_EMBEDDING_DIM` | Image vector dimensions | `1408` | ❌ |
| `SECRET_KEY` | JWT signing key | - | ✅ |
| `DEBUG` | Enable debug mode | `false` | ❌ |
| `ENVIRONMENT` | Deployment environment | `development` | ❌ |

See `.env.example` for complete list with detailed comments.

---

## 🚢 Deployment

### Docker (Coming Soon)
```bash
# Build image
docker build -t product-recommendation-api .

# Run container
docker run -p 8000:8000 --env-file .env product-recommendation-api
```

### Docker Compose (Coming Soon)
```bash
# Start all services (app + postgres + qdrant)
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

---

## 🎯 Development Roadmap

### ✅ Phase 0-9: Foundation & Qdrant Setup (Complete)
- [x] Project skeleton and folder structure
- [x] FastAPI setup with CORS middleware
- [x] Environment configuration with Pydantic settings
- [x] PostgreSQL connection with SQLAlchemy
- [x] Alembic migrations setup
- [x] User model with JSONB preferences
- [x] Product model with CSV field mapping
- [x] Health check service and router
- [x] Qdrant client connection
- [x] Financial products collection with named vectors
- [x] INT8 scalar quantization configuration
- [x] Debug endpoints for testing
- [x] Lifespan events for collection initialization
- [x] API documentation (Swagger/ReDoc)

### ✅ Phase 10-19: Embedding & Ingestion (Complete)
- [x] Vertex AI embedding service (multimodalembedding@001)
- [x] Vertex AI image embedding service (multimodalembedding@001)
- [x] Product service (CRUD operations)
- [x] Chunking service for long descriptions
- [x] Upsert service for Qdrant
- [x] CSV ingestion endpoint (Integrated in services)
- [x] JSON product ingestion endpoint (Integrated in services)
- [x] Batch processing for embeddings
- [x] Error handling and retry logic

### 📋 Phase 20-24: Authentication & User Features
- [ ] JWT authentication
- [ ] User registration and login
- [ ] User preferences management
- [ ] Behavior logging service
- [ ] Wishlist CRUD operations
- [ ] Budget management

### 📋 Phase 25-28: Recommendation Engine
- [ ] LangGraph recommendation agent
- [ ] Query vector construction from user preferences
- [ ] Qdrant filters (price, brand, category)
- [ ] Re-ranking with behavior data
- [ ] Gemini explanations
- [ ] Recommendation API endpoint
- [ ] Oversampling and rescoring

### 📋 Phase 29-30: Testing & Polish
- [ ] Unit tests for critical paths
- [ ] Integration tests for recommendation flow
- [ ] Performance optimization
- [ ] Load testing
- [ ] Documentation polish
- [ ] Deployment configuration

---

## 🤝 Contributing

1. Follow the existing folder structure
2. Write tests for new features
3. Use type hints and docstrings
4. Format code with `black` and `isort`
5. Keep commits atomic and descriptive
6. Update migrations for schema changes
7. Document API endpoints in docstrings

---

## 📝 Troubleshooting

### Common Issues

**Database connection fails:**
```bash
# Check PostgreSQL is running
pg_isready

# Verify DATABASE_URL in .env
cat .env | grep DATABASE_URL

# Test connection manually
psql -U postgres -d product_recommendation_db
```

**Qdrant connection fails:**
```bash
# Check if Qdrant is running
curl http://localhost:6333/collections

# Test connection via API
curl http://localhost:8000/debug/qdrant/connection

# Check Docker container (if using Docker)
docker ps | grep qdrant
docker logs <qdrant-container-id>
```

**Vertex AI authentication fails:**
```bash
# Verify service account key exists
ls -la /path/to/service-account-key.json

# Check environment variable is set
echo $GOOGLE_APPLICATION_CREDENTIALS

# Test authentication
gcloud auth application-default print-access-token
```

**Alembic migration fails:**
```bash
# Reset to specific version
alembic downgrade <revision>

# Check current version
alembic current

# View migration history
alembic history --verbose

# Generate new migration
alembic revision --autogenerate -m "description"
```

**Import errors:**
```bash
# Ensure virtual environment is activated
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Reinstall dependencies
pip install -r requirements.txt

# Verify Python path
python -c "import sys; print(sys.path)"
```

---

## 📞 Support

For questions or issues:
- Open an issue on GitHub
- Check `/docs` for API documentation
- Review migration history: `alembic history`
- Check Qdrant dashboard: `http://localhost:6333/dashboard`

---

## 📄 License

[Add your license here]

---

## 🏆 Hackathon Focus

**This project showcases Qdrant as the core technology:**

✨ **Key Qdrant Features Used:**
- Named vectors for multi-modal embeddings (text + image)
- INT8 scalar quantization for memory efficiency
- COSINE distance for similarity search
- Payload filtering for budget-aware recommendations
- High-dimensional vector support (3072-dim text, 1408-dim image)

🎯 **Why Qdrant?**
- **Performance**: Sub-millisecond search on millions of products
- **Flexibility**: Named vectors + rich payload filtering
- **Efficiency**: Quantization reduces memory by 4x
- **Scalability**: Handles high-dimensional embeddings (3072-dim)
- **Accuracy**: Oversampling + rescoring maintains quality

---

**Built with ❤️ for the Qdrant Hackathon**

**Current Status**: ✅ Foundation & Qdrant setup complete | 🚧 Embedding service next