#!/usr/bin/env python3
"""
Test script for the simplified facts feature
Tests JSON-based approach without database complexity
"""

import sys
import os
import asyncio
import logging
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from facts.simple_facts import SimpleFacts

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def test_simple_facts():
    """Test the simple facts functionality"""
    try:
        logger.info("🧪 Testing simple facts...")

        # Initialize facts
        facts = SimpleFacts()

        # Test getting a random fact
        logger.info("Getting random fact...")
        fact = facts.get_random_fact()
        if fact:
            logger.info(
                f"✅ Got random fact: {fact['category']} - {fact['fact'][:50]}..."
            )
        else:
            logger.error("❌ No random fact retrieved")
            return False

        # Test getting facts by category
        logger.info("Testing category facts...")
        categories = facts.get_all_categories()
        logger.info(f"✅ Available categories: {categories}")

        if categories:
            category_fact = facts.get_fact_by_category(categories[0])
            if category_fact:
                logger.info(
                    f"✅ Got {categories[0]} fact: {category_fact['fact'][:50]}..."
                )
            else:
                logger.warning(f"⚠️ No facts found for category {categories[0]}")

        # Test search functionality
        logger.info("Testing search functionality...")
        search_results = facts.search_facts("Dodgers")
        logger.info(f"✅ Found {len(search_results)} facts matching 'Dodgers'")

        # Test statistics
        logger.info("Getting statistics...")
        stats = facts.get_stats()
        if stats:
            logger.info(
                f"✅ Stats: {stats['total_facts']} total facts, {stats['category_count']} categories"
            )
            for category, count in stats["categories"].items():
                logger.info(f"   - {category}: {count} facts")
        else:
            logger.error("❌ No stats retrieved")
            return False

        logger.info("🎉 All simple facts tests passed!")
        return True

    except Exception as e:
        logger.error(f"❌ Simple facts test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_commands_integration():
    """Test the commands integration"""
    try:
        logger.info("🧪 Testing commands integration...")

        # Test importing commands
        from facts.simple_commands import SimpleFactsCommands

        logger.info("✅ Commands import successful")

        # Test creating commands instance
        class MockBot:
            pass

        bot = MockBot()
        commands = SimpleFactsCommands(bot)

        # Test that commands can access facts
        fact = commands.facts.get_random_fact()
        if fact:
            logger.info(f"✅ Commands can access facts: {fact['category']}")
        else:
            logger.error("❌ Commands cannot access facts")
            return False

        logger.info("🎉 All commands integration tests passed!")
        return True

    except Exception as e:
        logger.error(f"❌ Commands integration test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    logger.info("🚀 Starting simplified facts feature tests...")

    # Test simple facts
    facts_success = test_simple_facts()

    # Test commands integration
    commands_success = test_commands_integration()

    if facts_success and commands_success:
        logger.info("🎉 All tests passed! Simplified facts feature is ready to use.")
        logger.info("📝 Benefits of simplified approach:")
        logger.info("   - No database complexity")
        logger.info("   - Faster startup time")
        logger.info("   - Easier to maintain")
        logger.info("   - No SQLite dependencies")
        logger.info("   - JSON file is human-readable")
        return 0
    else:
        logger.error("❌ Some tests failed. Please check the logs.")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
