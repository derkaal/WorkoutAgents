"""
Application Integration Example

This module demonstrates how to integrate secure API key handling
into the main application using the environment validator.
"""

import os
from fastapi import FastAPI, Depends, HTTPException, status, Response
from typing import Dict, Callable
from env_validator import validate_environment_or_exit, APIKeyConfig
from pydantic import BaseModel
from dotenv import load_dotenv
import requests


# Load environment variables at module level
load_dotenv()


class EnvDependency:
    """Dependency provider for validated environment variables."""
    
    def __init__(self):
        """Initialize with validated environment variables."""
        # Validate environment on initialization
        self.env_vars = validate_environment_or_exit()
    
    def get_openai_key(self) -> str:
        """Get validated OpenAI API key."""
        return self.env_vars.get("openai_api_key", "")
    
    def get_mistral_key(self) -> str:
        """Get validated Mistral API key."""
        return self.env_vars.get("mistral_api_key", "")
    
    def get_elevenlabs_key(self) -> str:
        """Get validated ElevenLabs API key."""
        return self.env_vars.get("elevenlabs_api_key", "")


# Create a singleton instance
env_dependency = EnvDependency()


# FastAPI dependency functions
def get_openai_key() -> str:
    """Dependency for OpenAI API key."""
    return env_dependency.get_openai_key()


def get_mistral_key() -> str:
    """Dependency for Mistral API key."""
    return env_dependency.get_mistral_key()


def get_elevenlabs_key() -> str:
    """Dependency for ElevenLabs API key."""
    return env_dependency.get_elevenlabs_key()


# Example FastAPI application with secure API key handling
app = FastAPI(
    title="Secure API Integration Example",
    description="Demonstrates secure API key handling in a FastAPI application",
    version="1.0.0"
)


class TextToSpeechRequest(BaseModel):
    """Request model for text-to-speech conversion."""
    
    text: str
    voice_id: str = "21m00Tcm4TlvDq8ikWAM"  # Default voice ID


@app.post("/api/text-to-speech")
async def text_to_speech(
    request: TextToSpeechRequest,
    elevenlabs_api_key: str = Depends(get_elevenlabs_key)
):
    """
    Convert text to speech using ElevenLabs API.
    
    This endpoint demonstrates secure API key handling using FastAPI dependencies.
    The API key is injected via dependency injection rather than being hardcoded.
    """
    # API endpoint
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{request.voice_id}"
    
    # Request headers with API key from dependency
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": elevenlabs_api_key
    }
    
    # Request body
    data = {
        "text": request.text,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.5
        }
    }
    
    try:
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()
        
        # Return audio data as a response with appropriate content type
        return Response(
            content=response.content,
            media_type="audio/mpeg"
        )
    except requests.exceptions.RequestException as e:
        # Log error without exposing API key
        print(f"Error calling ElevenLabs API: {type(e).__name__}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response status code: {e.response.status_code}")
        
        # Return appropriate error response
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error processing text-to-speech request"
        )


# Example of integrating with the existing Mike Lawry agent
def integrate_with_mike_agent():
    """
    Example of how to integrate secure API key handling with the Mike Lawry agent.
    
    This is a code snippet showing how the existing agent code could be modified
    to use the secure environment validation.
    """
    # Import necessary components
    from langchain_openai import ChatOpenAI
    from langchain_core.prompts import ChatPromptTemplate
    from langchain.agents import AgentExecutor, create_openai_functions_agent
    
    # Validate environment variables
    env_vars = validate_environment_or_exit({"openai_api_key"})
    
    # Initialize the LLM with the validated API key
    # Note: We're not using os.getenv directly anymore
    llm = ChatOpenAI(
        api_key=env_vars["openai_api_key"],
        model="gpt-4o",
        temperature=0.7
    )
    
    # Create a prompt template
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are Mike Lawry, a fitness trainer."),
        ("human", "{input}")
    ])
    
    # Create the agent
    agent = create_openai_functions_agent(llm, [], prompt)
    agent_executor = AgentExecutor(agent=agent, tools=[], verbose=True)
    
    return agent_executor


# Example of integrating with the existing Trystero agent
def integrate_with_trystero_agent():
    """
    Example of how to integrate secure API key handling with the Trystero agent.
    
    This is a code snippet showing how the existing agent code could be modified
    to use the secure environment validation.
    """
    # Import necessary components
    from langchain_mistralai.chat_models import ChatMistralAI
    from langchain_core.prompts import ChatPromptTemplate
    from langchain.agents import AgentExecutor, create_tool_calling_agent
    
    # Validate environment variables
    env_vars = validate_environment_or_exit({"mistral_api_key"})
    
    # Initialize the LLM with the validated API key
    # Note: We're not using os.getenv directly anymore
    llm = ChatMistralAI(
        api_key=env_vars["mistral_api_key"],
        model="mistral-small-latest",
        temperature=0.5
    )
    
    # Create a prompt template
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are Trystero, a progress tracking analyst."),
        ("human", "{input}")
    ])
    
    # Create the agent
    agent = create_tool_calling_agent(llm, [], prompt)
    agent_executor = AgentExecutor(agent=agent, tools=[], verbose=True)
    
    return agent_executor


if __name__ == "__main__":
    """
    Run the application with Uvicorn when executed directly.
    
    This allows the application to be run with:
    python -m app_integration_example
    """
    import uvicorn
    
    # Validate environment variables before starting the server
    print("Validating environment variables...")
    validate_environment_or_exit()
    print("Environment validation successful!")
    
    # Start the server
    uvicorn.run("app_integration_example:app", host="0.0.0.0", port=8000, reload=True)