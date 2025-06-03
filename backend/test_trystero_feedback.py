"""
Test Trystero's feedback references validation agent rules.

This test suite verifies that Trystero's workout progress feedback
properly incorporates the workout goal rules from the validation agent.
"""

import unittest
from unittest.mock import patch, MagicMock
import asyncio

# Import the validation agent
from rule_based_validation_agent import RuleBasedValidationAgent
from tracking_agent_trystero import (
    check_progress_with_validation_agent
)


class TestTrysteroFeedback(unittest.TestCase):
    """Test Trystero's feedback references validation agent rules correctly."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.validation_agent = RuleBasedValidationAgent()
        
        # Save original rules
        self.original_rules = self.validation_agent.instance_rules.get(
            'workout_goals', {}).copy()
    
    def tearDown(self):
        """Tear down test fixtures."""
        # Restore original rules
        if hasattr(self, 'original_rules'):
            self.validation_agent.instance_rules['workout_goals'] = (
                self.original_rules)
    
    @patch('backend.tracking_agent_trystero.validation_agent_executor')
    def test_feedback_references_weekly_target(self, mock_executor):
        """Test that Trystero's feedback references the weekly target value."""
        # Configure mock response
        mock_result = MagicMock()
        mock_result.return_values = {
            'output': {
                'status': 'success',
                'workout_goals': {
                    'weekly_target': 4,
                    'calculation_method': 'any_type',
                    'workout_types': ['strength', 'yoga', 'runs']
                }
            }
        }
        mock_executor.run.return_value = mock_result
        
        # Create test progress data
        progress_data = {
            'strength_done': 2,
            'yoga_done': 1,
            'runs_done': 0,
            'notes': 'Testing Trystero feedback'
        }
        
        # Run the tool function (synchronously for testing)
        result = asyncio.run(
            check_progress_with_validation_agent(progress_data)
        )
        
        # Verify the tool function called the validation agent
        mock_executor.run.assert_called_once()
        
        # Verify the result contains references to the weekly target
        self.assertIn('weekly_target', str(result))
        self.assertIn('4', str(result))  # The target value should be included
    
    @patch('backend.tracking_agent_trystero.validation_agent_executor')
    def test_feedback_with_modified_weekly_target(self, mock_executor):
        """Test feedback reflects changes to weekly target value."""
        # Configure mock response with modified weekly target
        mock_result = MagicMock()
        mock_result.return_values = {
            'output': {
                'status': 'success',
                'workout_goals': {
                    'weekly_target': 5,  # Changed from 4 to 5
                    'calculation_method': 'any_type',
                    'workout_types': ['strength', 'yoga', 'runs']
                }
            }
        }
        mock_executor.run.return_value = mock_result
        
        # Create test progress data
        progress_data = {
            'strength_done': 2,
            'yoga_done': 1,
            'runs_done': 0,
            'notes': 'Testing Trystero feedback'
        }
        
        # Run the tool function
        result = asyncio.run(
            check_progress_with_validation_agent(progress_data)
        )
        
        # Verify the result references the modified weekly target
        self.assertIn('weekly_target', str(result))
        self.assertIn('5', str(result))  # The modified target value
    
    @patch('backend.tracking_agent_trystero.validation_agent_executor')
    def test_feedback_includes_calculation_method(self, mock_executor):
        """Test that Trystero's feedback includes the calculation method."""
        # Configure mock response
        mock_result = MagicMock()
        mock_result.return_values = {
            'output': {
                'status': 'success',
                'workout_goals': {
                    'weekly_target': 4,
                    'calculation_method': 'any_type',
                    'workout_types': ['strength', 'yoga', 'runs']
                }
            }
        }
        mock_executor.run.return_value = mock_result
        
        # Create test progress data with mixed workout types
        progress_data = {
            'strength_done': 1,
            'yoga_done': 1,
            'runs_done': 1,
            'notes': 'Testing calculation method'
        }
        
        # Run the tool function
        result = asyncio.run(
            check_progress_with_validation_agent(progress_data)
        )
        
        # Verify the result includes reference to the calculation method
        self.assertIn('calculation_method', str(result))
        self.assertIn('any_type', str(result))


if __name__ == '__main__':
    unittest.main()