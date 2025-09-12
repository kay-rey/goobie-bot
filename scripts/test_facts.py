#!/usr/bin/env python3
"""
Test script for the daily facts feature
Tests database operations and fact retrieval
"""

import sys
import os
import asyncio
import logging
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from facts.database import FactsDatabase

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def test_facts_database():
    """Test the facts database functionality"""
    try:
        logger.info("🧪 Testing facts database...")

        # Initialize database
        db = FactsDatabase("facts/data/facts.db")

        # Load facts from JSON
        logger.info("Loading facts from JSON...")
        success = db.load_facts_from_json()
        if not success:
            logger.error("❌ Failed to load facts from JSON")
            return False

        # Test getting a random fact
        logger.info("Getting random fact...")
        fact = db.get_random_fact()
        if fact:
            logger.info(
                f"✅ Got random fact: {fact['category']} - {fact['fact'][:50]}..."
            )
        else:
            logger.error("❌ No random fact retrieved")
            return False

        # Test marking fact as used
        logger.info("Marking fact as used...")
        db.mark_fact_used(fact["id"])
        logger.info("✅ Fact marked as used")

        # Test getting stats
        logger.info("Getting fact stats...")
        stats = db.get_fact_stats()
        if stats:
            logger.info(
                f"✅ Stats: {stats['total_facts']} total facts, {stats['facts_today']} posted today"
            )
        else:
            logger.error("❌ No stats retrieved")
            return False

        # Test daily post tracking
        logger.info("Testing daily post tracking...")
        daily_post = db.get_daily_fact_post()
        if daily_post is None:
            logger.info("✅ No daily post found (expected for new database)")
        else:
            logger.info(f"✅ Daily post found: {daily_post}")

        logger.info("🎉 All database tests passed!")
        return True

    except Exception as e:
        logger.error(f"❌ Database test failed: {e}")
        return False


def test_facts_commands():
    """Test the facts commands (without Discord bot)"""
    try:
        logger.info("🧪 Testing facts commands...")

        # Test database operations directly (commands use the same database)
        db = FactsDatabase("facts/data/facts.db")

        # Test getting a random fact
        fact = db.get_random_fact()
        if fact:
            logger.info(f"✅ Commands can retrieve fact: {fact['category']}")
        else:
            logger.error("❌ Commands cannot retrieve facts")
            return False

        logger.info("🎉 All command tests passed!")
        return True

    except Exception as e:
        logger.error(f"❌ Command test failed: {e}")
        return False


def main():
    """Run all tests"""
    logger.info("🚀 Starting facts feature tests...")

    # Test database
    db_success = test_facts_database()

    # Test commands
    cmd_success = test_facts_commands()

    if db_success and cmd_success:
        logger.info("🎉 All tests passed! Facts feature is ready to use.")
        return 0
    else:
        logger.error("❌ Some tests failed. Please check the logs.")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
