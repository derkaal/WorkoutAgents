"""
ElevenLabs API Integration Example

This module demonstrates secure handling of API keys for ElevenLabs
text-to-speech integration. It shows proper environment variable loading,
validation, and usage in API calls.
"""

import os
import sys
from typing import Optional
from dotenv import load_dotenv
import requests
from pydantic import BaseModel, Field, validator


class EnvironmentConfig(BaseModel):
    """Validate and store environment configuration."""
    
    elevenlabs_api_key: str = Field(..., min_length=32)
    
    @validator("elevenlabs_api_key")
    def validate_api_key(cls, v):
        """Ensure API key meets minimum security requirements."""
        if not v or len(v) < 32:
            raise ValueError("ElevenLabs API key is missing or invalid")
        return v


def load_environment() -> EnvironmentConfig:
    """
    Load and validate environment variables.
    
    Returns:
        EnvironmentConfig: Validated environment configuration
        
    Raises:
        ValueError: If required environment variables are missing or invalid
    """
    # Load environment variables from .env file
    load_dotenv()
    
    try:
        # Create and validate config
        config = EnvironmentConfig(
            elevenlabs_api_key=os.getenv("ELEVENLABS_API_KEY", "")
        )
        return config
    except ValueError as e:
        print(f"Environment configuration error: {e}")
        sys.exit(1)


def text_to_speech(text: str, voice_id: str = "21m00Tcm4TlvDq8ikWAM") -> Optional[bytes]:
    """
    Convert text to speech using ElevenLabs API.
    
    Args:
        text: The text to convert to speech
        voice_id: The ElevenLabs voice ID to use (default: Rachel voice)
        
    Returns:
        Optional[bytes]: Audio data if successful, None otherwise
    """
    # Load environment configuration securely
    config = load_environment()
    
    # API endpoint
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    
    # Request headers with API key
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": config.elevenlabs_api_key
    }
    
    # Request body
    data = {
        "text": text,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.5
        }
    }
    
    try:
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()
        return response.content
    except requests.exceptions.RequestException as e:
        print(f"Error calling ElevenLabs API: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response status code: {e.response.status_code}")
            print(f"Response body: {e.response.text}")
        return None


def save_audio_file(audio_data: bytes, output_file: str = "output.mp3") -> bool:
    """
    Save audio data to a file.
    
    Args:
        audio_data: The audio data to save
        output_file: The output file path
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        with open(output_file, "wb") as f:
            f.write(audio_data)
        print(f"Audio saved to {output_file}")
        return True
    except Exception as e:
        print(f"Error saving audio file: {e}")
        return False


def main():
    """Example usage of the ElevenLabs text-to-speech API."""
    # Example text to convert to speech
    text = "This is a secure example of using the ElevenLabs API with proper API key handling."
    
    # Convert text to speech
    audio_data = text_to_speech(text)
    
    # Save audio to file if successful
    if audio_data:
        save_audio_file(audio_data)


if __name__ == "__main__":
    main()