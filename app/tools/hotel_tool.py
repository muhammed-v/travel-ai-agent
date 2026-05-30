"""
Hotel Tool module for the Agentic AI Travel Planning Assistant.
"""

from typing import Any, Dict, Optional

from langchain.tools import tool
import logging

logger = logging.getLogger(__name__)

from app.services.data_loader import get_hotels_data

# _ at the start of the function name means private function, not accessible outside the module.
def _calculate_value_score(hotel: Dict[str, Any]) -> float:
    price = float(hotel.get("price_per_night", 0))
    rating = float(hotel.get("stars", 0))

    if price <= 0:
        return 0.0
    
    return rating / price


def _format_hotel_explanation(hotel: Dict[str, Any], recommendation_type: str) -> str:
    name = hotel.get('name', 'Unknown Hotel')
    price = hotel.get('price_per_night', 'N/A')
    rating = hotel.get('stars', 'N/A')

    explanation = f"Recommended '{name}' (Rating: {rating}/5, Price: ₹{price}/night)."

    if recommendation_type == "cheapest":
        explanation += " This is the most budget-friendly option available that meets your criteria."
    elif recommendation_type == "highest_rated":
        explanation += " This option boasts the highest guest rating among the available choices."
    elif recommendation_type == "best_value":
        explanation += " This hotel offers the best balance of high ratings and affordable pricing."
    else:
        explanation += " This hotel matches your search preferences."

    return explanation


@tool
def search_hotels(
    destination: str,
    max_budget: Optional[float] = None,
    min_rating: Optional[float] = None
) -> Dict[str, Any]: #dictionary of string (key), value can be anything

    # AI cannot see the python code, only the docstring can be seen by it as a description to the search hotels tool.
    """
    Search for hotels in a specific destination city and get intelligent recommendations.

    Args:
        destination: The destination city to search for hotels.
        max_budget: Maximum price per night in INR. WARNING: Database prices are in INR (e.g. 4000). If your budget is in USD, leave this as None to avoid filtering out all results.
        min_rating: The minimum acceptable hotel rating (e.g., 4.0).

    Returns:
        A structured dictionary containing intelligent recommendations (cheapest, 
        highest rated, best value) and the full list of matching hotels.
    """
    logger.info(f"Tool executed: search_hotels in '{destination}' (max_budget: {max_budget}, min_rating: {min_rating})")

    #Load Data
    all_hotels = get_hotels_data()
    if not all_hotels or not isinstance(all_hotels, list):
        logger.error("Failed to load hotel data or data is empty.")
        return {
            "status": "error",
            "message": "Hotel data is currently unavailable.",
            "recommendations": {},
            "results": []
        }

    # Filter Hotels
    matching_hotels = []
    city_lower = destination.lower()

    for h in all_hotels:
        h_city = str(h.get("city", "")).lower()
        
        if h_city == city_lower:
            h_price = float(h.get("price_per_night", 999999))
            h_rating = float(h.get("stars", 0.0))

           
            if max_budget is not None and h_price > max_budget:
                continue
            
            if min_rating is not None and h_rating < min_rating:
                continue
                
            matching_hotels.append(h)

    if not matching_hotels:
        logger.info(f"No hotels found in {destination} matching criteria.")
        return {
            "status": "success",
            "message": f"No hotels found in {destination} matching your budget and rating criteria.",
            "recommendations": {},
            "results": []
        }

    #Categorize & Rank Recommendations
    try:
        cheapest_hotel = min(matching_hotels, key=lambda x: float(x.get("price_per_night", 999999)))
        highest_rated_hotel = max(matching_hotels, key=lambda x: float(x.get("stars", 0.0)))
        best_value_hotel = max(matching_hotels, key=_calculate_value_score) # _calculate_value_score, Not calling the funtion here. The function itself is passed, thats why no parenthesis

        #Add explanations
        recommendations = {
            "cheapest": {
                **cheapest_hotel, # Spread operator: takes the whole dictionary of cheapest_hotel and adds it here
                "recommendation_reason": _format_hotel_explanation(cheapest_hotel, "cheapest")
            },
            "highest_rated": {
                **highest_rated_hotel,
                "recommendation_reason": _format_hotel_explanation(highest_rated_hotel, "highest_rated")
            },
            "best_value": {
                **best_value_hotel,
                "recommendation_reason": _format_hotel_explanation(best_value_hotel, "best_value")
            }
        }
    except Exception as e:
        logger.error(f"Error calculating hotel recommendations: {e}")
        recommendations = {}

    logger.info(f"Successfully processed {len(matching_hotels)} hotels in {destination}.")

    return {
        "status": "success",
        "message": f"Found {len(matching_hotels)} hotel(s) matching your criteria.",
        "recommendations": recommendations,
        "results": matching_hotels
    }
