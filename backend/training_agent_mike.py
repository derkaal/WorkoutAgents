"""
Mike Lawry Training Agent

This script implements a 'Mike Lawry' training agent using Langchain and
GPT-4o.
The agent generates workout plans with the persona of Mike Lawry from Bad Boys,
and validates the plans using a rule-based validation tool.
"""

# Import necessary components
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import AgentExecutor, create_openai_functions_agent
from validation_tool import validate_workout_plan_with_executor
from rule_based_validation_agent import RuleBasedValidationAgent
from langchain.agents import AgentExecutor as LangchainAgentExecutor
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def main():
    """
    Main function to set up and run the Mike Lawry training agent
    """
    # Step 1: Create the validation agent executor
    validation_agent = RuleBasedValidationAgent()
    
    # Create the validation agent executor and make it available globally
    # This is what our validation tool expects to find
    global validation_agent_executor
    validation_agent_executor = LangchainAgentExecutor.from_agent_and_tools(
        agent=validation_agent,
        tools=[],
        handle_parsing_errors=True,
        verbose=True
    )
    
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
        
        TRYSTERO BRIEFING:
        - You may receive an optional trystero_briefing dictionary with
          recommendations
        - If provided, consider the following from the briefing:
          * focus_areas: Specific areas to emphasize in the workout
          * energy_level: User's current energy level to adjust intensity
          * recommended_adjustments: Specific exercise modifications
        - Incorporate these recommendations while still addressing the user's
          direct request
        - Acknowledge the briefing in your response (e.g., "Trystero gave me
          the lowdown...")
        - Balance the briefing recommendations with the user's immediate needs
        
        WORKOUT PLAN STRUCTURE:
        1. Warm-up (3-5 minutes)
        2. Main workout section (20-25 minutes)
        3. Cool-down (3-5 minutes)
        
        For each exercise and rest period, specify:
        - name: Name of exercise (e.g., "Push-Ups") or "Rest"
        - duration_seconds: (Optional) Duration in seconds for timed exercises or rest periods
        - sets: (Optional) Number of sets for the exercise
        - reps: (Optional) Number of reps or rep range (e.g., "6-8")
        - instruction_text: A concise (1-2 sentences) instruction on how to perform the movement or what to do during rest.
          - For exercises: Explain how to perform the movement.
          - For rest periods: Provide a motivational or practical instruction (e.g., "Great job! Take a 30-second rest now. Breathe deeply.").
        
        MANDATORY VALIDATION STEP:
        After generating the workout plan, you MUST call the
        `validate_workout_plan_with_executor` tool.
        
        The argument to this tool MUST be a dictionary with a single key:
        `plan_to_validate`. The value associated with this key MUST be the
        structured workout plan you generated, formatted as a JSON object
        conforming to the `WorkoutPlan` schema.
        
        Example of tool call (the entire workout plan object should be the value for 'plan_to_validate'):
        `validate_workout_plan_with_executor(plan_to_validate={
            "duration_minutes": 30,
            "days": [
                {
                    "name": "Day 1 - Full Body",
                    "exercises": [
                        {
                            "name": "Push-Ups",
                            "sets": 3,
                            "reps": 10,
                            "instruction_text": "Keep your body straight."
                        },
                        {
                            "name": "Rest",
                            "duration_seconds": 60,
                            "instruction_text": "Take a break."
                        }
                    ]
                }
            ]
        })`
        
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
        MessagesPlaceholder(variable_name="trystero_briefing", optional=True),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])
    
    # Step 5: Create the agent runnable and executor
    agent = create_openai_functions_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
    
    # Step 6: Testing block
    print("\n--- Testing Mike Lawry Training Agent: "
          "Successful Case (No Trystero Briefing) ---")
    result1 = agent_executor.invoke({
        "input": "I need a quick full-body workout that I can do at home with "
                 "minimal equipment.",
        "chat_history": []  # Initialize empty chat history
    })
    print(f"Result: {result1['output']}")
    
    print("\n--- Testing Mike Lawry Training Agent: "
          "With Trystero Briefing ---")
    result2 = agent_executor.invoke({
        "input": "I need a workout for today.",
        "chat_history": [],  # Initialize empty chat history
        "trystero_briefing": {
            "fitness_level": "intermediate",
            "focus_areas": ["lower body strength", "core stability"],
            "energy_level": "medium",
            "recommended_adjustments": {
                "intensity": "moderate",
                "add_assistance_exercises": ["goblet squats", "planks"]
            },
            "previous_adherence": 0.85
        }
    })
    print(f"Result: {result2['output']}")
    
    print("\n--- Testing Mike Lawry Training Agent: Potentially Failing "
          "Case ---")
    result3 = agent_executor.invoke({
        "input": "I need a very short 15-minute workout.",
        "chat_history": []  # Initialize empty chat history
    })
    print(f"Result: {result3['output']}")


if __name__ == "__main__":
    main()