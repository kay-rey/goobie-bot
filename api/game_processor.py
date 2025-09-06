"""
Game processor module for goobie-bot
Handles combining ESPN game data with TheSportsDB logos and creating Discord embeds
"""

import logging
from datetime import datetime
import pytz
import discord

from .espn import get_team_name_from_ref
from .sportsdb import search_team_logos, search_venue_logos

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
                    logger.info(f"Getting logos for team: {team_name}")

                    # Search TheSportsDB for this team
                    team_logos = await search_team_logos(team_name)
                    if team_logos:
                        logos[team_name] = team_logos
                        logger.info(f"Found logos for {team_name}: {team_logos}")

        # Get venue information from competitions (like the old code)
        competitions = game_data.get("competitions", [])
        if competitions:
            competition = competitions[0]
            venue_info = competition.get("venue", {})
            logger.info(f"Venue info from competition: {venue_info}")
            if venue_info:
                venue_name = venue_info.get("fullName", "")
                logger.info(f"Venue name: {venue_name}")
                if venue_name:
                    logger.info(f"Getting venue image for: {venue_name}")
                    venue_logos = await search_venue_logos(venue_name)
                    if venue_logos:
                        logos["venue"] = venue_logos
                        logger.info(f"Found venue logos: {venue_logos}")
                    else:
                        logger.warning(f"No venue logos found for: {venue_name}")
                else:
                    logger.warning("No venue name found in venue info")
            else:
                logger.warning("No venue info found in competition")
        else:
            logger.warning("No competitions found in game data")

        return logos

    except Exception as e:
        logger.error(f"Error getting game logos: {e}")
        return {}


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

        # Add venue information (check competitions first, like the old code)
        logger.info(f"Venue logos: {venue_logos}")

        # Get venue from competitions (same as old code)
        competitions = game_data.get("competitions", [])
        venue_name = None
        if competitions:
            competition = competitions[0]
            venue_info = competition.get("venue", {})
            venue_name = venue_info.get("fullName", "")
            logger.info(f"Game data venue from competition: {venue_name}")

        if venue_logos.get("venue_name"):
            embed.add_field(
                name="🏟️ Venue", value=venue_logos["venue_name"], inline=True
            )
            logger.info(f"Added venue from logos: {venue_logos['venue_name']}")
        elif venue_name:
            embed.add_field(name="🏟️ Venue", value=venue_name, inline=True)
            logger.info(f"Added venue from game data: {venue_name}")
        else:
            logger.warning("No venue information available")

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
