"""
Test the integration between agents and workout history.

This module tests how Mike and Trystero agents interact with
the workout history system, particularly for rest recommendations.
"""

import os
import unittest
from datetime import datetime, timedelta
from unittest.mock import patch

# Import the necessary modules for testing
from backend.app.models.workout_history import WorkoutHistory
from backend.workout_history_tool import check_workout_history
from backend.rule_based_validation_agent import RuleBasedValidationAgent


class TestAgentWorkoutHistoryIntegration(unittest.TestCase):
    """Test the integration between agents and workout history."""

    def setUp(self):
        """Set up the test environment."""
        # Use a test-specific history file
        self.test_file = "test_agent_workout_history.json"
        
        # Delete the test file if it exists
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
        
        # Create a mock workout history with known state
        self.workout_history = WorkoutHistory(history_file_path=self.test_file)
        
        # Initialize validation agent for testing
        self.validation_agent = RuleBasedValidationAgent()
        
        # Patch the global workout_history in workout_history_tool.py
        self.patcher = patch(
            'backend.workout_history_tool.workout_history',
            self.workout_history
        )
        self.mock_workout_history = self.patcher.start()
    
    def tearDown(self):
        """Clean up after the tests."""
        # Delete the test file if it exists
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
        
        # Stop the patch
        self.patcher.stop()

    def test_trystero_check_workout_history_tool(self):
        """Test the check_workout_history tool that Trystero uses."""
        # Record 4 workouts to hit weekly goal
        for _ in range(4):
            self.workout_history.record_workout("strength")
        
        # Get the response from the tool
        result = check_workout_history()
        
        # Verify the tool correctly identifies weekly goal completion
        self.assertEqual(result["weekly_count"], 4)
        self.assertEqual(result["weekly_completion_percentage"], 100)
        self.assertTrue(
            any("weekly goal" in rec.lower() 
                for rec in result.get("recommendations", []))
        )
    
    def test_consecutive_days_rest_recommendation_from_tool(self):
        """
        Test that check_workout_history tool recommends rest
        after consecutive days.
        """
        # Record workouts for 3 consecutive days
        for i in range(3):
            date = datetime.now() - timedelta(days=i)
            self.workout_history.record_workout("strength", date=date)
        
        # Get the response from the tool
        result = check_workout_history()
        
        # Verify the tool correctly identifies consecutive days
        self.assertEqual(result["consecutive_days"], 3)
        self.assertTrue(result["rest_recommended"])
        self.assertTrue(
            any("rest" in rec.lower() 
                for rec in result.get("recommendations", []))
        )
    
    def test_workout_history_data_in_summary(self):
        """Test that workout history data is included in the summary."""
        # Record workouts of different types
        self.workout_history.record_workout("strength")
        self.workout_history.record_workout("yoga")
        self.workout_history.record_workout("runs")
        
        # Get the workout history summary
        result = check_workout_history()
        
        # Verify the distribution data is included
        self.assertIn("distribution", result)
        distribution = result["distribution"]
        
        # Each workout type should be approximately 33.3%
        self.assertAlmostEqual(distribution["strength"], 33.3, delta=0.1)
        self.assertAlmostEqual(distribution["yoga"], 33.3, delta=0.1)
        self.assertAlmostEqual(distribution["runs"], 33.3, delta=0.1)


if __name__ == "__main__":
    unittest.main()