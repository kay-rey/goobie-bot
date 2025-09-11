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

        # Use search API instead of direct lookup due to TheSportsDB API issue
        # The direct lookup with ID 134153 returns Arsenal instead of LA Galaxy
        search_url = "https://www.thesportsdb.com/api/v1/json/123/searchteams.php"
        search_params = {"t": "LA Galaxy"}

        data = await get_json(search_url, params=search_params)
        logger.info(f"TheSportsDB search response status: {200 if data else 'Failed'}")
        if data:
            logger.debug(f"Search results: {data}")

        if data and data.get("teams") and len(data["teams"]) > 0:
            # Find the correct LA Galaxy team
            for team in data["teams"]:
                if (
                    team.get("strTeam", "").lower() == "la galaxy"
                    and "mls" in team.get("strLeague", "").lower()
                ):
                    logger.info(
                        f"Found LA Galaxy team: {team.get('strTeam')} with ID: {team.get('idTeam')}"
                    )
                    # Cache the result
                    await set_cached(cache_key, team, "team_metadata")
                    return team

        # Fallback: Create LA Galaxy data with correct logo URL
        logger.warning(
            "Could not find LA Galaxy team data from API, using fallback data"
        )
        fallback_team = {
            "idTeam": "134153",
            "strTeam": "LA Galaxy",
            "strLeague": "American Major League Soccer",
            "strSport": "Soccer",
            "strBadge": "https://r2.thesportsdb.com/images/media/team/badge/ysyysr1420227188.png",
            "strLogo": "https://r2.thesportsdb.com/images/media/team/logo/ysyysr1420227188.png",
            "strStadium": "Dignity Health Sports Park",
            "strStadiumThumb": "https://www.thesportsdb.com/images/media/venue/thumb/15529.jpg",
            "strEquipment": "https://www.thesportsdb.com/images/media/team/equipment/ysyysr1420227188.png",
        }

        # Cache the fallback result
        await set_cached(cache_key, fallback_team, "team_metadata")
        return fallback_team

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

        # Special handling for LA teams with hardcoded logos for reliability
        la_team_logos = {
            "134153": {  # LA Galaxy
                "logo": "https://r2.thesportsdb.com/images/media/team/badge/ysyysr1420227188.png",
                "logo_small": "https://r2.thesportsdb.com/images/media/team/badge/ysyysr1420227188.png/small",
                "jersey": "https://www.thesportsdb.com/images/media/team/equipment/ysyysr1420227188.png",
                "stadium": "Dignity Health Sports Park",
                "stadium_thumb": "https://www.thesportsdb.com/images/media/venue/thumb/15529.jpg",
                "stadium_thumb_small": "https://www.thesportsdb.com/images/media/venue/thumb/15529.jpg/small",
            },
            "1416": {  # Los Angeles Dodgers
                "logo": "https://a.espncdn.com/i/teamlogos/mlb/500/19.png",
                "logo_small": "https://a.espncdn.com/i/teamlogos/mlb/500/19.png",
                "jersey": "https://a.espncdn.com/i/teamlogos/mlb/500/19.png",
                "stadium": "Dodger Stadium",
                "stadium_thumb": "https://a.espncdn.com/i/teamlogos/mlb/500/19.png",
                "stadium_thumb_small": "https://a.espncdn.com/i/teamlogos/mlb/500/19.png",
            },
            "134154": {  # Los Angeles Lakers
                "logo": "https://a.espncdn.com/i/teamlogos/nba/500/13.png",
                "logo_small": "https://a.espncdn.com/i/teamlogos/nba/500/13.png",
                "jersey": "https://a.espncdn.com/i/teamlogos/nba/500/13.png",
                "stadium": "Crypto.com Arena",
                "stadium_thumb": "https://a.espncdn.com/i/teamlogos/nba/500/13.png",
                "stadium_thumb_small": "https://a.espncdn.com/i/teamlogos/nba/500/13.png",
            },
            "135907": {  # Los Angeles Rams
                "logo": "https://a.espncdn.com/i/teamlogos/nfl/500/14.png",
                "logo_small": "https://a.espncdn.com/i/teamlogos/nfl/500/14.png",
                "jersey": "https://a.espncdn.com/i/teamlogos/nfl/500/14.png",
                "stadium": "SoFi Stadium",
                "stadium_thumb": "https://a.espncdn.com/i/teamlogos/nfl/500/14.png",
                "stadium_thumb_small": "https://a.espncdn.com/i/teamlogos/nfl/500/14.png",
            },
            "134852": {  # Los Angeles Kings
                "logo": "https://a.espncdn.com/i/teamlogos/nhl/500/8.png",
                "logo_small": "https://a.espncdn.com/i/teamlogos/nhl/500/8.png",
                "jersey": "https://a.espncdn.com/i/teamlogos/nhl/500/8.png",
                "stadium": "Crypto.com Arena",
                "stadium_thumb": "https://a.espncdn.com/i/teamlogos/nhl/500/8.png",
                "stadium_thumb_small": "https://a.espncdn.com/i/teamlogos/nhl/500/8.png",
            },
        }

        if team_id in la_team_logos:
            team_name = {
                "134153": "LA Galaxy",
                "1416": "Los Angeles Dodgers",
                "134154": "Los Angeles Lakers",
                "135907": "Los Angeles Rams",
                "134852": "Los Angeles Kings",
            }[team_id]

            logger.info(f"Using hardcoded logos for {team_name} (ID: {team_id})")
            logos = la_team_logos[team_id]
            # Cache the result
            await set_cached(cache_key, logos, "team_logos")
            return logos

        # Use direct lookup with team ID for other teams
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
    # Log team data structure for debugging
    logger.debug(f"Team data keys: {list(team.keys())}")
    logger.debug(f"Team data sample: {dict(list(team.items())[:3])}...")

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

        # Check cache first
        cache_key = team_metadata_key("dodgers")
        cached_result = await get_cached(cache_key)
        if cached_result is not None:
            logger.info("Returning cached Dodgers team data")
            return cached_result

        # Use hardcoded data for reliability
        logger.info("Using hardcoded Dodgers team data")
        dodgers_data = {
            "idTeam": "1416",
            "strTeam": "Los Angeles Dodgers",
            "strLeague": "Major League Baseball",
            "strSport": "Baseball",
            "strBadge": "https://a.espncdn.com/i/teamlogos/mlb/500/19.png",
            "strLogo": "https://a.espncdn.com/i/teamlogos/mlb/500/19.png",
            "strStadium": "Dodger Stadium",
            "strStadiumThumb": "https://a.espncdn.com/i/teamlogos/mlb/500/19.png",
            "strEquipment": "https://a.espncdn.com/i/teamlogos/mlb/500/19.png",
        }

        # Cache the result
        await set_cached(cache_key, dodgers_data, "team_metadata")
        return dodgers_data

    except Exception as e:
        logger.error(f"Error fetching Dodgers team data: {e}")
        return None


