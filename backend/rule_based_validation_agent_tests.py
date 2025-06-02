"""
Test Specification for Rule-Based Validation Agent

This file provides comprehensive test cases for the RuleBasedValidationAgent.
Tests follow TDD principles and cover all major functionality.
"""

import pytest
from typing import Dict, Any
from langchain_core.agents import AgentFinish
from rule_based_validation_agent_implementation import RuleBasedValidationAgent


class TestRuleBasedValidationAgent:
    """Test suite for RuleBasedValidationAgent."""
    
    def test_agent_initialization(self):
        """Test agent initialization and default properties."""
        # Arrange & Act
        agent = RuleBasedValidationAgent()
        
        # Assert
        assert agent.input_keys == ['input_data']
        assert agent.output_keys == ['output']
        assert agent.get_metrics()['total_validations'] == 0
        assert agent.get_metrics()['successful_validations'] == 0
        assert agent.get_metrics()['failed_validations'] == 0
    
    def test_validate_workout_valid(self):
        """Test workout validation with valid data."""
        # Arrange
        agent = RuleBasedValidationAgent()
        input_data = {
            'task': 'validate_workout_plan',
            'data': {'duration_minutes': 30}
        }
        
        # Act
        result = agent.plan(
            intermediate_steps=[],
            input_data=input_data
        )
        
        # Assert
        assert isinstance(result, AgentFinish)
        assert result.return_values['output']['valid'] is True
        assert result.return_values['output']['status'] == 'success'
        assert 'validated_data' in result.return_values['output']
    
    def test_validate_workout_invalid_duration_too_short(self):
        """Test workout validation with duration too short."""
        # Arrange
        agent = RuleBasedValidationAgent()
        input_data = {
            'task': 'validate_workout_plan',
            'data': {'duration_minutes': 20}
        }
        
        # Act
        result = agent.plan(
            intermediate_steps=[],
            input_data=input_data
        )
        
        # Assert
        assert result.return_values['output']['valid'] is False
        assert result.return_values['output']['status'] == 'failed'
        errors = result.return_values['output']['errors']
        assert any('at least 25 minutes' in error for error in errors)
    
    def test_validate_workout_invalid_duration_too_long(self):
        """Test workout validation with duration too long."""
        # Arrange
        agent = RuleBasedValidationAgent()
        input_data = {
            'task': 'validate_workout_plan',
            'data': {'duration_minutes': 40}
        }
        
        # Act
        result = agent.plan(
            intermediate_steps=[],
            input_data=input_data
        )
        
        # Assert
        assert result.return_values['output']['valid'] is False
        assert result.return_values['output']['status'] == 'failed'
        errors = result.return_values['output']['errors']
        assert any('not exceed 35 minutes' in error for error in errors)
    
    def test_validate_workout_with_warning(self):
        """Test workout validation that generates a warning."""
        # Arrange
        agent = RuleBasedValidationAgent()
        input_data = {
            'task': 'validate_workout_plan',
            'data': {'duration_minutes': 25}
        }
        
        # Act
        result = agent.plan(
            intermediate_steps=[],
            input_data=input_data
        )
        
        # Assert
        assert result.return_values['output']['valid'] is True
        assert result.return_values['output']['status'] == 'success'
        warnings = result.return_values['output'].get('warnings', [])
        assert len(warnings) > 0
        assert any('30 minutes' in warning for warning in warnings)
    
    def test_validate_workout_missing_duration(self):
        """Test workout validation with missing duration field."""
        # Arrange
        agent = RuleBasedValidationAgent()
        input_data = {
            'task': 'validate_workout_plan',
            'data': {}
        }
        
        # Act
        result = agent.plan(
            intermediate_steps=[],
            input_data=input_data
        )
        
        # Assert
        assert result.return_values['output']['valid'] is False
        errors = result.return_values['output']['errors']
        assert any('Missing required field' in error for error in errors)
    
    def test_validate_workout_invalid_duration_type(self):
        """Test workout validation with invalid duration type."""
        # Arrange
        agent = RuleBasedValidationAgent()
        input_data = {
            'task': 'validate_workout_plan',
            'data': {'duration_minutes': 'thirty'}
        }
        
        # Act
        result = agent.plan(
            intermediate_steps=[],
            input_data=input_data
        )
        
        # Assert
        assert result.return_values['output']['valid'] is False
        errors = result.return_values['output']['errors']
        assert any('must be a number' in error for error in errors)
    
    def test_missing_input_data(self):
        """Test agent behavior when input_data is missing."""
        # Arrange
        agent = RuleBasedValidationAgent()
        
        # Act
        result = agent.plan(intermediate_steps=[])
        
        # Assert
        assert result.return_values['output']['valid'] is False
        assert result.return_values['output']['status'] == 'error'
        assert 'Missing required input_data' in result.return_values['output']['message']
    
    def test_invalid_input_data_type(self):
        """Test agent behavior with invalid input_data type."""
        # Arrange
        agent = RuleBasedValidationAgent()
        
        # Act
        result = agent.plan(
            intermediate_steps=[],
            input_data="not a dictionary"
        )
        
        # Assert
        assert result.return_values['output']['valid'] is False
        assert result.return_values['output']['status'] == 'error'
        assert 'must be a dictionary' in result.return_values['output']['message']
    
    def test_missing_task_type(self):
        """Test agent behavior when task type is missing."""
        # Arrange
        agent = RuleBasedValidationAgent()
        
        # Act
        result = agent.plan(
            intermediate_steps=[],
            input_data={'data': {}}
        )
        
        # Assert
        assert result.return_values['output']['valid'] is False
        assert result.return_values['output']['status'] == 'error'
        assert 'Missing task type' in result.return_values['output']['message']
    
    def test_unknown_task_type(self):
        """Test agent behavior with unknown task type."""
        # Arrange
        agent = RuleBasedValidationAgent()
        
        # Act
        result = agent.plan(
            intermediate_steps=[],
            input_data={'task': 'unknown_task'}
        )
        
        # Assert
        assert result.return_values['output']['valid'] is False
        assert 'Unknown task type' in result.return_values['output']['message']
    
    def test_validate_progress(self):
        """Test progress validation functionality."""
        # Arrange
        agent = RuleBasedValidationAgent()
        input_data = {
            'task': 'validate_progress_tracking',
            'data': {'progress': 50}
        }
        
        # Act
        result = agent.plan(
            intermediate_steps=[],
            input_data=input_data
        )
        
        # Assert
        assert result.return_values['output']['valid'] is True
        assert result.return_values['output']['status'] == 'success'
        assert 'validated_data' in result.return_values['output']
    
    def test_metrics_tracking(self):
        """Test that metrics are properly tracked."""
        # Arrange
        agent = RuleBasedValidationAgent()
        
        # Act - Perform successful validation
        agent.plan(
            intermediate_steps=[],
            input_data={
                'task': 'validate_workout_plan',
                'data': {'duration_minutes': 30}
            }
        )
        
        # Act - Perform failed validation
        agent.plan(
            intermediate_steps=[],
            input_data={
                'task': 'validate_workout_plan',
                'data': {'duration_minutes': 10}
            }
        )
        
        # Assert
        metrics = agent.get_metrics()
        assert metrics['total_validations'] == 2
        assert metrics['successful_validations'] == 1
        assert metrics['failed_validations'] == 1
    
    def test_exception_handling(self):
        """Test that exceptions are properly handled."""
        # Arrange
        agent = RuleBasedValidationAgent()
        
        # Monkey patch to force an exception
        original_validate = agent._validate_workout
        def raise_exception(*args, **kwargs):
            raise ValueError("Test exception")
        agent._validate_workout = raise_exception
        
        # Act
        result = agent.plan(
            intermediate_steps=[],
            input_data={
                'task': 'validate_workout_plan',
                'data': {'duration_minutes': 30}
            }
        )
        
        # Assert
        assert result.return_values['output']['valid'] is False
        assert result.return_values['output']['status'] == 'error'
        assert 'Test exception' in result.return_values['output']['message']
        
        # Restore original method
        agent._validate_workout = original_validate
    
    def test_missing_data_field_in_workout(self):
        """Test workout validation when data field is missing."""
        # Arrange
        agent = RuleBasedValidationAgent()
        input_data = {
            'task': 'validate_workout_plan'
            # Missing 'data' field
        }
        
        # Act
        result = agent.plan(
            intermediate_steps=[],
            input_data=input_data
        )
        
        # Assert
        assert result.return_values['output']['valid'] is False
        assert result.return_values['output']['status'] == 'error'
        assert 'Missing data field' in result.return_values['output']['message']


