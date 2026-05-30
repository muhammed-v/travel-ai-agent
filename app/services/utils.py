"""
Utility functions for the Agentic AI Travel Planning Assistant.
"""

import os
import sys
import logging

logger = logging.getLogger(__name__)


def setup_logger() -> None:
    """
    Initializes standard Python logging.
    Logs to stdout and a file if logs directory exists.
    """
    os.makedirs("logs", exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("logs/app.log")
        ]
    )
    logger.info("Standard logging initialized successfully.")