async def get_lakers_team_data():
    """Get Los Angeles Lakers team data from TheSportsDB"""
    try:
        logger.info("Fetching Los Angeles Lakers team data...")

        # Check cache first
        cache_key = team_metadata_key("lakers")
        cached_result = await get_cached(cache_key)
        if cached_result is not None:
            logger.info("Returning cached Lakers team data")
            return cached_result

        # Use hardcoded data for reliability
        logger.info("Using hardcoded Lakers team data")
        lakers_data = {
            "idTeam": "134154",
            "strTeam": "Los Angeles Lakers",
            "strLeague": "National Basketball Association",
            "strSport": "Basketball",
            "strBadge": "https://a.espncdn.com/i/teamlogos/nba/500/13.png",
            "strLogo": "https://a.espncdn.com/i/teamlogos/nba/500/13.png",
            "strStadium": "Crypto.com Arena",
            "strStadiumThumb": "https://a.espncdn.com/i/teamlogos/nba/500/13.png",
            "strEquipment": "https://a.espncdn.com/i/teamlogos/nba/500/13.png",
        }

        # Cache the result
        await set_cached(cache_key, lakers_data, "team_metadata")
        return lakers_data

    except Exception as e:
        logger.error(f"Error fetching Lakers team data: {e}")
        return None


async def get_rams_team_data():
    """Get Los Angeles Rams team data from TheSportsDB"""
    try:
        logger.info("Fetching Los Angeles Rams team data...")

        # Check cache first
        cache_key = team_metadata_key("rams")
        cached_result = await get_cached(cache_key)
        if cached_result is not None:
            logger.info("Returning cached Rams team data")
            return cached_result

        # Use hardcoded data for reliability
        logger.info("Using hardcoded Rams team data")
        rams_data = {
            "idTeam": "135907",
            "strTeam": "Los Angeles Rams",
            "strLeague": "National Football League",
            "strSport": "American Football",
            "strBadge": "https://a.espncdn.com/i/teamlogos/nfl/500/14.png",
            "strLogo": "https://a.espncdn.com/i/teamlogos/nfl/500/14.png",
            "strStadium": "SoFi Stadium",
            "strStadiumThumb": "https://a.espncdn.com/i/teamlogos/nfl/500/14.png",
            "strEquipment": "https://a.espncdn.com/i/teamlogos/nfl/500/14.png",
        }

        # Cache the result
        await set_cached(cache_key, rams_data, "team_metadata")
        return rams_data

    except Exception as e:
        logger.error(f"Error fetching Rams team data: {e}")
        return None


async def get_kings_team_data():
    """Get Los Angeles Kings team data from TheSportsDB"""
    try:
        logger.info("Fetching Los Angeles Kings team data...")

        # Check cache first
        cache_key = team_metadata_key("kings")
        cached_result = await get_cached(cache_key)
        if cached_result is not None:
            logger.info("Returning cached Kings team data")
            return cached_result

        # Use hardcoded data for reliability
        logger.info("Using hardcoded Kings team data")
        kings_data = {
            "idTeam": "134852",
            "strTeam": "Los Angeles Kings",
            "strLeague": "National Hockey League",
            "strSport": "Ice Hockey",
            "strBadge": "https://a.espncdn.com/i/teamlogos/nhl/500/8.png",
            "strLogo": "https://a.espncdn.com/i/teamlogos/nhl/500/8.png",
            "strStadium": "Crypto.com Arena",
            "strStadiumThumb": "https://a.espncdn.com/i/teamlogos/nhl/500/8.png",
            "strEquipment": "https://a.espncdn.com/i/teamlogos/nhl/500/8.png",
        }

        # Cache the result
        await set_cached(cache_key, kings_data, "team_metadata")
        return kings_data

    except Exception as e:
        logger.error(f"Error fetching Kings team data: {e}")
        return None
