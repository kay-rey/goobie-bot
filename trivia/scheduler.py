"""
Daily trivia scheduler for goobie-bot
Handles sending daily trivia posts every day at 8 PM PT
"""

import asyncio
import logging
from datetime import datetime, timedelta
import pytz
import discord
import json
from pathlib import Path

from .database import TriviaDatabase
from .ui import TriviaView

logger = logging.getLogger(__name__)


class TriviaScheduler:
    """Manages daily trivia scheduling and posting"""

    def __init__(self, db_path: str = "trivia/data/trivia.db"):
        self.db = TriviaDatabase(db_path)
        self.questions_loaded = False
        self._load_initial_questions()

    def _load_initial_questions(self):
        """Load initial questions from JSON file if database is empty"""
        try:
            # Check if we have any questions in the database
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM trivia_questions")
                count = cursor.fetchone()[0]

                if count == 0:
                    # Load questions from JSON file
                    questions_file = Path("trivia/data/questions.json")
                    if questions_file.exists():
                        with open(questions_file, "r") as f:
                            data = json.load(f)

                        for question_data in data["questions"]:
                            self.db.add_question(
                                question=question_data["question"],
                                correct_answer=question_data["correct_answer"],
                                wrong_answers=question_data["wrong_answers"],
                                category=question_data["category"],
                                difficulty=question_data["difficulty"],
                            )

                        logger.info(
                            f"Loaded {len(data['questions'])} trivia questions from JSON"
                        )
                    else:
                        logger.warning("No questions.json file found")
                else:
                    logger.info(f"Database already has {count} questions")

            self.questions_loaded = True

        except Exception as e:
            logger.error(f"Error loading initial questions: {e}")

    async def send_daily_trivia_post(self, bot, channel_id: int):
        """Send daily trivia post to channel with start button"""
        try:
            logger.info("Sending daily trivia post...")

            # Check if we already posted today
            daily_post = self.db.get_daily_post()
            if daily_post:
                logger.info("Daily trivia already posted today")
                return

            # Get a random question for today
            question = self.db.get_random_question()
            if not question:
                logger.error("No available questions for today's trivia")
                return

            # Mark question as used
            self.db.mark_question_used(question["id"])

            # Create embed
            embed = discord.Embed(
                title="🧠 Daily Trivia - LA Sports",
                description=f"**{datetime.now(pytz.timezone('America/Los_Angeles')).strftime('%B %d, %Y')}**\n\n"
                f"Test your LA sports knowledge! Answer questions about "
                f"Galaxy, Dodgers, Lakers, Rams, and Kings.\n\n"
                f"⏰ You have 30 seconds per question\n"
                f"🏆 Earn points for correct answers and speed\n"
                f"📊 Compete on the leaderboard!\n\n"
                f"*Click the button below to start your private trivia session!*",
                color=0x00923F,  # LA City green
                timestamp=datetime.now(),
            )

            # Add thumbnail
            embed.set_thumbnail(
                url="https://raw.githubusercontent.com/kay-rey/goobie-bot/main/assets/images/goobiebotla.png"
            )

            # Add footer
            embed.set_footer(text="🔄 Resets every 24 hours at 8 PM PT • 🏆 Go LA!")

            # Create view with buttons
            view = TriviaView(self.db, question["id"])

            # Send message
            channel = bot.get_channel(channel_id)
            if channel:
                message = await channel.send(embed=embed, view=view)

                # Record the daily post
                self.db.create_daily_post(channel_id, message.id, question["id"])

                logger.info(f"Daily trivia post sent to channel {channel_id}")
            else:
                logger.error(f"Channel {channel_id} not found")

        except Exception as e:
            logger.error(f"Error sending daily trivia post: {e}")

    async def schedule_daily_trivia(self, bot, channel_id: int):
        """Schedule daily trivia posts for 8 PM PT every day"""
        try:
            logger.info("Setting up daily trivia scheduler...")

            pacific_tz = pytz.timezone("America/Los_Angeles")

            while True:
                # Get current time in Pacific
                now_pacific = datetime.now(pacific_tz)

                # Calculate next 8 PM PT
                next_8pm = now_pacific.replace(
                    hour=20, minute=0, second=0, microsecond=0
                )

                # If it's already past 8 PM today, schedule for tomorrow
                if now_pacific >= next_8pm:
                    next_8pm += timedelta(days=1)

                # Calculate seconds until next 8 PM PT
                seconds_until_next = (next_8pm - now_pacific).total_seconds()

                logger.info(f"Next daily trivia scheduled for: {next_8pm}")
                logger.info(f"Waiting {seconds_until_next / 3600:.1f} hours...")

                # Wait until next 8 PM PT
                await asyncio.sleep(seconds_until_next)

                # Send the daily trivia post
                await self.send_daily_trivia_post(bot, channel_id)

                # Wait a bit before calculating the next run
                await asyncio.sleep(60)  # Wait 1 minute to avoid rapid re-scheduling

        except Exception as e:
            logger.error(f"Error in daily trivia scheduler: {e}")
            # Restart the scheduler after a delay
            await asyncio.sleep(300)  # Wait 5 minutes before restarting
            await self.schedule_daily_trivia(bot, channel_id)


async def schedule_daily_trivia(bot, channel_id: int):
    """Main function to start the daily trivia scheduler"""
    scheduler = TriviaScheduler()
    await scheduler.schedule_daily_trivia(bot, channel_id)
