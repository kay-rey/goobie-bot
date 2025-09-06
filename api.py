"""
API module for goobie-bot
Handles all external API calls to ESPN and TheSportsDB
"""

import logging
import requests
from datetime import datetime, timezone
import pytz
import discord

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


async def get_galaxy_next_game():
    """Get LA Galaxy's next game from ESPN API"""
    try:
        logger.info("Fetching next game data...")

        # Get current date and 2 weeks from now
        now = datetime.now(timezone.utc)
        future_date = now.replace(day=now.day + 14)

        # Format dates for ESPN API
        start_date = now.strftime("%Y%m%d")
        end_date = future_date.strftime("%Y%m%d")

        logger.info(f"Date range: {start_date} to {end_date}")

        # ESPN API endpoint for LA Galaxy events
        url = f"http://sports.core.api.espn.com/v2/sports/soccer/leagues/usa.1/teams/187/events"
        params = {"dates": f"{start_date}-{end_date}", "limit": 10}

        response = requests.get(url, params=params, timeout=10)
        logger.info(f"ESPN API response status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            logger.info(f"ESPN API data keys: {list(data.keys())}")

            if data.get("items"):
                # Get the first upcoming game
                return data["items"][0]

        logger.warning("No upcoming games found")
        return None

    except Exception as e:
        logger.error(f"Error fetching game data: {e}")
        return None


async def get_galaxy_next_game_extended():
    """Get LA Galaxy's next game with detailed information from ESPN API"""
    try:
        logger.info("Fetching next game data...")

        # Get current date and 2 weeks from now
        now = datetime.now(timezone.utc)
        future_date = now.replace(day=now.day + 14)

        # Format dates for ESPN API
        start_date = now.strftime("%Y%m%d")
        end_date = future_date.strftime("%Y%m%d")

        logger.info(f"Date range: {start_date} to {end_date}")

        # ESPN API endpoint for LA Galaxy events
        url = f"http://sports.core.api.espn.com/v2/sports/soccer/leagues/usa.1/teams/187/events"
        params = {"dates": f"{start_date}-{end_date}", "limit": 10}

        response = requests.get(url, params=params, timeout=10)
        logger.info(f"ESPN API response status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            logger.info(f"ESPN API data keys: {list(data.keys())}")

            if data.get("items"):
                # Find the closest upcoming game
                closest_game = None
                closest_date = None

                for game in data["items"]:
                    if game.get("date"):
                        try:
                            game_date = datetime.fromisoformat(
                                game["date"].replace("Z", "+00:00")
                            )
                            if game_date > now:
                                if closest_date is None or game_date < closest_date:
                                    closest_date = game_date
                                    closest_game = game
                                    logger.info(
                                        f"Found upcoming game on {game_date.strftime('%Y-%m-%d %H:%M')}"
                                    )
                        except Exception as e:
                            logger.warning(
                                f"Error parsing date {game.get('date')}: {e}"
                            )
                            continue

                if closest_game:
                    logger.info(
                        f"Returning closest upcoming game on {closest_date.strftime('%Y-%m-%d %H:%M')}"
                    )
                    return closest_game

        logger.warning("No upcoming games found")
        return None

    except Exception as e:
        logger.error(f"Error fetching game data: {e}")
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
    stadium_thumb = ""

    # Try to get stadium image - we can use the venue ID if available
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


async def get_team_name_from_ref(team_ref):
    """Get team name from ESPN team reference URL"""
    if not team_ref:
        return "TBD"

    try:
        response = requests.get(team_ref, timeout=10)
        if response.status_code == 200:
            team_data = response.json()
            # Try different name fields in order of preference
            return (
                team_data.get("displayName")
                or team_data.get("name")
                or team_data.get("shortDisplayName")
                or team_data.get("abbreviation")
                or "TBD"
            )
    except Exception as e:
        logger.error(f"Error fetching team name from {team_ref}: {e}")

    return "TBD"


async def test_logo_url(url):
    """Test if a logo URL is accessible"""
    try:
        response = requests.head(url, timeout=5)
        return response.status_code == 200
    except Exception as e:
        logger.error(f"Error testing logo URL {url}: {e}")
        return False


async def create_game_embed(game_data, logos):
    """Create a Discord embed for the game data"""
    try:
        logger.info("Creating embed...")
        logger.info(f"Creating embed with logos: {logos}")

        # Create embed
        embed = discord.Embed(
            title="LA Galaxy Next Game",
            color=0x00245D,  # LA Galaxy blue
            timestamp=datetime.now(timezone.utc),
        )

        # Add team logo as thumbnail if available
        if logos.get("logo"):
            embed.set_thumbnail(url=logos["logo"])
            logger.info(f"Setting thumbnail to: {logos['logo']}")
        else:
            logger.warning("No team logo available")

        # Add stadium image if available
        if logos.get("stadium_thumb"):
            embed.set_image(url=logos["stadium_thumb"])
            logger.info(f"Setting image to: {logos['stadium_thumb']}")
        else:
            logger.warning("No stadium image available")

        # Parse game date
        if game_data.get("date"):
            try:
                game_date = datetime.fromisoformat(
                    game_data["date"].replace("Z", "+00:00")
                )

                # Convert to Pacific Time
                pacific_tz = pytz.timezone("America/Los_Angeles")
                game_date_pacific = game_date.astimezone(pacific_tz)

                # Format the date nicely
                formatted_date = game_date_pacific.strftime(
                    "%A, %B %d, %Y at %I:%M %p %Z"
                )
                logger.info(
                    f"Game date: {game_date} (UTC) -> {game_date_pacific} (PDT) -> {formatted_date}"
                )

                embed.add_field(
                    name="📅 Date & Time", value=formatted_date, inline=False
                )
            except Exception as e:
                logger.warning(f"Error parsing date {game_data.get('date')}: {e}")
                embed.add_field(
                    name="📅 Date & Time",
                    value=game_data.get("date", "TBD"),
                    inline=False,
                )

        # Add game name
        if game_data.get("name"):
            embed.add_field(name="⚽ Match", value=game_data["name"], inline=False)

        # Add venue information
        if logos.get("stadium"):
            embed.add_field(name="🏟️ Venue", value=logos["stadium"], inline=True)

        # Add league information
        embed.add_field(name="🏆 Competition", value="Major League Soccer", inline=True)

        # Add footer
        embed.set_footer(text="LA Galaxy Bot • Data from ESPN & TheSportsDB")

        return embed

    except Exception as e:
        logger.error(f"Error creating embed: {e}")
        # Return a basic embed if there's an error
        embed = discord.Embed(
            title="LA Galaxy Next Game",
            description="Error loading game information",
            color=0xFF0000,
        )
        return embed
