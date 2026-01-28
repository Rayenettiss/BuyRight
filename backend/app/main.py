"""
FastAPI main application entry point.
Includes lifespan events for Qdrant collection initialization.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import routers
from app.routers import health, debug,auth,ingestion

# Import services
from app.services.qdrant_service import qdrant_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan event handler - runs on startup and shutdown.
    Creates Qdrant collection if it doesn't exist.
    """
    # Startup
    print("🚀 Starting up...")
    
    # Create Qdrant collection on startup
    result = qdrant_service.create_financial_products_collection()
    print(f"📦 Qdrant Collection: {result['status']} - {result['message']}")
    
    yield
    
    # Shutdown
    print("👋 Shutting down...")


# Create FastAPI app instance with lifespan
app = FastAPI(
    title="Product Recommendation API",
    description="Qdrant-powered personalized product recommendation system",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS Middleware - Allow all origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router)
app.include_router(debug.router)
app.include_router(auth.router)
app.include_router(ingestion.router)


@app.get("/")
async def root():
    """Root endpoint - health check."""
    return {
        "message": "Product Recommendation API is running",
        "status": "healthy",
        "version": "1.0.0"
    }


# Uvicorn run block for development
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True  # Auto-reload on code changes
    )