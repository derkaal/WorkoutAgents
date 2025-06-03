"""
Trystero Tracking Agent Module

This module implements a 'Trystero' agent using Langchain and OpenAI.
The agent analyzes workout progress data with the persona of Trystero,
and validates the data using a rule-based validation tool.
"""

# Import necessary components
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import initialize_agent, AgentType
from backend.agent_tools import check_progress_with_validation_agent
from backend.workout_history_tool import check_workout_history
from backend.rule_based_validation_agent import RuleBasedValidationAgent
from langchain.agents import AgentExecutor as LangchainAgentExecutor

# Use pydantic v1 compatibility for Langchain components 
os.environ["PYDANTIC_V1"] = "1"

# Load environment variables from .env file
load_dotenv()

# Step 1: Create the validation agent executor
validation_agent = RuleBasedValidationAgent()

# Create the validation agent executor and make it available globally
validation_agent_executor = LangchainAgentExecutor.from_agent_and_tools(
    agent=validation_agent,
    tools=[],
    handle_parsing_errors=True,
    verbose=True
)

# Step 2: Initialize the LLM with a simpler, more robust approach
llm = ChatOpenAI(model="gpt-4o", temperature=0.5)

# Step 3: Create a tools list
tools = [check_progress_with_validation_agent, check_workout_history]

# Step 4: Create a simplified system prompt as a string
SYSTEM_PROMPT = """
You are Trystero – The Underground Courier of Insight – an agent for analyzing 
workout progress with clarity and precision.

PERSONA:
- Warmly honest: Direct but never cruel
- Grounded in reality: Focus on data and repeatable patterns
- Quietly enigmatic: Use dry wit and understated metaphors
- Pragmatic: Be useful, not poetic or mystical

VOICE:
- Measured and clear: No fluff, no rush
- Precise: Use well-formed sentences
- Minimalist: Be concise and to the point

TASK:
When analyzing workout progress data, do the following:
1. Use the check_progress_with_validation_agent tool to validate the data
   - Pass the complete progress data directly to the progress_data parameter
   - Example: If the data is {"completed_strength": 2}, use:
     progress_data={"completed_strength": 2}
   - The tool will handle the data format appropriately
   - The tool will return workout goal rules including weekly targets
2. Consult the validation agent's response for weekly workout targets and calculation rules
3. Use the check_workout_history tool to retrieve workout history data including:
   - Consecutive workout days
   - Weekly workout count vs. target
   - Whether rest is recommended
4. Assess completion rates against targets (not hardcoded values)
5. Identify patterns or emerging trends
6. Consider rest recommendations in your analysis
7. Provide structured feedback

OUTPUT FORMAT:
1. Brief feedback section with clear observations
2. A section titled "briefing_for_next_plan" with:
   - Key observations
   - Suggested focus areas
   - Potential adjustments

End with a single, composed line - no slogans or recycled wisdom.
"""

# Step 5: Create the agent with a simpler approach
trystero_agent_executor = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.OPENAI_FUNCTIONS,  # More robust format
    verbose=True,
    handle_parsing_errors=True,
    agent_kwargs={
        "system_message": SYSTEM_PROMPT,
    },
)