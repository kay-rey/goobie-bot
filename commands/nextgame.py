"""
Next game command implementation
"""

import discord
from discord import app_commands
import logging
from api import create_game_embed
from api.local_logos import get_local_team_logos, get_team_key_from_choice
from api.team_config import (
    get_team_data,
    get_team_config,
    get_team_display_name,
    get_game_function,
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
        # Get team configuration (no API call required)
        team_key = get_team_key_from_choice(team.value)
        team_config = get_team_config(team_key)
        team_name = get_team_display_name(team_key)
        game_data_func = get_game_function(team_key)

        if not team_config:
            await interaction.followup.send(f"❌ Unknown team: {team.value}")
            return

        # Get team data (no API call - uses hardcoded data)
        # Note: team_data available if needed for future enhancements
        get_team_data(team_key)
        logger.debug(f"Team data loaded for {team_name}")

        # Get next game from ESPN API
        logger.info(f"Fetching next {team_name} game data...")
        game_data = await game_data_func()
        logger.debug(f"Game data result: {bool(game_data)}")

        if not game_data:
            await interaction.followup.send(
                f"❌ Could not find {team_name}'s next game. The season may be over or no upcoming games are scheduled."
            )
            return

        # Get logos from local storage (includes built-in fallbacks)
        logger.debug("Getting local team logos...")
        local_logos = get_local_team_logos(team_key)

        if local_logos:
            logos = {team_name: local_logos}
            logger.debug(f"Using local logos for {team_name}")
        else:
            # This should rarely happen as local logo system has built-in fallbacks
            logger.warning(f"No logos found for {team_name}, using team config default")
            team_config = get_team_config(team_key)
            default_logo = team_config.get("default_logo", "")
            logos = {
                team_name: {
                    "logo": default_logo,
                    "logo_small": default_logo,
                }
            }

        # Create rich embed
        logger.debug("Creating embed...")
        embed = await create_game_embed(game_data, logos, team_name)
        await interaction.followup.send(embed=embed)
        logger.info(f"{team_name} nextgame command completed successfully")

    except Exception as e:
        logger.error(f"Error in nextgame command: {e}")
        import traceback

        traceback.print_exc()
        await interaction.followup.send("❌ An error occurred while fetching game data")
