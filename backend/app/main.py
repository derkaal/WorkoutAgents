"""
FastAPI main application for the Workout Agents API.

This module initializes the FastAPI application, includes routers,
sets up middleware, and configures the application to run with Uvicorn.
"""

# Use pydantic v1 compatibility for components not fully compatible with v2
import os
os.environ["PYDANTIC_V1"] = "1"

# Monkey patch SecretStr to add the missing __get_pydantic_json_schema__ method
# This fixes the compatibility issue with Pydantic v2
import sys
from pydantic import SecretStr

# Only add the method if it doesn't already exist
if not hasattr(SecretStr, "__get_pydantic_json_schema__"):
    def _secret_str_get_json_schema(cls, _schema_generator, _field_schema):
        schema = _field_schema or {}
        schema.update(type="string", format="password")
        return schema
    
    # Add the missing method to SecretStr
    setattr(SecretStr, "__get_pydantic_json_schema__", classmethod(_secret_str_get_json_schema))

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import routers

# Add the parent directory to sys.path to allow imports to work
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Now we can import using the app prefix
from routers.workout import router as workout_router
from routers.progress import router as progress_router

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

# Create data directory for workout history if it doesn't exist
data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
if not os.path.exists(data_dir):
    os.makedirs(data_dir)
    print(f"Created data directory at {data_dir}")

# Import workout history router
from routers.workout_history import router as workout_history_router

# Include routers
app.include_router(workout_router)
app.include_router(progress_router)
app.include_router(workout_history_router)


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
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)