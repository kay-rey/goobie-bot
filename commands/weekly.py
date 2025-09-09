"""
Weekly matches command for goobie-bot
Allows manual testing of the weekly matches notification
"""

import discord
from discord import app_commands
import logging

from scheduler.weekly_matches import send_weekly_matches_notification

logger = logging.getLogger(__name__)


@app_commands.command(
    name="weekly",
    description="Send the weekly matches notification for LA teams (Monday-Sunday schedule)",
)
async def weekly_command(interaction: discord.Interaction):
    """Send the weekly matches notification"""
    try:
        logger.info(f"Weekly command called by {interaction.user}")

        # Send typing indicator
        await interaction.response.defer(ephemeral=True)

        # Send the weekly matches notification
        await send_weekly_matches_notification(
            interaction.client, interaction.channel.id
        )

        # Send confirmation
        await interaction.followup.send(
            "📅 Weekly matches notification sent!", ephemeral=True
        )

    except Exception as e:
        logger.error(f"Error in weekly command: {e}")
        await interaction.followup.send(
            "❌ Error sending weekly matches notification", ephemeral=True
        )


# Export the command
weekly_command = weekly_command
