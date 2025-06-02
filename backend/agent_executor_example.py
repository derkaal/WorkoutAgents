"""
Example of using AgentExecutor with RuleBasedValidationAgent

This module demonstrates how to instantiate and use the
RuleBasedValidationAgent with LangChain's AgentExecutor.
The RuleBasedValidationAgent is a rule-based agent
that validates different types of input data without using external tools.
"""

# Import necessary modules
from langchain.agents import AgentExecutor
from rule_based_validation_agent import RuleBasedValidationAgent


def main():
    """
    Main function demonstrating how to use AgentExecutor with
    RuleBasedValidationAgent
    """
    # Step 1: Instantiate the RuleBasedValidationAgent
    validation_agent = RuleBasedValidationAgent()
    
    # Step 2: Create an AgentExecutor with the validation agent
    # Note: This agent doesn't use external tools, so the tools list is empty
    agent_executor = AgentExecutor.from_agent_and_tools(
        agent=validation_agent,
        tools=[],  # Empty tools list since this agent doesn't use tools
        handle_parsing_errors=True,  # For robustness in handling errors
        verbose=True  # Set to True to see the execution process
    )
    
    # Step 3: Use the AgentExecutor to run validations
    
    # Example 1: Valid workout plan
    print("\n--- Example 1: Valid Workout Plan ---")
    result1 = agent_executor.run(
        input_data={
            'task': 'validate_workout_plan',
            'data': {
                'duration_minutes': 30,
                'exercises': ['push-ups', 'squats'],
                'rest_periods': [60, 90]
            }
        }
    )
    print(f"Result: {result1}")
    
    # Example 2: Invalid workout plan
    print("\n--- Example 2: Invalid Workout Plan ---")
    result2 = agent_executor.run(
        input_data={
            'task': 'validate_workout_plan',
            'data': {
                'duration_minutes': 20  # Less than minimum 25 minutes
            }
        }
    )
    print(f"Result: {result2}")
    
    # Example 3: Progress tracking validation
    print("\n--- Example 3: Progress Tracking Validation ---")
    result3 = agent_executor.run(
        input_data={
            'task': 'validate_progress_tracking',
            'data': {
                'progress': 50,
                'date': '2025-05-30'
            }
        }
    )
    print(f"Result: {result3}")
    
    # Example 4: Error handling with invalid task
    print("\n--- Example 4: Error Handling with Invalid Task ---")
    try:
        result4 = agent_executor.run(
            input_data={
                'task': 'invalid_task',  # This task doesn't exist
                'data': {
                    'some_field': 'some_value'
                }
            }
        )
        print(f"Result: {result4}")
    except Exception as e:
        print(f"Error handled: {str(e)}")


if __name__ == "__main__":
    main()