#!/bin/bash
# Debug trivia functionality in Docker container

echo "🔍 Debugging trivia functionality..."

# Check if container is running
if ! docker ps | grep -q goobie-bot; then
    echo "❌ goobie-bot container is not running. Please start it first with:"
    echo "   docker-compose up -d"
    exit 1
fi

echo "✅ Container is running"

# Check environment variables
echo ""
echo "🔧 Checking environment variables..."
docker exec goobie-bot printenv | grep -E "(DISCORD_TOKEN|TRIVIA_CHANNEL_ID|ADMIN_USER_IDS)" || echo "⚠️ Some environment variables not found"

# Check database
echo ""
echo "📊 Checking trivia database..."
docker exec goobie-bot python -c "
from trivia.database import TriviaDatabase
import sqlite3

db = TriviaDatabase()
with db.get_connection() as conn:
    cursor = conn.cursor()
    
    # Check tables
    cursor.execute(\"SELECT name FROM sqlite_master WHERE type='table'\")
    tables = cursor.fetchall()
    print(f'📋 Database tables: {[t[0] for t in tables]}')
    
    # Check question count
    cursor.execute('SELECT COUNT(*) FROM trivia_questions')
    question_count = cursor.fetchone()[0]
    print(f'📝 Questions in database: {question_count}')
    
    # Check daily posts
    cursor.execute('SELECT COUNT(*) FROM trivia_daily_posts WHERE date = date(\"now\")')
    daily_posts = cursor.fetchone()[0]
    print(f'📅 Daily posts today: {daily_posts}')
    
    # Check user attempts
    cursor.execute('SELECT COUNT(*) FROM trivia_attempts WHERE date = date(\"now\")')
    attempts = cursor.fetchone()[0]
    print(f'🎯 User attempts today: {attempts}')
"

# Check logs
echo ""
echo "📋 Recent bot logs:"
docker logs goobie-bot --tail 20

echo ""
echo "✅ Debug complete!"
