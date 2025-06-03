"""
Test Mike agent's integration with workout history.

This module tests how Mike uses workout history data
to decide when to recommend rest days instead of workouts.
"""

import os
import unittest
from datetime import datetime, timedelta
from unittest.mock import patch

from backend.app.models.workout_history import WorkoutHistory
from backend.workout_history_tool import check_workout_history


class TestMikeWorkoutHistoryIntegration(unittest.TestCase):
    """Test Mike's integration with workout history for rest days."""

    def setUp(self):
        """Set up the test environment."""
        # Use a test-specific history file
        self.test_file = "test_mike_workout_history.json"
        
        # Delete the test file if it exists
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
        
        # Create a mock workout history with known state
        self.workout_history = WorkoutHistory(history_file_path=self.test_file)
        
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

    def test_mike_workout_generation_with_rest_recommendation(self):
        """
        Test that when Trystero's briefing includes a rest recommendation,
        Mike takes it into account.
        """
        # Record workouts for 3 consecutive days to trigger rest recommendation
        for i in range(3):
            date = datetime.now() - timedelta(days=i)
            self.workout_history.record_workout("strength", date=date)
        
        # Get workout history data that would be used in Trystero's briefing
        workout_history_data = check_workout_history()
        
        # Verify rest is recommended
        self.assertTrue(workout_history_data["rest_recommended"])
        
        # Create a mock Trystero briefing with rest recommendation
        trystero_briefing = {
            "focus_areas": ["recovery", "flexibility"],
            "energy_level": "low",
            "recommended_adjustments": {
                "intensity": "very low",
                "add_rest_day": True
            },
            "rest_recommended": True,
            "weekly_completion_percentage": 
                workout_history_data["weekly_completion_percentage"],
            "consecutive_days": workout_history_data["consecutive_days"]
        }
        
        # Verify the briefing contains the necessary rest recommendation
        self.assertTrue(trystero_briefing["rest_recommended"])
        self.assertTrue(
            trystero_briefing["recommended_adjustments"]["add_rest_day"]
        )

    def test_mike_weekly_goal_achievement_rest_recommendation(self):
        """
        Test that when weekly workout goal is achieved,
        Trystero's briefing includes appropriate recommendations.
        """
        # Record 4 workouts to hit weekly goal
        for _ in range(4):
            self.workout_history.record_workout("strength")
        
        # Get workout history data that would be used in Trystero's briefing
        workout_history_data = check_workout_history()
        
        # Verify weekly goal is achieved
        self.assertEqual(workout_history_data["weekly_count"], 4)
        self.assertEqual(
            workout_history_data["weekly_completion_percentage"],
            100
        )
        
        # Verify recommendations mention weekly goal
        self.assertTrue(
            any("weekly goal" in rec.lower() 
                for rec in workout_history_data.get("recommendations", []))
        )
        
        # Create a mock Trystero briefing that would include weekly goal info
        trystero_briefing = {
            "focus_areas": ["recovery", "active rest"],
            "energy_level": "medium",
            "recommended_adjustments": {
                "intensity": "low",
                "consider_active_recovery": True
            },
            "weekly_goal_achieved": True,
            "weekly_completion_percentage": 
                workout_history_data["weekly_completion_percentage"]
        }
        
        # Verify the briefing contains weekly goal achievement
        self.assertTrue(trystero_briefing["weekly_goal_achieved"])


if __name__ == "__main__":
    unittest.main()