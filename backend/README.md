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
- **Embeddings**: Google Vertex AI (text-embedding-004 + multimodalembedding@001)
- **AI/ML**: LangGraph agents for recommendation workflow
- **Authentication**: JWT-based with bcrypt password hashing
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
GOOGLE_CLOUD_PROJECT=your-gcp-project-id
GOOGLE_APPLICATION_CREDENTIALS=C:/path/to/service-account-key.json  # Use forward slashes on Windows
VERTEX_AI_LOCATION=us-central1

# Embedding Models
TEXT_EMBEDDING_MODEL=text-embedding-004
IMAGE_EMBEDDING_MODEL=multimodalembedding@001

# Vector Dimensions
TEXT_EMBEDDING_DIM=3072
TEXT_EMBEDDING_DIMENSIONS=3072
IMAGE_EMBEDDING_DIM=1408

# Chunking
MAX_CHUNK_SIZE=512
CHUNK_OVERLAP=50

# JWT Authentication
SECRET_KEY=your-super-secret-key-min-32-chars
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
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

#### Core Endpoints

| Method | Endpoint | Description | Auth | Status |
|--------|----------|-------------|------|--------|
| GET | `/` | Root health check | ❌ | ✅ |
| GET | `/health` | Detailed health status | ❌ | ✅ |

#### Authentication Endpoints

| Method | Endpoint | Description | Auth | Status |
|--------|----------|-------------|------|--------|
| POST | `/auth/register` | Register new user | ❌ | ✅ |
| POST | `/auth/login` | Login and get JWT token | ❌ | ✅ |

#### Debug Endpoints

| Method | Endpoint | Description | Auth | Status |
|--------|----------|-------------|------|--------|
| GET | `/debug/qdrant/connection` | Check Qdrant connection | ❌ | ✅ |
| GET | `/debug/qdrant/collection` | Get collection info | ❌ | ✅ |

#### Product Ingestion (Coming Soon)

| Method | Endpoint | Description | Auth | Status |
|--------|----------|-------------|------|--------|
| POST | `/ingestion/csv` | Upload CSV file | ✅ | 🔜 |
| POST | `/ingestion/json` | Ingest single product | ✅ | 🔜 |
| POST | `/scrape` | Real-time scrape from extension | ✅ | 🔜 |

---

## 🔐 Authentication

### Register a New User

**Request:**
```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword123"
  }'
```

**Response:**
```json
{
  "id": "uuid-here",
  "email": "user@example.com",
  "preferences": {},
  "created_at": "2024-01-28T10:00:00"
}
```

### Login

**Request:**
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user@example.com&password=securepassword123"
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Using Protected Endpoints

Add the token to the `Authorization` header:
```bash
curl -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  http://localhost:8000/some-protected-endpoint
```

**In Swagger UI:**
1. Click the "Authorize" button (top right)
2. Enter: `Bearer YOUR_TOKEN_HERE`
3. Click "Authorize"
4. Now you can test protected endpoints

---

