# Agentic AI Travel Planning Assistant

A comprehensive, production-ready AI travel planning assistant utilizing Python, LangChain, Gemini Flash Latest, Streamlit, and local JSON datasets.

## Project Structure

* `app/`: The core application code.
  * `main.py`: The main entry point for the application, initializing the app and orchestrating components.
  * `agent/`: Contains the LangChain agent setup, including the builder and prompt templates.
  * `tools/`: Individual modules for specific tools (flights, hotels, places, weather, budget).
  * `services/`: Helper services, such as data loading utilities for JSON parsing and other shared utility functions.
  * `ui/`: Streamlit user interface implementation.
* `data/`: Local JSON datasets for flights, hotels, and places.


## Getting Started

1. Set up a virtual environment.
2. Install dependencies via `pip install -r requirements.txt`.
3. Configure your `.env` file with your `GEMINI_API_KEY`.
4. Run the Streamlit application.
