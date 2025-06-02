"""
ElevenLabs Client Example

This script demonstrates how to use the ElevenLabsClient class
to convert text to speech using the ElevenLabs API.
"""

import asyncio
import os
import sys

# Add the parent directory to the path to import the services module
sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
)

# Import after path modification
from app.services.eleven_labs_client import ElevenLabsClient  # noqa


async def main():
    """
    Example of how to use the ElevenLabsClient.
    
    This function demonstrates how to instantiate the client,
    call the text_to_speech method, and handle the returned audio bytes.
    """
    try:
        print("Initializing ElevenLabs client...")
        # Instantiate the client
        client = ElevenLabsClient()
        
        # Sample text and voice ID (Rachel voice)
        sample_text = (
            "This is a test of the ElevenLabs text-to-speech API "
            "using the updated SDK."
        )
        voice_id = "21m00Tcm4TlvDq8ikWAM"  # Rachel voice ID
        
        print(f"Converting text to speech using voice ID: {voice_id}")
        
        # Call the text_to_speech method
        audio_bytes = await client.text_to_speech(sample_text, voice_id)
        
        # Save the audio to a file
        output_file = "elevenlabs_output.mp3"
        with open(output_file, "wb") as f:
            f.write(audio_bytes)
        
        print(f"Audio successfully generated and saved to {output_file}")
        print(f"Audio size: {len(audio_bytes) / 1024:.2f} KB")
        
    except ValueError as e:
        if "placeholder" in str(e):
            print("\nERROR: You need to set up a real ElevenLabs API key")
            print("1. Sign up at https://elevenlabs.io to get an API key")
            print("2. Update the .env file with your real API key")
            print("   Current .env file has:")
            print("   ELEVENLABS_API_KEY=\"your-elevenlabs-api-key-here\"")
            print("   Change it to:")
            print("   ELEVENLABS_API_KEY=\"your-actual-api-key-here\"")
        else:
            print(f"Error in example usage: {e}")
    except Exception as e:
        print(f"Error in example usage: {e}")


if __name__ == "__main__":
    # Run the example
    asyncio.run(main())