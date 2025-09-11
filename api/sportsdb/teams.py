"""
TheSportsDB Teams API module for goobie-bot
Handles all TheSportsDB API calls related to team data and logos
"""

import logging
from api.http_client import get_json
from api.cache import (
    get_cached,
    set_cached,
    team_logos_key,
    team_logos_by_name_key,
    team_metadata_key,
)

logger = logging.getLogger(__name__)


async def get_galaxy_team_data():
    """Get LA Galaxy team data from TheSportsDB"""
    try:
        logger.info("Fetching LA Galaxy team data...")

        # Check cache first
        cache_key = team_metadata_key("galaxy")
        cached_result = await get_cached(cache_key)
        if cached_result is not None:
            logger.info("Returning cached Galaxy team data")
            return cached_result

        # Use direct lookup with team ID
        lookup_url = "https://www.thesportsdb.com/api/v1/json/123/lookupteam.php"
        lookup_params = {"id": "134153"}

        data = await get_json(lookup_url, params=lookup_params)
        logger.info(f"TheSportsDB lookup response status: {200 if data else 'Failed'}")
        logger.info(f"Lookup results: {data}")

        if data and data.get("teams") and len(data["teams"]) > 0:
            team = data["teams"][0]
            logger.info(
                f"Found LA Galaxy team: {team.get('strTeam')} with ID: {team.get('idTeam')}"
            )
            # Cache the result
            await set_cached(cache_key, team, "team_metadata")
            return team

        logger.warning("Could not find LA Galaxy team data")
        return None

    except Exception as e:
        logger.error(f"Error fetching team data: {e}")
        return None


async def get_team_logos(team_id):
    """Get team logos from TheSportsDB"""
    try:
        logger.info(f"Attempting to get logos for team ID: {team_id}")

        # Check cache first
        cache_key = team_logos_key(team_id)
        cached_result = await get_cached(cache_key)
        if cached_result is not None:
            logger.info(f"Returning cached logos for team ID: {team_id}")
            return cached_result

        # Use direct lookup with team ID
        lookup_url = "https://www.thesportsdb.com/api/v1/json/123/lookupteam.php"
        lookup_params = {"id": team_id}

        data = await get_json(lookup_url, params=lookup_params)
        logger.info(f"TheSportsDB lookup response status: {200 if data else 'Failed'}")

        # Handle rate limiting - aiohttp wrapper handles this
        if not data:
            logger.warning(
                "Rate limited by TheSportsDB API (429). Free tier allows 30 requests per minute."
            )
            return {}

        if data and data.get("teams") and len(data["teams"]) > 0:
            team = data["teams"][0]
            logger.info(
                f"Lookup found team: {team.get('strTeam')} (ID: {team.get('idTeam')})"
            )
            logos = extract_logos_from_team(team)
            # Cache the result
            await set_cached(cache_key, logos, "team_logos")
            return logos

        logger.warning(f"Could not find team data for logos with ID: {team_id}")
        return {}

    except Exception as e:
        logger.error(f"Error getting team logos: {e}")
        return {}


def extract_logos_from_team(team):
    """Extract logos from team data using actual SportsDB URLs"""
    # Log all available fields for debugging
    logger.info(f"Team data keys: {list(team.keys())}")
    logger.info(f"Full team data: {team}")

    # Get the actual logo URLs from the team data
    # The search API actually returns the logo URLs in strBadge and strLogo fields
    base_logo = team.get("strBadge", "")

    # Try alternative logo fields if the main one is empty
    if not base_logo:
        base_logo = team.get("strLogo", "") or team.get("strBanner", "")

    # Get stadium information
    stadium_name = team.get("strStadium", "")
    stadium_thumb = team.get("strStadiumThumb", "")

    # If no stadium thumb from API, try to construct using venue ID
    if not stadium_thumb:
        venue_id = team.get("idVenue", "")
        if venue_id:
            stadium_thumb = (
                f"https://www.thesportsdb.com/images/media/venue/thumb/{venue_id}.jpg"
            )
            logger.info(
                f"Constructed stadium thumb URL using venue ID {venue_id}: {stadium_thumb}"
            )

    # Create logos dictionary using actual SportsDB URLs
    # Reference: https://www.thesportsdb.com/team/134153-la-galaxy
    logos = {
        "logo": base_logo,
        "logo_small": f"{base_logo}/small" if base_logo else "",
        "jersey": team.get("strEquipment", ""),  # Equipment is the jersey image
        "stadium": stadium_name,
        "stadium_thumb": stadium_thumb,
        "stadium_thumb_small": f"{stadium_thumb}/small" if stadium_thumb else "",
    }

    # Log the actual URLs from SportsDB
    logger.info(f"Using actual SportsDB URLs: {logos}")

    return logos


