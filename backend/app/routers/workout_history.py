"""
Workout History Router

This module provides API endpoints for tracking workout history:
- Record workout completion
- Get workout history summary
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from datetime import datetime
import os
import logging

from backend.app.models.workout_history import WorkoutHistory

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(
    prefix="/api/v1/workout-history",
    tags=["workout-history"],
    responses={404: {"description": "Not found"}},
)

# Create a singleton instance of WorkoutHistory
# Use a data directory within the app directory
history_file_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
    "data", 
    "workout_history.json"
)
workout_history = WorkoutHistory(history_file_path=history_file_path)


class WorkoutCompletionRequest(BaseModel):
    """Request model for recording workout completion."""
    workout_type: str = Field(
        ..., 
        description="Type of workout completed (strength, yoga, runs)"
    )
    date: Optional[datetime] = Field(
        None, 
        description="Date of workout completion (defaults to current date/time)"
    )


class WorkoutHistoryResponse(BaseModel):
    """Response model for workout history data."""
    weekly_count: int = Field(..., description="Number of workouts in the current week")
    weekly_goal: int = Field(..., description="Weekly workout goal target")
    weekly_completion_percentage: float = Field(
        ..., 
        description="Percentage of weekly goal completed"
    )
    consecutive_days: int = Field(
        ..., 
        description="Number of consecutive days with workouts"
    )
    max_consecutive_days: int = Field(
        ...,
        description="Maximum recommended consecutive workout days"
    )
    distribution: Dict[str, float] = Field(
        ...,
        description="Distribution of workout types as percentages"
    )
    rest_recommended: bool = Field(
        ...,
        description="Whether a rest day is recommended"
    )
    warnings: List[str] = Field(
        [],
        description="Any warnings about workout patterns"
    )
    recommendations: List[str] = Field(
        [],
        description="Recommendations for future workouts"
    )


@router.post("/record", response_model=Dict[str, Any])
async def record_workout_completion(request: WorkoutCompletionRequest):
    """
    Record a completed workout and return status with any warnings or recommendations.
    """
    try:
        # Validate workout type
        valid_types = ["strength", "yoga", "runs"]
        if request.workout_type not in valid_types:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid workout type. Must be one of: {', '.join(valid_types)}"
            )
        
        # Record the workout
        result = workout_history.record_workout(
            workout_type=request.workout_type,
            date=request.date
        )
        
        return result
    except Exception as e:
        logger.error(f"Error recording workout: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to record workout: {str(e)}"
        )


@router.get("/summary", response_model=WorkoutHistoryResponse)
async def get_workout_history_summary():
    """
    Get a summary of workout history, including weekly count, consecutive days,
    and distribution of workout types.
    """
    try:
        summary = workout_history.get_workout_history_summary()
        
        # Add empty lists for warnings and recommendations if they don't exist
        if "warnings" not in summary:
            summary["warnings"] = []
        if "recommendations" not in summary:
            summary["recommendations"] = []
        
        # Add rest recommendation if needed
        if summary["rest_recommended"] and "Consider taking a rest day" not in summary["recommendations"]:
            summary["recommendations"].append(
                "Consider taking a rest day to allow for recovery."
            )
        
        return summary
    except Exception as e:
        logger.error(f"Error retrieving workout history: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve workout history: {str(e)}"
        )