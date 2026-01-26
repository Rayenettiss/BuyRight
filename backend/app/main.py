from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import ingestion
from app.services.qdrant import qdrant_service
from app.models.product import HealthResponse
from config.settings import get_settings
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)
settings = get_settings()

# Initialize FastAPI app
app = FastAPI(
    title="Financial Product Search - Ingestion Service",
    description="AI-powered product ingestion service with separate text and image embeddings",
    version="1.0.0"
)

# Configure CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://*.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(ingestion.router)


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("Starting up Financial Product Ingestion Service")
    
    try:
        # Initialize Qdrant collection
        await qdrant_service.init_collection()
        logger.info("Qdrant collection initialized successfully")
    except Exception as e:
        logger.error(f"Error during startup: {e}")
        raise


@app.get("/", tags=["root"])
async def root():
    """Root endpoint"""
    return {
        "service": "Financial Product Search - Ingestion Service",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health", response_model=HealthResponse, tags=["health"])
async def health_check():
    """Health check endpoint"""
    qdrant_status = await qdrant_service.health_check()
    
    # Check if Vertex AI is configured
    vertex_configured = True
    try:
        from app.services.embeddings import embedding_service
        vertex_configured = embedding_service is not None
    except Exception:
        vertex_configured = False
    
    return HealthResponse(
        status="healthy" if qdrant_status and vertex_configured else "unhealthy",
        qdrant_connected=qdrant_status,
        vertex_ai_configured=vertex_configured
    )


@app.get("/collection/info", tags=["admin"])
async def get_collection_info():
    """Get Qdrant collection information"""
    try:
        info = await qdrant_service.get_collection_info()
        if info:
            return {
                "collection_name": settings.collection_name,
                "vectors_count": info.vectors_count,
                "points_count": info.points_count,
                "status": info.status
            }
        else:
            return {"error": "Collection not found"}
    except Exception as e:
        logger.error(f"Error getting collection info: {e}")
        return {"error": str(e)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True
    )