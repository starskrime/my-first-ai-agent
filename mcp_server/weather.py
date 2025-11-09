"""
Weather tools for MCP Server
"""

import os
import requests
from datetime import datetime

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "")


def _get_coordinates(location: str) -> dict | None:
    """Get latitude and longitude for a location using OpenWeatherMap Geocoding API.

    Args:
        location: City name or location string

    Returns:
        Dictionary with lat, lon, and name, or None if not found
    """
    if not OPENWEATHER_API_KEY:
        return None

    url = "http://api.openweathermap.org/geo/1.0/direct"
    params = {
        "q": location,
        "limit": 1,
        "appid": OPENWEATHER_API_KEY
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if data:
            return {
                "lat": data[0]["lat"],
                "lon": data[0]["lon"],
                "name": data[0].get("name", location)
            }
    except Exception as e:
        print(f"Error getting coordinates: {e}")

    return None


def _fetch_weather_data(lat: float, lon: float) -> dict | None:
    """Fetch weather forecast data from OpenWeatherMap API.

    Args:
        lat: Latitude
        lon: Longitude

    Returns:
        Weather forecast data or None if error
    """
    url = "http://api.openweathermap.org/data/2.5/forecast"
    params = {
        "lat": lat,
        "lon": lon,
        "appid": OPENWEATHER_API_KEY,
        "units": "metric"
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching weather data: {e}")
        return None


def _format_current_conditions(forecast_item: dict) -> str:
    """Format current weather conditions.

    Args:
        forecast_item: First item from forecast list

    Returns:
        Formatted current conditions string
    """
    temp = forecast_item["main"]["temp"]
    feels_like = forecast_item["main"]["feels_like"]
    humidity = forecast_item["main"]["humidity"]
    description = forecast_item["weather"][0]["description"].title()
    wind_speed = forecast_item["wind"]["speed"]

    result = "📍 Current Conditions:\n"
    result += f"   Temperature: {temp}°C (feels like {feels_like}°C)\n"
    result += f"   Conditions: {description}\n"
    result += f"   Humidity: {humidity}%\n"
    result += f"   Wind Speed: {wind_speed} m/s\n"

    return result


def _format_5day_forecast(forecast_list: list) -> str:
    """Format 5-day forecast summary.

    Args:
        forecast_list: List of forecast items

    Returns:
        Formatted 5-day forecast string
    """
    result = "📅 5-Day Forecast:\n"
    seen_dates = set()

    for item in forecast_list:
        date_str = datetime.fromtimestamp(item["dt"]).strftime("%Y-%m-%d")

        if date_str not in seen_dates:
            seen_dates.add(date_str)
            date_display = datetime.fromtimestamp(item["dt"]).strftime("%a, %b %d")
            temp_day = item["main"]["temp"]
            desc = item["weather"][0]["description"].title()
            result += f"   {date_display}: {temp_day}°C - {desc}\n"

            if len(seen_dates) >= 5:
                break

    return result


def get_weather(location: str) -> str:
    """Get current weather and 5-day forecast for a location.

    Includes temperature, conditions, humidity, and wind speed.

    Args:
        location: City name or 'City, Country Code' (e.g., 'Paris', 'Tokyo, JP', 'New York, US')

    Returns:
        Formatted weather forecast string
    """
    # Validate API key
    if not OPENWEATHER_API_KEY:
        return "❌ OpenWeatherMap API key not configured. Please add OPENWEATHER_API_KEY to your .env file."

    # Get coordinates
    coords = _get_coordinates(location)
    if not coords:
        return f"❌ Could not find location: {location}. Please check the spelling or try a different format (e.g., 'Paris, FR')."

    # Fetch weather data
    weather_data = _fetch_weather_data(coords["lat"], coords["lon"])
    if not weather_data:
        return "❌ Error fetching weather data. Please try again later."

    # Build response
    city_name = coords["name"]
    result = f"🌤️ Weather Forecast for {city_name}\n\n"
    result += _format_current_conditions(weather_data["list"][0])
    result += "\n"
    result += _format_5day_forecast(weather_data["list"])

    return result
