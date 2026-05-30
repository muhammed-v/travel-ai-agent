"""
Weather Tool module for the Agentic AI Travel Planning Assistant.
Provides a LangChain tool to fetch weather forecasts using the Open-Meteo API.
"""

import time
from typing import Any, Dict

import requests
from langchain.tools import tool
import logging

logger = logging.getLogger(__name__)

# Open-Meteo API endpoint (No API key required)
OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"


def _interpret_wmo_code(code: int) -> str:
    wmo_codes = {
        0: "Clear sky",
        1: "Mainly clear",
        2: "Partly cloudy",
        3: "Overcast",
        45: "Fog",
        48: "Depositing rime fog",
        51: "Light drizzle",
        53: "Moderate drizzle",
        55: "Dense drizzle",
        56: "Light freezing drizzle",
        57: "Dense freezing drizzle",
        61: "Slight rain",
        63: "Moderate rain",
        65: "Heavy rain",
        66: "Light freezing rain",
        67: "Heavy freezing rain",
        71: "Slight snow fall",
        73: "Moderate snow fall",
        75: "Heavy snow fall",
        77: "Snow grains",
        80: "Slight rain showers",
        81: "Moderate rain showers",
        82: "Violent rain showers",
        85: "Slight snow showers",
        86: "Heavy snow showers",
        95: "Thunderstorm",
        96: "Thunderstorm with slight hail",
        99: "Thunderstorm with heavy hail"
    }
    return wmo_codes.get(code, "Unknown conditions")

@tool
def get_weather_forecast(latitude: float, longitude: float, days: int = 7) -> Dict[str, Any]:
    """
    Fetch the weather forecast for a specific location using latitude and longitude.
    
    Args:
        latitude: The latitude of the destination (e.g., 40.7128 for NYC).
        longitude: The longitude of the destination (e.g., -74.0060 for NYC).
        days: Number of days to forecast (default is 7, maximum is 16).
        
    Returns:
        A structured JSON response with daily temperatures, weather conditions, 
        and a travel-friendly summary.
    """
    logger.info(f"Tool executed: get_weather_forecast for lat: {latitude}, lon: {longitude}, days: {days}")
    
    #Validation
    if not (-90 <= latitude <= 90):
        return {"status": "error", "message": "Invalid latitude. Must be between -90 and 90."}
    if not (-180 <= longitude <= 180):
        return {"status": "error", "message": "Invalid longitude. Must be between -180 and 180."}
    if not (1 <= days <= 16):
        days = max(1, min(days, 16))
        logger.warning(f"Days parameter out of bounds. Clamped to {days} days.")

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "daily": ["temperature_2m_max", "temperature_2m_min", "weathercode", "precipitation_probability_max"],
        "timezone": "auto",
        "forecast_days": days
    }
    
    max_retries = 3
    retry_delay = 2.0
    timeout = 10.0

    #Fetching data with retries
    for attempt in range(max_retries):
        try:
            response = requests.get(OPEN_METEO_URL, params=params, timeout=timeout)
            response.raise_for_status()
            
            data = response.json()
            daily_forecast = data.get("daily", {})
            
            if not daily_forecast:
                logger.error("Open-Meteo response did not contain 'daily' data.")
                return {"status": "error", "message": "Weather forecast data format is invalid."}

            #Structuring the output
            dates = daily_forecast.get("time", [])
            max_temps = daily_forecast.get("temperature_2m_max", [])
            min_temps = daily_forecast.get("temperature_2m_min", [])
            weather_codes = daily_forecast.get("weathercode", [])
            precip_probs = daily_forecast.get("precipitation_probability_max", [])
            
            structured_daily = []
            for i in range(len(dates)):
                structured_daily.append({
                    "date": dates[i] if i < len(dates) else "Unknown",
                    "max_temperature_c": max_temps[i] if i < len(max_temps) else None,
                    "min_temperature_c": min_temps[i] if i < len(min_temps) else None,
                    "condition": _interpret_wmo_code(weather_codes[i]) if i < len(weather_codes) else "Unknown",
                    "precipitation_probability": precip_probs[i] if i < len(precip_probs) else None
                })
                
            logger.info("Successfully fetched and processed weather forecast.")
            return {
                "status": "success",
                "message": "Weather forecast retrieved successfully.",
                "daily_forecast": structured_daily
            }
            
        except requests.exceptions.Timeout:
            logger.warning(f"Weather API timeout on attempt {attempt + 1}/{max_retries}.")
        except requests.exceptions.HTTPError as http_err:
            logger.error(f"HTTP error occurred: {http_err}")
            # Do not retry on client errors (4xx)
            if response.status_code < 500:
                break
        except requests.exceptions.RequestException as req_err:
            logger.error(f"Request error occurred: {req_err}")
            
        time.sleep(retry_delay)
        
    return {
        "status": "error",
        "message": "Failed to fetch weather forecast after multiple attempts. Please try again later."
    }
