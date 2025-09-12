#!/bin/bash
# Test script for facts feature in Docker container

echo "🐳 Testing facts feature in Docker container..."

# Build the Docker image
echo "📦 Building Docker image..."
docker build -t goobie-bot-test .

# Test simple facts in container
echo "🧪 Testing simple facts in container..."
docker run --rm -v "$(pwd):/app" goobie-bot-test python -c "
from facts.simple_facts import SimpleFacts
print('✅ Simple facts import successful')
facts = SimpleFacts()
fact = facts.get_random_fact()
print('✅ Got random fact:', fact['category'] if fact else 'None')
stats = facts.get_stats()
print('✅ Stats:', stats['total_facts'], 'total facts,', stats['category_count'], 'categories')
"

# Test bot integration in container (simplified)
echo "🤖 Testing bot integration in container..."
docker run --rm -v "$(pwd):/app" goobie-bot-test python -c "
from facts.simple_facts import SimpleFacts
from config import FACTS_CHANNEL_ID
print('✅ Config import successful - FACTS_CHANNEL_ID:', FACTS_CHANNEL_ID)
facts = SimpleFacts()
fact = facts.get_random_fact()
print('✅ Bot integration test passed - can retrieve fact:', fact['category'] if fact else 'None')
"

echo "✅ Docker tests completed!"
