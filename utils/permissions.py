"""
Permission utilities for goobie-bot
Handles admin permission checks and user authorization
"""

import logging
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


def has_admin_permissions(context) -> bool:
    """
    Check if user has admin permissions using multiple methods:
    1. User ID whitelist (if configured)
    2. Guild administrator permission
    3. Guild owner

    Args:
        context: Discord interaction or context object to check

    Returns:
        True if user has admin permissions, False otherwise
    """
    # Handle both interaction and context objects
    if hasattr(context, "user"):
        user = context.user
        guild = context.guild
    elif hasattr(context, "author"):
        user = context.author
        guild = context.guild
    else:
        logger.error(f"Unknown context type: {type(context)}")
        return False

    # Check user ID whitelist first (if configured)
    if ADMIN_USER_IDS and is_admin_user(user):
        logger.info(
            f"User {user} ({user.id}) granted admin access via user ID whitelist"
        )
        return True

    # Check guild administrator permission
    if guild and user.guild_permissions.administrator:
        logger.info(
            f"User {user} ({user.id}) granted admin access via guild administrator permission"
        )
        return True

    # Check if user is guild owner
    if guild and user.id == guild.owner_id:
        logger.info(f"User {user} ({user.id}) granted admin access as guild owner")
        return True

    logger.info(f"User {user} ({user.id}) denied admin access")
    return False


def require_admin_permissions(context) -> bool:
    """
    Check admin permissions and send error message if not authorized

    Args:
        context: Discord interaction or context object to check

    Returns:
        True if user has admin permissions, False otherwise
    """
    if has_admin_permissions(context):
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

    # Handle both interaction and context objects
    try:
        if hasattr(context, "response"):
            # Interaction object
            context.response.send_message(embed=embed, ephemeral=True)
        else:
            # Context object (text command)
            context.send(embed=embed)
    except Exception as e:
        logger.error(f"Error sending permission denied message: {e}")

    return False