## 📁 Project Structure
```
product-recommendation-backend/
├── app/
│   ├── __init__.py
│   ├── main.py                      # ✅ FastAPI app with lifespan events
│   ├── dependencies.py              # ✅ Database session, OAuth2, get_current_user
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── health.py                # ✅ Health check endpoints
│   │   ├── debug.py                 # ✅ Debug/testing endpoints
│   │   ├── auth.py                  # ✅ Authentication (register, login)
│   │   ├── ingestion.py             # 🔜 CSV/JSON product ingestion
│   │   └── scrape.py                # 🔜 Real-time scraping from extension
│   ├── services/
│   │   ├── __init__.py
│   │   ├── health_service.py        # ✅ Health check logic
│   │   ├── auth_service.py          # ✅ JWT & password hashing
│   │   ├── qdrant_service.py        # ✅ ⭐ CORE: Qdrant operations
│   │   ├── product_service.py       # ✅ Product CRUD operations
│   │   ├── embedding_service.py     # ✅ Vertex AI embeddings
│   │   └── chunking_service.py      # ✅ Chonkie semantic chunking
│   ├── agents/
│   │   └── recommendation_agent.py  # 🔜 LangGraph agent
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py                  # ✅ User model with JSONB prefs
│   │   └── product.py               # ✅ Product model (CSV fields)
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── user.py                  # ✅ UserCreate, UserOut
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
| `text_vector` | text-embedding-004 | 3072 | Product title + description embeddings |
| `image_vector` | multimodalembedding@001 | 1408 | Product image embeddings |

**Payload Schema:**
```json
{
  "product_id": "uuid",
  "chunk_idx": 0,
  "text": "chunk text...",
  "title": "string",
  "price": 99.99,
  "currency": "TND",
  "brand": "string",
  "category": "string",
  "source": "amazon",
  "url": "string"
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

### Testing Services

**Test embedding and chunking:**
```bash
python test_service.py
```

Expected output:
```
=== Testing Embedding and Chunking Services ===

Testing text embedding...
✅ Text embedding generated: 3072 dimensions

Testing image embedding...
✅ Image embedding generated: 1408 dimensions

Testing chunking service...
✅ Chunking completed: 5 chunks created
  Chunk 0: 487 chars, tokens: 89
  Chunk 1: 502 chars, tokens: 91
  Chunk 2: 498 chars, tokens: 90

✅ All tests completed!
```

### Running Tests (Coming Soon)
```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run all tests
pytest

# Run specific test file
pytest tests/test_auth.py

# Run with coverage
pytest --cov=app tests/
```

### Code Style
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
| `JWT_ALGORITHM` | JWT algorithm | `HS256` | ❌ |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiration | `1440` | ❌ |
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

### ✅ Phase 10-16: Services Layer (Complete)
- [x] Product service (CRUD operations)
- [x] Vertex AI embedding service (text-embedding-004)
- [x] Vertex AI image embedding service (multimodalembedding@001)
- [x] Chunking service with Chonkie
- [x] Qdrant upsert functions
- [x] Delete old product chunks function

### ✅ Phase 17-20: Authentication (Complete)
- [x] JWT token generation and verification
- [x] Password hashing with bcrypt
- [x] User registration endpoint
- [x] User login endpoint
- [x] OAuth2 password bearer dependency
- [x] get_current_user dependency
- [x] Protected route examples

### 🚧 Phase 21-24: Product Ingestion (Next - Not Started)
- [ ] CSV upload and parsing endpoint
- [ ] JSON product ingestion endpoint
- [ ] Batch embedding generation
- [ ] Multi-chunk upsert workflow
- [ ] Real-time scraping endpoint (from browser extension)
- [ ] Error handling and retry logic
- [ ] Ingestion progress tracking

### 📋 Phase 25-28: User Features (Not Started)
- [ ] User preferences management
- [ ] Behavior logging service
- [ ] Wishlist CRUD operations
- [ ] Budget management
- [ ] Budget alerts

### 📋 Phase 29-32: Recommendation Engine (Not Started)
- [ ] LangGraph recommendation agent
- [ ] Query vector construction from user preferences
- [ ] Qdrant filters (price, brand, category)
- [ ] Re-ranking with behavior data
- [ ] Gemini explanations
- [ ] Recommendation API endpoint
- [ ] Oversampling and rescoring

### 📋 Phase 33-35: Testing & Polish (Not Started)
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

# Windows: Use forward slashes in path
GOOGLE_APPLICATION_CREDENTIALS=C:/Users/path/to/key.json
```

**Import errors with Optional:**
```bash
# Make sure typing imports include Optional
from typing import List, Dict, Any, Optional

# Reinstall dependencies
pip install -r requirements.txt
```

**JWT token issues:**
```bash
# Verify SECRET_KEY is set and long enough (min 32 chars)
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Check token expiration time
# Default is 1440 minutes (24 hours)
ACCESS_TOKEN_EXPIRE_MINUTES=1440
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
- INT8 scalar quantization for memory efficiency (4x reduction)
- COSINE distance for similarity search
- Payload filtering for budget-aware recommendations
- High-dimensional vector support (3072-dim text, 1408-dim image)
- Chunk-based product representation with shared image vectors

🎯 **Why Qdrant?**
- **Performance**: Sub-millisecond search on millions of products
- **Flexibility**: Named vectors + rich payload filtering
- **Efficiency**: Quantization reduces memory by 4x without accuracy loss
- **Scalability**: Handles high-dimensional embeddings (up to 3072-dim)
- **Accuracy**: Oversampling + rescoring maintains search quality

📊 **Architecture Highlights:**
- Text embeddings: 3072 dimensions (Vertex AI text-embedding-004)
- Image embeddings: 1408 dimensions (Vertex AI multimodalembedding@001)
- Semantic chunking with Chonkie for long product descriptions
- Each product can have multiple text chunks but shares one image vector
- Filters: price range, brand, category, source for precise recommendations

---

**Built with ❤️ for the Qdrant Hackathon**

**Current Status**: 
- ✅ Foundation, Qdrant, Services, Authentication complete
- 🚧 Product ingestion (CSV/JSON) next
- 📋 Recommendation engine and user features to follow