"""
FastAPI backend for options dashboard.
Wraps Python analytics functions (utils.py, options_utils.py) as REST endpoints.
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import json
from pathlib import Path

# Import route handlers
from .routes.stock import router as stock_router
from .routes.options import router as options_router


# Lifespan context manager for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    print("🚀 FastAPI backend starting...")
    yield
    print("🛑 FastAPI backend shutting down...")


# Initialize FastAPI app
app = FastAPI(
    title="Options Dashboard API",
    description="Stock analysis and options analytics backend",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to specific domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include route modules
app.include_router(stock_router, prefix="/api/stock", tags=["stock"])
app.include_router(options_router, prefix="/api/options", tags=["options"])


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "ok",
        "message": "Options Dashboard API is running",
        "docs": "/docs",
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
