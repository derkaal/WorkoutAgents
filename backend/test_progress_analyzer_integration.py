"""
Test the integration between Progress Analyzer frontend and validation agent.

This test suite verifies that:
1. The frontend correctly receives workout goal rules
2. The progress calculation follows the validation agent rules
3. Changes to validation agent rules properly affect calculations
"""

import unittest
from unittest.mock import patch
import sys
import os

# Adjust path to allow imports from project
sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')))
# noqa: E402 imports below are intentionally after path adjustment
from app.routers.progress import analyze_progress  # noqa: E402
# Import the validation agent
from rule_based_validation_agent import (  # noqa: E402
    RuleBasedValidationAgent
)
from app.models.schemas import ProgressAnalysisRequest  # noqa: E402


class TestProgressAnalyzerIntegration(unittest.TestCase):
    """
    Tests for the integration between frontend Progress Analyzer and
    validation agent.
    """
    
    def setUp(self):
        """Set up test fixtures, if any."""
        # Create a validation agent instance
        self.validation_agent = RuleBasedValidationAgent()
        
        # Save original rules for restoration
        self.original_rules = self.validation_agent.instance_rules.get(
            'workout_goals', {}).copy()
    
    def tearDown(self):
        """Tear down test fixtures, if any."""
        # Restore original rules
        if hasattr(self, 'original_rules'):
            self.validation_agent.instance_rules['workout_goals'] = (
                self.original_rules)
    
    @patch('backend.app.routers.progress.validation_agent')
    async def test_analyze_progress_uses_validation_agent_rules(
            self, mock_validation_agent):
        """
        Test that analyze_progress uses workout goal rules from the
        validation agent.
        """
        # Configure the mock validation agent
        mock_validation_agent.instance_rules = {
            'workout_goals': {
                'weekly_target': 4,
                'calculation_method': 'any_type',
                'workout_types': ['strength', 'yoga', 'runs']
            }
        }
        
        # Create a test request with 2 workouts completed
        request_data = ProgressAnalysisRequest(
            progress_data={
                'strength_done': 1,
                'yoga_done': 1,
                'runs_done': 0,
                'notes': 'Test progress'
            }
        )
        
        # Call the analyze_progress function
        response = await analyze_progress(request_data)
        
        # Verify that response contains the expected calculations
        self.assertIsNotNone(response)
        self.assertIn('trystero_feedback_text', response.__dict__)
        
        # Progress should be 2/4 = 50%
        self.assertIn('50%', response.trystero_feedback_text)
        
        # Verify that the weekly target is mentioned
        self.assertIn('4 workouts', response.trystero_feedback_text.lower())
    
    @patch('backend.app.routers.progress.validation_agent')
    async def test_analyze_progress_with_modified_rules(
            self, mock_validation_agent):
        """
        Test that changes to validation agent rules affect the progress
        calculation.
        """
        # Configure the mock validation agent with a higher weekly target
        mock_validation_agent.instance_rules = {
            'workout_goals': {
                'weekly_target': 5,  # Changed from default 4
                'calculation_method': 'any_type',
                'workout_types': ['strength', 'yoga', 'runs']
            }
        }
        
        # Create a test request with 2 workouts completed
        request_data = ProgressAnalysisRequest(
            progress_data={
                'strength_done': 1,
                'yoga_done': 1,
                'runs_done': 0,
                'notes': 'Test progress'
            }
        )
        
        # Call the analyze_progress function
        response = await analyze_progress(request_data)
        
        # Verify that response contains the expected calculations
        self.assertIsNotNone(response)
        
        # Progress should now be 2/5 = 40%
        self.assertIn('40%', response.trystero_feedback_text)
        
        # Verify that the new weekly target is mentioned
        self.assertIn('5 workouts', response.trystero_feedback_text.lower())
    
    @patch('backend.app.routers.progress.validation_agent')
    async def test_analyze_progress_100_percent_cap(
            self, mock_validation_agent):
        """
        Test that progress percentage is capped at 100% even when exceeding
        weekly target.
        """
        # Configure the mock validation agent
        mock_validation_agent.instance_rules = {
            'workout_goals': {
                'weekly_target': 3,
                'calculation_method': 'any_type',
                'workout_types': ['strength', 'yoga', 'runs']
            }
        }
        
        # Create a test request with 4 workouts (exceeding target)
        request_data = ProgressAnalysisRequest(
            progress_data={
                'strength_done': 2,
                'yoga_done': 1,
                'runs_done': 1,
                'notes': 'Exceeded weekly goal'
            }
        )
        
        # Call the analyze_progress function
        response = await analyze_progress(request_data)
        
        # Verify that response contains the expected calculations
        self.assertIsNotNone(response)
        
        # Progress should be capped at 100%
        self.assertIn('100%', response.trystero_feedback_text)


if __name__ == '__main__':
    unittest.main()