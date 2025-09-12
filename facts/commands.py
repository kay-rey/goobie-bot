"""
Commands module for facts feature
Handles slash commands and text commands for daily facts
"""

import discord
from discord.ext import commands
import logging
from datetime import datetime
import pytz

from .database import FactsDatabase

logger = logging.getLogger(__name__)


class FactsCommands(commands.Cog):
    """Commands for the facts feature"""

    def __init__(self, bot):
        self.bot = bot
        self.db = FactsDatabase()

    @discord.app_commands.command(
        name="fact", description="Get a random LA sports fact"
    )
    async def fact_command(self, interaction: discord.Interaction):
        """Slash command to get a random fact"""
        try:
            # Get a random fact
            fact_data = self.db.get_random_fact()
            if not fact_data:
                await interaction.response.send_message(
                    "❌ No facts available at the moment. Please try again later.",
                    ephemeral=True,
                )
                return

            # Create embed
            embed = discord.Embed(
                title=f"{fact_data['emoji']} LA Sports Fact",
                description=f"**{fact_data['category']}**\n\n{fact_data['fact']}",
                color=0x00923F,  # LA City green
                timestamp=datetime.now(),
            )

            # Add thumbnail
            embed.set_thumbnail(
                url="https://raw.githubusercontent.com/kay-rey/goobie-bot/main/assets/images/goobiebotla.png"
            )

            # Add footer
            embed.set_footer(text="🏆 Go LA! • Use /fact for more random facts")

            # Send response
            await interaction.response.send_message(embed=embed)

            # Mark fact as used
            self.db.mark_fact_used(fact_data["id"])

            logger.info(f"Sent fact {fact_data['id']} to {interaction.user.name}")

        except Exception as e:
            logger.error(f"Error in fact command: {e}")
            await interaction.response.send_message(
                "❌ An error occurred while getting a fact. Please try again later.",
                ephemeral=True,
            )

    @discord.app_commands.command(
        name="factstats", description="Get statistics about daily facts"
    )
    async def fact_stats_command(self, interaction: discord.Interaction):
        """Slash command to get fact statistics"""
        try:
            # Check if user is admin
            from utils.permissions import is_admin

            if not is_admin(interaction.user.id):
                await interaction.response.send_message(
                    "❌ You don't have permission to use this command.", ephemeral=True
                )
                return

            # Get stats
            stats = self.db.get_fact_stats()
            if not stats:
                await interaction.response.send_message(
                    "❌ Could not retrieve fact statistics.", ephemeral=True
                )
                return

            # Create embed
            embed = discord.Embed(
                title="📊 Daily Facts Statistics",
                color=0x00923F,
                timestamp=datetime.now(),
            )

            # Add stats fields
            embed.add_field(
                name="📚 Total Facts", value=str(stats["total_facts"]), inline=True
            )
            embed.add_field(
                name="📅 Facts Posted Today",
                value=str(stats["facts_today"]),
                inline=True,
            )

            if stats["most_used"]:
                most_used_fact = (
                    stats["most_used"][0][:100] + "..."
                    if len(stats["most_used"][0]) > 100
                    else stats["most_used"][0]
                )
                embed.add_field(
                    name="🔥 Most Used Fact",
                    value=f"*{most_used_fact}*\nUsed {stats['most_used'][1]} times",
                    inline=False,
                )

            # Add thumbnail
            embed.set_thumbnail(
                url="https://raw.githubusercontent.com/kay-rey/goobie-bot/main/assets/images/goobiebotla.png"
            )

            # Add footer
            embed.set_footer(text="🏆 Go LA! • Admin only command")

            await interaction.response.send_message(embed=embed)

        except Exception as e:
            logger.error(f"Error in fact stats command: {e}")
            await interaction.response.send_message(
                "❌ An error occurred while getting statistics. Please try again later.",
                ephemeral=True,
            )


# Text command for random fact
@commands.command(name="fact")
async def fact_text_command(ctx):
    """Text command to get a random fact"""
    try:
        db = FactsDatabase()

        # Get a random fact
        fact_data = db.get_random_fact()
        if not fact_data:
            await ctx.send(
                "❌ No facts available at the moment. Please try again later."
            )
            return

        # Create embed
        embed = discord.Embed(
            title=f"{fact_data['emoji']} LA Sports Fact",
            description=f"**{fact_data['category']}**\n\n{fact_data['fact']}",
            color=0x00923F,  # LA City green
            timestamp=datetime.now(),
        )

        # Add thumbnail
        embed.set_thumbnail(
            url="https://raw.githubusercontent.com/kay-rey/goobie-bot/main/assets/images/goobiebotla.png"
        )

        # Add footer
        embed.set_footer(text="🏆 Go LA! • Use !fact for more random facts")

        # Send message
        await ctx.send(embed=embed)

        # Mark fact as used
        db.mark_fact_used(fact_data["id"])

        logger.info(f"Sent fact {fact_data['id']} to {ctx.author.name}")

    except Exception as e:
        logger.error(f"Error in fact text command: {e}")
        await ctx.send(
            "❌ An error occurred while getting a fact. Please try again later."
        )


# Text command for fact stats
@commands.command(name="factstats")
async def fact_stats_text_command(ctx):
    """Text command to get fact statistics"""
    try:
        # Check if user is admin
        from utils.permissions import is_admin

        if not is_admin(ctx.author.id):
            await ctx.send("❌ You don't have permission to use this command.")
            return

        db = FactsDatabase()

        # Get stats
        stats = db.get_fact_stats()
        if not stats:
            await ctx.send("❌ Could not retrieve fact statistics.")
            return

        # Create embed
        embed = discord.Embed(
            title="📊 Daily Facts Statistics",
            color=0x00923F,
            timestamp=datetime.now(),
        )

        # Add stats fields
        embed.add_field(
            name="📚 Total Facts", value=str(stats["total_facts"]), inline=True
        )
        embed.add_field(
            name="📅 Facts Posted Today", value=str(stats["facts_today"]), inline=True
        )

        if stats["most_used"]:
            most_used_fact = (
                stats["most_used"][0][:100] + "..."
                if len(stats["most_used"][0]) > 100
                else stats["most_used"][0]
            )
            embed.add_field(
                name="🔥 Most Used Fact",
                value=f"*{most_used_fact}*\nUsed {stats['most_used'][1]} times",
                inline=False,
            )

        # Add thumbnail
        embed.set_thumbnail(
            url="https://raw.githubusercontent.com/kay-rey/goobie-bot/main/assets/images/goobiebotla.png"
        )

        # Add footer
        embed.set_footer(text="🏆 Go LA! • Admin only command")

        await ctx.send(embed=embed)

    except Exception as e:
        logger.error(f"Error in fact stats text command: {e}")
        await ctx.send(
            "❌ An error occurred while getting statistics. Please try again later."
        )


# Create command instances
fact_command = discord.app_commands.Command(
    name="fact",
    description="Get a random LA sports fact",
    callback=FactsCommands.fact_command,
)

fact_stats_command = discord.app_commands.Command(
    name="factstats",
    description="Get statistics about daily facts",
    callback=FactsCommands.fact_stats_command,
)
