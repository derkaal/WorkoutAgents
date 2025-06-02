"""
Rule-Based Validation Agent Implementation

This module implements a secure RuleBasedValidationAgent that validates different types of input data
using a rule-based approach. It follows security best practices including input validation,
sanitization, secure error handling, and logging with sensitive data masking.
"""

import logging
import re
import json
from typing import Dict, Any, List, Tuple, ClassVar
from pydantic import Field, ValidationError
from datetime import datetime
from models.schemas import WorkoutPlan, ProgressAnalysisRequest
# Fix import issue - BaseSingleActionAgent might be in a different module
# Try alternative import paths
try:
    from langchain.agents import BaseSingleActionAgent, AgentAction, AgentFinish
except ImportError:
    try:
        from langchain.agents.agent import BaseSingleActionAgent
        from langchain_core.agents import AgentAction, AgentFinish
    except ImportError:
        # Create a minimal implementation if we can't import it
        class BaseSingleActionAgent:
            """Minimal implementation of BaseSingleActionAgent."""
            @property
            def input_keys(self) -> List[str]:
                raise NotImplementedError()
                
            @property
            def output_keys(self) -> List[str]:
                raise NotImplementedError()
                
            def aplan(self, *args, **kwargs):
                """Abstract method that needs to be implemented."""
                raise NotImplementedError()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("validation_agent.log"),
        logging.StreamHandler()
    ]
)

# Create logger
logger = logging.getLogger("RuleBasedValidationAgent")


