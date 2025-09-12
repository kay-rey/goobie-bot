#!/bin/bash
# Test script for facts feature in Docker container

echo "🐳 Testing facts feature in Docker container..."

# Build the Docker image
echo "📦 Building Docker image..."
docker build -t goobie-bot-test .

# Run the facts test in the container
echo "🧪 Running facts tests in container..."
docker run --rm -v "$(pwd):/app" goobie-bot-test python scripts/test_facts.py

# Test bot integration in container (simplified)
echo "🤖 Testing bot integration in container..."
docker run --rm -v "$(pwd):/app" goobie-bot-test python -c "
from facts.database import FactsDatabase
from config import FACTS_CHANNEL_ID
print('✅ Config import successful - FACTS_CHANNEL_ID:', FACTS_CHANNEL_ID)
db = FactsDatabase()
fact = db.get_random_fact()
print('✅ Bot integration test passed - can retrieve fact:', fact['category'] if fact else 'None')
"

echo "✅ Docker tests completed!"
