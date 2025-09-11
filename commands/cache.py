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
            logger.info(f"Retrieving cache statistics for {interaction.user}")
            stats = await get_cache_stats()

            embed = discord.Embed(
                title="📊 Cache Statistics",
                color=0x00FF00,
                timestamp=discord.utils.utcnow(),
            )

            # Performance metrics
            hit_rate_color = (
                "🟢"
                if stats["hit_rate"] >= 70
                else "🟡"
                if stats["hit_rate"] >= 40
                else "🔴"
            )
            embed.add_field(
                name="📈 Performance",
                value=f"**Hit Rate:** {hit_rate_color} {stats['hit_rate']}%\n"
                f"**Total Requests:** {stats['total_requests']}\n"
                f"**Cache Hits:** {stats['hits']}\n"
                f"**Cache Misses:** {stats['misses']}",
                inline=True,
            )

            # Storage metrics
            embed.add_field(
                name="💾 Storage",
                value=f"**Total Entries:** {stats['total_entries']}\n"
                f"**Cache Sets:** {stats['sets']}\n"
                f"**Cache Deletes:** {stats['deletes']}\n"
                f"**Cache Clears:** {stats['clears']}",
                inline=True,
            )

            # Performance status
            if stats["total_requests"] > 0:
                if stats["hit_rate"] >= 70:
                    status = "🟢 Excellent"
                elif stats["hit_rate"] >= 40:
                    status = "🟡 Good"
                else:
                    status = "🔴 Needs Improvement"
            else:
                status = "⚪ No Data"

            embed.add_field(
                name="📊 Status",
                value=f"**Performance:** {status}\n"
                f"**Memory Usage:** {stats['total_entries']} entries\n"
                f"**Efficiency:** {stats['hit_rate']}% hit rate",
                inline=False,
            )

            embed.set_footer(
                text="Cache performance metrics • Use /cache clear to reset"
            )

            await interaction.followup.send(embed=embed, ephemeral=True)
            logger.info(
                f"Cache statistics displayed: {stats['hit_rate']}% hit rate, {stats['total_entries']} entries"
            )

        elif action.value == "clear":
            # Clear all cache
            logger.info(f"Clearing all cache entries for {interaction.user}")
            cleared_count = await clear_cache()

            embed = discord.Embed(
                title="🧹 Cache Cleared",
                description=f"Successfully cleared **{cleared_count}** cache entries",
                color=0xFFA500,
                timestamp=discord.utils.utcnow(),
            )

            await interaction.followup.send(embed=embed, ephemeral=True)
            logger.info(f"Cache cleared: {cleared_count} entries removed")

        elif action.value == "cleanup":
            # Cleanup expired entries
            logger.info(f"Cleaning up expired cache entries for {interaction.user}")
            cleaned_count = await cleanup_expired_cache()

            embed = discord.Embed(
                title="🧽 Cache Cleanup",
                description=f"Successfully cleaned up **{cleaned_count}** expired entries",
                color=0x00BFFF,
                timestamp=discord.utils.utcnow(),
            )

            await interaction.followup.send(embed=embed, ephemeral=True)
            logger.info(
                f"Cache cleanup completed: {cleaned_count} expired entries removed"
            )

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
