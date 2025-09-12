"""
Simple facts module for goobie-bot
Uses JSON file directly without database complexity
"""

import json
import random
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class SimpleFacts:
    """Simple facts manager using JSON file"""

    def __init__(self, json_path: str = "facts/data/facts.json"):
        self.json_path = json_path
        self.facts = []
        self.load_facts()

    def load_facts(self):
        """Load facts from JSON file"""
        try:
            facts_file = Path(self.json_path)
            if not facts_file.exists():
                logger.error(f"Facts JSON file not found: {self.json_path}")
                return

            with open(facts_file, "r") as f:
                data = json.load(f)

            self.facts = data.get("facts", [])
            logger.info(f"Loaded {len(self.facts)} facts from JSON")

        except Exception as e:
            logger.error(f"Error loading facts from JSON: {e}")

    def get_random_fact(self):
        """Get a random fact from the loaded facts"""
        if not self.facts:
            logger.error("No facts available")
            return None

        fact = random.choice(self.facts)
        logger.debug(f"Selected random fact: {fact['category']}")
        return fact

    def get_fact_by_category(self, category: str):
        """Get a random fact from a specific category"""
        if not self.facts:
            return None

        category_facts = [
            f for f in self.facts if f.get("category", "").lower() == category.lower()
        ]
        if not category_facts:
            return None

        return random.choice(category_facts)

    def get_all_categories(self):
        """Get list of all available categories"""
        if not self.facts:
            return []

        categories = list(set(fact.get("category", "") for fact in self.facts))
        return sorted(categories)

    def get_stats(self):
        """Get basic statistics about facts"""
        if not self.facts:
            return {"total_facts": 0, "categories": []}

        categories = {}
        for fact in self.facts:
            category = fact.get("category", "Unknown")
            categories[category] = categories.get(category, 0) + 1

        return {
            "total_facts": len(self.facts),
            "categories": categories,
            "category_count": len(categories),
        }

    def search_facts(self, search_term: str):
        """Search facts by text content"""
        if not self.facts or not search_term:
            return []

        search_term = search_term.lower()
        matching_facts = []

        for fact in self.facts:
            if (
                search_term in fact.get("fact", "").lower()
                or search_term in fact.get("category", "").lower()
            ):
                matching_facts.append(fact)

        return matching_facts
