"""
ElevenLabs Client Service

This module provides a client for interacting with the ElevenLabs API
using their official SDK. It handles secure API key management and
provides asynchronous methods for text-to-speech conversion.
"""

import os
import logging
import asyncio
from dotenv import load_dotenv
from pydantic import BaseModel, Field, validator

# Import the ElevenLabs SDK
from elevenlabs import ElevenLabs, VoiceSettings

# Set up logging
logger = logging.getLogger(__name__)


class ElevenLabsConfig(BaseModel):
    """Validate and store ElevenLabs configuration."""
    
    api_key: str = Field(..., min_length=32)
    
    @validator("api_key")
    def validate_api_key(cls, v):
        """Ensure API key meets minimum security requirements."""
        if not v:
            raise ValueError("ElevenLabs API key is missing")
        if len(v) < 32:
            raise ValueError("ElevenLabs API key is invalid (too short)")
        return v


class ElevenLabsClient:
    """
    Client for interacting with the ElevenLabs API.
    
    This class provides methods for text-to-speech conversion using
    the ElevenLabs API through their official SDK.
    """
    
    def __init__(self):
        """
        Initialize the ElevenLabs client.
        
        Loads the API key from environment variables and initializes
        the ElevenLabs SDK client.
        
        Raises:
            ValueError: If the API key is missing or invalid
        """
        # Force reload environment variables from .env file
        # Construct path to the root .env file (3 levels up from this file)
        current_dir = os.path.dirname(__file__)
        app_dir = os.path.dirname(current_dir)
        root_dir = os.path.dirname(app_dir)
        env_path = os.path.join(root_dir, '.env')
        logger.info(f"Loading environment variables from: {env_path}")
        load_dotenv(dotenv_path=env_path, override=True)
        
        # Get API key from environment
        api_key = os.getenv("ELEVENLABS_API_KEY", "")
        
        # Debug output (masked for security)
        if api_key:
            # Mask the API key for secure logging
            # Show first 4 and last 4 chars only
            if len(api_key) > 8:
                prefix = api_key[:4]
                suffix = api_key[-4:]
                mask_length = len(api_key) - 8
                masked_key = prefix + '*' * mask_length + suffix
            else:
                masked_key = '****'
            logger.info(f"Loaded API key: {masked_key}")
        else:
            logger.warning("No API key found in environment variables")
        
        # Check for placeholder values before validation
        if "your-" in api_key.lower() or "api-key" in api_key.lower():
            logger.error("ElevenLabs API key is a placeholder value")
            raise ValueError("placeholder")
        
        # Validate configuration
        try:
            self.config = ElevenLabsConfig(api_key=api_key)
            # Initialize the ElevenLabs client with the API key
            self.client = ElevenLabs(api_key=api_key)
        except ValueError as e:
            logger.error(f"ElevenLabs configuration error: {e}")
            raise
        
    async def text_to_speech(self, text_input: str, voice_id: str) -> bytes:
        """
        Convert text to speech using the ElevenLabs API.
        
        Args:
            text_input: The text to convert to speech
            voice_id: The ElevenLabs voice ID to use
            
        Returns:
            bytes: The generated audio content
            
        Raises:
            Exception: If there's an error during the API call
        """
        try:
            # Since the SDK is synchronous, run it in a thread pool
            return await asyncio.to_thread(
                self._generate_speech, 
                text_input, 
                voice_id
            )
        except Exception as e:
            logger.error(f"Error in text_to_speech: {e}")
            raise
    
    def _generate_speech(self, text_input: str, voice_id: str) -> bytes:
        """
        Internal method to generate speech using the ElevenLabs SDK.
        
        This method is called by the asynchronous text_to_speech method
        and runs in a separate thread.
        
        Args:
            text_input: The text to convert to speech
            voice_id: The ElevenLabs voice ID to use
            
        Returns:
            bytes: The generated audio content
        """
        # Generate speech using the ElevenLabs SDK client
        audio_generator = self.client.text_to_speech.convert(
            text=text_input,
            voice_id=voice_id,
            model_id="eleven_monolingual_v1",
            voice_settings=VoiceSettings(
                stability=0.5,
                similarity_boost=0.5
            )
        )
        
        # Convert generator to bytes
        audio = b''.join(chunk for chunk in audio_generator)
        
        return audio


# Example usage
async def example_usage():
    """
    Example of how to use the ElevenLabsClient.
    
    This function demonstrates how to instantiate the client,
    call the text_to_speech method, and handle the returned audio bytes.
    """
    try:
        # Instantiate the client
        client = ElevenLabsClient()
        
        # Sample text and voice ID (Rachel voice)
        sample_text = "This is a test of the ElevenLabs text-to-speech API."
        voice_id = "21m00Tcm4TlvDq8ikWAM"  # Rachel voice ID
        
        print(f"Converting text to speech using voice ID: {voice_id}")
        
        # Call the text_to_speech method
        audio_bytes = await client.text_to_speech(sample_text, voice_id)
        
        # Save the audio to a file
        output_file = "elevenlabs_output.mp3"
        with open(output_file, "wb") as f:
            f.write(audio_bytes)
        
        print(f"Audio saved to {output_file}")
        print(f"Audio size: {len(audio_bytes) / 1024:.2f} KB")
        
    except Exception as e:
        print(f"Error in example usage: {e}")


if __name__ == "__main__":
    # Run the example
    asyncio.run(example_usage())