# Integration test examples
class TestRuleBasedValidationAgentIntegration:
    """Integration tests for RuleBasedValidationAgent."""
    
    def test_multiple_validations_sequence(self):
        """Test a sequence of different validations."""
        # Arrange
        agent = RuleBasedValidationAgent()
        
        # Act - Multiple validations
        results = []
        
        # Valid workout
        results.append(agent.plan(
            intermediate_steps=[],
            input_data={
                'task': 'validate_workout_plan',
                'data': {'duration_minutes': 30}
            }
        ))
        
        # Invalid workout
        results.append(agent.plan(
            intermediate_steps=[],
            input_data={
                'task': 'validate_workout_plan',
                'data': {'duration_minutes': 50}
            }
        ))
        
        # Progress tracking
        results.append(agent.plan(
            intermediate_steps=[],
            input_data={
                'task': 'validate_progress_tracking',
                'data': {'progress': 75}
            }
        ))
        
        # Assert
        assert results[0].return_values['output']['valid'] is True
        assert results[1].return_values['output']['valid'] is False
        assert results[2].return_values['output']['valid'] is True
        
        # Check final metrics
        metrics = agent.get_metrics()
        assert metrics['total_validations'] == 3
        assert metrics['successful_validations'] == 2
        assert metrics['failed_validations'] == 1


