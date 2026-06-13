from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os

from src.core.config import settings
from src.core.logging import setup_logging

# Setup logging
setup_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Starting MEMORIA AI Backend...")
    yield
    # Shutdown
    print("🛑 Shutting down MEMORIA AI Backend...")

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="MEMORIA AI - Your Personal AI Operating System",
    version="0.1.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "memoria-ai-backend"}

@app.get("/")
async def root():
    return {
        "message": "Welcome to MEMORIA AI",
        "version": "0.1.0",
        "docs": "/docs"
    }

@app.get("/ready")
async def readiness_check():
    return {"status": "ready"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
