"""
Test suite for Workout History API endpoints.

This module tests the API endpoints for workout history functionality:
- Recording workout completion
- Getting workout history summary
- Verifying rest recommendations
"""

import os
import unittest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
import json

# Adjust the import based on your project structure
from backend.app.main import app


class TestWorkoutHistoryAPI(unittest.TestCase):
    """Test the Workout History API endpoints."""

    def setUp(self):
        """Set up the test environment."""
        self.client = TestClient(app)
        
        # Reset workout history file for testing
        history_file_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "app",
            "data",
            "workout_history.json"
        )
        
        # Create the directory if it doesn't exist
        os.makedirs(os.path.dirname(history_file_path), exist_ok=True)
        
        # Reset the history file with empty data
        with open(history_file_path, 'w') as f:
            json.dump({"workouts": []}, f)

    def test_record_workout_completion(self):
        """Test recording a workout completion."""
        # Make a request to record a workout
        response = self.client.post(
            "/api/v1/workout-history/record",
            json={"workout_type": "strength"}
        )
        
        # Verify the response
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "success")
        self.assertEqual(data["message"], "Workout recorded successfully")
        
        # Now get the summary to verify the workout was recorded
        summary_response = self.client.get("/api/v1/workout-history/summary")
        summary = summary_response.json()
        
        # Verify workout count
        self.assertEqual(summary["weekly_count"], 1)
        self.assertEqual(summary["consecutive_days"], 1)

    def test_weekly_goal_recommendation(self):
        """
        Test that rest is recommended when the weekly goal is achieved.
        Weekly goal is 4 workouts per week.
        """
        # Record 4 workouts
        for _ in range(4):
            self.client.post(
                "/api/v1/workout-history/record",
                json={"workout_type": "strength"}
            )
        
        # Get the summary
        response = self.client.get("/api/v1/workout-history/summary")
        self.assertEqual(response.status_code, 200)
        
        summary = response.json()
        
        # Verify the weekly goal completion
        self.assertEqual(summary["weekly_count"], 4)
        self.assertEqual(summary["weekly_completion_percentage"], 100)
        
        # Verify that recommendations include mention of weekly goal
        self.assertTrue(
            any("weekly goal" in rec.lower() 
                for rec in summary.get("recommendations", []))
        )

    def test_consecutive_days_recommendation(self):
        """
        Test that rest is recommended when workouts are done on
        consecutive days. Maximum consecutive days is 3.
        """
        # Record workouts for 3 consecutive days with specific dates
        for i in range(3):
            date = (datetime.now() - timedelta(days=i)).isoformat()
            self.client.post(
                "/api/v1/workout-history/record",
                json={"workout_type": "strength", "date": date}
            )
        
        # Get the summary
        response = self.client.get("/api/v1/workout-history/summary")
        self.assertEqual(response.status_code, 200)
        
        summary = response.json()
        
        # Verify consecutive days count
        self.assertEqual(summary["consecutive_days"], 3)
        
        # Verify that rest is recommended
        self.assertTrue(summary["rest_recommended"])
        self.assertTrue(
            any("rest" in rec.lower() 
                for rec in summary.get("recommendations", []))
        )


if __name__ == "__main__":
    unittest.main()