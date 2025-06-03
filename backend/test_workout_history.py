import os
import json
import unittest
from datetime import datetime, timedelta
from backend.app.models.workout_history import WorkoutHistory


class TestWorkoutHistory(unittest.TestCase):
    """Test suite for the WorkoutHistory class."""
    
    def setUp(self):
        """Set up the test environment."""
        # Use a test-specific history file
        self.test_file = "test_workout_history.json"
        
        # Delete the test file if it exists
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
            
        # Create a fresh WorkoutHistory instance
        self.history = WorkoutHistory(history_file_path=self.test_file)
    
    def tearDown(self):
        """Clean up after the tests."""
        # Delete the test file if it exists
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
    
    def test_record_workout(self):
        """Test that a workout is correctly recorded and stored in the file."""
        # Record a workout
        workout_type = "strength"
        result = self.history.record_workout(workout_type)
        
        # Check the result
        self.assertEqual(result["status"], "success")
        self.assertEqual(len(self.history.workouts), 1)
        self.assertEqual(self.history.workouts[0]["type"], workout_type)
        
        # Verify the file was created and contains the workout
        self.assertTrue(os.path.exists(self.test_file))
        
        # Read the file content
        with open(self.test_file, 'r') as f:
            data = json.load(f)
            
        # Check the file content
        self.assertEqual(len(data["workouts"]), 1)
        self.assertEqual(data["workouts"][0]["type"], workout_type)
    
    def test_weekly_goal_rest_recommendation(self):
        """
        Test that rest is recommended when the weekly goal is achieved.
        Weekly goal is 4 workouts per week.
        """
        # Record 4 workouts
        for _ in range(4):
            self.history.record_workout("strength")
        
        # Check the workout count
        weekly_count = self.history.get_weekly_workout_count()
        self.assertEqual(weekly_count, 4)
        
        # Get the summary
        summary = self.history.get_workout_history_summary()
        
        # Verify the weekly goal completion percentage
        self.assertEqual(summary["weekly_completion_percentage"], 100)
        
        # Verify recommendations mention weekly goal achievement
        self.assertTrue(
            any("weekly goal" in rec.lower()
                for rec in summary.get("recommendations", []))
        )
    
    def test_consecutive_days_rest_recommendation(self):
        """
        Test that rest is recommended when workouts are done on
        consecutive days. Maximum consecutive days is 3.
        """
        # Record workouts for 3 consecutive days
        for i in range(3):
            date = datetime.now() - timedelta(days=i)
            self.history.record_workout("strength", date=date)
        
        # Check the consecutive days count
        consecutive_days = self.history.get_consecutive_workout_days()
        self.assertEqual(consecutive_days, 3)
        
        # Check if rest is recommended
        should_rest = self.history.should_recommend_rest()
        self.assertTrue(should_rest)
        
        # Get the workout history summary
        summary = self.history.get_workout_history_summary()
        
        # Verify that rest is recommended in the summary
        self.assertTrue(summary["rest_recommended"])
        self.assertTrue(
            any("rest" in rec.lower()
                for rec in summary.get("recommendations", []))
        )


if __name__ == "__main__":
    unittest.main()