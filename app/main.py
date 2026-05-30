"""
Main Application Entry Point for the Agentic AI Travel Planning Assistant.
Validates the environment, initializes logging, and launches the Streamlit frontend.
"""

import os
import subprocess
import sys
from pathlib import Path

from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)

# Add the project root to sys.path to ensure absolute imports work correctly
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from app.services.utils import setup_logger


def _verify_environment() -> bool:
    
    is_valid = True

    #Check API Keys
    if not os.getenv("GEMINI_API_KEY"):
        logger.error("CRITICAL: GEMINI_API_KEY is not set in the environment or .env file.")
        logger.error("Please add GEMINI_API_KEY=your_key to your .env file.")
        is_valid = False

    #Check Data Files
    data_dir = PROJECT_ROOT / "data"
    required_files = ["flights.json", "hotels.json", "places.json"]
    
    if not data_dir.exists():
        logger.error(f"CRITICAL: Data directory not found at {data_dir}.")
        is_valid = False
    else:
        for file_name in required_files:
            file_path = data_dir / file_name
            if not file_path.exists():
                logger.error(f"CRITICAL: Required data file missing: {file_path}")
                is_valid = False
                
    return is_valid


def main() -> None:
    """
    Main execution loop.
    Initializes services, validates the environment, and starts the Streamlit server.
    """
    try:
        load_dotenv()
        
        setup_logger()
        logger.info("Starting Agentic AI Travel Planner...")
        
        if not _verify_environment():
            logger.error("Environment validation failed. Please fix the issues above and restart.")
            sys.exit(1)
            
        logger.info("Environment validation successful.")
        
        # Determine path to the streamlit application
        streamlit_app_path = PROJECT_ROOT / "app" / "ui" / "streamlit_app.py"
        
        if not streamlit_app_path.exists():
            logger.error(f"CRITICAL: Streamlit application file not found at {streamlit_app_path}")
            sys.exit(1)
            
        logger.info("Launching Streamlit Web Interface...")
        
        # We use subprocess to call 'streamlit run' which is the officially supported method for programmatic Streamlit execution.
        result = subprocess.run(
            [sys.executable, "-m", "streamlit", "run", str(streamlit_app_path)],
            cwd=str(PROJECT_ROOT),
            check=False
        )
        
        if result.returncode != 0:
            logger.warning(f"Streamlit exited with non-zero status code: {result.returncode}")
        else:
            logger.info("Streamlit application closed successfully.")
            
    except KeyboardInterrupt:
        logger.info("Application terminated by user (KeyboardInterrupt).")
        sys.exit(0)
    except Exception as e:
        logger.exception(f"An unhandled application-level exception occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
