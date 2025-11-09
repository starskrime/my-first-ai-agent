"""
News tools for MCP Server
"""

import os
import requests
from datetime import datetime

NEWS_API_KEY = os.getenv("NEWS_API_KEY", "")

# Country code mapping for news queries
COUNTRY_MAP = {
    "france": "fr", "paris": "fr",
    "japan": "jp", "tokyo": "jp",
    "usa": "us", "united states": "us", "new york": "us", "san francisco": "us",
    "uk": "gb", "united kingdom": "gb", "london": "gb",
    "germany": "de", "berlin": "de",
    "italy": "it", "rome": "it",
    "spain": "es", "madrid": "es", "barcelona": "es",
    "canada": "ca", "toronto": "ca",
    "australia": "au", "sydney": "au",
}


def _get_country_code(location: str) -> str | None:
    """Get country code from location string.

    Args:
        location: Location name (city or country)

    Returns:
        ISO country code or None if not found
    """
    return COUNTRY_MAP.get(location.lower())


def _build_news_params(location: str, category: str) -> dict:
    """Build API parameters for news request.

    Args:
        location: Location name
        category: News category

    Returns:
        Dictionary of API parameters
    """
    params = {
        "apiKey": NEWS_API_KEY,
        "pageSize": 5,
        "category": category
    }

    country_code = _get_country_code(location)

    if country_code:
        params["country"] = country_code
    else:
        params["q"] = location

    return params


def _fetch_news_data(params: dict) -> dict | None:
    """Fetch news data from NewsAPI.

    Args:
        params: API request parameters

    Returns:
        News data or None if error
    """
    url = "https://newsapi.org/v2/top-headlines"

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if data["status"] != "ok":
            print(f"NewsAPI error: {data.get('message', 'Unknown error')}")
            return None

        return data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching news: {e}")
        return None


def _format_date(published_at: str) -> str:
    """Format publication date.

    Args:
        published_at: ISO format date string

    Returns:
        Formatted date string
    """
    if not published_at:
        return ""

    try:
        pub_date = datetime.fromisoformat(published_at.replace("Z", "+00:00"))
        return pub_date.strftime("%b %d, %Y")
    except Exception:
        return published_at


def _format_article(index: int, article: dict) -> str:
    """Format a single news article.

    Args:
        index: Article number (1-based)
        article: Article data dictionary

    Returns:
        Formatted article string
    """
    title = article.get("title", "No title")
    source = article.get("source", {}).get("name", "Unknown source")
    published = _format_date(article.get("publishedAt", ""))
    description = article.get("description", "")

    result = f"{index}. {title}\n"
    result += f"   Source: {source} | {published}\n"

    if description:
        truncated = description[:150]
        if len(description) > 150:
            truncated += "..."
        result += f"   {truncated}\n"

    result += "\n"
    return result


def _format_news_response(location: str, category: str, articles: list) -> str:
    """Format complete news response.

    Args:
        location: Location name
        category: News category
        articles: List of article dictionaries

    Returns:
        Formatted news response string
    """
    result = f"📰 Latest News for {location.title()}\n"

    if category != "general":
        result += f"Category: {category.title()}\n"

    result += "\n"

    for i, article in enumerate(articles[:5], 1):
        result += _format_article(i, article)

    return result


def get_local_news(location: str, category: str = "general") -> str:
    """Get recent news headlines for a specific location or country.

    Helps understand what's currently happening at the destination.

    Args:
        location: Country or city name (e.g., 'France', 'Japan', 'United Kingdom')
        category: News category - general, business, entertainment, health, science, sports, technology

    Returns:
        Formatted news headlines string
    """
    # Validate API key
    if not NEWS_API_KEY:
        return "❌ NewsAPI key not configured. Please add NEWS_API_KEY to your .env file."

    # Build request parameters
    params = _build_news_params(location, category)

    # Fetch news data
    news_data = _fetch_news_data(params)
    if not news_data:
        return f"❌ Error from NewsAPI. Please try again later."

    # Check for articles
    articles = news_data.get("articles", [])
    if not articles:
        return f"📰 No recent news found for {location} in category '{category}'."

    # Format and return response
    return _format_news_response(location, category, articles)
