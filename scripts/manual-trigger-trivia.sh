#!/bin/bash
# Manually trigger trivia post in Docker container

echo "🎯 Manually triggering trivia post..."

# Check if container is running
if ! docker ps | grep -q goobie-bot; then
    echo "❌ goobie-bot container is not running. Please start it first with:"
    echo "   docker-compose up -d"
    exit 1
fi

echo "✅ Container is running"

# Reset daily trivia first
echo "🔄 Resetting daily trivia..."
docker exec goobie-bot python reset_trivia_daily.py

# Trigger the trivia post
echo "🚀 Triggering trivia post..."
docker exec goobie-bot python test_trivia_manual.py

echo ""
echo "✅ Trivia post should now be visible in your Discord channel!"
echo "💡 Check the channel specified by TRIVIA_CHANNEL_ID in your .env file"
