"""
Error event handlers
"""

import discord
import logging

logger = logging.getLogger(__name__)


async def on_command_error(ctx, error):
    """Handle command errors"""
    logger.error(f"❌ Command error: {error}")


async def on_app_command_error(interaction, error):
    """Handle slash command errors"""
    logger.error(f"❌ Slash command error: {error}")
    if not interaction.response.is_done():
        await interaction.response.send_message("An error occurred!", ephemeral=True)
