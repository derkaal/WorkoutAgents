"""
Workout History Validation Tool

This module provides tools for checking workout history and determining
if rest should be recommended based on consecutive days and weekly goals.
"""

from langchain_core.tools import tool
from typing import Dict, Any, Optional
from backend.app.models.workout_history import WorkoutHistory
import os
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Initialize workout history with data directory path
history_file_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 
    "app", 
    "data", 
    "workout_history.json"
)
workout_history = WorkoutHistory(history_file_path=history_file_path)

@tool
def check_workout_history() -> Dict[str, Any]:
    """
    Checks the user's workout history to determine if rest should be recommended
    based on consecutive workout days and weekly goal achievement.
    
    Returns a dictionary containing workout history summary, including:
    - Weekly workout count
    - Consecutive workout days
    - Whether rest is recommended
    - Any warnings or recommendations
    
    This tool should be used before recommending new workouts to ensure
    proper recovery and avoid overtraining.
    """
    try:
        # Get workout history summary
        summary = workout_history.get_workout_history_summary()
        
        # Add empty lists for warnings and recommendations if they don't exist
        if "warnings" not in summary:
            summary["warnings"] = []
        if "recommendations" not in summary:
            summary["recommendations"] = []
        
        # Check consecutive days
        consecutive_days = summary.get("consecutive_days", 0)
        max_consecutive_days = summary.get("max_consecutive_days", 3)
        
        if consecutive_days >= max_consecutive_days:
            summary["warnings"].append(
                f"User has worked out {consecutive_days} consecutive days, "
                f"which equals or exceeds the recommended maximum of {max_consecutive_days}."
            )
            summary["recommendations"].append(
                "Recommend taking a rest day to allow for recovery."
            )
        
        # Check weekly goal
        weekly_count = summary.get("weekly_count", 0)
        weekly_goal = summary.get("weekly_goal", 4)
        
        if weekly_count >= weekly_goal:
            summary["recommendations"].append(
                f"User has reached their weekly goal of {weekly_goal} workouts. "
                f"Consider suggesting a lighter workout or rest day."
            )
        
        return summary
    except Exception as e:
        logger.error(f"Error checking workout history: {str(e)}")
        return {
            "status": "error",
            "message": f"Failed to check workout history: {str(e)}",
            "warnings": ["Unable to check workout history due to an error"],
            "recommendations": ["Proceed with caution"],
            "rest_recommended": False
        }

@tool
def record_workout_completion(workout_type: str) -> Dict[str, Any]:
    """
    Records a completed workout in the workout history.
    
    Args:
        workout_type: Type of workout completed (strength, yoga, runs)
        
    Returns:
        A dictionary with status, warnings, and recommendations
    """
    try:
        # Validate workout type
        valid_types = ["strength", "yoga", "runs"]
        if workout_type not in valid_types:
            return {
                "status": "error",
                "message": f"Invalid workout type. Must be one of: {', '.join(valid_types)}",
                "warnings": [],
                "recommendations": []
            }
        
        # Record the workout
        result = workout_history.record_workout(workout_type=workout_type)
        
        return result
    except Exception as e:
        logger.error(f"Error recording workout completion: {str(e)}")
        return {
            "status": "error",
            "message": f"Failed to record workout: {str(e)}",
            "warnings": [],
            "recommendations": []
        }