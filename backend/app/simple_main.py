"""
Simplified FastAPI main application for testing after directory move.
"""

# Use pydantic v1 compatibility for components not fully compatible with v2
import os
os.environ["PYDANTIC_V1"] = "1"

# Import FastAPI components
from fastapi import FastAPI, Body
from fastapi.middleware.cors import CORSMiddleware

# Import schema models
from models.schemas import (
    WorkoutRequest,
    WorkoutResponse,
    ProgressAnalysisRequest,
    ProgressAnalysisResponse
)

# Create FastAPI application with metadata
app = FastAPI(
    title="Workout Agents API",
    description="A multi-agent system for workout planning and progress tracking.",
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

# Simple mock endpoints to replace the agent-based ones
@app.post("/api/v1/generate-workout/", response_model=WorkoutResponse)
async def generate_workout(request: WorkoutRequest = Body(...)):
    """Mock workout generation endpoint"""
    return WorkoutResponse(
        mike_response_text="This is a mock response from Mike Lawry",
        generated_plan={
            "days": [
                {
                    "name": "Day 1 - Push Focus",
                    "exercises": [
                        {"name": "Bench Press", "sets": 4, "reps": "6-8"}
                    ]
                }
            ]
        }
    )

@app.post("/api/v1/analyze-progress/", response_model=ProgressAnalysisResponse)
async def analyze_progress(request: ProgressAnalysisRequest = Body(...)):
    """Mock progress analysis endpoint"""
    return ProgressAnalysisResponse(
        trystero_feedback_text="This is a mock response from Trystero",
        briefing_for_next_plan={
            "fitness_level": "intermediate",
            "focus_areas": ["strength"]
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("simple_main:app", host="0.0.0.0", port=8000, reload=True)