"""
Streamlit UI module for the Agentic AI Travel Planning Assistant.
Provides a modern, responsive, and professional web interface.
"""

import os

import streamlit as st
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)

from app.agent.agent_builder import build_travel_agent

# Initialize env
load_dotenv()


def init_session_state() -> None:
    """Initialize required Streamlit session state variables."""
    if "agent_response" not in st.session_state:
        st.session_state.agent_response = None
    if "is_loading" not in st.session_state:
        st.session_state.is_loading = False


def build_user_query(source: str, destination: str, duration: int, budget: float, preferences: str) -> str:
    """Constructs the structured prompt to send to the LangChain agent."""
    query = (
        f"Please plan a {duration}-day trip from {source} to {destination}. "
        f"My total maximum budget is ₹{budget:.2f}. "
    )
    if preferences:
        query += f"My personal preferences and interests are: {preferences}. "
    
    query += "Please verify the weather, recommend flights and hotels, calculate the budget, and generate a day-by-day itinerary."
    return query


def render_sidebar() -> tuple:
    
    st.sidebar.header("✈️ Trip Parameters")
    
    st.sidebar.markdown("### Route Details")
    source = st.sidebar.text_input("Departure City", placeholder="e.g., New York, NYC")
    destination = st.sidebar.text_input("Destination City", placeholder="e.g., London, LHR")
    
    st.sidebar.markdown("### Logistics")
    duration = st.sidebar.number_input("Trip Duration (Days)", min_value=1, max_value=30, value=7, step=1)
    budget = st.sidebar.number_input("Total Budget (₹)", min_value=10000.0, max_value=100000.0, value=30000.0, step=5000.0)
    
    st.sidebar.markdown("### Preferences")
    preferences = st.sidebar.text_area(
        "Interests & Requirements", 
        placeholder="e.g., family-friendly, museums, fine dining, budget travel."
    )
    
    return source, destination, duration, budget, preferences


def render_main_content() -> None:
    """Renders the primary application UI and handles agent interaction."""
    st.title("🌍 Agentic AI Travel Planner")
    st.markdown(
        """
        Welcome to your personal, professional travel concierge. 
        Powered by LangChain and Gemini Flash Lite, this assistant intelligently searches 
        flights, hotels, attractions, and weather to craft the perfect itinerary within your budget.
        """
    )
    
    source, destination, duration, budget, preferences = render_sidebar()
    
    with st.form("travel_form"):
        submitted = st.form_submit_button("✨ Generate My Itinerary", use_container_width=True)
        
        if submitted:
            #Validation
            if not source or not destination:
                st.error("⚠️ Please provide both a Departure City and a Destination City.")
                return
            if not os.getenv("GEMINI_API_KEY"):
                st.error("⚠️ GEMINI_API_KEY is not set in your environment. Please configure your .env file.")
                return
                
            #Execution Initialization
            st.session_state.agent_response = None
            st.session_state.is_loading = True
            
    if st.session_state.is_loading:
        with st.spinner("🤖 Analyzing routes, weather, and budget to craft your perfect trip..."):
            try:
                # Initialize agent
                agent = build_travel_agent(require_budget=True, require_itinerary=True)
                query = build_user_query(source, destination, duration, budget, preferences)
                
                # Execute agent
                response = agent.run(query)
                st.session_state.agent_response = response
                
            except Exception as e:
                st.error(f"An error occurred during planning: {e}")
                logger.error(f"UI Execution Error: {e}")
            finally:
                st.session_state.is_loading = False

    #Display Results
    if st.session_state.agent_response:
        response = st.session_state.agent_response
        
        if response.get("status") == "error":
            st.error("❌ " + response.get("message", "An unexpected error occurred."))
            if "details" in response:
                with st.expander("Technical Details"):
                    st.code(response["details"])
        else:
            st.success("🎉 Your itinerary is ready!")
            
            # The agent returns highly structured markdown text in the "output" field
            agent_text = response.get("output", "")
            
            # Displaying the main output
            st.markdown("---")
            st.markdown(agent_text)
            st.markdown("---")
            
            # JSON Output Toggle for debugging and transparency
            if st.toggle("Show Raw Agent Output (JSON)"):
                st.json(response)


def main() -> None:
    """Main Streamlit application entry point."""
    st.set_page_config(
        page_title="AI Travel Planner",
        page_icon="✈️",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Clean UI formatting: hide default Streamlit styling
    hide_streamlit_style = """
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        .stButton>button {
            background-color: #4CAF50;
            color: white;
            font-weight: bold;
            border-radius: 8px;
        }
        </style>
    """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)
    
    init_session_state()
    render_main_content()


if __name__ == "__main__":
    main()
