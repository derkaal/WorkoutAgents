"""
Test script to understand how to use the ElevenLabs SDK correctly.
"""

import os
from dotenv import load_dotenv
from elevenlabs import ElevenLabs, VoiceSettings

# Load environment variables
load_dotenv()

# Get API key from environment
api_key = os.getenv("ELEVENLABS_API_KEY", "")

print("Testing ElevenLabs SDK usage...")

try:
    # Initialize the ElevenLabs client with the API key
    client = ElevenLabs(api_key=api_key)
    
    # Sample text and voice ID (Rachel voice)
    sample_text = "This is a test of the ElevenLabs text-to-speech API."
    voice_id = "21m00Tcm4TlvDq8ikWAM"  # Rachel voice ID
    
    print(f"Converting text to speech using voice ID: {voice_id}")
    
    # Generate speech using the ElevenLabs SDK client
    audio_generator = client.text_to_speech.convert(
        text=sample_text,
        voice_id=voice_id,
        model_id="eleven_monolingual_v1",
        voice_settings=VoiceSettings(
            stability=0.5,
            similarity_boost=0.5
        )
    )
    
    # Convert generator to bytes
    audio_bytes = b''.join(chunk for chunk in audio_generator)
    
    # Save the audio to a file
    with open("test_output.mp3", "wb") as f:
        f.write(audio_bytes)
    
    print("Audio successfully generated and saved to test_output.mp3")
    print(f"Audio size: {len(audio_bytes) / 1024:.2f} KB")
    
except Exception as e:
    print(f"Error: {e}")