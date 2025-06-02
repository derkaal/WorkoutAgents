"""
FastAPI router for the 'Mike Lawry' workout generation endpoint.

This module defines an asynchronous API endpoint for generating workouts
using the Mike Lawry agent.
"""

import base64
from fastapi import APIRouter, HTTPException
from app.models.schemas import WorkoutRequest, WorkoutResponse
from app.agents.mike_lawry import mike_agent_executor
from app.services.eleven_labs_client import ElevenLabsClient


# Create router with prefix and tags
router = APIRouter(prefix="/api/v1", tags=["workout"])


@router.post("/generate-workout/", response_model=WorkoutResponse)
async def generate_workout(request_data: WorkoutRequest) -> WorkoutResponse:
    """
    Generate a workout plan using the Mike Lawry agent.
    
    This endpoint takes a user's workout request and optional Trystero briefing data,
    then uses the Mike Lawry agent to generate a personalized workout plan.
    
    Args:
        request_data: The workout request containing user input and optional briefing
    
    Returns:
        A WorkoutResponse containing Mike's response text and the generated workout plan
    
    Raises:
        HTTPException: If there's an error during workout generation
    
    Example:
        ```python
        from fastapi import FastAPI
        from app.models.schemas import WorkoutRequest
        
        app = FastAPI()
        
        # Create a request
        request = WorkoutRequest(
            user_input="I need a 3-day full body workout plan for strength",
            trystero_briefing={
                "fitness_level": "intermediate",
                "focus_areas": ["strength", "hypertrophy"],
                "previous_adherence": 0.8
            }
        )
        
        # Call the endpoint
        response = await client.post("/api/v1/generate-workout/", json=request.dict())
        workout_response = response.json()
        ```
    """
    try:
        # Prepare the input for mike_agent_executor
        agent_input = {
            "input": request_data.user_input,
            "chat_history": []
        }
        
        # Add trystero_briefing if provided
        if request_data.trystero_briefing:
            agent_input["trystero_briefing"] = request_data.trystero_briefing
        
        # Call the agent executor
        result = await mike_agent_executor.ainvoke(agent_input)
        
        # Extract the response text and any generated plan
        # The output format depends on how mike_agent_executor structures its response
        mike_response_text = result.get("output", "")
        
        # The generated plan might be in a specific format or part of the response
        # This is a simplified extraction - adjust based on actual response structure
        generated_plan = None
        if isinstance(result, dict) and "plan" in result:
            generated_plan = result["plan"]
        
        # Generate audio using ElevenLabs
        audio_base64 = None
        try:
            # Instantiate the ElevenLabs client
            eleven_labs_client = ElevenLabsClient()
            
            # Convert text to speech
            audio_bytes = await eleven_labs_client.text_to_speech(
                text_input=mike_response_text,
                voice_id='6OzrBCQf8cjERkYgzSg8'
            )
            
            # Encode audio bytes to base64
            audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
        except Exception as e:
            # Log the error but continue with text response
            print(f"Error generating audio: {str(e)}")
            # We don't raise an exception here to ensure the API still returns a text response
        
        # Return the workout response with audio if available
        return WorkoutResponse(
            mike_response_text=mike_response_text,
            generated_plan=generated_plan,
            audio_base64=audio_base64
        )
    
    except Exception as e:
        # Log the error (in a production environment)
        print(f"Error generating workout: {str(e)}")
        
        # Raise an HTTP exception
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate workout: {str(e)}"
        )


# In your main.py file, include this router with:
# from app.routers.workout import router as workout_router
# app.include_router(workout_router)