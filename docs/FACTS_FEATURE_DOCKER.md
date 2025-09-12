# Daily Facts Feature - Docker Deployment

## Overview

The daily facts feature has been designed to work seamlessly with the existing Docker container setup. It automatically posts random LA sports facts every day at 12 PM PT.

## Docker Integration

### Database Storage

- **SQLite database**: `facts/data/facts.db` (created at runtime)
- **Facts data**: `facts/data/facts.json` (copied during build)
- **Persistent storage**: Database persists across container restarts via volume mounting

### Environment Variables

Add the following to your `.env` file:

```bash
# Daily facts channel (optional)
FACTS_CHANNEL_ID=your_discord_channel_id_here
```

### Docker Commands

#### Build and Run

```bash
# Build the image
docker build -t goobie-bot .

# Run with docker-compose (recommended)
docker-compose up -d

# Or run directly
docker run -d --name goobie-bot --env-file .env goobie-bot
```

#### Testing

```bash
# Run facts tests in Docker
./scripts/test_facts_docker.sh

# Test individual components
docker run --rm -v "$(pwd):/app" goobie-bot python scripts/test_facts.py
docker run --rm -v "$(pwd):/app" goobie-bot python scripts/test_facts_bot.py
```

#### Logs

```bash
# View bot logs
docker logs goobie-bot

# Follow logs in real-time
docker logs -f goobie-bot
```

## Features

### Commands Available

- `/fact` - Get a random LA sports fact (slash command)
- `/factstats` - View fact statistics (admin only)
- `!fact` - Get a random fact (text command)
- `!factstats` - View statistics (admin only, text command)

### Daily Scheduling

- **Time**: 12 PM PT every day
- **Channel**: Set via `FACTS_CHANNEL_ID` environment variable
- **Content**: Random fact about LA teams (Dodgers, Lakers, Galaxy, Rams, Kings)
- **Prevention**: No duplicate posts on the same day

### Database Management

- **Auto-initialization**: Database created on first run
- **Fact loading**: 30 facts loaded from JSON during startup
- **Usage tracking**: Prevents repeating facts for 7 days
- **Statistics**: Track total facts, daily usage, most used facts

## Troubleshooting

### Common Issues

1. **Facts not posting daily**

   - Check `FACTS_CHANNEL_ID` is set correctly
   - Verify bot has permissions in the target channel
   - Check logs for scheduler errors

2. **Database errors**

   - Ensure volume mounting is working (`-v "$(pwd):/app"`)
   - Check file permissions in the container
   - Verify SQLite is working properly

3. **Import errors**
   - Rebuild the Docker image: `docker build -t goobie-bot .`
   - Check all dependencies are installed
   - Verify Python path is correct

### Debug Commands

```bash
# Check if facts database exists
docker exec goobie-bot ls -la facts/data/

# View database contents
docker exec goobie-bot sqlite3 facts/data/facts.db "SELECT COUNT(*) FROM facts;"

# Check daily posts
docker exec goobie-bot sqlite3 facts/data/facts.db "SELECT * FROM daily_facts ORDER BY posted_at DESC LIMIT 5;"

# Test fact retrieval
docker exec goobie-bot python -c "from facts.database import FactsDatabase; db = FactsDatabase(); print(db.get_random_fact())"
```

## File Structure

```
facts/
├── __init__.py
├── database.py          # SQLite database operations
├── commands.py          # Discord commands
├── scheduler.py         # Daily posting scheduler
└── data/
    ├── facts.json       # 30 LA sports facts
    └── facts.db         # SQLite database (created at runtime)
```

## Monitoring

### Log Messages

- `Starting daily facts scheduler...` - Scheduler started
- `Next daily fact scheduled for: ...` - Next posting time
- `Daily fact post sent to channel ...` - Successful post
- `Daily fact already posted today` - Duplicate prevention

### Health Checks

- Database connectivity
- Fact retrieval functionality
- Scheduler status
- Channel permissions

## Production Deployment

### Environment Setup

1. Set `FACTS_CHANNEL_ID` in production `.env`
2. Ensure bot has proper permissions in target channel
3. Monitor logs for any errors
4. Set up log rotation for database files

### Backup Considerations

- Database file: `facts/data/facts.db`
- Facts data: `facts/data/facts.json`
- Consider backing up these files if you add custom facts

## Support

For issues with the facts feature in Docker:

1. Check the logs: `docker logs goobie-bot`
2. Run the test script: `./scripts/test_facts_docker.sh`
3. Verify environment variables are set correctly
4. Ensure the bot has proper Discord permissions
