"""
Game processor module for goobie-bot
Handles combining ESPN game data with TheSportsDB logos and creating Discord embeds
"""

import logging
from datetime import datetime
import pytz
import discord

from api import get_team_name_from_ref, search_team_logos

logger = logging.getLogger(__name__)


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
                    logger.debug(f"Getting logos for team: {team_name}")

                    # Search TheSportsDB for this team
                    team_logos = await search_team_logos(team_name)
                    if team_logos:
                        logos[team_name] = team_logos
                        logger.debug(f"Found logos for {team_name}: {team_logos}")

        # Note: Venue/stadium image fetching removed for now

        return logos

    except Exception as e:
        logger.error(f"Error getting game logos: {e}")
        return {}


async def create_game_embed(game_data, logos, team_name=None):
    """Create a Discord embed for the game data"""
    try:
        # Team configuration mapping for quick lookup
        TEAM_CONFIG = {
            "dodgers": {"emoji": "⚾", "color": 0x005A9C},
            "lakers": {"emoji": "🏀", "color": 0x552583},
            "rams": {"emoji": "🏈", "color": 0xFFD700},
            "kings": {"emoji": "🏒", "color": 0xA2AAAD},
            "galaxy": {"emoji": "⚽", "color": 0x00245D},
        }

        # Determine team name and configuration
        if not team_name:
            # Use first available team from logos or default to Galaxy
            team_name = list(logos.keys())[0] if logos else "LA Galaxy"

        # Find team configuration by matching team name
        team_key = None
        for key, config in TEAM_CONFIG.items():
            if key in team_name.lower():
                team_key = key
                break

        # Default to Galaxy if no match found
        if not team_key:
            team_key = "galaxy"
            team_name = "LA Galaxy"

        config = TEAM_CONFIG[team_key]
        emoji = config["emoji"]
        color = config["color"]

        # Create embed
        embed = discord.Embed(
            title=f"{team_name} Next Game",
            color=color,
            timestamp=datetime.now(),
        )

        # Add team logo as thumbnail if available
        team_logos = logos.get(team_name, {})
        if team_logos.get("logo"):
            embed.set_thumbnail(url=team_logos["logo"])

        # Parse and add game date
        if game_data.get("date"):
            try:
                game_date = datetime.fromisoformat(
                    game_data["date"].replace("Z", "+00:00")
                )
                # Convert to Pacific Time
                pacific_tz = pytz.timezone("America/Los_Angeles")
                game_date_pacific = game_date.astimezone(pacific_tz)
                formatted_date = game_date_pacific.strftime(
                    "%A, %B %d, %Y at %I:%M %p %Z"
                )
                # Truncate if too long for Discord embed
                if len(formatted_date) > 1024:
                    formatted_date = formatted_date[:1021] + "..."
                embed.add_field(
                    name="📅 Date & Time", value=formatted_date, inline=False
                )
            except Exception as e:
                logger.warning(f"Error parsing date: {e}")
                embed.add_field(
                    name="📅 Date & Time",
                    value=game_data.get("date", "TBD"),
                    inline=False,
                )

        # Add game name
        if game_data.get("name"):
            game_name = game_data["name"]
            if len(game_name) > 1024:
                game_name = game_name[:1021] + "..."
            embed.add_field(name=f"{emoji} Match", value=game_name, inline=False)

        # Add venue information
        competitions = game_data.get("competitions", [])
        if competitions:
            venue_name = competitions[0].get("venue", {}).get("fullName", "")
            if venue_name:
                if len(venue_name) > 1024:
                    venue_name = venue_name[:1021] + "..."
                embed.add_field(name="🏟️ Venue", value=venue_name, inline=True)

        # Add footer
        embed.set_footer(text="Go LA!")

        return embed

    except Exception as e:
        logger.error(f"Error creating embed: {e}")
        # Return a basic embed if there's an error
        embed = discord.Embed(
            title="Next Game",
            description="Error loading game information",
            color=0xFF0000,
        )
        return embed
