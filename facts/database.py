"""
Database module for facts feature
Handles storage and retrieval of daily facts
"""

import sqlite3
import json
import logging
from pathlib import Path
from datetime import datetime
import pytz

logger = logging.getLogger(__name__)


class FactsDatabase:
    """Manages facts database operations"""

    def __init__(self, db_path: str = "facts/data/facts.db"):
        self.db_path = db_path
        # Ensure the directory exists (important for Docker)
        import os

        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self._init_database()

    def _init_database(self):
        """Initialize the facts database with required tables"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                # Create facts table
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS facts (
                        id INTEGER PRIMARY KEY,
                        fact TEXT NOT NULL,
                        category TEXT NOT NULL,
                        emoji TEXT NOT NULL,
                        used_count INTEGER DEFAULT 0,
                        last_used TIMESTAMP
                    )
                    """
                )

                # Create daily_facts table to track daily posts
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS daily_facts (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        channel_id INTEGER NOT NULL,
                        message_id INTEGER NOT NULL,
                        fact_id INTEGER NOT NULL,
                        posted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (fact_id) REFERENCES facts (id)
                    )
                    """
                )

                conn.commit()
                logger.info("Facts database initialized successfully")

        except Exception as e:
            logger.error(f"Error initializing facts database: {e}")

    def get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path)

    def load_facts_from_json(self, json_path: str = "facts/data/facts.json"):
        """Load facts from JSON file into database"""
        try:
            facts_file = Path(json_path)
            if not facts_file.exists():
                logger.error(f"Facts JSON file not found: {json_path}")
                return False

            with open(facts_file, "r") as f:
                data = json.load(f)

            with self.get_connection() as conn:
                cursor = conn.cursor()

                # Clear existing facts
                cursor.execute("DELETE FROM facts")

                # Insert facts from JSON
                for fact_data in data["facts"]:
                    cursor.execute(
                        """
                        INSERT INTO facts (id, fact, category, emoji)
                        VALUES (?, ?, ?, ?)
                        """,
                        (
                            fact_data["id"],
                            fact_data["fact"],
                            fact_data["category"],
                            fact_data["emoji"],
                        ),
                    )

                conn.commit()
                logger.info(f"Loaded {len(data['facts'])} facts from JSON")
                return True

        except Exception as e:
            logger.error(f"Error loading facts from JSON: {e}")
            return False

    def get_random_fact(self):
        """Get a random fact that hasn't been used recently"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                # Get current time in Pacific timezone
                pacific_tz = pytz.timezone("America/Los_Angeles")
                now_pacific = datetime.now(pacific_tz)

                # Get facts that haven't been used in the last 7 days
                from datetime import timedelta

                seven_days_ago = now_pacific - timedelta(days=7)

                cursor.execute(
                    """
                    SELECT id, fact, category, emoji, used_count
                    FROM facts
                    WHERE last_used IS NULL OR last_used < ?
                    ORDER BY used_count ASC, RANDOM()
                    LIMIT 1
                    """,
                    (seven_days_ago,),
                )

                result = cursor.fetchone()
                if result:
                    return {
                        "id": result[0],
                        "fact": result[1],
                        "category": result[2],
                        "emoji": result[3],
                        "used_count": result[4],
                    }

                # If no unused facts, get the least recently used
                cursor.execute(
                    """
                    SELECT id, fact, category, emoji, used_count
                    FROM facts
                    ORDER BY last_used ASC, used_count ASC, RANDOM()
                    LIMIT 1
                    """
                )

                result = cursor.fetchone()
                if result:
                    return {
                        "id": result[0],
                        "fact": result[1],
                        "category": result[2],
                        "emoji": result[3],
                        "used_count": result[4],
                    }

                return None

        except Exception as e:
            logger.error(f"Error getting random fact: {e}")
            return None

    def mark_fact_used(self, fact_id: int):
        """Mark a fact as used and update usage statistics"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                # Update fact usage
                pacific_tz = pytz.timezone("America/Los_Angeles")
                now_pacific = datetime.now(pacific_tz)

                cursor.execute(
                    """
                    UPDATE facts
                    SET used_count = used_count + 1, last_used = ?
                    WHERE id = ?
                    """,
                    (now_pacific, fact_id),
                )

                conn.commit()
                logger.debug(f"Marked fact {fact_id} as used")

        except Exception as e:
            logger.error(f"Error marking fact as used: {e}")

    def get_daily_fact_post(self):
        """Check if a daily fact was already posted today"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                # Get today's date in Pacific timezone
                pacific_tz = pytz.timezone("America/Los_Angeles")
                today = datetime.now(pacific_tz).date()

                cursor.execute(
                    """
                    SELECT id, channel_id, message_id, fact_id, posted_at
                    FROM daily_facts
                    WHERE DATE(posted_at) = ?
                    ORDER BY posted_at DESC
                    LIMIT 1
                    """,
                    (today,),
                )

                result = cursor.fetchone()
                if result:
                    return {
                        "id": result[0],
                        "channel_id": result[1],
                        "message_id": result[2],
                        "fact_id": result[3],
                        "posted_at": result[4],
                    }

                return None

        except Exception as e:
            logger.error(f"Error checking daily fact post: {e}")
            return None

    def create_daily_fact_post(self, channel_id: int, message_id: int, fact_id: int):
        """Record a daily fact post"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                cursor.execute(
                    """
                    INSERT INTO daily_facts (channel_id, message_id, fact_id)
                    VALUES (?, ?, ?)
                    """,
                    (channel_id, message_id, fact_id),
                )

                conn.commit()
                logger.info(
                    f"Recorded daily fact post: fact {fact_id} in channel {channel_id}"
                )

        except Exception as e:
            logger.error(f"Error creating daily fact post: {e}")

    def get_fact_stats(self):
        """Get statistics about fact usage"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                # Total facts
                cursor.execute("SELECT COUNT(*) FROM facts")
                total_facts = cursor.fetchone()[0]

                # Facts used today
                pacific_tz = pytz.timezone("America/Los_Angeles")
                today = datetime.now(pacific_tz).date()

                cursor.execute(
                    """
                    SELECT COUNT(*) FROM daily_facts
                    WHERE DATE(posted_at) = ?
                    """,
                    (today,),
                )
                facts_today = cursor.fetchone()[0]

                # Most used fact
                cursor.execute(
                    """
                    SELECT fact, used_count FROM facts
                    ORDER BY used_count DESC
                    LIMIT 1
                    """
                )
                most_used = cursor.fetchone()

                return {
                    "total_facts": total_facts,
                    "facts_today": facts_today,
                    "most_used": most_used,
                }

        except Exception as e:
            logger.error(f"Error getting fact stats: {e}")
            return None
