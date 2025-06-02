"""
Example of using the Workout Plan Validation Tool with another LangChain agent

This example demonstrates how to use the validate_workout_plan_with_executor
tool with a LangChain agent.
"""

from dotenv import load_dotenv
from langchain.agents import initialize_agent, AgentType
from langchain.llms import OpenAI
from rule_based_validation_agent import RuleBasedValidationAgent
from langchain.agents import AgentExecutor as LangchainAgentExecutor

# Import our validation tool
from validation_tool import validate_workout_plan_with_executor, set_validation_agent_executor

# Load environment variables from .env file
load_dotenv()


def main():
    """
    Main function demonstrating how to use the validation tool with
    another agent
    """
    # Step 1: Create the validation agent executor
    # (same as in agent_executor_example.py)
    validation_agent = RuleBasedValidationAgent()
    
    # Create the validation agent executor
    validation_agent_executor = LangchainAgentExecutor.from_agent_and_tools(
        agent=validation_agent,
        tools=[],
        handle_parsing_errors=True,
        verbose=True
    )
    
    # Register the validation agent executor with the validation tool
    set_validation_agent_executor(validation_agent_executor)
    
    # Step 2: Set up the Mike Lawry agent with the validation tool
    # The API key is loaded from the OPENAI_API_KEY environment variable
    llm = OpenAI(temperature=0)
    
    # Create a list of tools for the Mike Lawry agent, including
    # our validation tool
    tools = [
        validate_workout_plan_with_executor
    ]
    
    # Initialize the Mike Lawry agent
    mike_lawry_agent = initialize_agent(
        tools=tools,
        llm=llm,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True
    )
    
    # Step 3: Use the Mike Lawry agent to create and validate a workout plan
    mike_lawry_agent.run(
        "Create a workout plan and validate it using the validation tool."
    )
    
    # Example of directly calling the validation tool with a workout plan
    print("\n--- Direct Tool Usage Example ---")
    workout_plan = {
        'duration_minutes': 30,
        'exercises': ['push-ups', 'squats', 'lunges'],
        'rest_periods': [60, 60]
    }
    
    validation_result = validate_workout_plan_with_executor(workout_plan)
    print(f"Validation Result: {validation_result}")


if __name__ == "__main__":
    main()