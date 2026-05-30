"""
Data loader service for the Agentic AI Travel Planning Assistant.
Handles the secure and robust loading of local JSON datasets.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import logging

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"


def load_json_data(file_path: Union[str, Path]) -> Optional[Union[List[Any], Dict[str, Any]]]:
   
    path = Path(file_path)
    
    if not path.exists():
        logger.error(f"File not found: {path}")
        return None
        
    if not path.is_file():
        logger.error(f"Path exists but is not a file: {path}")
        return None

    try:
        with open(path, "r", encoding="utf-8") as f: # using with, no need to close the file after use. Automatically closes the file.
            data = json.load(f)
            logger.debug(f"Successfully loaded JSON data from: {path}")
            return data
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error in file {path}: {e}")
    except Exception as e:
        logger.error(f"Unexpected error reading file {path}: {e}")

    return None


def get_flights_data() -> Optional[Union[List[Any], Dict[str, Any]]]:
    
    flights_path = DATA_DIR / "flights.json"
    logger.info(f"Loading flights data from {flights_path}")
    return load_json_data(flights_path)


def get_hotels_data() -> Optional[Union[List[Any], Dict[str, Any]]]:
    
    hotels_path = DATA_DIR / "hotels.json"
    logger.info(f"Loading hotels data from {hotels_path}")
    return load_json_data(hotels_path)


def get_places_data() -> Optional[Union[List[Any], Dict[str, Any]]]:
    
    places_path = DATA_DIR / "places.json"
    logger.info(f"Loading places data from {places_path}")
    return load_json_data(places_path)
