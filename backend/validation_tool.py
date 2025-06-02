"""
Validation Tool for Workout Plans

This module provides a tool that wraps the RuleBasedValidationAgent's
AgentExecutor for use as a tool in other LangChain agents.
"""

from dotenv import load_dotenv
from langchain_core.tools import tool

# Load environment variables from .env file
load_dotenv()


# Global variable to store the validation agent executor
# This will be set by the application that uses this tool
validation_agent_executor = None

@tool
def validate_workout_plan_with_executor(plan_to_validate: dict) -> dict:
    """
    Validates a workout plan dictionary using the rule-based validation agent.
    
    Input is the plan dictionary containing workout details such as
    duration_minutes, exercises, rest_periods, etc. Returns validation
    results including whether the
    plan is valid and any errors or warnings.
    
    Args:
        plan_to_validate: A dictionary containing the workout plan to validate
        
    Returns:
        A dictionary containing the validation results
    """
    # Check if validation_agent_executor is available
    if validation_agent_executor is None:
        return {
            "status": "error",
            "message": "Validation agent executor not initialized",
            "valid": False,
            "errors": ["Internal configuration error: validation agent not available"]
        }
    
    # Construct the input dictionary for the validation agent
    input_dict = {
        'input_data': {
            'task': 'validate_workout_plan',
            'plan_to_validate': plan_to_validate
        }
    }
    
    # Call the validation agent executor
    result = validation_agent_executor.invoke(input_dict)
    
    # Extract and return the output part of the result
    return result['output']

def set_validation_agent_executor(executor):
    """
    Set the validation agent executor to be used by the tool.
    
    Args:
        executor: The validation agent executor instance
    """
    global validation_agent_executor
    validation_agent_executor = executor