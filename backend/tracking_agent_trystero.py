"""
Trystero Tracking Agent

This script implements a 'Trystero' agent using Langchain and MistralAI.
The agent analyzes workout progress data with the persona of Trystero,
and validates the data using a rule-based validation tool.
"""

# Import necessary components
import os
import json
from typing import Any, List, Optional
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage, AIMessage
from langchain_core.callbacks.manager import CallbackManagerForLLMRun
from langchain_mistralai.chat_models import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import AgentExecutor, create_tool_calling_agent
from agent_tools import check_progress_with_validation_agent
from rule_based_validation_agent import RuleBasedValidationAgent
from langchain.agents import AgentExecutor as LangchainAgentExecutor
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Check if we should use a mock LLM for testing
USE_MOCK_LLM = False

# Check if MISTRAL_API_KEY is set and valid
if "MISTRAL_API_KEY" not in os.environ:
    print("Warning: MISTRAL_API_KEY environment variable is not set.")
    print("Using mock LLM for testing purposes.")
    USE_MOCK_LLM = True
elif os.environ["MISTRAL_API_KEY"] == "your-mistral-api-key-here":
    print("Warning: MISTRAL_API_KEY is set to the placeholder value.")
    print("Using mock LLM for testing purposes.")
    USE_MOCK_LLM = True


# Create a mock LLM for testing purposes
class MockChatModel(BaseChatModel):
    """Mock Chat Model for testing purposes."""
    
    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> AIMessage:
        """Generate a mock response."""
        # Extract the user's message
        user_message = messages[-1].content
        
        # Check if it contains progress data
        if "progress data" in user_message:
            # Create a mock response that includes tool calls
            return AIMessage(content="", additional_kwargs={
                "tool_calls": [
                    {
                        "id": "call_123",
                        "type": "function",
                        "function": {
                            "name": "check_progress_with_validation_agent",
                            "arguments": json.dumps({
                                "progress_data": {
                                    "completed_strength": 1,
                                    "target_strength": 2,
                                    "completed_yoga": 0,
                                    "target_yoga": 1,
                                    "completed_runs_logged": 2,
                                    "target_runs": 2,
                                    "user_notes": "Felt tired, skipped yoga."
                                }
                            })
                        }
                    }
                ]
            })
        
        # Default response
        return AIMessage(
            content=(
                "I am Trystero, the Underground Courier of Insight. "
                "How may I assist you with your workout progress?"
            )
        )
    
    async def _agenerate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> AIMessage:
        """Generate a mock response asynchronously."""
        return self._generate(messages, stop, run_manager, **kwargs)


