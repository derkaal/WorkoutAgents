"""
FastAPI router for the 'Mike Lawry' workout generation endpoint.

This module defines an asynchronous API endpoint for generating workouts
using the Mike Lawry agent.
"""

import base64
import json
from fastapi import APIRouter, HTTPException
from pydantic import ValidationError
from models.schemas import WorkoutRequest, WorkoutResponse, WorkoutPlan
from agents.mike_lawry import mike_agent_executor
from services.eleven_labs_client import ElevenLabsClient
from utils.text_cleaner import clean_text_for_tts
from langchain_core.messages import HumanMessage


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
            # Convert the briefing to a list of messages as expected by the agent
            briefing_content = request_data.trystero_briefing
            
            # If the briefing is a string, convert it to a readable format
            if isinstance(briefing_content, str):
                message_content = f"Trystero Briefing: {briefing_content}"
            else:
                # Format dictionary in a readable way
                message_content = "Trystero Briefing:\n"
                for key, value in briefing_content.items():
                    message_content += f"- {key}: {value}\n"
            
            # Create a list of messages as expected by the MessagesPlaceholder
            agent_input["trystero_briefing"] = [
                HumanMessage(content=message_content)
            ]
        
        # Call the agent executor
        result = await mike_agent_executor.ainvoke(agent_input)
        
        # Extract the response text and any generated plan
        # The output format depends on how mike_agent_executor structures its response
        mike_response_text = result.get("output", "")
        
        # The generated plan might be in a specific format or part of the response
        # This is a simplified extraction - adjust based on actual response structure
        generated_plan = None
        # The generated plan should now be a dictionary that conforms to the WorkoutPlan schema
        generated_plan_data = result.get("plan")
        if generated_plan_data:
            try:
                generated_plan = WorkoutPlan(**generated_plan_data)
            except ValidationError as e:
                print(f"Error validating generated plan against schema: {e.errors()}")
                generated_plan = None # Set to None if validation fails
        
        # Generate audio using ElevenLabs
        audio_base64 = None
        try:
            # Instantiate the ElevenLabs client
            eleven_labs_client = ElevenLabsClient()
            
            # Convert text to speech
            cleaned_mike_response_text = clean_text_for_tts(mike_response_text)
            audio_bytes = await eleven_labs_client.text_to_speech(
                text_input=cleaned_mike_response_text,
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
# from backend.app.routers.workout import router as workout_router
# app.include_router(workout_router)