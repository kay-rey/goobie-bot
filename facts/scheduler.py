"""
Daily facts scheduler for goobie-bot
Handles sending daily random facts every day at 12 PM PT
"""

import asyncio
import logging
from datetime import datetime, timedelta
import pytz
import discord

from .database import FactsDatabase

logger = logging.getLogger(__name__)


class FactsScheduler:
    """Manages daily facts scheduling and posting"""

    def __init__(self, db_path: str = "facts/data/facts.db"):
        self.db = FactsDatabase(db_path)
        self.facts_loaded = False
        self._load_initial_facts()

    def _load_initial_facts(self):
        """Load initial facts from JSON file if database is empty"""
        try:
            # Check if we have any facts in the database
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM facts")
                count = cursor.fetchone()[0]

                if count == 0:
                    # Load facts from JSON file
                    success = self.db.load_facts_from_json()
                    if success:
                        logger.info("Loaded facts from JSON file")
                    else:
                        logger.error("Failed to load facts from JSON file")
                else:
                    logger.info(f"Database already has {count} facts")

            self.facts_loaded = True

        except Exception as e:
            logger.error(f"Error loading initial facts: {e}")

    async def send_daily_fact_post(self, bot, channel_id: int):
        """Send daily fact post to channel"""
        try:
            logger.info("Sending daily fact post...")

            # Check if we already posted today
            daily_post = self.db.get_daily_fact_post()
            if daily_post:
                logger.info("Daily fact already posted today")
                return

            # Get a random fact for today
            fact_data = self.db.get_random_fact()
            if not fact_data:
                logger.error("No available facts for today's post")
                return

            # Mark fact as used
            self.db.mark_fact_used(fact_data["id"])

            # Create embed
            embed = discord.Embed(
                title=f"📚 Daily LA Sports Fact - {datetime.now(pytz.timezone('America/Los_Angeles')).strftime('%B %d, %Y')}",
                description=f"**{fact_data['emoji']} {fact_data['category']}**\n\n{fact_data['fact']}",
                color=0x00923F,  # LA City green
                timestamp=datetime.now(),
            )

            # Add thumbnail
            embed.set_thumbnail(
                url="https://raw.githubusercontent.com/kay-rey/goobie-bot/main/assets/images/goobiebotla.png"
            )

            # Add footer
            embed.set_footer(text="🔄 Posted daily at 12 PM PT • 🏆 Go LA!")

            # Send message
            channel = bot.get_channel(channel_id)
            if channel:
                message = await channel.send(embed=embed)

                # Record the daily post
                self.db.create_daily_fact_post(channel_id, message.id, fact_data["id"])

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
    scheduler = FactsScheduler()
    await scheduler.schedule_daily_facts(bot, channel_id)
