#!/usr/bin/env python3
"""
Reset daily trivia script for goobie-bot
This script resets the daily trivia so you can test it multiple times
"""

import sys
import logging
from pathlib import Path
from datetime import date

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from config import setup_logging
from trivia.database import TriviaDatabase

# Set up logging
logger = setup_logging()


def reset_daily_trivia():
    """Reset daily trivia to allow testing multiple times"""
    try:
        logger.info("🔄 Resetting daily trivia...")

        db = TriviaDatabase()

        with db.get_connection() as conn:
            cursor = conn.cursor()

            # Delete today's daily post record
            cursor.execute(
                "DELETE FROM trivia_daily_posts WHERE date = ?", (date.today(),)
            )
            daily_posts_deleted = cursor.rowcount

            # Reset questions used today
            cursor.execute(
                "UPDATE trivia_questions SET used_date = NULL WHERE used_date = ?",
                (date.today(),),
            )
            questions_reset = cursor.rowcount

            # Delete today's attempts (optional - comment out if you want to keep user attempts)
            cursor.execute(
                "DELETE FROM trivia_attempts WHERE date = ?", (date.today(),)
            )
            attempts_deleted = cursor.rowcount

            conn.commit()

            logger.info(f"✅ Reset complete:")
            logger.info(f"  - Daily posts deleted: {daily_posts_deleted}")
            logger.info(f"  - Questions reset: {questions_reset}")
            logger.info(f"  - User attempts deleted: {attempts_deleted}")
            logger.info("🎯 You can now test trivia again!")

    except Exception as e:
        logger.error(f"❌ Error resetting daily trivia: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    reset_daily_trivia()
