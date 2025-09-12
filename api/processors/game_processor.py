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
        logger.debug("Creating embed...")
        logger.debug(f"Creating embed with logos: {logos}")

        # Determine team from game data or use provided team name
        if not team_name:
            team_name = "LA Galaxy"  # Default
            color = 0x00245D  # LA Galaxy blue
            emoji = "⚽"  # Soccer emoji

            # Check if this is a baseball game
            if "baseball" in game_data.get("$ref", "").lower():
                emoji = "⚾"
                color = 0x005A9C  # Dodgers blue

                # Try to find Dodgers team name from logos
                for team, team_logos in logos.items():
                    if "dodgers" in team.lower():
                        team_name = team
                        break
                else:
                    # Fallback: look for any team with logos
                    if logos:
                        team_name = list(logos.keys())[0]

            # Check if this is a basketball game
            elif "basketball" in game_data.get("$ref", "").lower():
                emoji = "🏀"
                color = 0xFDB927  # Lakers gold

                # Try to find Lakers team name from logos
                for team, team_logos in logos.items():
                    if "lakers" in team.lower():
                        team_name = team
                        break
                else:
                    # Fallback: look for any team with logos
                    if logos:
                        team_name = list(logos.keys())[0]

            # Check if this is a football game
            elif "football" in game_data.get("$ref", "").lower():
                emoji = "🏈"
                color = 0xFFD700  # Rams yellow/gold

                # Try to find Rams team name from logos
                for team, team_logos in logos.items():
                    if "rams" in team.lower():
                        team_name = team
                        break
                else:
                    # Fallback: look for any team with logos
                    if logos:
                        team_name = list(logos.keys())[0]

            # Check if this is a hockey game
            elif "hockey" in game_data.get("$ref", "").lower():
                emoji = "🏒"
                color = 0xA2AAAD  # Kings black

                # Try to find Kings team name from logos
                for team, team_logos in logos.items():
                    if "kings" in team.lower():
                        team_name = team
                        break
                else:
                    # Fallback: look for any team with logos
                    if logos:
                        team_name = list(logos.keys())[0]
        else:
            # Use provided team name and determine sport/color/emoji
            if "dodgers" in team_name.lower():
                emoji = "⚾"
                color = 0x005A9C  # Dodgers blue
            elif "lakers" in team_name.lower():
                emoji = "🏀"
                color = 0x552583  # Lakers purple
            elif "rams" in team_name.lower():
                emoji = "🏈"
                color = 0xFFD700  # Rams yellow/gold
            elif "kings" in team_name.lower():
                emoji = "🏒"
                color = 0xA2AAAD  # Kings black
            else:  # Galaxy
                emoji = "⚽"
                color = 0x00245D  # LA Galaxy blue

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
            logger.debug(f"Setting {team_name} thumbnail to: {team_logos['logo']}")
        else:
            logger.warning(f"No {team_name} logo available")

        # Note: Stadium/venue images removed for now

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
                logger.debug(
                    f"Game date: {game_date} (UTC) -> {game_date_pacific} (PDT) -> {formatted_date}"
                )

                # Truncate date if too long for Discord embed
                logger.debug(f"Date value length: {len(formatted_date)}")
                if len(formatted_date) > 1024:
                    logger.warning(
                        f"Date value too long ({len(formatted_date)} chars), truncating"
                    )
                    formatted_date = formatted_date[:1021] + "..."

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
            # Truncate game name if too long for Discord embed
            game_name = game_data["name"]
            logger.debug(f"Game name value length: {len(game_name)}")
            if len(game_name) > 1024:
                logger.warning(
                    f"Game name value too long ({len(game_name)} chars), truncating"
                )
                game_name = game_name[:1021] + "..."
            embed.add_field(name=f"{emoji} Match", value=game_name, inline=False)

        # Add venue information from game data
        competitions = game_data.get("competitions", [])
        venue_name = None
        if competitions:
            competition = competitions[0]
            venue_info = competition.get("venue", {})
            venue_name = venue_info.get("fullName", "")
            logger.debug(f"Game data venue from competition: {venue_name}")

        if venue_name:
            # Truncate venue name if too long for Discord embed
            logger.debug(f"Venue value length: {len(venue_name)}")
            if len(venue_name) > 1024:
                logger.warning(
                    f"Venue value too long ({len(venue_name)} chars), truncating"
                )
                venue_name = venue_name[:1021] + "..."
            embed.add_field(name="🏟️ Venue", value=venue_name, inline=True)
            logger.debug(f"Added venue: {venue_name}")
        else:
            logger.warning("No venue information available")

        # Competition field removed - users already know what competition teams play in

        # Add footer
        footer_text = "Go LA!"
        # Truncate footer if too long for Discord embed
        if len(footer_text) > 2048:  # Footer has higher limit
            footer_text = footer_text[:2045] + "..."
        embed.set_footer(text=footer_text)

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
