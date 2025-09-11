"""
TheSportsDB Venues API module for goobie-bot
Handles all TheSportsDB API calls related to venue information and images
"""

import logging
from api.http_client import get_json

logger = logging.getLogger(__name__)


async def search_venue_logos(venue_name):
    """Search TheSportsDB for venue logos"""
    try:
        search_url = "https://www.thesportsdb.com/api/v1/json/123/searchvenues.php"
        search_params = {"t": venue_name}

        data = await get_json(search_url, params=search_params)
        if data and data.get("venues"):
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
