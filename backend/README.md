# RuleBasedValidationAgent

## Overview

The RuleBasedValidationAgent is a custom Langchain agent that provides modular, extensible validation logic for different types of input data. It implements a rule-based approach to validate workout plans, progress tracking, and can be extended to support additional validation types.

This agent follows security best practices including input validation, sanitization, secure error handling, and logging with sensitive data masking. It's designed to be easily integrated into Langchain workflows or used as a standalone validation component.

### Key Features

- **Modular Design**: Separate validation methods for each task type
- **Security-First Approach**: Input sanitization, audit logging, and sensitive data masking
- **Metrics Tracking**: Built-in validation metrics collection
- **Comprehensive Error Handling**: Detailed error messages without leaking sensitive information
- **Extensible Architecture**: Easy to add new validation types
- **Test Coverage**: Full test suite included

## Installation

### Prerequisites

- Python 3.8+
- Langchain library (optional, minimal implementation provided if not available)

### Install from PyPI

```bash
pip install rule-based-validation-agent
```

### Manual Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/workout-agents.git
cd workout-agents
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Basic Usage

### Validating a Workout Plan

```python
from rule_based_validation_agent import RuleBasedValidationAgent

# Create agent instance
agent = RuleBasedValidationAgent()

# Prepare input data
input_data = {
    'task': 'validate_workout_plan',
    'data': {
        'duration_minutes': 30,
        'exercises': [
            {'name': 'Push-ups', 'sets': 3, 'reps': 10}
        ]
    }
}

# Execute validation
result = agent.plan(intermediate_steps=[], input_data=input_data)

# Process result
if result.return_values['output']['valid']:
    print("Validation successful!")
    validated_data = result.return_values['output']['validated_data']
else:
    print("Validation failed:")
    for error in result.return_values['output']['errors']:
        print(f"- {error}")
```

### Validating Progress Tracking

```python
from rule_based_validation_agent import RuleBasedValidationAgent

# Create agent instance
agent = RuleBasedValidationAgent()

# Prepare input data
input_data = {
    'task': 'validate_progress_tracking',
    'data': {
        'user_id': 'user123',
        'workout_id': 'workout456',
        'completion_percentage': 85,
        'metrics': {
            'calories_burned': 250,
            'heart_rate_avg': 140
        }
    }
}

# Execute validation
result = agent.plan(intermediate_steps=[], input_data=input_data)

# Process result
if result.return_values['output']['valid']:
    print("Progress tracking data is valid!")
else:
    print("Progress tracking validation failed.")
```

## API Reference

### RuleBasedValidationAgent Class

The main agent class that handles validation requests.

```python
class RuleBasedValidationAgent(BaseSingleActionAgent):
    def __init__(self):
        # Initialize the agent
        
    def plan(self, intermediate_steps, callbacks=None, **kwargs):
        # Execute validation based on input data
        
    def get_metrics(self):
        # Return validation metrics
```

### Constructor Parameters

The constructor takes no parameters but initializes several internal components:

```python
agent = RuleBasedValidationAgent()
```

Internally, it initializes:
- Validation rules registry
- Metrics collector
- Input sanitizer
- Security audit logger

### Properties

#### input_keys

```python
@property
def input_keys(self) -> List[str]:
    """Define expected input keys for the agent."""
    return ['input_data']
```

The agent expects a single input key: `input_data`.

#### output_keys

```python
@property
def output_keys(self) -> List[str]:
    """Define output keys produced by the agent."""
    return ['output']
```

The agent produces a single output key: `output`.

### Methods

#### plan

```python
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
```

The main method that processes validation requests. It expects `input_data` in `kwargs` and returns an `AgentFinish` object with validation results.

#### Validation Methods

##### _validate_workout

```python
def _validate_workout(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate workout plan data.
    
    Args:
        input_data: Dictionary containing workout data
        
    Returns:
        Validation result dictionary
    """
```

Validates workout plan data, checking for required fields and applying validation rules.

##### _validate_progress

```python
def _validate_progress(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate progress tracking data.
    
    Args:
        input_data: Dictionary containing progress data
        
    Returns:
        Validation result dictionary
    """
```

Validates progress tracking data.

#### Metrics Tracking

##### _update_metrics

```python
def _update_metrics(self, validation_result: Dict[str, Any]) -> None:
    """Update internal metrics based on validation result."""
```

Updates internal metrics based on validation results.

