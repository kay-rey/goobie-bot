"""
Next game command implementation
"""

import discord
from discord import app_commands
import logging
from api import create_game_embed
from api.local_logos import get_local_team_logos, get_team_key_from_choice
from api.team_config import get_team_config

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

        if not team_config:
            await interaction.followup.send(f"❌ Unknown team: {team.value}")
            return

        team_name = team_config.get("name", "Unknown Team")
        game_data_func = team_config.get("game_func")

        # Get next game from ESPN API
        logger.info(f"Fetching next {team_name} game data...")
        game_data = await game_data_func()

        if not game_data:
            await interaction.followup.send(
                f"❌ Could not find {team_name}'s next game. The season may be over or no upcoming games are scheduled."
            )
            return

        # Get logos from local storage (includes built-in fallbacks)
        local_logos = get_local_team_logos(team_key)
        logos = {team_name: local_logos} if local_logos else {team_name: {}}

        # Create rich embed
        embed = await create_game_embed(game_data, logos, team_name)
        await interaction.followup.send(embed=embed)
        logger.info(f"{team_name} nextgame command completed successfully")

    except Exception as e:
        logger.error(f"Error in nextgame command: {e}")
        import traceback

        traceback.print_exc()
        await interaction.followup.send("❌ An error occurred while fetching game data")
