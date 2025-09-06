"""
TheSportsDB Venues API module for goobie-bot
Handles all TheSportsDB API calls related to venue information and images
"""

import logging
import requests

logger = logging.getLogger(__name__)


async def search_venue_logos(venue_name):
    """Search TheSportsDB for venue logos"""
    try:
        search_url = "https://www.thesportsdb.com/api/v1/json/123/searchvenues.php"
        search_params = {"t": venue_name}

        response = requests.get(search_url, params=search_params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get("venues"):
                for venue in data["venues"]:
                    if venue_name.lower() in venue.get("strVenue", "").lower():
                        return {
                            "venue_name": venue.get("strVenue", ""),
                            "venue_thumb": venue.get("strVenueThumb", ""),
                            "venue_image": venue.get("strVenueImage", ""),
                        }
        return {}
    except Exception as e:
        logger.error(f"Error searching venue logos for {venue_name}: {e}")
        return {}