# Parametrized tests
@pytest.mark.parametrize("duration,expected_valid", [
    (24, False),  # Too short
    (25, True),   # Minimum valid
    (30, True),   # Optimal
    (35, True),   # Maximum valid
    (36, False),  # Too long
])
def test_workout_duration_boundaries(duration, expected_valid):
    """Test workout validation at duration boundaries."""
    # Arrange
    agent = RuleBasedValidationAgent()
    input_data = {
        'task': 'validate_workout_plan',
        'data': {'duration_minutes': duration}
    }
    
    # Act
    result = agent.plan(
        intermediate_steps=[],
        input_data=input_data
    )
    
    # Assert
    assert result.return_values['output']['valid'] is expected_valid


# Performance test example
def test_validation_performance():
    """Test that validation completes within reasonable time."""
    import time
    
    # Arrange
    agent = RuleBasedValidationAgent()
    input_data = {
        'task': 'validate_workout_plan',
        'data': {'duration_minutes': 30}
    }
    
    # Act
    start_time = time.time()
    for _ in range(100):  # Run 100 validations
        agent.plan(
            intermediate_steps=[],
            input_data=input_data
        )
    end_time = time.time()
    
    # Assert
    elapsed_time = end_time - start_time
    assert elapsed_time < 1.0  # Should complete 100 validations in under 1 second


if __name__ == "__main__":
    # Run basic tests
    test_suite = TestRuleBasedValidationAgent()
    test_suite.test_agent_initialization()
    test_suite.test_validate_workout_valid()
    test_suite.test_metrics_tracking()
    print("Basic tests passed!")