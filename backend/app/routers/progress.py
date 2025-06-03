"""
FastAPI router for the 'Trystero' progress analysis endpoint.

This module defines an asynchronous API endpoint for analyzing workout progress
using the Trystero agent.
"""

import base64
from fastapi import APIRouter, HTTPException
from models.schemas import ProgressAnalysisRequest, ProgressAnalysisResponse
from agents.trystero import validation_agent
from services.eleven_labs_client import ElevenLabsClient
from utils.text_cleaner import clean_text_for_tts


# Create router with prefix and tags
router = APIRouter(prefix="/api/v1", tags=["progress"])


@router.post("/analyze-progress/", response_model=ProgressAnalysisResponse)
async def analyze_progress(request_data: ProgressAnalysisRequest) -> ProgressAnalysisResponse:
    """
    Analyze workout progress data using the Trystero agent.
    
    This endpoint takes a user's progress data and uses the Trystero agent
    to analyze it and provide feedback and recommendations for future workouts.
    
    Args:
        request_data: The progress analysis request containing progress data
    
    Returns:
        A ProgressAnalysisResponse containing Trystero's feedback and briefing for next plan
    
    Raises:
        HTTPException: If there's an error during progress analysis
    
    Example:
        ```python
        from fastapi import FastAPI
        from app.models.schemas import ProgressAnalysisRequest
        
        app = FastAPI()
        
        # Create a request
        request = ProgressAnalysisRequest(
            progress_data={
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
        )
        
        # Call the endpoint
        response = await client.post("/api/v1/analyze-progress/", json=request.dict())
        analysis_response = response.json()
        ```
    """
    try:
        # TEMPORARY WORKAROUND: Implement a direct mock response instead of using the agent
        # This will help us test the API endpoint while we fix the underlying agent issue
        import traceback
        
        progress_dict = dict(request_data.progress_data)
        print(f"DEBUG - Progress dict: {progress_dict}")
        
        # Mock implementation for testing
        try:
            # Get workout goal rules from validation agent
            workout_goals = validation_agent.instance_rules.get('workout_goals', {})
            weekly_target = workout_goals.get('weekly_target', 4)  # Default to 4 if not specified
            calculation_method = workout_goals.get('calculation_method', 'any_type')
            
            # Get individual workout counts
            strength_done = progress_dict.get("strength_done", 0)
            yoga_done = progress_dict.get("yoga_done", 0)
            runs_done = progress_dict.get("runs_done", 0)
            
            # Calculate total workouts completed based on calculation method
            if calculation_method == 'any_type':
                # Any workout type counts toward the total
                total_workouts = strength_done + yoga_done + runs_done
            else:
                # Future implementation could support different calculation methods
                # For now, default to the 'any_type' method
                total_workouts = strength_done + yoga_done + runs_done
            
            # Calculate overall completion percentage (capped at 100%)
            overall_completion = min((total_workouts / weekly_target) * 100, 100)
            
            # Calculate distribution percentages
            if total_workouts > 0:
                strength_distribution = (strength_done / total_workouts) * 100
                yoga_distribution = (yoga_done / total_workouts) * 100
                runs_distribution = (runs_done / total_workouts) * 100
            else:
                strength_distribution = 0
                yoga_distribution = 0
                runs_distribution = 0
            
            # Generate mock analysis with new calculation approach
            trystero_feedback = (
                f"Progress analysis: You've completed {overall_completion:.0f}% of your weekly goal "
                f"({total_workouts} of {weekly_target} workouts).\n\n"
                f"Workout distribution: {strength_distribution:.0f}% strength, "
                f"{yoga_distribution:.0f}% yoga, and {runs_distribution:.0f}% running.\n\n"
                f"Notable patterns: {progress_dict.get('notes', 'No notes provided.')}"
            )
            
            # Create a dynamic mock result based on user input
            # Extract useful information from the progress data
            strength_done = progress_dict.get('strength_done', 0)
            yoga_done = progress_dict.get('yoga_done', 0)
            runs_done = progress_dict.get('runs_done', 0)
            notes = progress_dict.get('notes', '').lower()
            
            # Generate focus areas based on actual data
            focus_areas = []
            if strength_done > 0:
                focus_areas.append("strength training")
            if yoga_done > 0:
                focus_areas.append("yoga consistency")
            if runs_done > 0:
                focus_areas.append("cardio endurance")
            # Default if nothing done yet
            if not focus_areas:
                focus_areas = ["general fitness"]
            
            # Generate recommendations based on notes and activity balance
            recommendations = ""
            if "strength" in notes:
                recommendations += "Focus on strength training as requested. "
            elif "yoga" in notes:
                recommendations += "Incorporate more yoga sessions as mentioned. "
            elif "run" in notes or "cardio" in notes:
                recommendations += "Emphasize cardio workouts as indicated. "
            
            # Balance recommendation based on activity counts
            activity_counts = [strength_done, yoga_done, runs_done]
            if max(activity_counts) > 0 and min(activity_counts) == 0:
                # If some activities have count > 0 but others are 0, recommend balance
                if strength_done == 0:
                    recommendations += "Add strength training for better balance. "
                if yoga_done == 0:
                    recommendations += "Consider adding yoga for flexibility and recovery. "
                if runs_done == 0:
                    recommendations += "Include some cardio for heart health. "
            
            if not recommendations:
                recommendations = "Maintain a balanced routine with a mix of strength, yoga, and cardio."
            
            # Create the result with dynamic briefing data
            result = {
                "output": trystero_feedback,
                "briefing_for_next_plan": {
                    "focus_areas": focus_areas,
                    "activity_counts": {
                        "strength": strength_done,
                        "yoga": yoga_done,
                        "cardio": runs_done
                    },
                    "progress": {
                        "overall_completion": overall_completion,
                        "total_workouts": total_workouts,
                        "weekly_target": weekly_target,
                        "distribution": {
                            "strength": strength_distribution,
                            "yoga": yoga_distribution,
                            "runs": runs_distribution
                        }
                    },
                    "recommendations": recommendations.strip()
                }
            }
            
        except Exception as e:
            print(f"Error in mock implementation: {str(e)}")
            print(traceback.format_exc())
            result = {
                "output": "Error analyzing your progress data. Please try again later."
            }
        
        # Extract the response text and any generated briefing
        trystero_feedback_text = result.get("output", "")
        
        # Extract the briefing for next plan if available
        briefing_for_next_plan = None
        if isinstance(result, dict) and "briefing_for_next_plan" in result:
            briefing_for_next_plan = result["briefing_for_next_plan"]
        
        # Generate audio using ElevenLabs
        audio_base64 = None
        try:
            # Instantiate the ElevenLabs client
            eleven_labs_client = ElevenLabsClient()
            
            # Convert text to speech
            cleaned_trystero_feedback_text = clean_text_for_tts(trystero_feedback_text)
            audio_bytes = await eleven_labs_client.text_to_speech(
                text_input=cleaned_trystero_feedback_text,
                voice_id='QMJTqaMXmGnG8TCm8WQG'
            )
            
            # Encode audio bytes to base64
            audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
        except Exception as e:
            # Log the error but continue with text response
            print(f"Error generating audio: {str(e)}")
            # We don't raise an exception here to ensure the API still returns a text response
        
        # Return the progress analysis response with audio if available
        return ProgressAnalysisResponse(
            trystero_feedback_text=trystero_feedback_text,
            briefing_for_next_plan=briefing_for_next_plan,
            audio_base64=audio_base64
        )
    
    except Exception as e:
        # Log the error (in a production environment)
        print(f"Error analyzing progress: {str(e)}")
        
        # Raise an HTTP exception
        raise HTTPException(
            status_code=500,
            detail=f"Failed to analyze progress: {str(e)}"
        )


# In your main.py file, include this router with:
# from backend.app.routers.progress import router as progress_router
# app.include_router(progress_router)