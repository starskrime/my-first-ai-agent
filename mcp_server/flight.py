"""
Flight search tools for MCP Server
"""

import os
import json
import datetime
import requests


def search_flights(origin: str, destination: str, departure_date: str, return_date: str = None) -> str:
    """
    Search for real airline tickets using Google Flights data via SerpApi.

    Args:
        origin: Departure airport code (e.g., 'JFK', 'LAX', 'ORD')
        destination: Arrival airport code (e.g., 'LAX', 'LHR', 'CDG')
        departure_date: Departure date in YYYY-MM-DD format
        return_date: Optional return date in YYYY-MM-DD format for round-trip

    Returns:
        JSON string with real flight options from Google Flights
    """
    # Get API key from environment
    serpapi_key = os.getenv("SERPAPI_API_KEY")

    if not serpapi_key:
        return json.dumps({
            "error": "SERPAPI_API_KEY not found in environment variables",
            "instructions": "Please add SERPAPI_API_KEY to your .env file. Get a free key at https://serpapi.com"
        })

    try:
        # Validate date format
        datetime.datetime.strptime(departure_date, "%Y-%m-%d")
        if return_date:
            datetime.datetime.strptime(return_date, "%Y-%m-%d")

        # Build API request
        params = {
            "engine": "google_flights",
            "departure_id": origin.upper(),
            "arrival_id": destination.upper(),
            "outbound_date": departure_date,
            "currency": "USD",
            "hl": "en",
            "api_key": serpapi_key
        }

        # Add return date if specified (round trip)
        if return_date:
            params["return_date"] = return_date
            params["type"] = "1"  # Round trip
        else:
            params["type"] = "2"  # One way

        # Make API request
        response = requests.get("https://serpapi.com/search", params=params, timeout=30)
        response.raise_for_status()

        data = response.json()

        # Check for errors
        if "error" in data:
            return json.dumps({
                "error": data["error"],
                "debug_info": f"API returned error. Status code: {response.status_code}"
            }, indent=2)

        # Debug: Check if we have flight data
        if "best_flights" not in data and "other_flights" not in data:
            return json.dumps({
                "error": "No flight data in response",
                "available_keys": list(data.keys()),
                "raw_response_preview": str(data)[:500]
            }, indent=2)

        # Extract flight information
        best_flights = data.get("best_flights", [])
        other_flights = data.get("other_flights", [])
        price_insights = data.get("price_insights", {})

        # Format flight options in a readable way
        formatted_flights = []
        for flight_option in (best_flights + other_flights)[:5]:  # Top 5 options
            flight_info = {
                "price": flight_option.get("price", "N/A"),
                "type": flight_option.get("type", "N/A"),
                "total_duration": flight_option.get("total_duration", "N/A"),
                "legs": []
            }

            for leg in flight_option.get("flights", []):
                flight_info["legs"].append({
                    "airline": leg.get("airline", "Unknown"),
                    "flight_number": leg.get("flight_number", "N/A"),
                    "departure": {
                        "airport": leg.get("departure_airport", {}).get("id", ""),
                        "time": leg.get("departure_airport", {}).get("time", "")
                    },
                    "arrival": {
                        "airport": leg.get("arrival_airport", {}).get("id", ""),
                        "time": leg.get("arrival_airport", {}).get("time", "")
                    },
                    "duration": leg.get("duration", "N/A"),
                    "airplane": leg.get("airplane", "N/A")
                })

            formatted_flights.append(flight_info)

        # Format results
        result = {
            "search_date": datetime.datetime.now().strftime("%Y-%m-%d"),
            "route": f"{origin.upper()} → {destination.upper()}",
            "trip_type": "round-trip" if return_date else "one-way",
            "departure_date": departure_date,
            "return_date": return_date,
            "flights_found": len(formatted_flights),
            "flights": formatted_flights,
            "price_insights": {
                "lowest_price": price_insights.get("lowest_price"),
                "typical_price_range": price_insights.get("typical_price_range", []),
                "price_level": price_insights.get("price_level")
            }
        }

        return json.dumps(result, indent=2)

    except requests.RequestException as e:
        return json.dumps({"error": f"API request failed: {str(e)}"})
    except ValueError as e:
        return json.dumps({"error": f"Invalid date format. Use YYYY-MM-DD: {str(e)}"})
    except Exception as e:
        return json.dumps({"error": f"Unexpected error: {str(e)}"})
