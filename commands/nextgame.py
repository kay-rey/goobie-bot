"""
Next game command implementation
"""

import discord
from discord import app_commands
import logging
from api import (
    get_galaxy_team_data,
    get_galaxy_next_game_extended,
    get_dodgers_team_data,
    get_dodgers_next_game,
    get_lakers_team_data,
    get_lakers_next_game,
    get_rams_team_data,
    get_rams_next_game,
    get_kings_team_data,
    get_kings_next_game,
    get_team_logos,
    extract_logos_from_team,
    get_game_logos,
    create_game_embed,
)

logger = logging.getLogger(__name__)


@app_commands.command(name="nextgame", description="Get the next game for a team")
@app_commands.choices(
    team=[
        app_commands.Choice(name="Galaxy", value="galaxy"),
        app_commands.Choice(name="Dodgers", value="dodgers"),
        app_commands.Choice(name="Lakers", value="lakers"),
        app_commands.Choice(name="Rams", value="rams"),
        app_commands.Choice(name="Kings", value="kings"),
    ]
)
async def nextgame_command(
    interaction: discord.Interaction, team: app_commands.Choice[str]
):
    """Get the next game for a specified team"""
    logger.info(
        f"Nextgame command triggered by {interaction.user} for team: {team.value}"
    )
    await interaction.response.defer()

    try:
        # Determine which team function to use based on choice value
        if team.value == "dodgers":
            team_name = "Los Angeles Dodgers"
            team_data_func = get_dodgers_team_data
            game_data_func = get_dodgers_next_game
            default_logo = "https://a.espncdn.com/i/teamlogos/mlb/500/19.png"
            default_stadium = "Dodger Stadium"
        elif team.value == "lakers":
            team_name = "Los Angeles Lakers"
            team_data_func = get_lakers_team_data
            game_data_func = get_lakers_next_game
            default_logo = "https://a.espncdn.com/i/teamlogos/nba/500/13.png"
            default_stadium = "Crypto.com Arena"
        elif team.value == "rams":
            team_name = "Los Angeles Rams"
            team_data_func = get_rams_team_data
            game_data_func = get_rams_next_game
            default_logo = "https://a.espncdn.com/i/teamlogos/nfl/500/14.png"
            default_stadium = "SoFi Stadium"
        elif team.value == "kings":
            team_name = "Los Angeles Kings"
            team_data_func = get_kings_team_data
            game_data_func = get_kings_next_game
            default_logo = "https://a.espncdn.com/i/teamlogos/nhl/500/8.png"
            default_stadium = "Crypto.com Arena"
        else:  # galaxy
            team_name = "LA Galaxy"
            team_data_func = get_galaxy_team_data
            game_data_func = get_galaxy_next_game_extended
            default_logo = "https://r2.thesportsdb.com/images/media/team/badge/ysyysr1420227188.png"
            default_stadium = "Dignity Health Sports Park"

        # Get team data from TheSportsDB
        logger.info(f"Fetching {team_name} team data...")
        team_data = await team_data_func()
        logger.info(f"Team data result: {bool(team_data)}")
        if not team_data:
            await interaction.followup.send(f"❌ Could not find {team_name} team data")
            return

        # Get next game from ESPN API
        logger.info(f"Fetching next {team_name} game data...")
        game_data = await game_data_func()
        logger.info(f"Game data result: {bool(game_data)}")
        if game_data:
            logger.info(f"Game data structure: {game_data}")
        if not game_data:
            await interaction.followup.send(
                f"❌ Could not find {team_name}'s next game. The season may be over or no upcoming games are scheduled."
            )
            return

        # Get logos for the game (teams and venue)
        logger.info("Getting game logos...")
        logos = await get_game_logos(game_data)
        logger.info(f"Game logos: {logos}")

        # If no logos found, try fallback from team data
        if not any(logos.values()):
            logger.info("No logos from game search, trying fallback...")
            team_id = team_data.get("idTeam")
            if team_id:
                fallback_logos = await get_team_logos(team_id)
                if not any(fallback_logos.values()):
                    fallback_logos = extract_logos_from_team(team_data)
                # Convert to new format
                logos = {team_name: fallback_logos}
                logger.info(f"Using fallback logos: {logos}")

        # If still no logos, use default
        if not any(logos.values()):
            logger.warning(
                f"No logos found from any source, using default {team_name} logo"
            )
            logos = {
                team_name: {
                    "logo": default_logo,
                    "logo_small": default_logo,
                    "jersey": "",
                    "stadium": team_data.get("strStadium", default_stadium),
                    "stadium_thumb": "",
                    "stadium_thumb_small": "",
                }
            }
            logger.info(f"Using fallback logos for {team_name}: {logos}")

        # Create rich embed
        logger.info("Creating embed...")
        embed = await create_game_embed(game_data, logos, team_name)
        await interaction.followup.send(embed=embed)
        logger.info(f"{team_name} nextgame command completed successfully")

    except Exception as e:
        logger.error(f"Error in nextgame command: {e}")
        import traceback

        traceback.print_exc()
        await interaction.followup.send("❌ An error occurred while fetching game data")