##### get_metrics

```python
def get_metrics(self) -> Dict[str, int]:
    """Return current validation metrics."""
    return self._validation_metrics.copy()
```

Returns a copy of the current validation metrics.

### Security Features

#### InputSanitizer Class

```python
class InputSanitizer:
    """Utility class for sanitizing input data to prevent injection attacks."""
    
    @staticmethod
    def sanitize_string(value: str) -> str:
        """Sanitize string input to prevent injection attacks."""
        
    @staticmethod
    def sanitize_dict(data: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively sanitize dictionary data."""
        
    @staticmethod
    def sanitize_list(data: List[Any]) -> List[Any]:
        """Sanitize list data."""
        
    @staticmethod
    def sanitize_number(value: Any) -> Any:
        """Sanitize numeric values."""
```

Provides methods to sanitize different types of input data to prevent injection attacks.

#### SecurityAuditLogger Class

```python
class SecurityAuditLogger:
    """Security audit logger with sensitive data masking."""
    
    def __init__(self):
        """Initialize the security audit logger."""
        
    def log_event(self, event_type: str, details: Dict[str, Any], user_context: Dict[str, Any] = None):
        """Log security event with context."""
        
    def _mask_sensitive_data(self, data: Any) -> Any:
        """Recursively mask sensitive data."""
```

Provides security audit logging with sensitive data masking.

## Configuration Options

The RuleBasedValidationAgent can be configured through several mechanisms:

### Validation Rules

The agent uses predefined validation rules for different task types:

#### Workout Plan Validation Rules

- `duration_minutes` must be present
- `duration_minutes` must be a number
- `duration_minutes` must be between 25 and 35 minutes
- Warning if `duration_minutes` is less than 30 minutes

#### Progress Tracking Validation Rules

Currently implements a basic validation that always succeeds. This can be extended with custom rules.

### Security Configuration

The agent includes several security features that can be configured:

#### Input Sanitization

- HTML tag removal
- Control character filtering
- Length limiting to prevent DoS attacks
- Numeric bounds checking

#### Audit Logging

- Sensitive data patterns for masking:
  - 'password', 'token', 'secret', 'key', 'auth'
  - 'ssn', 'credit', 'card', 'cvv', 'pin'

## Advanced Usage Patterns

### Integration with Langchain Workflows

```python
from langchain.chains import LLMChain, SequentialChain

# Create validation chain
validation_chain = LLMChain(
    llm=None,  # No LLM needed for rule-based validation
    agent=RuleBasedValidationAgent(),
    verbose=True
)

# Use in larger workflow
workflow = SequentialChain(
    chains=[
        data_preparation_chain,
        validation_chain,
        processing_chain
    ]
)

# Execute workflow
result = workflow.run(input_data)
```

### Integration with FastAPI

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List

from rule_based_validation_agent import RuleBasedValidationAgent

app = FastAPI()
validation_agent = RuleBasedValidationAgent()

class ValidationRequest(BaseModel):
    task: str
    data: Dict[str, Any]

class ValidationResponse(BaseModel):
    valid: bool
    status: str
    message: str
    errors: List[str] = []
    warnings: List[str] = []
    validated_data: Dict[str, Any] = {}

@app.post("/validate", response_model=ValidationResponse)
async def validate_data(request: ValidationRequest):
    # Prepare input for agent
    input_data = {
        'task': request.task,
        'data': request.data
    }
    
    # Execute validation
    result = validation_agent.plan(intermediate_steps=[], input_data=input_data)
    
    # Return validation result
    return result.return_values['output']
```

### Handling Validation Errors

```python
from rule_based_validation_agent import RuleBasedValidationAgent

agent = RuleBasedValidationAgent()

try:
    # Prepare input data
    input_data = {
        'task': 'validate_workout_plan',
        'data': {
            'duration_minutes': 20  # Invalid duration
        }
    }
    
    # Execute validation
    result = agent.plan(intermediate_steps=[], input_data=input_data)
    
    # Check validation result
    if not result.return_values['output']['valid']:
        print("Validation failed:")
        for error in result.return_values['output']['errors']:
            print(f"- {error}")
        
        # Handle warnings
        if 'warnings' in result.return_values['output']:
            print("Warnings:")
            for warning in result.return_values['output']['warnings']:
                print(f"- {warning}")
                
        # Take corrective action
        # ...
    
