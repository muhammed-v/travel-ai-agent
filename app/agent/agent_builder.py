"""
Agent Builder module for the Agentic AI Travel Planning Assistant.
Constructs the LangGraph agent, binds tools, and configures the execution environment.
"""

import os
from typing import Any, Dict
import logging

from langgraph.prebuilt import create_react_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

from app.agent.prompts import build_agent_prompt
from app.tools.budget_tool import calculate_trip_budget
from app.tools.flight_tool import search_flights
from app.tools.hotel_tool import search_hotels
from app.tools.places_tool import search_places
from app.tools.weather_tool import get_weather_forecast

logger = logging.getLogger(__name__)


def _get_available_tools() -> list:
    return [
        search_flights,
        search_hotels,
        search_places,
        get_weather_forecast,
        calculate_trip_budget
    ]


def _initialize_llm() -> ChatGoogleGenerativeAI:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        logger.warning("GEMINI_API_KEY environment variable is not set. The agent will fail to execute.")

    return ChatGoogleGenerativeAI(
        model="gemini-flash-lite-latest",
        temperature=0.2, 
        max_retries=3,   
        timeout=60,
    )


class TravelAgent:
    """
    A wrapper class for the LangGraph travel planning agent.
    Encapsulates the agent creation, prompt management, and execution logic.
    """
    
    def __init__(self, require_budget: bool = False, require_itinerary: bool = False):
        logger.info("Initializing Travel Agent...")
        
        self.llm = _initialize_llm()
        self.tools = _get_available_tools()
        self.system_prompt = build_agent_prompt(require_budget=require_budget, require_itinerary=require_itinerary)
        
        try:
            #Creating the LangGraph ReAct Agent
            self.agent = create_react_agent(
                self.llm,
                tools=self.tools,
                prompt=self.system_prompt
            )
            logger.info("Travel Agent successfully initialized.")
        except Exception as e:
            logger.error(f"Failed to initialize Travel Agent: {e}")
            raise

    def run(self, user_input: str) -> Dict[str, Any]:
        logger.info(f"Processing user request: '{user_input}'")
        
        try:
            # Execute the LangGraph agent
            response = self.agent.invoke(
                {"messages": [HumanMessage(content=user_input)]}
            )


            raw_content = response["messages"][-1].content# -1 means the last item in the list of messages.
            if isinstance(raw_content, list): # isinstance() checks type of raw_content
                # Extract text from all text blocks (list comprehension is used here )
                final_message = "\n".join([block.get("text", "") for block in raw_content if block.get("type") == "text"])
            else:
                final_message = str(raw_content)
            
            logger.info("Agent execution completed successfully.")
            return {
                "status": "success",
                "output": final_message
            }
            
        except Exception as e:
            logger.error(f"Agent execution encountered an error: {e}")
            return {
                "status": "error",
                "message": "The AI assistant encountered an unexpected error while processing your request.",
                "details": str(e)
            }


def build_travel_agent(require_budget: bool = False, require_itinerary: bool = False) -> TravelAgent:
    """
    Factory function to easily build and retrieve a configured TravelAgent.
    """
    return TravelAgent(require_budget=require_budget, require_itinerary=require_itinerary)
