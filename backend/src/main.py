"""Main FastAPI application."""
import logging
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config import settings

# Configure logging to match Uvicorn's format
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s:\t %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

# Set specific loggers to appropriate levels
logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "message": "Welcome to Quran App API",
        "status": "running",
        "docs": "/api/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {"status": "healthy"}


# Import and include routers here
from src.admin.router import router as admin_router
from src.morphology_item.router import router as morphology_item_router
from src.ism.router import router as ism_router

app.include_router(admin_router, prefix="/api/admin", tags=["Admin"])
app.include_router(morphology_item_router, prefix="/api/morphology_item", tags=["Morphology"])
app.include_router(ism_router, prefix="/api/ism", tags=["Ism"])
