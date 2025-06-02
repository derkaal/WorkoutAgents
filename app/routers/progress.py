"""
FastAPI router for the 'Trystero' progress analysis endpoint.

This module defines an asynchronous API endpoint for analyzing workout progress
using the Trystero agent.
"""

import base64
from fastapi import APIRouter, HTTPException
from app.models.schemas import ProgressAnalysisRequest, ProgressAnalysisResponse
from app.agents.trystero import trystero_agent_executor
from app.services.eleven_labs_client import ElevenLabsClient


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
        # Prepare the input for trystero_agent_executor
        agent_input = {
            "input": f"Analyze this progress data: {request_data.progress_data}"
        }
        
        # Call the agent executor
        result = await trystero_agent_executor.ainvoke(agent_input)
        
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
            audio_bytes = await eleven_labs_client.text_to_speech(
                text_input=trystero_feedback_text,
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
# from app.routers.progress import router as progress_router
# app.include_router(progress_router)