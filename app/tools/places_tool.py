"""
Places Tool module for the Agentic AI Travel Planning Assistant.
"""

from typing import Any, Dict, Optional

from langchain.tools import tool
import logging

logger = logging.getLogger(__name__)

from app.services.data_loader import get_places_data


def _is_family_friendly(place: Dict[str, Any]) -> bool:
    if place.get("family_friendly") is True:
        return True
    
    tags = [str(tag).lower() for tag in place.get("tags", [])]
    return "family" in tags or "kids" in tags or "family-friendly" in tags


def _is_budget_friendly(place: Dict[str, Any], max_budget_threshold: float = 20.0) -> bool:
    price = float(place.get("price", 0.0))
    return price <= max_budget_threshold



@tool
def search_places(
    destination: str,
    place_type: Optional[str] = None,
    min_rating: Optional[float] = None,
    max_price: Optional[float] = None,
    require_family_friendly: bool = False,
    limit: int = 10
) -> Dict[str, Any]:
    """
    Search for places, attractions, and landmarks in a destination to build an itinerary.
    
    Args:
        destination: The destination city to search.
        place_type: Optional filter for type (e.g., 'museum', 'park', 'restaurant').
        min_rating: Minimum acceptable rating out of 5.
        max_price: Maximum entry fee or cost.
        require_family_friendly: If True, only returns family-friendly locations.
        limit: Maximum number of general results to return (useful for itinerary building).
        
    Returns:
        Structured JSON response with categorized recommendations and a general list of places.
    """
    logger.info(f"Tool executed: search_places in '{destination}' (type: {place_type})")
    
    all_places = get_places_data()
    if not all_places or not isinstance(all_places, list):
        logger.error("Failed to load places data or data is empty.")
        return {
            "status": "error",
            "message": "Places data is currently unavailable.",
            "recommendations": {},
            "results": []
        }
        
    #Filter Places by city, type etc...
    matching_places = []
    city_lower = destination.lower()
    
    for p in all_places:
        p_city = str(p.get("city", "")).lower()
        if city_lower not in p_city:
            continue

        if place_type:
            p_type = str(p.get("type", "")).lower()
            if place_type.lower() not in p_type:
                continue
 
        if min_rating:
            p_rating = float(p.get("rating", 0))
            if p_rating < min_rating:
                continue
     
        if max_price is not None:
            p_price = float(p.get("price", 0))
            if p_price > max_price:
                continue
       
        if require_family_friendly and not _is_family_friendly(p):
            continue
            
        matching_places.append(p)
        
    if not matching_places:
        logger.info(f"No places found in {destination} matching criteria.")
        return {
            "status": "success",
            "message": f"No places found in {destination} matching your criteria.",
            "recommendations": {},
            "results": []
        }
        
    #Categorize and Recommend - Best family friendly, best budget friendly, etc...
    recommendations = {}
    
    try:
        top = max(matching_places, key=lambda x: float(x.get("rating", 0)))
        recommendations["top_attraction"] = top
            
        family_places = [p for p in matching_places if _is_family_friendly(p)]
        if family_places:
            best_family = max(family_places, key=lambda x: float(x.get("rating", 0)))
            recommendations["best_family_friendly"] = best_family
            
        budget_places = [p for p in matching_places if _is_budget_friendly(p)]
        if budget_places:
            best_budget = max(budget_places, key=lambda x: float(x.get("rating", 0)))
            recommendations["best_budget_friendly"] = best_budget
            
    except Exception as e:
        logger.error(f"Error calculating place recommendations: {e}")
        
    #Sort general results by rating and apply limit
    try:
        sorted_results = sorted(matching_places, key=lambda x: float(x.get("rating", 0)), reverse=True)
        limited_results = sorted_results[:limit]
    except Exception as e:
        logger.error(f"Error sorting places: {e}")
        limited_results = matching_places[:limit]
        
    logger.info(f"Successfully processed {len(matching_places)} places in {destination}.")
    
    return {
        "status": "success",
        "message": f"Found {len(matching_places)} places in {destination}. Returning top {len(limited_results)} results.",
        "recommendations": recommendations,
        "results": limited_results
    }
