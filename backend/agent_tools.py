"""
Trystero Agent Tools

This module provides tools for the Trystero agent, including a tool that wraps
the RuleBasedValidationAgent's AgentExecutor for validating workout progress
data.
"""

from langchain_core.tools import tool
from typing import Dict, Any


@tool
def check_progress_with_validation_agent(
    progress_data: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Consults the Rule-Based Validation Agent to get a factual check on whether
    the provided workout progress data (e.g., workouts completed vs. target)
    aligns with the established, hard-coded workout schedule rules. Input is a
    dictionary of progress data. Returns a
    dictionary with validation results including 'is_valid' and a 'reason'.
    """
    # Import validation_agent_executor from the module where it's defined
    # This assumes validation_agent_executor is available in the global scope
    # when this function is used as a tool
    from __main__ import validation_agent_executor
    
    # Handle case where no progress data is provided
    if progress_data is None:
        return {
            "status": "error",
            "message": "No progress data provided",
            "valid": False,
            "errors": ["Missing progress data"]
        }
    
    # Handle case where progress data might be nested
    # This makes the tool more robust against different input formats
    actual_data = progress_data
    if isinstance(progress_data, dict) and "progress_data" in progress_data:
        actual_data = progress_data["progress_data"]
    
    # Construct the input dictionary for the validation agent
    input_dict = {
        'input_data': {
            'task': 'validate_progress_tracking',
            'data': actual_data
        }
    }
    
    # Call the validation agent executor
    result = validation_agent_executor.invoke(input_dict)
    
    # Extract and return the output part of the result
    return result['output']