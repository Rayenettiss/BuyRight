# BuyRight Backend - Project Structure

## 📁 Directory Structure

```
buyright-backend/
├── app/
│   ├── __init__.py                 # Package initialization
│   ├── main.py                     # FastAPI application entry point
│   ├── config.py                   # Configuration management (Pydantic)
│   ├── database.py                 # PostgreSQL connection & session
│   │
│   ├── models/                     # SQLAlchemy ORM Models
│   │   ├── __init__.py
│   │   ├── user.py                 # User table (profile, financial context)
│   │   ├── product.py              # Product table (e-commerce items)
│   │   ├── budget.py               # Budget table (constraints)
│   │   └── recommendation.py       # Recommendation, PaymentMethod, Transaction
│   │
│   ├── schemas/                    # Pydantic Schemas (validation)
│   │   ├── __init__.py
│   │   ├── user.py                 # User request/response schemas
│   │   ├── product.py              # Product schemas (TODO)
│   │   └── recommendation.py       # Recommendation schemas (TODO)
│   │
│   ├── routers/                    # FastAPI Route Handlers
│   │   ├── __init__.py
│   │   ├── auth.py                 # Authentication (register, login, JWT)
│   │   ├── user.py                 # User profile management
│   │   ├── ingestion.py            # Product CSV ingestion (TODO)
│   │   └── recommend.py            # Recommendation engine (TODO)
│   │
│   ├── utils/                      # Utility Functions
│   │   ├── __init__.py
│   │   ├── logger.py               # Structured logging (observability)
│   │   ├── security.py             # Auth, encryption, anonymization
│   │   ├── embedding.py            # Vertex AI embeddings (TODO)
│   │   └── qdrant_client.py        # Qdrant wrapper (TODO)
│   │
│   └── middleware/                 # FastAPI Middleware
│       ├── __init__.py
│       └── logging.py              # Request logging (TODO)
│
├── .env.example                    # Example environment variables
├── requirements.txt                # Python dependencies
├── README.md                       # Main documentation
├── PROJECT_STRUCTURE.md            # This file
├── run.sh                          # Startup script
└── test_api.py                     # API test script
```

## 🔑 Key Files Explained

### Core Application

**`app/main.py`** (419 lines)
- FastAPI application initialization
- Lifespan management (startup/shutdown)
- CORS middleware configuration
- Request logging middleware
- Global exception handler
- Health check endpoint
- Router inclusion

**`app/config.py`** (109 lines)
- Centralized configuration using Pydantic Settings
- Environment variable management
- Database URLs
- Qdrant configuration
- Security settings
- Logging configuration

**`app/database.py`** (64 lines)
- SQLAlchemy engine setup
- Session factory
- Database dependency for FastAPI
- Connection health checks
- Table initialization

### Data Models (SQLAlchemy)

**`app/models/user.py`** (73 lines)
- User authentication (email, password)
- Financial context (income, profession, price sensitivity)
- Preferences (categories, goals)
- Temporal data (last payday for timing recommendations)

**`app/models/budget.py`** (99 lines)
- Category-specific budget constraints
- Hard max (absolute limit)
- Soft max (preferred limit)
- Monthly limits with spending tracking
- Affordability checking methods

**`app/models/product.py`** (129 lines)
- Product information (title, description, price)
- Categorization (category, subcategory)
- Specs and features
- Payment options (installments, cashback)
- Quality metrics (rating, durability, resale value)
- True cost calculation methods

**`app/models/recommendation.py`** (148 lines)
- Recommendation history with explanations
- Payment methods with encrypted limits
- Transaction tracking
- Feedback loop (clicks, purchases)

### API Schemas (Pydantic)

**`app/schemas/user.py`** (82 lines)
- Request validation schemas (UserRegister, UserLogin, UserUpdate)
- Response schemas (UserResponse, TokenResponse)
- User profile vector schema for Qdrant
- Field validation (email, password strength)

### API Routes

**`app/routers/auth.py`** (188 lines)
- `POST /auth/register` - User registration with JWT token
- `POST /auth/login` - Authentication
- `GET /auth/me` - Get current user info
- `POST /auth/refresh` - Refresh JWT token
- `get_current_user()` - Dependency for protected routes

**`app/routers/user.py`** (238 lines)
- `PUT /user/profile` - Update user profile
- `POST /user/budgets` - Create budget constraint
- `GET /user/budgets` - Get all budgets
- `POST /user/payment-methods` - Add payment method (encrypted)
- `GET /user/payment-methods` - Get payment methods

### Utilities

**`app/utils/logger.py`** (128 lines)
- Structured logging setup (JSON format)
- Specialized logging functions:
  - `log_search_query()` - Track searches
  - `log_recommendation_decision()` - Explainability
  - `log_embedding_generation()` - Model version tracking
  - `log_financial_filter()` - Budget filtering transparency
  - `log_data_quality_issue()` - Data reliability

