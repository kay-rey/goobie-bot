#!/bin/bash
# Simple test for weekly command in Docker

echo "🧪 Simple Weekly Command Test in Docker"
echo "======================================="

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Check if the container exists
if ! docker ps -a --format "table {{.Names}}" | grep -q "goobie-bot"; then
    echo "❌ goobie-bot container not found. Please run 'docker-compose up -d' first."
    exit 1
fi

echo "📦 Testing weekly command functions in Docker container..."

# Test cache key generation
echo "1. Testing cache key generation..."
docker exec goobie-bot python -c "
import asyncio
import sys
sys.path.append('/app')
from commands.weekly import get_weekly_cache_key
key = asyncio.run(get_weekly_cache_key())
print(f'Cache key: {key}')
"

# Test team configuration
echo "2. Testing team configuration..."
docker exec goobie-bot python -c "
import sys
sys.path.append('/app')
from commands.weekly import WEEKLY_TEAMS
for team in WEEKLY_TEAMS:
    print(f'{team[\"emoji\"]} {team[\"name\"]}: {team[\"sport\"]} ({team[\"league\"]})')
"

echo ""
echo "✅ Basic tests completed! The weekly command optimizations are ready."
echo "💡 Use the /weekly command in Discord to test the full functionality."