except Exception as e:
    print(f"An error occurred: {str(e)}")
```

### Configuring Security Features

```python
from rule_based_validation_agent import RuleBasedValidationAgent, SecurityAuditLogger

# Create custom audit logger
custom_logger = SecurityAuditLogger()

# Add additional sensitive patterns
custom_logger.sensitive_patterns.extend([
    'health', 'medical', 'diagnosis'
])

# Create agent
agent = RuleBasedValidationAgent()

# Replace default audit logger with custom one
agent._audit_logger = custom_logger

# Use agent with enhanced security
result = agent.plan(intermediate_steps=[], input_data=input_data)
```

## Extending with New Validation Types

You can extend the RuleBasedValidationAgent with new validation types by following these steps:

### 1. Add a New Validation Method

```python
def _validate_nutrition_plan(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate nutrition plan data.
    
    Args:
        input_data: Dictionary containing nutrition data
        
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
            'errors': ['No nutrition data provided']
        }
    
    nutrition_data = input_data['data']
    
    # Validate calorie_target
    if 'calorie_target' not in nutrition_data:
        validation_errors.append('Missing required field: calorie_target')
    else:
        try:
            calorie_target = float(str(nutrition_data['calorie_target']))
            
            if calorie_target < 1200:
                validation_errors.append('Calorie target must be at least 1200')
            elif calorie_target > 4000:
                validation_errors.append('Calorie target must not exceed 4000')
        except (TypeError, ValueError):
            validation_errors.append('calorie_target must be a valid number')
    
    # Construct result
    if validation_errors:
        return {
            'status': 'failed',
            'message': 'Nutrition plan validation failed',
            'valid': False,
            'errors': validation_errors,
            'warnings': warnings
        }
    else:
        return {
            'status': 'success',
            'message': 'Nutrition plan is valid',
            'valid': True,
            'warnings': warnings,
            'validated_data': nutrition_data
        }
```

### 2. Update the Plan Method

Modify the `plan` method to include the new validation type:

```python
# Add to the allowed tasks set
allowed_tasks = {'validate_workout_plan', 'validate_progress_tracking', 'validate_nutrition_plan'}

# Add to the routing logic
if task_type == 'validate_workout_plan':
    validation_result = self._validate_workout(input_data)
elif task_type == 'validate_progress_tracking':
    validation_result = self._validate_progress(input_data)
elif task_type == 'validate_nutrition_plan':
    validation_result = self._validate_nutrition_plan(input_data)
else:
    # This should never happen due to the whitelist check above
    validation_result = {
        'status': 'error',
        'message': f'Unknown task type: {task_type}',
        'valid': False
    }
```

### 3. Create Tests for the New Validation Type

```python
def test_validate_nutrition_plan_valid(self, agent):
    """Test _validate_nutrition_plan with valid input"""
    # Arrange
    input_data = {
        'data': {
            'calorie_target': 2000,
            'macros': {
                'protein': 150,
                'carbs': 200,
                'fat': 70
            }
        }
    }
    
    # Act
    result = agent._validate_nutrition_plan(input_data)
    
    # Assert
    assert result['valid'] is True
    assert result['status'] == 'success'

def test_validate_nutrition_plan_invalid(self, agent):
    """Test _validate_nutrition_plan with invalid input"""
    # Arrange
    input_data = {
        'data': {
            'calorie_target': 800  # Too low
        }
    }
    
    # Act
    result = agent._validate_nutrition_plan(input_data)
    
    # Assert
    assert result['valid'] is False
    assert any('at least 1200' in error for error in result['errors'])
```

## Troubleshooting

### Common Issues and Solutions

#### Issue: Missing Required Input Data

**Symptom**: Error message "Missing required input_data"

**Solution**: Ensure you're passing the `input_data` parameter to the `plan` method:

```python
# Incorrect
result = agent.plan(intermediate_steps=[])

# Correct
result = agent.plan(intermediate_steps=[], input_data=your_data)
```

#### Issue: Unknown Task Type

**Symptom**: Error message "Unknown task type: [your_task]"

**Solution**: Use one of the supported task types:

```python
# Supported task types
input_data = {
    'task': 'validate_workout_plan',  # or 'validate_progress_tracking'
    'data': { ... }
}
```

#### Issue: Invalid Input Structure

**Symptom**: Error message "input_data must be a dictionary"

**Solution**: Ensure your input data is properly structured:

```python
# Correct structure
input_data = {
    'task': 'validate_workout_plan',
    'data': {
        'duration_minutes': 30
    }
}
```

#### Issue: Missing Data Field

**Symptom**: Error message "Missing data field in input"

**Solution**: Include the 'data' field in your input:

```python
# Incorrect
input_data = {
    'task': 'validate_workout_plan'
}