**`app/utils/security.py`** (98 lines)
- Password hashing (bcrypt)
- JWT token creation/validation
- Fernet encryption for sensitive data
- User ID anonymization
- Financial amount masking

## 📊 Implementation Status

### ✅ Phase 1: Authentication & User Management (COMPLETE)

- [x] Project structure
- [x] Configuration management
- [x] Database models (User, Budget, Product, Recommendation)
- [x] Pydantic schemas
- [x] Authentication (JWT)
- [x] User profile management
- [x] Budget constraints
- [x] Payment methods
- [x] Security (encryption, hashing, anonymization)
- [x] Logging infrastructure
- [x] API documentation
- [x] Health checks

**Total Lines of Code**: ~1,800 lines

### 🚧 Phase 2: Core Features (TODO)

**Qdrant Integration** (~300 lines estimated)
- `app/utils/qdrant_client.py`
  - Connection management
  - Collection creation (products, user_profiles)
  - HNSW indexing
  - Payload indexing for filters
  - Batch upsert operations

**Vertex AI Embeddings** (~250 lines estimated)
- `app/utils/embedding.py`
  - Text embedding generation (text-embedding-004)
  - Image embedding generation (multimodalembedding@001)
  - Batch processing
  - Rate limiting
  - Caching

**Product Ingestion** (~400 lines estimated)
- `app/routers/ingestion.py`
  - CSV upload endpoint
  - Data normalization
  - Text chunking (chonkie)
  - Multimodal embedding generation
  - Batch Qdrant upsert
  - PostgreSQL sync
- `app/schemas/product.py`
  - Product validation schemas

**Recommendation Engine** (~500 lines estimated)
- `app/routers/recommend.py`
  - Semantic search endpoint
  - Financial constraint filtering
  - Ranking algorithm
  - Explainability generation
  - Alternative suggestions
  - Feedback loop
- `app/schemas/recommendation.py`
  - Recommendation request/response schemas

**Total Estimated**: ~1,450 additional lines

## 🎯 Hackathon Deliverables Mapping

### 1. Architecture Diagram
**Location**: README.md (ASCII diagram)
**Status**: ✅ Complete

### 2. Data Description
**Location**: 
- Models: `app/models/*.py`
- README.md (data model section)
**Status**: ✅ Complete

### 3. Security/Privacy
**Implementation**: 
- `app/utils/security.py` (encryption, hashing, anonymization)
- `app/routers/auth.py` (JWT authentication)
**Status**: ✅ Complete

### 4. Observability
**Implementation**:
- `app/utils/logger.py` (structured logging)
- `app/main.py` (request middleware)
**Status**: ✅ Complete

### 5. Explainability
**Implementation**:
- `app/models/recommendation.py` (ranking_factors field)
- `app/utils/logger.py` (log_recommendation_decision)
**Status**: 🚧 Infrastructure ready, algorithm TODO

### 6. Evaluation
**Status**: 🚧 TODO (metrics collection endpoints)

## 🚀 Getting Started

### 1. Setup Environment
```bash
cp .env.example .env
# Edit .env with your credentials
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run Application
```bash
./run.sh
# Or manually:
uvicorn app.main:app --reload
```

### 4. Test Endpoints
```bash
python test_api.py
```

### 5. Access Documentation
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 📝 Code Quality

### Design Principles
1. **Separation of Concerns**: Models, schemas, routers, utils
2. **Type Safety**: Pydantic for validation, type hints throughout
3. **Security First**: Encryption, hashing, anonymization
4. **Observability**: Structured logging at every step
5. **Async/Await**: FastAPI async for performance
6. **Configuration**: Environment-based (12-factor app)

### Naming Conventions
- **Files**: lowercase_with_underscores.py
- **Classes**: PascalCase
- **Functions**: snake_case
- **Constants**: UPPER_CASE
- **Environment Variables**: UPPER_CASE

### Documentation
- Docstrings for all modules, classes, functions
- Inline comments for complex logic
- Hackathon requirement annotations
- Type hints for parameters and returns

## 🔄 Next Steps

1. **Implement Qdrant Client** (`app/utils/qdrant_client.py`)
2. **Implement Vertex AI Embeddings** (`app/utils/embedding.py`)
3. **Build Product Ingestion** (`app/routers/ingestion.py`)
4. **Build Recommendation Engine** (`app/routers/recommend.py`)
5. **Add Unit Tests** (`tests/` directory)
6. **Add Integration Tests** (end-to-end scenarios)
7. **Performance Benchmarks** (response time, throughput)
8. **Docker Containerization** (`Dockerfile`, `docker-compose.yml`)

## 📞 Support

For questions or issues, refer to:
- README.md for setup instructions
- API docs at /docs endpoint
- Code comments for implementation details
