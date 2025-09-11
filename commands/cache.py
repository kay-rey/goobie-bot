"""
Cache management command for goobie-bot
Provides cache statistics and management functionality
"""

import discord
from discord import app_commands
import logging
from api.cache import get_cache_stats, clear_cache, cleanup_expired_cache

logger = logging.getLogger(__name__)


@app_commands.command(name="cache", description="Get cache statistics and manage cache")
@app_commands.choices(
    action=[
        app_commands.Choice(name="stats", value="stats"),
        app_commands.Choice(name="clear", value="clear"),
        app_commands.Choice(name="cleanup", value="cleanup"),
    ]
)
async def cache_command(
    interaction: discord.Interaction, action: app_commands.Choice[str]
):
    """Get cache statistics and manage cache"""
    logger.info(
        f"Cache command triggered by {interaction.user} for action: {action.value}"
    )
    await interaction.response.defer(ephemeral=True)

    try:
        if action.value == "stats":
            # Get cache statistics
            stats = await get_cache_stats()

            embed = discord.Embed(
                title="📊 Cache Statistics",
                color=0x00FF00,
                timestamp=discord.utils.utcnow(),
            )

            embed.add_field(
                name="📈 Performance",
                value=f"**Hit Rate:** {stats['hit_rate']}%\n"
                f"**Total Requests:** {stats['total_requests']}\n"
                f"**Cache Hits:** {stats['hits']}\n"
                f"**Cache Misses:** {stats['misses']}",
                inline=True,
            )

            embed.add_field(
                name="💾 Storage",
                value=f"**Total Entries:** {stats['total_entries']}\n"
                f"**Cache Sets:** {stats['sets']}\n"
                f"**Cache Deletes:** {stats['deletes']}\n"
                f"**Cache Clears:** {stats['clears']}",
                inline=True,
            )

            embed.set_footer(text="Cache performance metrics")

            await interaction.followup.send(embed=embed, ephemeral=True)

        elif action.value == "clear":
            # Clear all cache
            cleared_count = await clear_cache()

            embed = discord.Embed(
                title="🧹 Cache Cleared",
                description=f"Successfully cleared **{cleared_count}** cache entries",
                color=0xFFA500,
                timestamp=discord.utils.utcnow(),
            )

            await interaction.followup.send(embed=embed, ephemeral=True)

        elif action.value == "cleanup":
            # Cleanup expired entries
            cleaned_count = await cleanup_expired_cache()

            embed = discord.Embed(
                title="🧽 Cache Cleanup",
                description=f"Successfully cleaned up **{cleaned_count}** expired entries",
                color=0x00BFFF,
                timestamp=discord.utils.utcnow(),
            )

            await interaction.followup.send(embed=embed, ephemeral=True)

        logger.info(f"Cache command completed successfully for {action.value}")

    except Exception as e:
        logger.error(f"Error in cache command: {e}")
        import traceback

        traceback.print_exc()
        await interaction.followup.send(
            "❌ An error occurred while managing cache", ephemeral=True
        )


# Export the command
cache_command = cache_command
