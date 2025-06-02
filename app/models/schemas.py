"""
Pydantic models for the FastAPI backend.

This module defines the request and response structures for two agents:
- Mike Lawry (workout generation)
- Trystero (progress analysis)
"""

from typing import Dict, Optional, Any
from pydantic import BaseModel, Field



class WorkoutRequest(BaseModel):
    """
    Request model for Mike Lawry's workout generation.
    
    Attributes:
        user_input: The user's workout request text
        trystero_briefing: Optional briefing data from Trystero
        
    Example:
        ```json
        {
            "user_input": "I need a 3-day full body workout plan for strength",
            "trystero_briefing": {
                "fitness_level": "intermediate",
                "focus_areas": ["strength", "hypertrophy"],
                "previous_adherence": 0.8
            }
        }
        ```
    """
    user_input: str = Field(..., description="The user's workout request")
    trystero_briefing: Optional[Dict[str, Any]] = Field(
        None, 
        description="Optional briefing data from Trystero's analysis"
    )
    
    class Config:
        """Pydantic model configuration."""
        schema_extra = {
            "example": {
                "user_input": "I need a 3-day full body workout plan for strength",
                "trystero_briefing": {
                    "fitness_level": "intermediate",
                    "focus_areas": ["strength", "hypertrophy"],
                    "previous_adherence": 0.8
                }
            }
        }


class WorkoutResponse(BaseModel):
    """
    Response model for Mike Lawry's workout generation.
    
    Attributes:
        mike_response_text: Mike's enthusiastic output text
        generated_plan: Optional structured workout plan
        
    Example:
        ```json
        {
            "mike_response_text": "BOOM! Here's your 3-day full body strength plan!",
            "generated_plan": {
                "days": [
                    {
                        "name": "Day 1 - Push Focus",
                        "exercises": [
                            {"name": "Bench Press", "sets": 4, "reps": "6-8"},
                            {"name": "Squats", "sets": 4, "reps": "6-8"},
                            {"name": "Overhead Press", "sets": 3, "reps": "8-10"}
                        ]
                    },
                    {
                        "name": "Day 2 - Pull Focus",
                        "exercises": [
                            {"name": "Deadlifts", "sets": 4, "reps": "5-6"},
                            {"name": "Pull-ups", "sets": 4, "reps": "8-10"},
                            {"name": "Barbell Rows", "sets": 3, "reps": "8-10"}
                        ]
                    }
                ]
            }
        }
        ```
    """
    mike_response_text: str = Field(..., description="Mike's enthusiastic output text")
    generated_plan: Optional[Dict[str, Any]] = Field(
        None,
        description="The structured workout plan"
    )
    audio_base64: Optional[str] = Field(
        None,
        description="Base64-encoded audio of Mike's response"
    )
    
    class Config:
        """Pydantic model configuration."""
        schema_extra = {
            "example": {
                "mike_response_text": "BOOM! Here's your 3-day full body strength plan!",
                "generated_plan": {
                    "days": [
                        {
                            "name": "Day 1 - Push Focus",
                            "exercises": [
                                {"name": "Bench Press", "sets": 4, "reps": "6-8"},
                                {"name": "Squats", "sets": 4, "reps": "6-8"},
                                {"name": "Overhead Press", "sets": 3, "reps": "8-10"}
                            ]
                        },
                        {
                            "name": "Day 2 - Pull Focus",
                            "exercises": [
                                {"name": "Deadlifts", "sets": 4, "reps": "5-6"},
                                {"name": "Pull-ups", "sets": 4, "reps": "8-10"},
                                {"name": "Barbell Rows", "sets": 3, "reps": "8-10"}
                            ]
                        }
                    ]
                },
                "audio_base64": "base64_encoded_audio_string_here"
            }
        }


class ProgressAnalysisRequest(BaseModel):
    """
    Request model for Trystero's progress analysis.
    
    Attributes:
        progress_data: The user's progress data
        
    Example:
        ```json
        {
            "progress_data": {
                "completed_workouts": [
                    {
                        "date": "2025-05-25",
                        "workout_id": "strength_day1",
                        "completed_exercises": [
                            {"name": "Bench Press", "sets_completed": 4, "reps_per_set": [8, 7, 7, 6]},
                            {"name": "Squats", "sets_completed": 3, "reps_per_set": [8, 7, 6]}
                        ],
                        "difficulty_rating": 7,
                        "energy_level": 6
                    }
                ],
                "measurements": {
                    "weight": [{"date": "2025-05-20", "value": 75.5}, {"date": "2025-05-27", "value": 75.2}],
                    "body_fat": [{"date": "2025-05-20", "value": 18.2}, {"date": "2025-05-27", "value": 17.9}]
                },
                "subjective_feedback": "Feeling stronger but still struggling with squats"
            }
        }
        ```
    """
    progress_data: Dict[str, Any] = Field(..., description="The user's progress data")
    
    class Config:
        """Pydantic model configuration."""
        schema_extra = {
            "example": {
                "progress_data": {
                    "completed_workouts": [
                        {
                            "date": "2025-05-25",
                            "workout_id": "strength_day1",
                            "completed_exercises": [
                                {"name": "Bench Press", "sets_completed": 4, "reps_per_set": [8, 7, 7, 6]},
                                {"name": "Squats", "sets_completed": 3, "reps_per_set": [8, 7, 6]}
                            ],
                            "difficulty_rating": 7,
                            "energy_level": 6
                        }
                    ],
                    "measurements": {
                        "weight": [{"date": "2025-05-20", "value": 75.5}, {"date": "2025-05-27", "value": 75.2}],
                        "body_fat": [{"date": "2025-05-20", "value": 18.2}, {"date": "2025-05-27", "value": 17.9}]
                    },
                    "subjective_feedback": "Feeling stronger but still struggling with squats"
                }
            }
        }


class ProgressAnalysisResponse(BaseModel):
    """
    Response model for Trystero's progress analysis.
    
    Attributes:
        trystero_feedback_text: Trystero's feedback text
        briefing_for_next_plan: Optional briefing for the next workout plan
        
    Example:
        ```json
        {
            "trystero_feedback_text": "Your progress shows consistent improvement in upper body strength. Your squat form may need attention based on your feedback.",
            "briefing_for_next_plan": {
                "fitness_level": "intermediate",
                "focus_areas": ["lower body strength", "squat technique"],
                "recommended_adjustments": {
                    "squat_weight": "reduce by 10%",
                    "add_assistance_exercises": ["goblet squats", "leg press"]
                },
                "previous_adherence": 0.85
            }
        }
        ```
    """
    trystero_feedback_text: str = Field(..., description="Trystero's feedback text")
    briefing_for_next_plan: Optional[Dict[str, Any]] = Field(
        None,
        description="Briefing for the next workout plan"
    )
    audio_base64: Optional[str] = Field(
        None,
        description="Base64-encoded audio of Trystero's feedback"
    )
    
    class Config:
        """Pydantic model configuration."""
        schema_extra = {
            "example": {
                "trystero_feedback_text": "Your progress shows consistent improvement in upper body strength. Your squat form may need attention based on your feedback.",
                "briefing_for_next_plan": {
                    "fitness_level": "intermediate",
                    "focus_areas": ["lower body strength", "squat technique"],
                    "recommended_adjustments": {
                        "squat_weight": "reduce by 10%",
                        "add_assistance_exercises": ["goblet squats", "leg press"]
                    },
                    "previous_adherence": 0.85
                },
                "audio_base64": "base64_encoded_audio_string_here"
            }
        }