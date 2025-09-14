"""
Simple daily facts scheduler for goobie-bot
Uses JSON file directly without database complexity
"""

import asyncio
import logging
from datetime import datetime, timedelta
import pytz
import discord

from .simple_facts import SimpleFacts

logger = logging.getLogger(__name__)


def get_category_style(category):
    """Get color and image based on fact category"""
    category_styles = {
        "Lego": {
            "color": 0xFF6B35,  # Orange (Lego's signature color)
            "image": "https://raw.githubusercontent.com/kay-rey/goobie-bot/main/assets/images/goobies/goobieheadclear.png",
        },
        "Disney": {
            "color": 0x1E90FF,  # Dodger Blue (Disney magic)
            "image": "https://raw.githubusercontent.com/kay-rey/goobie-bot/main/assets/images/goobies/goobieheadclear.png",
        },
        "Star Wars": {
            "color": 0xFFD700,  # Gold (Jedi/Sith theme)
            "image": "https://raw.githubusercontent.com/kay-rey/goobie-bot/main/assets/images/goobies/goobieheadclear.png",
        },
        "Galaxy": {
            "color": 0x00923F,  # LA Galaxy green
            "image": "https://raw.githubusercontent.com/kay-rey/goobie-bot/main/assets/images/goobies/goobieheadclear.png",
        },
        "Dodgers": {
            "color": 0x1E90FF,  # Dodger Blue
            "image": "https://raw.githubusercontent.com/kay-rey/goobie-bot/main/assets/images/goobies/goobieheadclear.png",
        },
        "Lakers": {
            "color": 0x552583,  # Lakers Purple
            "image": "https://raw.githubusercontent.com/kay-rey/goobie-bot/main/assets/images/goobies/goobieheadclear.png",
        },
    }

    # Default style for unknown categories
    default_style = {
        "color": 0xFF6B35,  # Orange
        "image": "https://raw.githubusercontent.com/kay-rey/goobie-bot/main/assets/images/goobies/goobieheadclear.png",
    }

    return category_styles.get(category, default_style)


class SimpleFactsScheduler:
    """Simple daily facts scheduler using JSON file"""

    def __init__(self):
        self.facts = SimpleFacts()
        self.last_posted_date = None

    async def send_daily_fact_post(self, bot, channel_id: int):
        """Send daily fact post to channel"""
        try:
            logger.info("Sending daily fact post...")

            # Check if we already posted today
            pacific_tz = pytz.timezone("America/Los_Angeles")
            today = datetime.now(pacific_tz).date()

            if self.last_posted_date == today:
                logger.info("Daily fact already posted today")
                return

            # Get a random fact for today
            fact_data = self.facts.get_random_fact()
            if not fact_data:
                logger.error("No available facts for today's post")
                return

            # Get category-specific styling
            style = get_category_style(fact_data["category"])

            # Create embed
            embed = discord.Embed(
                title=f"📚 Daily Goobie Fact - {today.strftime('%B %d, %Y')}",
                description=f"**{fact_data['emoji']} {fact_data['category']}**\n\n{fact_data['fact']}",
                color=style["color"],
                timestamp=datetime.now(),
            )

            # Add thumbnail
            embed.set_thumbnail(url=style["image"])

            # Add footer
            embed.set_footer(text="🔄 Posted daily at 12 PM PT")

            # Send message
            channel = bot.get_channel(channel_id)
            if channel:
                message = await channel.send(embed=embed)

                # Update last posted date
                self.last_posted_date = today

                logger.info(f"Daily fact post sent to channel {channel_id}")
            else:
                logger.error(f"Channel {channel_id} not found")

        except Exception as e:
            logger.error(f"Error sending daily fact post: {e}")

    async def schedule_daily_facts(self, bot, channel_id: int):
        """Schedule daily fact posts for 12 PM PT every day"""
        try:
            logger.info("Setting up daily facts scheduler...")

            pacific_tz = pytz.timezone("America/Los_Angeles")

            while True:
                # Get current time in Pacific
                now_pacific = datetime.now(pacific_tz)

                # Calculate next 12 PM PT
                next_12pm = now_pacific.replace(
                    hour=12, minute=0, second=0, microsecond=0
                )

                # If it's already past 12 PM today, schedule for tomorrow
                if now_pacific >= next_12pm:
                    next_12pm += timedelta(days=1)

                # Calculate seconds until next 12 PM PT
                seconds_until_next = (next_12pm - now_pacific).total_seconds()

                logger.info(f"Next daily fact scheduled for: {next_12pm}")
                logger.info(f"Waiting {seconds_until_next / 3600:.1f} hours...")

                # Wait until next 12 PM PT
                await asyncio.sleep(seconds_until_next)

                # Send the daily fact post
                await self.send_daily_fact_post(bot, channel_id)

                # Wait a bit before calculating the next run
                await asyncio.sleep(60)  # Wait 1 minute to avoid rapid re-scheduling

        except Exception as e:
            logger.error(f"Error in daily facts scheduler: {e}")
            # Restart the scheduler after a delay
            await asyncio.sleep(300)  # Wait 5 minutes before restarting
            await self.schedule_daily_facts(bot, channel_id)


async def schedule_daily_facts(bot, channel_id: int):
    """Main function to start the daily facts scheduler"""
    scheduler = SimpleFactsScheduler()
    await scheduler.schedule_daily_facts(bot, channel_id)
