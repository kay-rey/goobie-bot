"""
TheSportsDB Teams API module for goobie-bot
Handles all TheSportsDB API calls related to team data and logos
"""

import logging
import requests

logger = logging.getLogger(__name__)


async def get_galaxy_team_data():
    """Get LA Galaxy team data from TheSportsDB"""
    try:
        logger.info("Fetching LA Galaxy team data...")

        # Search for LA Galaxy team
        search_url = "https://www.thesportsdb.com/api/v1/json/123/searchteams.php"
        search_params = {"t": "LA Galaxy"}

        response = requests.get(search_url, params=search_params, timeout=10)
        logger.info(f"TheSportsDB search response status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            logger.info(f"Search results: {data}")

            if data.get("teams"):
                for team in data["teams"]:
                    # Look for LA Galaxy specifically in MLS
                    if (
                        (
                            "LA Galaxy" in team.get("strTeam", "")
                            or "Los Angeles Galaxy" in team.get("strTeam", "")
                        )
                        and "Soccer" in team.get("strSport", "")
                        and "American Major League Soccer" in team.get("strLeague", "")
                    ):
                        logger.info(
                            f"Found LA Galaxy team: {team.get('strTeam')} with ID: {team.get('idTeam')}"
                        )
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

        # Skip the problematic lookup API and go straight to search
        # The lookup API seems to have issues with LA Galaxy's ID
        logger.info("Using search approach for LA Galaxy logos...")
        search_url = "https://www.thesportsdb.com/api/v1/json/123/searchteams.php"
        search_params = {"t": "LA Galaxy"}

        search_response = requests.get(search_url, params=search_params, timeout=10)
        logger.info(
            f"TheSportsDB search response status: {search_response.status_code}"
        )

        # Handle rate limiting as per TheSportsDB docs
        if search_response.status_code == 429:
            logger.warning(
                "Rate limited by TheSportsDB API (429). Free tier allows 30 requests per minute."
            )
            return {}

        if search_response.status_code == 200:
            search_data = search_response.json()
            if search_data.get("teams"):
                for team in search_data["teams"]:
                    # Look for LA Galaxy specifically in MLS
                    if (
                        (
                            "LA Galaxy" in team.get("strTeam", "")
                            or "Los Angeles Galaxy" in team.get("strTeam", "")
                        )
                        and "Soccer" in team.get("strSport", "")
                        and "American Major League Soccer" in team.get("strLeague", "")
                    ):
                        logger.info(
                            f"Search found correct team: {team.get('strTeam')} (ID: {team.get('idTeam')})"
                        )
                        return extract_logos_from_team(team)

        logger.warning("Could not find LA Galaxy team data for logos")
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

        response = requests.get(search_url, params=search_params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get("teams"):
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
        response = requests.head(url, timeout=5)
        return response.status_code == 200
    except Exception as e:
        logger.error(f"Error testing logo URL {url}: {e}")
        return False


async def get_dodgers_team_data():
    """Get Los Angeles Dodgers team data from TheSportsDB"""
    try:
        logger.info("Fetching Los Angeles Dodgers team data...")

        # Search for Los Angeles Dodgers team
        search_url = "https://www.thesportsdb.com/api/v1/json/123/searchteams.php"
        search_params = {"t": "Los Angeles Dodgers"}

        response = requests.get(search_url, params=search_params, timeout=10)
        logger.info(f"TheSportsDB search response status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            logger.info(f"Search results: {data}")

            if data.get("teams"):
                for team in data["teams"]:
                    # Look for Los Angeles Dodgers specifically in MLB
                    if (
                        "Los Angeles Dodgers" in team.get("strTeam", "")
                        or "Dodgers" in team.get("strTeam", "")
                    ) and "Baseball" in team.get("strSport", ""):
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

        # Search for Los Angeles Lakers team
        search_url = "https://www.thesportsdb.com/api/v1/json/123/searchteams.php"
        search_params = {"t": "Los Angeles Lakers"}

        response = requests.get(search_url, params=search_params, timeout=10)
        logger.info(f"TheSportsDB search response status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            logger.info(f"Search results: {data}")

            if data.get("teams"):
                for team in data["teams"]:
                    # Look for Los Angeles Lakers specifically in NBA
                    if (
                        "Los Angeles Lakers" in team.get("strTeam", "")
                        or "Lakers" in team.get("strTeam", "")
                    ) and "Basketball" in team.get("strSport", ""):
                        logger.info(
                            f"Found Los Angeles Lakers team: {team.get('strTeam')} with ID: {team.get('idTeam')}"
                        )
                        return team

        logger.warning("Could not find Los Angeles Lakers team data")
        return None

    except Exception as e:
        logger.error(f"Error fetching Lakers team data: {e}")
        return None