def main():
    """
    Main function to set up and run the Trystero tracking agent
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
    if USE_MOCK_LLM:
        print("Using mock LLM for testing purposes")
        llm = MockChatModel()
    else:
        llm = ChatMistralAI(model="mistral-small-latest", temperature=0.5)
    
    # Step 3: Create a tools list
    tools = [check_progress_with_validation_agent]
    
    # Step 4: Create a ChatPromptTemplate with Trystero's persona
    prompt = ChatPromptTemplate.from_messages([
        ("system", """
        You are **Trystero – The Underground Courier of Insight** –  
        an agent for analyzing workout progress with clarity, calm, and a flicker of subversion.

        ---

        🔹 YOUR PERSONA  
        - **Warmly honest**: You speak truth with care — direct, never cruel.  
        - **Grounded in reality**: Your insights stem from data, structure, and repeatable patterns.  
        - **Quietly enigmatic**: You favor dry wit, understated metaphors, and the occasional literary nod.  
        - **Pragmatic**: Your aim is to be useful — not poetic, motivational, or mystical.

        ---

        🔹 YOUR VOICE  
        - **Measured and clear**: You speak with intentional cadence — no fluff, no rush.  
        - **Precise, not sterile**: Favor well-formed sentences over technical detail or filler.  
        - **Wry, but kind**: You may raise an eyebrow, but never a finger.  
        - **Minimalist**: If you can say it in 7 words, don’t use 12.

        ---

        🔹 YOUR BEHAVIORS  
        - **Spot signal**: Highlight what matters, even when it’s subtle.  
        - **Prompt reflection**: Pose one or two thoughtful questions that invite insight.  
        - **Offer grounded suggestions**: Avoid generic advice (e.g., “consult a nutritionist”). Base recommendations on the provided data.  
        - **Start with a shaped sentence**: Begin with a subtle interpretation, not a data list.  
        - **End clean**: Close with a line that either reframes or lets the idea breathe. Never trail off or echo slogans.

        ---

        🔹 YOUR REFERENCES  
        - Use metaphors drawn from literature, systems thinking, or art — **only when they reveal structure, habit, or tension**.  
          Never aim to sound “profound.” You are a courier, not a sage.

        ---

        🔹 YOUR TASK
        Given workout progress data (in dictionary format), do the following:
        1. **Validate** the data using `check_progress_with_validation_agent`
           - IMPORTANT: When calling this tool, you MUST pass the progress data directly to the "progress_data" parameter
           - Example: If you have progress data like {"completed_strength": 2}, pass it as {"progress_data": {"completed_strength": 2}}
           - Failure to format the tool input correctly will result in a validation error
        2. **Assess** completion rates against targets
        3. **Identify** patterns or emerging trends
        4. **Provide** concise, structured feedback in Trystero's voice

        ---

        🔹 YOUR OUTPUT FORMAT  
        1. A brief **feedback section** with clear observations (not judgments or praise)  
        2. A structured section titled `briefing_for_next_plan` with:
           - **Key observations**  
           - **Suggested focus areas**  
           - **Potential adjustments**

        Wrap up with a single, composed line — no slogans, no affirmations, no recycled wisdom.

        ---

        When in doubt: deliver insight, ask a better question, then disappear.

        """),
        MessagesPlaceholder(variable_name="chat_history", optional=True),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])
    
    # Step 5: Create the agent runnable and executor
    trystero_agent_runnable = create_tool_calling_agent(llm, tools, prompt)
    trystero_agent_executor = AgentExecutor(
        agent=trystero_agent_runnable,
        tools=tools,
        verbose=True,
        handle_parsing_errors=True,
        return_intermediate_steps=False
    )
    
    return trystero_agent_executor


if __name__ == "__main__":
    try:
        print("Creating Trystero agent executor...")
        # Create the Trystero agent executor
        trystero_agent_executor = main()
        
        # Sample progress data
        sample_progress = {
            'completed_strength': 1,
            'target_strength': 2,
            'completed_yoga': 0,
            'target_yoga': 1,
            'completed_runs_logged': 2,
            'target_runs': 2,
            'user_notes': 'Felt tired, skipped yoga.'
        }
        
        print("Sample progress data:", sample_progress)
        
        # Format input for Trystero
        input_data = {
            "input": f"Trystero, here is my progress data for the week: "
                     f"{sample_progress}"
        }
        
        print("Invoking Trystero agent...")
        # Invoke agent
        response = trystero_agent_executor.invoke(input_data)
        
        # Extract the briefing for next plan section
        output_text = response.get('output', '')
        briefing_section = None
        
        # Check for different possible formats of the briefing section
        if "### Briefing for Next Plan" in output_text:
            # Format with ### heading
            parts = output_text.split("### Briefing for Next Plan")
            if len(parts) > 1:
                briefing_section = "### Briefing for Next Plan" + parts[1]
                
                # Add the extracted briefing to the response
                response['briefing_for_next_plan'] = briefing_section
        elif "briefing_for_next_plan" in output_text:
            # Format with briefing_for_next_plan
            parts = output_text.split("### **briefing_for_next_plan**")
            if len(parts) > 1:
                briefing_section = "### **briefing_for_next_plan**" + parts[1]
                
                # Add the extracted briefing to the response
                response['briefing_for_next_plan'] = briefing_section
        elif "**Briefing for Next Plan**" in output_text:
            # Format with bold markdown
            parts = output_text.split("#### **Briefing for Next Plan**")
            if len(parts) > 1:
                briefing_section = "#### **Briefing for Next Plan**" + parts[1]
                
                # Add the extracted briefing to the response
                response['briefing_for_next_plan'] = briefing_section
        elif "Briefing for Next Plan" in output_text:
            # Alternative format without bold
            parts = output_text.split("#### Briefing for Next Plan")
            if len(parts) > 1:
                briefing_section = "#### Briefing for Next Plan" + parts[1]
                
                # Add the extracted briefing to the response
                response['briefing_for_next_plan'] = briefing_section
        
        # Display results
        print("Trystero's Full Output:", response)
        print("\nTrystero's Spoken Feedback:", response.get('output'))
        print("\nBriefing for Next Plan:",
              response.get('briefing_for_next_plan', "Not found in response"))
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        import traceback
        traceback.print_exc()