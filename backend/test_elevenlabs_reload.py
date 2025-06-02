"""
Test script to verify that the ElevenLabsClient correctly reloads the .env file.

This script tests the ElevenLabsClient's ability to load the API key from the .env file
and properly handle environment variable reloading.
"""

import os
import logging
import asyncio
from app.services.eleven_labs_client import ElevenLabsClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_elevenlabs_client():
    """Test the ElevenLabsClient's environment variable loading."""
    try:
        logger.info("Initializing ElevenLabsClient...")
        client = ElevenLabsClient()
        
        # If we get here, the client was initialized successfully
        logger.info("ElevenLabsClient initialized successfully!")
        
        # Test a simple text-to-speech conversion
        sample_text = "This is a test of the ElevenLabs API key loading."
        voice_id = "21m00Tcm4TlvDq8ikWAM"  # Rachel voice ID
        
        logger.info(f"Converting text to speech using voice ID: {voice_id}")
        audio_bytes = await client.text_to_speech(sample_text, voice_id)
        
        # Save the audio to a file
        output_file = "test_reload_output.mp3"
        with open(output_file, "wb") as f:
            f.write(audio_bytes)
        
        logger.info(f"Audio saved to {output_file}")
        logger.info(f"Audio size: {len(audio_bytes) / 1024:.2f} KB")
        
        return True
        
    except ValueError as e:
        if "placeholder" in str(e):
            logger.error("API key is still a placeholder value!")
            logger.error("Please update your .env file with a real API key.")
        else:
            logger.error(f"Validation error: {e}")
        return False
    except Exception as e:
        logger.error(f"Error testing ElevenLabsClient: {e}")
        return False


if __name__ == "__main__":
    logger.info("Starting ElevenLabsClient reload test...")
    
    # Print current working directory for debugging
    logger.info(f"Current working directory: {os.getcwd()}")
    
    # Run the test
    result = asyncio.run(test_elevenlabs_client())
    
    if result:
        logger.info("Test completed successfully!")
    else:
        logger.error("Test failed!")