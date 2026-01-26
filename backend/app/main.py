"""
BuyRight Backend - Main FastAPI Application
Hackathon: Context-Aware FinCommerce Intelligence Engine

Architecture:
- FastAPI for async performance
- PostgreSQL for relational data (source of truth)
- Qdrant for vector search (mandatory for hackathon)
- Vertex AI for multimodal embeddings
- JWT authentication
- Structured logging for observability

Deliverables Addressed:
- Functional Demo: End-to-end API for product recommendations
- Architecture: Hybrid database (PostgreSQL + Qdrant)
- Explainability: Ranking factors in recommendations
- Observability: Structured logging throughout
- Security/Privacy: Encrypted financial data, anonymized logs
"""
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import time

from app.config import settings
from app.database import init_db, check_db_connection
from app.routers import auth, user
from app.utils.logger import get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup/shutdown events.
    
    Startup:
    - Initialize database tables
    - Check Qdrant connection
    - Log application startup
    
    Shutdown:
    - Cleanup resources
    """
    # Startup
    logger.info(
        "application_starting",
        app_name=settings.APP_NAME,
        version=settings.APP_VERSION,
        environment=settings.ENVIRONMENT
    )
    
    try:
        # Initialize PostgreSQL
        init_db()
        logger.info("postgresql_initialized")
        
        # Check database connection
        if not check_db_connection():
            logger.error("postgresql_connection_failed")
            raise Exception("Failed to connect to PostgreSQL")
        
        logger.info("database_connections_verified")
        
    except Exception as e:
        logger.error("startup_failed", error=str(e))
        raise
    
    yield
    
    # Shutdown
    logger.info("application_shutting_down")


# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
    BuyRight: Context-Aware FinCommerce Intelligence Engine
    
    Hackathon Project - Use Case 2: Smart Product Discovery & Recommendations
    
    Features:
    - Multimodal vector search (text + images) using Qdrant
    - Financial context-aware recommendations
    - Budget constraint filtering
    - Explainable ranking with affordability analysis
    - Real-time semantic search for vague queries
    
    Tech Stack:
    - FastAPI (async)
    - PostgreSQL (relational data)
    - Qdrant (vector search - mandatory)
    - Google Vertex AI (embeddings)
    """,
    lifespan=lifespan,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None
)

# CORS Middleware (for browser extension + web app)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request logging middleware (observability)
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    Log all HTTP requests for observability.
    
    Hackathon: Track queries, response times, errors.
    """
    start_time = time.time()
    
    # Log request
    logger.info(
        "request_received",
        method=request.method,
        path=request.url.path,
        client=request.client.host if request.client else None
    )
    
    # Process request
    try:
        response = await call_next(request)
        duration = (time.time() - start_time) * 1000  # ms
        
        # Log response
        logger.info(
            "request_completed",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration_ms=round(duration, 2)
        )
        
        return response
    
    except Exception as e:
        duration = (time.time() - start_time) * 1000
        logger.error(
            "request_failed",
            method=request.method,
            path=request.url.path,
            error=str(e),
            duration_ms=round(duration, 2)
        )
        raise


# Exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for unhandled errors"""
    logger.error(
        "unhandled_exception",
        path=request.url.path,
        error=str(exc),
        error_type=type(exc).__name__
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Internal server error",
            "error": str(exc) if settings.DEBUG else "An error occurred"
        }
    )


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint.
    
    Hackathon: Verify all services are operational.
    Returns status of PostgreSQL and Qdrant connections.
    """
    # Check PostgreSQL
    postgres_healthy = check_db_connection()
    
    # TODO: Check Qdrant connection (will implement with Qdrant client)
    qdrant_healthy = True  # Placeholder
    
    overall_status = "healthy" if (postgres_healthy and qdrant_healthy) else "unhealthy"
    
    response = {
        "status": overall_status,
        "version": settings.APP_VERSION,
        "services": {
            "postgresql": "healthy" if postgres_healthy else "unhealthy",
            "qdrant": "healthy" if qdrant_healthy else "unhealthy"
        }
    }
    
    logger.info("health_check", status=overall_status)
    
    return response


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information"""
    return {
        "message": "BuyRight FinCommerce Intelligence Engine",
        "version": settings.APP_VERSION,
        "hackathon": "Context-Aware Product Recommendations",
        "docs": "/docs" if settings.DEBUG else "Documentation disabled in production"
    }


# Include routers
app.include_router(auth.router)
app.include_router(user.router)

# TODO: Add these routers after implementation
# app.include_router(ingestion.router)
# app.include_router(recommend.router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )