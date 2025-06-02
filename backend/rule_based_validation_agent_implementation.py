"""
Rule-Based Validation Agent Implementation Guide

This file provides the Python implementation structure for the RuleBasedValidationAgent.
Copy this code to your actual implementation file and fill in any additional logic as needed.
"""

# Import statements
from typing import Dict, Any, List, Tuple
from langchain_core.agents import BaseSingleActionAgent, AgentAction, AgentFinish


class RuleBasedValidationAgent(BaseSingleActionAgent):
    """
    A rule-based agent for validating different types of input data.
    Implements task-specific validation logic with extensible design.
    """
    
    def __init__(self):
        """Initialize the validation agent with default configuration."""
        super().__init__()
        # Initialize validation rules registry
        self._validation_rules = {}
        # Initialize metrics collector
        self._validation_metrics = {
            'total_validations': 0,
            'successful_validations': 0,
            'failed_validations': 0
        }
    
    @property
    def input_keys(self) -> List[str]:
        """Define expected input keys for the agent."""
        return ['input_data']
    
    @property
    def output_keys(self) -> List[str]:
        """Define output keys produced by the agent."""
        return ['output']
    
    def plan(
        self,
        intermediate_steps: List[Tuple[AgentAction, str]],
        callbacks: Any = None,
        **kwargs: Any
    ) -> AgentFinish:
        """
        Plan and execute validation based on input data.
        
        Args:
            intermediate_steps: Previous agent actions (unused in this implementation)
            callbacks: Optional callbacks for monitoring
            **kwargs: Must contain 'input_data' with task and data to validate
            
        Returns:
            AgentFinish with validation results
        """
        # Extract input data
        if 'input_data' not in kwargs:
            return AgentFinish(
                return_values={
                    'output': {
                        'status': 'error',
                        'message': 'Missing required input_data',
                        'valid': False
                    }
                },
                log='Error: Missing input_data parameter'
            )
        
        input_data = kwargs['input_data']
        
        # Validate input structure
        if not isinstance(input_data, dict):
            return AgentFinish(
                return_values={
                    'output': {
                        'status': 'error',
                        'message': 'input_data must be a dictionary',
                        'valid': False
                    }
                },
                log='Error: Invalid input_data type'
            )
        
        # Extract task type
        if 'task' not in input_data:
            return AgentFinish(
                return_values={
                    'output': {
                        'status': 'error',
                        'message': 'Missing task type in input_data',
                        'valid': False
                    }
                },
                log='Error: Missing task type'
            )
        
        task_type = input_data['task']
        
        # Route to appropriate validation method
        try:
            if task_type == 'validate_workout_plan':
                validation_result = self._validate_workout(input_data)
            elif task_type == 'validate_progress_tracking':
                validation_result = self._validate_progress(input_data)
            else:
                validation_result = {
                    'status': 'error',
                    'message': f'Unknown task type: {task_type}',
                    'valid': False
                }
            
            # Update metrics
            self._update_metrics(validation_result)
            
            # Return validation result
            return AgentFinish(
                return_values={'output': validation_result},
                log=f'Validation completed for task: {task_type}'
            )
            
        except Exception as e:
            return AgentFinish(
                return_values={
                    'output': {
                        'status': 'error',
                        'message': f'Validation error: {str(e)}',
                        'valid': False
                    }
                },
                log=f'Error during validation: {str(e)}'
            )
    
    def _validate_workout(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate workout plan data.
        
        Args:
            input_data: Dictionary containing workout data
            
        Returns:
            Validation result dictionary
        """
        validation_errors = []
        warnings = []
        
        # Check for required fields
        if 'data' not in input_data:
            return {
                'status': 'error',
                'message': 'Missing data field in input',
                'valid': False,
                'errors': ['No workout data provided']
            }
        
        workout_data = input_data['data']
        
        # Validate duration_minutes
        if 'duration_minutes' not in workout_data:
            validation_errors.append('Missing required field: duration_minutes')
        else:
            duration = workout_data['duration_minutes']
            if not isinstance(duration, (int, float)):
                validation_errors.append('duration_minutes must be a number')
            elif duration < 25:
                validation_errors.append('Workout duration must be at least 25 minutes')
            elif duration > 35:
                validation_errors.append('Workout duration must not exceed 35 minutes')
            elif duration < 30:
                warnings.append('Consider increasing workout duration to 30 minutes for optimal results')
        
        # Construct result
        if validation_errors:
            return {
                'status': 'failed',
                'message': 'Workout validation failed',
                'valid': False,
                'errors': validation_errors,
                'warnings': warnings
            }
        else:
            return {
                'status': 'success',
                'message': 'Workout plan is valid',
                'valid': True,
                'warnings': warnings,
                'validated_data': workout_data
            }
    
    def _validate_progress(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate progress tracking data.
        
        Args:
            input_data: Dictionary containing progress data
            
        Returns:
            Validation result dictionary
        """
        # Placeholder implementation
        return {
            'status': 'success',
            'message': 'Progress tracking validation successful',
            'valid': True,
            'validated_data': input_data.get('data', {})
        }
    
    def _update_metrics(self, validation_result: Dict[str, Any]) -> None:
        """Update internal metrics based on validation result."""
        self._validation_metrics['total_validations'] += 1
        if validation_result.get('valid', False):
            self._validation_metrics['successful_validations'] += 1
        else:
            self._validation_metrics['failed_validations'] += 1
    
    def get_metrics(self) -> Dict[str, int]:
        """Return current validation metrics."""
        return self._validation_metrics.copy()


# Example usage
if __name__ == "__main__":
    # Create agent instance
    agent = RuleBasedValidationAgent()
    
    # Example 1: Valid workout plan
    result1 = agent.plan(
        intermediate_steps=[],
        input_data={
            'task': 'validate_workout_plan',
            'data': {
                'duration_minutes': 30,
                'exercises': ['push-ups', 'squats'],
                'rest_periods': [60, 90]
            }
        }
    )
    print("Valid workout result:", result1.return_values['output'])
    
    # Example 2: Invalid workout plan
    result2 = agent.plan(
        intermediate_steps=[],
        input_data={
            'task': 'validate_workout_plan',
            'data': {
                'duration_minutes': 20
            }
        }
    )
    print("Invalid workout result:", result2.return_values['output'])
    
    # Example 3: Progress tracking
    result3 = agent.plan(
        intermediate_steps=[],
        input_data={
            'task': 'validate_progress_tracking',
            'data': {
                'progress': 50,
                'date': '2025-05-30'
            }
        }
    )
    print("Progress tracking result:", result3.return_values['output'])
    
    # Print metrics
    print("Validation metrics:", agent.get_metrics())