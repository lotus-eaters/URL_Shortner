"""
Main FastAPI application entry point
Initializes the app, middleware, and event handlers
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.core.config import get_settings
from app.core.logger import setup_logging
from app.core.database import connect_db, close_db
from app.core.db_init import init_database

# Setup logging
logger = setup_logging()
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events
    Handles database connections on app startup and shutdown
    """
    # Startup
    logger.info(" Starting URL Shortener Service...")
    
    try:
        # Connect to MongoDB and Redis (consolidated in database.py)
        await connect_db()
        
        # Initialize database (create indexes, seed data)
        await init_database()
        
        logger.info("Application started successfully")
    except Exception as e:
        logger.error(f" Startup failed: {str(e)}")
        raise
    
    yield
    
    # Shutdown
    logger.info(" Shutting down URL Shortener Service...")
    
    try:
        await close_db()
        logger.info("Application shutdown complete")
    except Exception as e:
        logger.error(f" Shutdown error: {str(e)}")


def create_app() -> FastAPI:
    """
    Create and configure FastAPI application
    """
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="A high-performance URL shortening service",
        debug=settings.debug,
        lifespan=lifespan,
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Change in production!
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    return app


# Create application instance
app = create_app()


# ============ Include Routes ============
from app.api.routes.auth import router as auth_router
from app.api.routes.urls import router as urls_router

app.include_router(auth_router)
app.include_router(urls_router)


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint
    Returns 200 if service is running
    """
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.app_version
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )
