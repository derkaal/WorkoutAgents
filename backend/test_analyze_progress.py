"""
Test script for the /analyze-progress/ endpoint.

This script sends a request to the FastAPI endpoint and verifies
that the response contains the expected fields including audio_base64.
"""

import requests
import json
import sys

# Define the API endpoint
API_URL = "http://127.0.0.1:8000/api/v1/analyze-progress/"

# Define the request payload based on the schema example
payload = {
    "progress_data": {
        "completed_workouts": [
            {
                "date": "2025-05-25",
                "workout_type": "strength",
                "exercises": [
                    {
                        "name": "Bench Press",
                        "sets": 3,
                        "reps": 10,
                        "weight": 135
                    },
                    {
                        "name": "Squats",
                        "sets": 3,
                        "reps": 8,
                        "weight": 185
                    }
                ],
                "duration_minutes": 45,
                "perceived_exertion": 7
            },
            {
                "date": "2025-05-28",
                "workout_type": "cardio",
                "exercises": [
                    {
                        "name": "Running",
                        "distance_km": 5,
                        "duration_minutes": 30
                    }
                ],
                "duration_minutes": 30,
                "perceived_exertion": 6
            }
        ],
        "goals": {
            "primary": "Build muscle",
            "secondary": "Improve endurance"
        },
        "subjective_feedback": "I'm feeling more tired than usual after my workouts"
    }
}

def test_analyze_progress_endpoint():
    """Test the analyze-progress endpoint."""
    print(f"Sending request to {API_URL}...")
    
    try:
        # Send the POST request
        response = requests.post(API_URL, json=payload)
        
        # Check if the request was successful
        if response.status_code == 200:
            print("Request successful!")
            
            # Parse the response
            response_data = response.json()
            
            # Check if the response contains the expected fields
            expected_fields = ["trystero_feedback_text", "briefing_for_next_plan", "audio_base64"]
            missing_fields = [field for field in expected_fields if field not in response_data]
            
            if not missing_fields:
                print("All expected fields are present in the response!")
                
                # Print the feedback text
                print("\nTrystero's Feedback:")
                print(response_data["trystero_feedback_text"])
                
                # Print the briefing for next plan
                print("\nBriefing for Next Plan:")
                print(json.dumps(response_data["briefing_for_next_plan"], indent=2) 
                      if response_data["briefing_for_next_plan"] else "None")
                
                # Check if audio_base64 is present and not None
                if response_data["audio_base64"]:
                    print("\naudio_base64 field is present and contains data!")
                    # Print the first 50 characters of the base64 string
                    print(f"First 50 characters of audio_base64: {response_data['audio_base64'][:50]}...")
                else:
                    print("\naudio_base64 field is present but is None or empty.")
            else:
                print(f"Missing expected fields in response: {', '.join(missing_fields)}")
                print("Response data:", json.dumps(response_data, indent=2))
        else:
            print(f"Request failed with status code: {response.status_code}")
            print("Response:", response.text)
    
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    success = test_analyze_progress_endpoint()
    sys.exit(0 if success else 1)