class InputSanitizer:
    """Utility class for sanitizing input data to prevent injection attacks."""
    
    @staticmethod
    def sanitize_string(value: str) -> str:
        """
        Sanitize string input to prevent injection attacks.
        
        Args:
            value: The string to sanitize
            
        Returns:
            Sanitized string
        """
        if not isinstance(value, str):
            return value
        
        # Remove potentially dangerous characters
        # Remove HTML tags
        sanitized = re.sub(r'<[^>]*>', '', value)
        
        # Remove null bytes and control characters
        sanitized = ''.join(char for char in sanitized if ord(char) >= 32 or char in '\n\r\t')
        
        # Limit length to prevent DoS
        max_length = 10000
        if len(sanitized) > max_length:
            sanitized = sanitized[:max_length]
            
        return sanitized
    
    @staticmethod
    def sanitize_dict(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Recursively sanitize dictionary data.
        
        Args:
            data: Dictionary to sanitize
            
        Returns:
            Sanitized dictionary
        """
        if not isinstance(data, dict):
            return data
        
        sanitized = {}
        max_items = 100  # Limit number of items to prevent DoS
        
        for key, value in list(data.items())[:max_items]:
            # Sanitize key
            safe_key = InputSanitizer.sanitize_string(str(key))
            
            # Sanitize value based on type
            if isinstance(value, str):
                sanitized[safe_key] = InputSanitizer.sanitize_string(value)
            elif isinstance(value, dict):
                sanitized[safe_key] = InputSanitizer.sanitize_dict(value)
            elif isinstance(value, list):
                sanitized[safe_key] = InputSanitizer.sanitize_list(value)
            elif isinstance(value, (int, float)):
                sanitized[safe_key] = InputSanitizer.sanitize_number(value)
            else:
                sanitized[safe_key] = value
        
        return sanitized
    
    @staticmethod
    def sanitize_list(data: List[Any]) -> List[Any]:
        """
        Sanitize list data.
        
        Args:
            data: List to sanitize
            
        Returns:
            Sanitized list
        """
        if not isinstance(data, list):
            return data
        
        max_items = 100  # Limit number of items to prevent DoS
        
        return [
            InputSanitizer.sanitize_dict(item) if isinstance(item, dict)
            else InputSanitizer.sanitize_string(item) if isinstance(item, str)
            else InputSanitizer.sanitize_number(item) if isinstance(item, (int, float))
            else item
            for item in data[:max_items]
        ]
    
    @staticmethod
    def sanitize_number(value: Any) -> Any:
        """
        Sanitize numeric values.
        
        Args:
            value: Number to sanitize
            
        Returns:
            Sanitized number
        """
        if isinstance(value, (int, float)):
            # Check for NaN, infinity
            if value != value or abs(value) == float('inf'):
                return 0
            # Apply reasonable bounds
            if abs(value) > 1e9:
                return 0
        return value


class SecurityAuditLogger:
    """Security audit logger with sensitive data masking."""
    
    def __init__(self):
        """Initialize the security audit logger."""
        self.logger = logging.getLogger("security_audit")
        self.logger.setLevel(logging.INFO)
        
        # Add file handler if not already added
        if not self.logger.handlers:
            handler = logging.FileHandler("security_audit.log")
            handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
            self.logger.addHandler(handler)
        
        # Sensitive patterns to mask
        self.sensitive_patterns = [
            'password', 'token', 'secret', 'key', 'auth',
            'ssn', 'credit', 'card', 'cvv', 'pin'
        ]
    
    def log_event(self, event_type: str, details: Dict[str, Any], user_context: Dict[str, Any] = None):
        """
        Log security event with context.
        
        Args:
            event_type: Type of security event
            details: Event details
            user_context: User context information
        """
        audit_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'event_type': event_type,
            'details': self._mask_sensitive_data(details),
            'user_context': self._mask_sensitive_data(user_context) if user_context else {},
        }
        
        self.logger.info(json.dumps(audit_entry))
    
    def _mask_sensitive_data(self, data: Any) -> Any:
        """
        Recursively mask sensitive data.
        
        Args:
            data: Data to mask
            
        Returns:
            Masked data
        """
        if isinstance(data, dict):
            masked = {}
            for key, value in data.items():
                if any(pattern in str(key).lower() for pattern in self.sensitive_patterns):
                    masked[key] = '***REDACTED***'
                else:
                    masked[key] = self._mask_sensitive_data(value)
            return masked
        elif isinstance(data, list):
            return [self._mask_sensitive_data(item) for item in data]
        elif isinstance(data, str):
            # Check if the string itself contains sensitive patterns
            if any(pattern in data.lower() for pattern in self.sensitive_patterns):
                return '***REDACTED***'
        return data


class RuleBasedValidationAgent(BaseSingleActionAgent):
    """
    A rule-based agent for validating different types of input data.
    Implements task-specific validation logic with extensible design and security features.
    """
    
    # Define class variables for Pydantic with proper type annotations
    validation_rules: ClassVar[Dict[str, Any]] = {}
    validation_metrics: ClassVar[Dict[str, int]] = {
        'total_validations': 0,
        'successful_validations': 0,
        'failed_validations': 0,
        'security_violations': 0
    }
    
    # Define instance variables as fields with default values
    instance_rules: Dict[str, Any] = Field(default_factory=dict)
    instance_metrics: Dict[str, int] = Field(default_factory=dict)
    input_sanitizer: Any = None
    audit_logger: Any = None
    logger: Any = None
    
    def __init__(self, **data):
        """Initialize the validation agent with default configuration and security components."""
        super().__init__(**data)
        
        # Create instance-specific copies of the class variables
        # to avoid modifying class variables
        self.instance_rules = self.validation_rules.copy()
        self.instance_metrics = self.validation_metrics.copy()
        
        # Initialize security components
        self.input_sanitizer = InputSanitizer()
        self.audit_logger = SecurityAuditLogger()
        self.logger = logging.getLogger(__name__)
    
    @property
    def input_keys(self) -> List[str]:
        """
        Define expected input keys for the agent.
        
        Returns:
            List of input keys
        """
        return ['input_data']
    
    @property
    def output_keys(self) -> List[str]:
        """
        Define output keys produced by the agent.
        
        Returns:
            List of output keys
        """
        return ['output']
    
    def aplan(self, *args, **kwargs):
        """
        Implementation of the abstract method required by BaseSingleActionAgent.
        Delegates to the plan method.
        """
        return self.plan(*args, **kwargs)
        
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
            self.audit_logger.log_event('validation_error', {
                'error': 'Missing required input_data',
                'timestamp': datetime.utcnow().isoformat()
            })
            
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
        
        # Get input data and sanitize it
        try:
            input_data = kwargs['input_data']
            
            # Validate input structure
            if not isinstance(input_data, dict):
                self.audit_logger.log_event('validation_error', {
                    'error': 'Invalid input_data type',
                    'received_type': str(type(input_data)),
                    'timestamp': datetime.utcnow().isoformat()
                })
                
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
            
            # Sanitize input data to prevent injection attacks
            input_data = self.input_sanitizer.sanitize_dict(input_data)
            
            # Extract task type
            if 'task' not in input_data:
                self.audit_logger.log_event('validation_error', {
                    'error': 'Missing task type',
                    'timestamp': datetime.utcnow().isoformat()
                })
                
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
            
            # Validate task type against whitelist
            allowed_tasks = {'validate_workout_plan', 'validate_progress_tracking'}
            if task_type not in allowed_tasks:
                self.audit_logger.log_event('validation_error', {
                    'error': 'Invalid task type',
                    'task_type': task_type,
                    'timestamp': datetime.utcnow().isoformat()
                })
                
                return AgentFinish(
                    return_values={
                        'output': {
                            'status': 'error',
                            'message': f'Unknown task type: {task_type}',
                            'valid': False
                        }
                    },
                    log=f'Error: Unknown task type: {task_type}'
                )
            
            # Route to appropriate validation method
            try:
                if task_type == 'validate_workout_plan':
                    validation_result = self._validate_workout(input_data)
                elif task_type == 'validate_progress_tracking':
                    validation_result = self._validate_progress(input_data)
                else:
                    # This should never happen due to the whitelist check above
                    validation_result = {
                        'status': 'error',
                        'message': f'Unknown task type: {task_type}',
                        'valid': False
                    }
                
                # Update metrics
                self.instance_metrics['total_validations'] += 1
                if validation_result.get('valid', False):
                    self.instance_metrics['successful_validations'] += 1
                else:
                    self.instance_metrics['failed_validations'] += 1
                
                # Log successful validation
                self.audit_logger.log_event('validation_success', {
                    'task': task_type,
                    'valid': validation_result.get('valid', False),
                    'timestamp': datetime.utcnow().isoformat()
                })
                
                # Return validation result
                return AgentFinish(
                    return_values={'output': validation_result},
                    log=f'Validation completed for task: {task_type}'
                )
                
            except Exception as e:
                # Log exception details internally
                self.logger.error(f"Validation error: {str(e)}", exc_info=True)
                
                # Log security event
                self.audit_logger.log_event('validation_error', {
                    'error_type': type(e).__name__,
                    'task': task_type,
                    'timestamp': datetime.utcnow().isoformat()
                })
                
                # Return sanitized error message to user
                return AgentFinish(
                    return_values={
                        'output': {
                            'status': 'error',
                            'message': 'An error occurred during validation',
                            'valid': False
                        }
                    },
                    log=f'Error during validation: {type(e).__name__}'
                )
        
        except Exception as e:
            # Log exception details internally
            self.logger.error(f"Unexpected error: {str(e)}", exc_info=True)
            
            # Log security event
            self.audit_logger.log_event('system_error', {
                'error_type': type(e).__name__,
                'timestamp': datetime.utcnow().isoformat()
            })
            
            # Return sanitized error message to user
            return AgentFinish(
                return_values={
                    'output': {
                        'status': 'error',
                        'message': 'An unexpected error occurred',
                        'valid': False
                    }
                },
                log=f'Unexpected error: {type(e).__name__}'
            )
    
    def _validate_workout(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate workout plan data against the WorkoutPlan schema.
        
        Args:
            input_data: Dictionary containing workout data, expected to be under 'plan_to_validate' key.
            
        Returns:
            Validation result dictionary
        """
        validation_errors = []
        warnings = []

        # Ensure 'plan_to_validate' key exists
        if 'plan_to_validate' not in input_data:
            return {
                'status': 'error',
                'message': 'Missing "plan_to_validate" key in input data',
                'valid': False,
                'errors': ['No workout plan data provided under "plan_to_validate"']
            }

        workout_plan_data = input_data['plan_to_validate']

        try:
            # Validate the entire workout plan against the Pydantic model
            workout_plan = WorkoutPlan(**workout_plan_data)

            # Rule 1: Validate total duration
            if not (25 <= workout_plan.duration_minutes <= 35):
                validation_errors.append(
                    f"Workout duration must be between 25 and 35 minutes, got {workout_plan.duration_minutes}."
                )

            # Rule 2: Validate each day and its exercises
            if not workout_plan.days:
                validation_errors.append("Workout plan must contain at least one day.")
            
            total_exercise_duration = 0
            for day_idx, day in enumerate(workout_plan.days):
                if not day.name:
                    validation_errors.append(f"Day {day_idx + 1} is missing a name.")
                
                if not day.exercises:
                    validation_errors.append(f"Day {day_idx + 1} must contain at least one exercise or rest period.")
                
                for exercise_idx, exercise in enumerate(day.exercises):
                    # Rule 2.1: Check for instruction_text
                    if not exercise.instruction_text:
                        validation_errors.append(
                            f"Exercise/Rest '{exercise.name}' on Day {day_idx + 1}, item {exercise_idx + 1} is missing 'instruction_text'."
                        )
                    
                    # Rule 2.2: Basic check for exercise name
                    if not exercise.name:
                        validation_errors.append(
                            f"Exercise/Rest on Day {day_idx + 1}, item {exercise_idx + 1} is missing a name."
                        )

                    # Accumulate duration for exercises with duration_seconds
                    if exercise.duration_seconds is not None:
                        total_exercise_duration += exercise.duration_seconds
                    elif exercise.sets is not None and exercise.reps is not None:
                        # Estimate duration for set/rep based exercises (e.g., 1 min per set)
                        # This is a rough estimate and can be refined
                        total_exercise_duration += exercise.sets * 60
            
            # Rule 3: Check if total estimated exercise duration is reasonable
            # Convert total_exercise_duration from seconds to minutes
            estimated_total_minutes = total_exercise_duration / 60
            if not (20 <= estimated_total_minutes <= 35): # Adjusted range for estimated duration
                warnings.append(
                    f"Estimated total exercise/rest duration ({estimated_total_minutes:.1f} minutes) "
                    f"is outside the typical 20-35 minute range for a 30-minute workout. "
                    f"Actual plan duration: {workout_plan.duration_minutes} minutes."
                )

        except ValidationError as e:
            # Pydantic validation errors
            for error in e.errors():
                validation_errors.append(f"Pydantic validation error: {error['loc']} - {error['msg']}")
            self.audit_logger.log_event('validation_error', {
                'error_type': 'PydanticValidationError',
                'details': e.errors(),
                'timestamp': datetime.utcnow().isoformat()
            })
        except Exception as e:
            # Catch any other unexpected errors during validation
            validation_errors.append(f"An unexpected error occurred during workout validation: {str(e)}")
            self.audit_logger.log_event('validation_error', {
                'error_type': type(e).__name__,
                'details': str(e),
                'timestamp': datetime.utcnow().isoformat()
            })
        
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
                'validated_data': workout_plan.model_dump()
            }
    
    def _validate_progress(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate progress tracking data against the ProgressAnalysisRequest schema.
        
        Args:
            input_data: Dictionary containing progress data, expected to be under 'progress_data_to_check' key.
            
        Returns:
            Validation result dictionary
        """
        validation_errors = []
        warnings = []

        # Ensure 'progress_data_to_check' key exists
        if 'progress_data_to_check' not in input_data:
            return {
                'status': 'error',
                'message': 'Missing "progress_data_to_check" key in input data',
                'valid': False,
                'errors': ['No progress data provided under "progress_data_to_check"']
            }

        progress_data = input_data['progress_data_to_check']

        try:
            # Validate the progress data against the Pydantic model
            # Note: ProgressAnalysisRequest expects 'progress_data' as its field
            # So we need to wrap the incoming data
            ProgressAnalysisRequest(progress_data=progress_data)
            
            # If validation passes, return success
            return {
                'status': 'success',
                'message': 'Progress tracking validation successful',
                'valid': True,
                'warnings': warnings,
                'validated_data': progress_data # Return the validated data
            }

        except ValidationError as e:
            # Pydantic validation errors
            for error in e.errors():
                validation_errors.append(f"Pydantic validation error: {error['loc']} - {error['msg']}")
            self.audit_logger.log_event('validation_error', {
                'error_type': 'PydanticValidationError',
                'details': e.errors(),
                'timestamp': datetime.utcnow().isoformat()
            })
            return {
                'status': 'failed',
                'message': 'Progress tracking validation failed',
                'valid': False,
                'errors': validation_errors,
                'warnings': warnings
            }
        except Exception as e:
            # Catch any other unexpected errors during validation
            validation_errors.append(f"An unexpected error occurred during progress validation: {str(e)}")
            self.audit_logger.log_event('validation_error', {
                'error_type': type(e).__name__,
                'details': str(e),
                'timestamp': datetime.utcnow().isoformat()
            })
            return {
                'status': 'failed',
                'message': 'An unexpected error occurred during progress validation',
                'valid': False,
                'errors': validation_errors,
                'warnings': warnings
            }
    
    def _update_metrics(self, validation_result: Dict[str, Any]) -> None:
        """
        Update internal metrics based on validation result.
        
        Args:
            validation_result: The validation result to update metrics with
        """
        self.instance_metrics['total_validations'] += 1
        if validation_result.get('valid', False):
            self.instance_metrics['successful_validations'] += 1
        else:
            self.instance_metrics['failed_validations'] += 1
    
    def get_metrics(self) -> Dict[str, int]:
        """
        Return current validation metrics.
        
        Returns:
            Dictionary of validation metrics
        """
        return self.instance_metrics.copy()


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