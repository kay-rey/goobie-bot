"""
Ping command implementation
"""

import discord
from discord import app_commands
import logging

logger = logging.getLogger(__name__)


@app_commands.command(name="ping", description="Test the bot's responsiveness")
async def ping_command(interaction: discord.Interaction):
    """Slash command that responds with Pong!"""
    logger.info(f"Ping command triggered by {interaction.user}")
    await interaction.response.send_message("Pong!", ephemeral=True)
