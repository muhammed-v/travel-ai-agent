"""
Flight Tool module for the Agentic AI Travel Planning Assistant.
"""

from typing import Any, Dict, Optional

from langchain.tools import tool
import logging

logger = logging.getLogger(__name__)

from app.services.data_loader import get_flights_data


def _calculate_flight_score(flight: Dict[str, Any], sort_by: str) -> float:
    if sort_by == "price":
        return float(flight.get("price", 999999))
    elif sort_by == "fastest":
        return float(flight.get("duration_minutes", 999999))


def _format_flight_explanation(flight: Dict[str, Any], sort_by: str) -> str:
    airline = flight.get('airline', 'Unknown Airline')
    source = flight.get('from', 'Unknown Source')
    destination = flight.get('to', 'Unknown Destination')
    
    explanation = f"Selected {airline} flight from {source} to {destination}."
    
    if sort_by == "price":
        price = flight.get('price', 'N/A')
        explanation += f" It was ranked highly due to its competitive price of ₹{price}."
    elif sort_by == "fastest":
        duration = flight.get('duration_minutes', 'N/A')
        explanation += f" It was ranked highly due to its short travel duration of {duration} minutes."
    else:
        explanation += " It matched the requested search criteria."
        
    return explanation


@tool
def search_flights(
    source: str, 
    destination: str, 
    preferred_airline: Optional[str] = None, 
    sort_by: str = "price"
) -> Dict[str, Any]:
    """
    Search for flights between a source and destination.
    
    Args:
        source: The full departure city name (e.g., 'Bangalore'). DO NOT use airport codes like 'BLR'.
        destination: The full arrival city name (e.g., 'Delhi'). DO NOT use airport codes like 'DEL'.
        preferred_airline: Optional name of the airline to filter by.
        sort_by: Criteria to rank flights. Options: 'price' (cheapest) or 'fastest'. Defaults to 'price'.
        
    Returns:
        A structured dictionary containing the search status, best match, and full result list.
    """
    logger.info(f"Tool executed: search_flights from '{source}' to '{destination}' (sort_by: {sort_by})")
    
    #Load Data
    all_flights = get_flights_data()
    if not all_flights or not isinstance(all_flights, list):
        logger.error("Failed to load flights data or data is empty.")
        return {
            "status": "error",
            "message": "Flight data is currently unavailable.",
            "results": []
        }

    #Filter flights
    matching_flights = []
    source_lower = source.lower()
    dest_lower = destination.lower()
    
    for f in all_flights:
        f_source = str(f.get("from", "")).lower()
        f_dest = str(f.get("to", "")).lower()
        
        if f_source == source_lower and f_dest == dest_lower:
            if preferred_airline:
                f_airline = str(f.get("airline", "")).lower()
                if preferred_airline.lower() not in f_airline: #"emirates" not in "emirates airlines" -> False
                    continue
            matching_flights.append(f)

    if not matching_flights:
        logger.info(f"No flights found for route {source} -> {destination}")
        return {
            "status": "success",
            "message": f"No flights found from {source} to {destination}.",
            "best_match": None,
            "results": []
        }

    #Sort / Rank flights
    valid_sort_options = ["price", "fastest"]
    if sort_by not in valid_sort_options:
        logger.warning(f"Invalid sort_by option '{sort_by}'. Defaulting to 'price'.")
        sort_by = "price"

    try:
        sorted_flights = sorted(matching_flights, key=lambda x: _calculate_flight_score(x, sort_by))
    except Exception as e:
        logger.error(f"Error sorting flights: {e}")
        sorted_flights = matching_flights  # Fallback to unsorted if an error occurs

    #Format Output and Add Explanations
    top_results = []
    for rank, flight in enumerate(sorted_flights, start=1): #enumerate returns 2 things: the index and the value (rank, flight). Also, start=1 makes the indexing start from 1
        
        flight_info = dict(flight)# Create a clean dict copy of the flight data 
        flight_info["rank"] = rank # Adds new key to dictionary.
        flight_info["recommendation_reason"] = _format_flight_explanation(flight, sort_by)
        top_results.append(flight_info)

    logger.info(f"Successfully processed {len(top_results)} flights matching the criteria.")
    
    return {
        "status": "success",
        "message": f"Found {len(top_results)} flight(s) matching your criteria.",
        "best_match": top_results[0] if top_results else None,
        "results": top_results
    }
