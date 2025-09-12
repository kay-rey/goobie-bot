"""
Permission utilities for goobie-bot
Handles admin permission checks and user authorization
"""

import logging
from typing import List, Optional
import discord

from config import ADMIN_USER_IDS

logger = logging.getLogger(__name__)


def is_admin_user(user: discord.User) -> bool:
    """
    Check if a user is an admin based on user ID whitelist

    Args:
        user: Discord user to check

    Returns:
        True if user is admin, False otherwise
    """
    if not ADMIN_USER_IDS:
        # If no admin user IDs configured, fall back to guild permissions
        return False

    return user.id in ADMIN_USER_IDS


def has_admin_permissions(interaction: discord.Interaction) -> bool:
    """
    Check if user has admin permissions using multiple methods:
    1. User ID whitelist (if configured)
    2. Guild administrator permission
    3. Guild owner

    Args:
        interaction: Discord interaction to check

    Returns:
        True if user has admin permissions, False otherwise
    """
    user = interaction.user

    # Check user ID whitelist first (if configured)
    if ADMIN_USER_IDS and is_admin_user(user):
        logger.info(
            f"User {user} ({user.id}) granted admin access via user ID whitelist"
        )
        return True

    # Check guild administrator permission
    if interaction.guild and user.guild_permissions.administrator:
        logger.info(
            f"User {user} ({user.id}) granted admin access via guild administrator permission"
        )
        return True

    # Check if user is guild owner
    if interaction.guild and user.id == interaction.guild.owner_id:
        logger.info(f"User {user} ({user.id}) granted admin access as guild owner")
        return True

    logger.info(f"User {user} ({user.id}) denied admin access")
    return False


def require_admin_permissions(interaction: discord.Interaction) -> bool:
    """
    Check admin permissions and send error message if not authorized

    Args:
        interaction: Discord interaction to check

    Returns:
        True if user has admin permissions, False otherwise
    """
    if has_admin_permissions(interaction):
        return True

    # Send error message
    embed = discord.Embed(
        title="❌ Access Denied",
        description="You don't have permission to use this command.",
        color=0xFF0000,
    )

    if ADMIN_USER_IDS:
        embed.add_field(
            name="Required Permissions",
            value="• Administrator role, OR\n• Guild owner, OR\n• Whitelisted user ID",
            inline=False,
        )
    else:
        embed.add_field(
            name="Required Permissions",
            value="• Administrator role, OR\n• Guild owner",
            inline=False,
        )

    embed.set_footer(text="Contact a server administrator for access")

    try:
        interaction.response.send_message(embed=embed, ephemeral=True)
    except:
        # If response already sent, use followup
        interaction.followup.send(embed=embed, ephemeral=True)

    return False