# Correct
input_data = {
    'task': 'validate_workout_plan',
    'data': { ... }
}
```

### Debugging Tips

1. **Check Validation Metrics**: Use `agent.get_metrics()` to see validation statistics
2. **Examine Log Files**: Check `validation_agent.log` and `security_audit.log` for details
3. **Validate Input Structure**: Ensure your input follows the expected format
4. **Test with Minimal Input**: Start with minimal valid input and add complexity

## Performance Considerations

### Optimization Strategies

1. **Input Size Limits**: The agent limits input size to prevent DoS attacks:
   - String length: 10,000 characters
   - Dictionary/list items: 100 items

2. **Numeric Bounds**: The agent applies reasonable bounds to numeric inputs:
   - Rejects NaN and infinity values
   - Limits absolute values to 1e9

3. **Lazy Validation**: The agent only validates required fields and stops on first failure

### Performance Metrics

The agent tracks performance metrics that can be accessed via `get_metrics()`:

```python
metrics = agent.get_metrics()
# Returns:
# {
#     'total_validations': 10,
#     'successful_validations': 7,
#     'failed_validations': 3,
#     'security_violations': 0
# }
```

### Scaling Considerations

For high-volume validation scenarios:

1. **Batch Processing**: Group similar validations together
2. **Caching**: Consider implementing a cache for repeated validations
3. **Async Implementation**: For I/O-bound validations, consider async methods
4. **Resource Limits**: Implement timeouts for long-running validations

## Security Best Practices

When using the RuleBasedValidationAgent, follow these security best practices:

1. **Input Validation**: Always validate input before processing
   ```python
   # Validate input structure
   if not isinstance(input_data, dict) or 'task' not in input_data or 'data' not in input_data:
       return {'valid': False, 'message': 'Invalid input structure'}
   ```

2. **Sanitize User Input**: Use the provided sanitization methods
   ```python
   from rule_based_validation_agent import InputSanitizer
   
   # Sanitize user input
   sanitized_input = InputSanitizer.sanitize_dict(user_input)
   ```

3. **Secure Error Handling**: Don't expose sensitive information in error messages
   ```python
   try:
       # Process data
   except Exception as e:
       # Log detailed error internally
       logger.error(f"Error: {str(e)}", exc_info=True)
       # Return sanitized error to user
       return {'status': 'error', 'message': 'An error occurred during processing'}
   ```

4. **Audit Logging**: Enable and monitor security audit logs
   ```python
   # Log security events
   audit_logger.log_event('validation_attempt', {
       'task': task_type,
       'timestamp': datetime.utcnow().isoformat()
   }, user_context)
   ```

5. **Sensitive Data Masking**: Mask sensitive data in logs
   ```python
   # Mask sensitive data
   masked_data = security_logger._mask_sensitive_data(sensitive_data)
   ```

6. **Resource Limits**: Implement timeouts and resource limits
   ```python
   # Set timeout for validation
   import signal
   
   def timeout_handler(signum, frame):
       raise TimeoutError("Validation timed out")
   
   signal.signal(signal.SIGALRM, timeout_handler)
   signal.alarm(5)  # 5 second timeout
   
   try:
       result = agent.plan(intermediate_steps=[], input_data=input_data)
       signal.alarm(0)  # Cancel alarm
   except TimeoutError:
       # Handle timeout
       signal.alarm(0)  # Cancel alarm
   ```

7. **Principle of Least Privilege**: Only expose necessary functionality
   ```python
   # Create restricted agent with limited validation types
   class RestrictedValidationAgent(RuleBasedValidationAgent):
       def plan(self, intermediate_steps, callbacks=None, **kwargs):
           input_data = kwargs.get('input_data', {})
           if input_data.get('task') not in ['validate_workout_plan']:
               return AgentFinish(
                   return_values={'output': {
                       'status': 'error',
                       'message': 'Unauthorized validation type',
                       'valid': False
                   }},
                   log='Error: Unauthorized validation type'
               )
           return super().plan(intermediate_steps, callbacks, **kwargs)