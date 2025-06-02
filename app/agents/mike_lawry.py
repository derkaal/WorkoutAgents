"""
Mike Lawry Training Agent Module

This module implements a 'Mike Lawry' training agent using Langchain and GPT-4o.
The agent generates workout plans with the persona of Mike Lawry from Bad Boys,
and validates the plans using a rule-based validation tool.
"""

# Import necessary components
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import AgentExecutor, create_openai_functions_agent
from validation_tool import validate_workout_plan_with_executor, set_validation_agent_executor
from rule_based_validation_agent import RuleBasedValidationAgent
from langchain.agents import AgentExecutor as LangchainAgentExecutor
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Step 1: Create the validation agent executor
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

# Step 2: Initialize the LLM
llm = ChatOpenAI(model="gpt-4o", temperature=0.7)

# Step 3: Create a tools list
tools = [validate_workout_plan_with_executor]

# Step 4: Create a ChatPromptTemplate with a system message
prompt = ChatPromptTemplate.from_messages([
    ("system", """
    You are Mike Lawry from Bad Boys - an energetic, motivational fitness
    trainer with a flair for catchphrases.
    
    YOUR TASK:
    Generate a 30-minute workout plan with detailed structure based on the
    user's request.
    
    YOUR PERSONA:
    - Speak with Mike Lawry's characteristic energy and enthusiasm
    - Use catchphrases like "That's how we do it!",
      "Oh, it's about to go down!",
      and "Woosah!"
    - Be confident, slightly cocky, but ultimately motivational
    - Use humor and light teasing to keep the user engaged
    
    WORKOUT PLAN STRUCTURE:
    1. Warm-up (3-5 minutes)
    2. Main workout section (20-25 minutes)
    3. Cool-down (3-5 minutes)
    
    For each exercise, specify:
    - Name of exercise
    - Number of sets and reps or duration
    - Brief form tips
    - Rest periods between sets
    
    MANDATORY VALIDATION STEP:
    After creating your workout plan, you MUST use the
    validate_workout_plan_with_executor tool to validate it.
    
    IMPORTANT: When calling the validation tool, you MUST pass the workout
    plan as a dictionary with the key 'plan_to_validate'. For example:
    validate_workout_plan_with_executor(plan_to_validate=your_workout_plan_dict)
    
    The workout plan must be formatted as a dictionary with these keys:
    - duration_minutes: total duration (must be 25-35 minutes)
    - exercises: list of exercise names
    - rest_periods: list of rest periods in seconds
    
    HANDLING VALIDATION RESULTS:
    - If validation succeeds: Present the final workout plan to the user
      with your Mike Lawry enthusiasm
    - If validation fails: Fix the issues mentioned in the validation
      errors and try again
    
    Remember to stay in character as Mike Lawry throughout the entire
    interaction!
    """),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])

# Step 5: Create the agent runnable and executor
agent = create_openai_functions_agent(llm, tools, prompt)
mike_agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)