async def search_team_logos(team_name):
    """Search TheSportsDB for team logos"""
    try:
        search_url = "https://www.thesportsdb.com/api/v1/json/123/searchteams.php"
        search_params = {"t": team_name}

        data = await get_json(search_url, params=search_params)
        if data and data.get("teams"):
            for team in data["teams"]:
                # Look for exact or close match
                if team_name.lower() in team.get("strTeam", "").lower():
                    return extract_logos_from_team(team)
        return {}
    except Exception as e:
        logger.error(f"Error searching team logos for {team_name}: {e}")
        return {}


async def test_logo_url(url):
    """Test if a logo URL is accessible"""
    try:
        from api.http_client import check_url_exists

        return await check_url_exists(url)
    except Exception as e:
        logger.error(f"Error testing logo URL {url}: {e}")
        return False


async def get_dodgers_team_data():
    """Get Los Angeles Dodgers team data from TheSportsDB"""
    try:
        logger.info("Fetching Los Angeles Dodgers team data...")

        # Use direct lookup with team ID
        lookup_url = "https://www.thesportsdb.com/api/v1/json/123/lookupteam.php"
        lookup_params = {"id": "1416"}

        data = await get_json(lookup_url, params=lookup_params)
        logger.info(f"TheSportsDB lookup response status: {200 if data else 'Failed'}")
        logger.info(f"Lookup results: {data}")

        if data and data.get("teams") and len(data["teams"]) > 0:
            team = data["teams"][0]
            logger.info(
                f"Found Los Angeles Dodgers team: {team.get('strTeam')} with ID: {team.get('idTeam')}"
            )
            return team

        logger.warning("Could not find Los Angeles Dodgers team data")
        return None

    except Exception as e:
        logger.error(f"Error fetching Dodgers team data: {e}")
        return None


async def get_lakers_team_data():
    """Get Los Angeles Lakers team data from TheSportsDB"""
    try:
        logger.info("Fetching Los Angeles Lakers team data...")

        # Use direct lookup with team ID
        lookup_url = "https://www.thesportsdb.com/api/v1/json/123/lookupteam.php"
        lookup_params = {"id": "134154"}

        data = await get_json(lookup_url, params=lookup_params)
        logger.info(f"TheSportsDB lookup response status: {200 if data else 'Failed'}")
        logger.info(f"Lookup results: {data}")

        if data and data.get("teams") and len(data["teams"]) > 0:
            team = data["teams"][0]
            logger.info(
                f"Found Los Angeles Lakers team: {team.get('strTeam')} with ID: {team.get('idTeam')}"
            )
            return team

        logger.warning("Could not find Los Angeles Lakers team data")
        return None

    except Exception as e:
        logger.error(f"Error fetching Lakers team data: {e}")
        return None


async def get_rams_team_data():
    """Get Los Angeles Rams team data from TheSportsDB"""
    try:
        logger.info("Fetching Los Angeles Rams team data...")

        # Use direct lookup with team ID
        lookup_url = "https://www.thesportsdb.com/api/v1/json/123/lookupteam.php"
        lookup_params = {"id": "135907"}

        data = await get_json(lookup_url, params=lookup_params)
        logger.info(f"TheSportsDB lookup response status: {200 if data else 'Failed'}")
        logger.info(f"Lookup results: {data}")

        if data and data.get("teams") and len(data["teams"]) > 0:
            team = data["teams"][0]
            logger.info(
                f"Found Los Angeles Rams team: {team.get('strTeam')} with ID: {team.get('idTeam')}"
            )
            return team

        logger.warning("Could not find Los Angeles Rams team data")
        return None

    except Exception as e:
        logger.error(f"Error fetching Rams team data: {e}")
        return None


async def get_kings_team_data():
    """Get Los Angeles Kings team data from TheSportsDB"""
    try:
        logger.info("Fetching Los Angeles Kings team data...")

        # Use direct lookup with team ID
        lookup_url = "https://www.thesportsdb.com/api/v1/json/123/lookupteam.php"
        lookup_params = {"id": "134852"}

        data = await get_json(lookup_url, params=lookup_params)
        logger.info(f"TheSportsDB lookup response status: {200 if data else 'Failed'}")
        logger.info(f"Lookup results: {data}")

        if data and data.get("teams") and len(data["teams"]) > 0:
            team = data["teams"][0]
            logger.info(
                f"Found Los Angeles Kings team: {team.get('strTeam')} with ID: {team.get('idTeam')}"
            )
            return team

        logger.warning("Could not find Los Angeles Kings team data")
        return None

    except Exception as e:
        logger.error(f"Error fetching Kings team data: {e}")
        return None
