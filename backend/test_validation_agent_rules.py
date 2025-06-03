"""
Test the validation agent rules implementation for workout goal tracking.

This test suite verifies that:
1. The validation agent correctly provides workout goal rules
2. The rules include the expected weekly_target and calculation_method
"""

import unittest
from rule_based_validation_agent import RuleBasedValidationAgent

# Add an extra blank line before class definition


class TestValidationAgentRules(unittest.TestCase):
    """Tests for the workout goal rules in the validation agent."""
    
    def setUp(self):
        """Set up a validation agent instance for testing."""
        self.validation_agent = RuleBasedValidationAgent()
    
    def test_workout_goal_rules_exist(self):
        """Test that workout goal rules exist in the validation agent."""
        # Verify that workout_goals exists in instance_rules
        self.assertIn('workout_goals', self.validation_agent.instance_rules)
        workout_goals = self.validation_agent.instance_rules.get(
            'workout_goals', {})
        self.assertIsInstance(workout_goals, dict)
    
    def test_weekly_target_is_correct(self):
        """Test that the weekly_target is set to 4."""
        workout_goals = self.validation_agent.instance_rules.get(
            'workout_goals', {})
        self.assertIn('weekly_target', workout_goals)
        self.assertEqual(workout_goals['weekly_target'], 4)
    
    def test_calculation_method_is_correct(self):
        """Test that the calculation_method is set to 'any_type'."""
        workout_goals = self.validation_agent.instance_rules.get(
            'workout_goals', {})
        self.assertIn('calculation_method', workout_goals)
        self.assertEqual(workout_goals['calculation_method'], 'any_type')
    
    def test_workout_types_are_correct(self):
        """Test that workout_types includes the expected types."""
        workout_goals = self.validation_agent.instance_rules.get(
            'workout_goals', {})
        self.assertIn('workout_types', workout_goals)
        self.assertIsInstance(workout_goals['workout_types'], list)
        self.assertIn('strength', workout_goals['workout_types'])
        self.assertIn('yoga', workout_goals['workout_types'])
        self.assertIn('runs', workout_goals['workout_types'])


if __name__ == '__main__':
    unittest.main()