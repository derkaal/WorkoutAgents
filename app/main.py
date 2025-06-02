"""
FastAPI main application for the Workout Agents API.

This module initializes the FastAPI application, includes routers,
sets up middleware, and configures the application to run with Uvicorn.
"""

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import routers
import sys
import os

# Add the parent directory to sys.path to allow imports to work
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Now we can import using the app prefix
from app.routers.workout import router as workout_router
from app.routers.progress import router as progress_router

# Create FastAPI application with metadata
app = FastAPI(
    title="Workout Agents API",
    description="""
    A multi-agent system for workout planning and progress tracking.
    
    Features two specialized agents:
    - **Mike Lawry**: Generates personalized workout plans
    - **Trystero**: Analyzes workout progress and provides feedback
    """,
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(workout_router)
app.include_router(progress_router)


@app.get("/")
async def root():
    """
    Root endpoint that provides basic API information.
    
    Returns:
        dict: Basic information about the API
    """
    return {
        "name": "Workout Agents API",
        "version": "1.0.0",
        "description": "Multi-agent system for workout planning and progress tracking",
        "docs": "/api/docs"
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring.
    
    Returns:
        dict: Status information
    """
    return {"status": "healthy"}


if __name__ == "__main__":
    """
    Run the application with Uvicorn when executed directly.
    
    This allows the application to be run with:
    python -m app.main
    """
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)