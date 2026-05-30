"""
Budget Tool module for the Agentic AI Travel Planning Assistant.
"""

from typing import Any, Dict, Optional

from langchain.tools import tool
import logging

logger = logging.getLogger(__name__)


def _calculate_totals(
    flight_cost: float,
    hotel_per_night: float,
    food_per_day: float,
    transport_per_day: float,
    activity_budget: float,
    days: int
) -> Dict[str, float]:
    hotel_total = hotel_per_night * days
    food_total = food_per_day * days
    transport_total = transport_per_day * days
    
    total_cost = flight_cost + hotel_total + food_total + transport_total + activity_budget
    
    return {
        "flight": flight_cost,
        "hotel": hotel_total,
        "food": food_total,
        "transportation": transport_total,
        "activities": activity_budget,
        "total": total_cost
    }



@tool
def calculate_trip_budget(
    flight_cost: float,
    hotel_per_night: float,
    food_per_day: float,
    transport_per_day: float,
    activity_budget: float,
    days: int,
    target_budget: Optional[float] = None
) -> Dict[str, Any]:
    """
    Calculate the total trip budget, break it down by category, and provide cost-saving recommendations.
    
    Args:
        flight_cost: Total cost for round-trip flights.
        hotel_per_night: Average cost of the hotel per night.
        food_per_day: Estimated cost for food and dining per day.
        transport_per_day: Estimated cost for local transportation per day.
        activity_budget: Total budget allocated for all activities and tours.
        days: Total duration of the trip in days.
        target_budget: Optional upper limit for the entire trip.
        
    Returns:
        A structured JSON response with the breakdown.
    """
    logger.info(f"Tool executed: calculate_trip_budget for {days} days.")
    
    #Validation
    if days <= 0:
        return {"status": "error", "message": "Trip duration must be at least 1 day."}
        
    if any(val < 0 for val in [flight_cost, hotel_per_night, food_per_day, transport_per_day, activity_budget]):
        return {"status": "error", "message": "Costs cannot be negative numbers."}

    try:
        #Calculation
        totals = _calculate_totals(
            flight_cost=flight_cost,
            hotel_per_night=hotel_per_night,
            food_per_day=food_per_day,
            transport_per_day=transport_per_day,
            activity_budget=activity_budget,
            days=days
        )


        budget_status = "within budget" if target_budget is None or totals["total"] <= target_budget else "over budget"
        
        logger.info(f"Budget calculated successfully. Total: ₹{totals['total']:.2f}")
        
        return {
            "status": "success",
            "message": "Trip budget calculated successfully.",
            "budget_status": budget_status,
            "target_budget": target_budget,
            "breakdown": {
                "flight_total": totals["flight"],
                "hotel_total": totals["hotel"],
                "food_total": totals["food"],
                "transportation_total": totals["transportation"],
                "activities_total": totals["activities"],
                "grand_total": totals["total"]
            }
        }
        
    except Exception as e:
        logger.error(f"Error calculating trip budget: {e}")
        return {"status": "error", "message": "An unexpected error occurred during budget calculation."}
