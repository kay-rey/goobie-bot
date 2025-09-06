"""
API module for goobie-bot
Handles all external API calls to ESPN and TheSportsDB
"""

import logging
import requests
from datetime import datetime, timedelta
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
        today = datetime.now()
        future_date = today + timedelta(days=14)

        # Format dates for ESPN API
        start_date = today.strftime("%Y%m%d")
        end_date = future_date.strftime("%Y%m%d")

        logger.info(f"Date range: {start_date} to {end_date}")

        # ESPN API endpoint for LA Galaxy events
        url = "http://sports.core.api.espn.com/v2/sports/soccer/leagues/usa.1/teams/187/events"
        params = {"dates": f"{start_date}-{end_date}", "limit": 10}

        response = requests.get(url, params=params, timeout=10)
        logger.info(f"ESPN API response status: {response.status_code}")
        logger.info(f"Date range: {start_date} to {end_date}")

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
        today = datetime.now()
        future_date = today + timedelta(days=14)

        # Format dates for ESPN API
        start_date = today.strftime("%Y%m%d")
        end_date = future_date.strftime("%Y%m%d")

        logger.info(f"Date range: {start_date} to {end_date}")

        # ESPN API endpoint for LA Galaxy events
        url = "http://sports.core.api.espn.com/v2/sports/soccer/leagues/usa.1/teams/187/events"
        params = {"dates": f"{start_date}-{end_date}", "limit": 10}

        response = requests.get(url, params=params, timeout=10)
        logger.info(f"ESPN API response status: {response.status_code}")
        logger.info(f"Date range: {start_date} to {end_date}")

        if response.status_code == 200:
            data = response.json()
            logger.info(f"ESPN API data keys: {list(data.keys())}")
            logger.info(f"ESPN API items count: {len(data.get('items', []))}")

            if data.get("items") and len(data["items"]) > 0:
                # Find the closest upcoming game by following $ref URLs
                upcoming_games = []

                for item in data["items"]:
                    event_ref = item.get("$ref")
                    if event_ref:
                        logger.info(f"Fetching event details from: {event_ref}")
                        event_response = requests.get(event_ref, timeout=10)
                        if event_response.status_code == 200:
                            event_data = event_response.json()
                            event_date_str = event_data.get("date", "")

                            if event_date_str:
                                try:
                                    # Parse the event date (make both timezone-aware)
                                    event_date = datetime.fromisoformat(
                                        event_date_str.replace("Z", "+00:00")
                                    )
                                    # Make today timezone-aware for comparison
                                    today_aware = today.replace(
                                        tzinfo=event_date.tzinfo
                                    )
                                    # Check if the event is in the future
                                    if event_date > today_aware:
                                        logger.info(
                                            f"Found upcoming game on {event_date.strftime('%Y-%m-%d %H:%M')}"
                                        )
                                        upcoming_games.append((event_date, event_data))
                                except Exception as e:
                                    logger.warning(f"Error parsing event date: {e}")
                                    continue

                if upcoming_games:
                    # Sort by date and get the closest upcoming game
                    upcoming_games.sort(key=lambda x: x[0])
                    closest_date, closest_game = upcoming_games[0]
                    logger.info(f"Found next game: {closest_game}")

                    # Now get team logos and venue info from TheSportsDB
                    logos = await get_game_logos(closest_game)

                    # Return both game data and logos
                    return {"game": closest_game, "logos": logos}

        logger.warning("No upcoming games found")
        return None

    except Exception as e:
        logger.error(f"Error fetching game data: {e}")
        return None


async def get_game_logos(game_data):
    """Get logos for both teams and venue from TheSportsDB"""
    try:
        logos = {}

        # Get team references from the game data
        competitions = game_data.get("competitions", [])
        if competitions:
            competition = competitions[0]
            competitors = competition.get("competitors", [])

            for competitor in competitors:
                team_ref = competitor.get("team", {}).get("$ref")
                if team_ref:
                    # Get team name and search for logos
                    team_name = await get_team_name_from_ref(team_ref)
                    logger.info(f"Getting logos for team: {team_name}")

                    # Search TheSportsDB for this team
                    team_logos = await search_team_logos(team_name)
                    if team_logos:
                        logos[team_name] = team_logos
                        logger.info(f"Found logos for {team_name}: {team_logos}")

        # Get venue information
        venue_info = game_data.get("venue", {})
        if venue_info:
            venue_name = venue_info.get("fullName", "")
            if venue_name:
                logger.info(f"Getting venue image for: {venue_name}")
                venue_logos = await search_venue_logos(venue_name)
                if venue_logos:
                    logos["venue"] = venue_logos
                    logger.info(f"Found venue logos: {venue_logos}")

        return logos

    except Exception as e:
        logger.error(f"Error getting game logos: {e}")
        return {}


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
            timestamp=datetime.now(),
        )

        # Add LA Galaxy logo as thumbnail if available
        la_galaxy_logos = logos.get("LA Galaxy", {})
        if la_galaxy_logos.get("logo"):
            embed.set_thumbnail(url=la_galaxy_logos["logo"])
            logger.info(f"Setting LA Galaxy thumbnail to: {la_galaxy_logos['logo']}")
        else:
            logger.warning("No LA Galaxy logo available")

        # Add venue image if available
        venue_logos = logos.get("venue", {})
        if venue_logos.get("venue_image"):
            embed.set_image(url=venue_logos["venue_image"])
            logger.info(f"Setting venue image to: {venue_logos['venue_image']}")
        elif venue_logos.get("venue_thumb"):
            embed.set_image(url=venue_logos["venue_thumb"])
            logger.info(f"Setting venue thumb to: {venue_logos['venue_thumb']}")
        else:
            logger.warning("No venue image available")

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
        if venue_logos.get("venue_name"):
            embed.add_field(
                name="🏟️ Venue", value=venue_logos["venue_name"], inline=True
            )
        elif game_data.get("venue", {}).get("fullName"):
            embed.add_field(
                name="🏟️ Venue", value=game_data["venue"]["fullName"], inline=True
            )

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
