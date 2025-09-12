# 🤖 Goobie-Bot

> **The Ultimate Discord Bot for LA Sports Statistics & Entertainment**  
> _Built with ❤️ for LA sports fans and Discord communities_

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![Discord.py](https://img.shields.io/badge/Discord.py-2.3.2-7289da.svg)](https://discordpy.readthedocs.io/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ed.svg)](https://docker.com)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Version](https://img.shields.io/badge/Version-0.2.0--beta-blue.svg)](VERSION)

<div align="center">
  <img src="https://raw.githubusercontent.com/kay-rey/goobie-bot/main/assets/images/goobiebotla.png" alt="Goobie-Bot LA Skyline Logo" width="200" height="200">
</div>

## 🌟 Overview

Goobie-Bot is a feature-rich Discord bot designed specifically for LA sports fans, providing real-time game data, interactive trivia, daily facts, and comprehensive team information. Currently supporting **LA Galaxy** (MLS), **Lakers** (NBA), **Dodgers** (MLB), and **Rams** (NFL), with plans to expand to the **Kings** (NHL).

Built with a modular, scalable architecture and containerized for easy deployment, Goobie-Bot brings the excitement of LA sports directly to your Discord server.

## ✨ Features

### 🏆 **Sports Statistics & Game Data**

- **Real-time Game Information** - Upcoming matches for all LA teams
- **Weekly Schedules** - Comprehensive weekly match schedules
- **Rich Discord Embeds** - Beautiful embeds with team logos and venue images
- **Automatic Notifications** - Weekly match notifications every Monday at 1 PM PT
- **Multi-Team Support** - Galaxy, Lakers, Dodgers, and Rams

### 🧠 **Interactive Trivia System**

- **Daily Trivia Questions** - Posted every day at 8 PM PT
- **Interactive Buttons** - Start Trivia, Leaderboard, How to Play
- **Private DM Sessions** - Questions sent directly to users
- **30-Second Timer** - Visual countdown with timeout enforcement
- **Scoring System** - Points based on difficulty and speed
- **Leaderboards** - Track user stats and rankings
- **Database Storage** - SQLite database for persistent data

### 📚 **Daily Facts Feature**

- **Daily Sports Facts** - Posted every day at 12 PM PT
- **Random Fact Retrieval** - On-demand fact commands
- **Usage Statistics** - Track fact engagement and usage
- **Smart Scheduling** - Prevents duplicate posts

### ⚡ **Performance & Reliability**

- **Intelligent Caching** - Optimized API calls with Redis-like caching
- **Rate Limit Management** - Respectful API usage
- **Error Handling** - Graceful error recovery and logging
- **Docker Ready** - Containerized for easy deployment
- **ARM Support** - Raspberry Pi compatible

### 🏗️ **Developer Features**

- **Modular Architecture** - Clean, scalable codebase
- **Comprehensive Testing** - Full test suite with Docker integration
- **Environment Configuration** - Flexible configuration management
- **Logging System** - Structured logging for debugging
- **API Integrations** - ESPN and TheSportsDB APIs

## 🚀 Quick Start

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/install/)
- A Discord Bot Token ([How to get one](https://discord.com/developers/applications))
- Python 3.9+ (for local development)

### 1. Clone the Repository

```bash
git clone https://github.com/kay-rey/goobie-bot.git
cd goobie-bot
```

### 2. Environment Configuration

Create a `.env` file in the project root:

```bash
# Required: Discord Bot Configuration
DISCORD_TOKEN=your_discord_bot_token_here

# Optional: Channel IDs for automated features
WEEKLY_NOTIFICATIONS_CHANNEL_ID=123456789012345678
TRIVIA_CHANNEL_ID=123456789012345678
FACTS_CHANNEL_ID=123456789012345678

# Optional: Admin user IDs (comma-separated)
ADMIN_USER_IDS=123456789012345678,987654321098765432
```

### 3. Docker Deployment

#### Development Mode

```bash
# Build and start with live reloading
./dev.sh build
./dev.sh start

# View logs
./dev.sh logs

# Stop the bot
./dev.sh stop
```

#### Production Mode

```bash
# Use production configuration
docker-compose -f docker-compose.prod.yml up -d
```

### 4. Bot Invitation

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Select your bot application
3. Navigate to OAuth2 → URL Generator
4. Select the following scopes:
   - `bot`
   - `applications.commands`
5. Select the following permissions:
   - Send Messages
   - Use Slash Commands
   - Embed Links
   - Attach Files
   - Read Message History
6. Copy the generated URL and invite the bot to your server

## 🎮 Commands

### Slash Commands

#### `/nextgame [team]`

Get the next upcoming game for any LA team with detailed information:

- 📅 Match date and time (converted to Pacific Time)
- 🏟️ Venue information and stadium image
- 🏆 Team logos and match details
- 📊 Competition information

**Supported Teams:** Galaxy, Lakers, Dodgers, Rams

#### `/weekly`

Get a comprehensive weekly schedule for all LA teams:

- 📅 All matches for the current week (Monday to Sunday)
- 🏟️ Venue information for each match
- ⚾🏀⚽🏈 Team-specific colors and emojis
- 🕐 Automatic weekly notifications every Monday at 1 PM PT

#### `/trivia`

View the trivia leaderboard and your personal statistics:

- 🏆 Top 10 players leaderboard
- 📊 Your personal stats and ranking
- 🎯 Accuracy and streak tracking
- 📈 Score history and achievements

#### `/fact`

Get a random LA sports fact on demand.

### Text Commands (Admin Only)

#### `!sync`

Synchronize slash commands with Discord.

#### `!cache [action]`

Manage the bot's cache system:

- `stats` - View cache performance statistics
- `clear` - Clear all cache entries
- `cleanup` - Remove expired cache entries

#### `!trivia-admin [action]`

Manage the trivia system:

- `stats` - View trivia system statistics
- `reset` - Reset daily trivia (emergency use)

#### `!factstats`

View fact system statistics and usage data.

## 🏗️ Architecture

### Project Structure

```
goobie-bot/
├── 🤖 bot.py                    # Main Discord bot application
├── ⚙️ config.py                 # Configuration and environment management
├── 📁 api/                      # API integration layer
│   ├── espn/                    # ESPN API functions
│   │   ├── games.py             # Game data fetching
│   │   └── teams.py             # Team information
│   ├── sportsdb/                # TheSportsDB API functions
│   │   ├── teams.py             # Team data and logos
│   │   └── venues.py            # Venue information
│   ├── processors/              # Data processing
│   │   └── game_processor.py    # Game data processing & embeds
│   ├── cache.py                 # Caching system
│   └── http_client.py           # HTTP client management
├── 📁 commands/                 # Discord command implementations
│   ├── nextgame.py              # Next game command
│   ├── weekly.py                # Weekly schedule command
│   └── cache.py                 # Cache management commands
├── 📁 trivia/                   # Trivia system
│   ├── commands.py              # Trivia slash commands
│   ├── database.py              # SQLite database operations
│   ├── scheduler.py             # Daily posting automation
│   ├── ui.py                    # Discord UI components
│   └── data/
│       ├── questions.json       # Trivia questions database
│       └── trivia.db            # SQLite database
├── 📁 facts/                    # Daily facts system
│   ├── simple_commands.py       # Fact commands
│   ├── simple_scheduler.py      # Daily posting scheduler
│   └── data/
│       ├── facts.json           # Facts database
│       └── facts.db             # SQLite database
├── 📁 events/                   # Discord event handlers
│   ├── ready.py                 # Bot ready event
│   ├── message.py               # Message event handler
│   └── errors.py                # Error handling
├── 📁 scheduler/                # Background schedulers
│   └── weekly_matches.py        # Weekly match notifications
├── 📁 utils/                    # Utility functions
│   └── permissions.py           # Permission management
├── 📁 tests/                    # Test suite
├── 📁 scripts/                  # Utility scripts
├── 📁 docs/                     # Documentation
├── 🐳 Dockerfile                # Container configuration
├── 🐙 docker-compose.yml        # Development environment
├── 🐙 docker-compose.prod.yml   # Production environment
└── 🚀 dev.sh                    # Development helper script
```

### API Integrations

- **ESPN API** - Real-time game data and match information
- **TheSportsDB API** - Team logos, stadium images, and detailed team data

### Database Systems

- **SQLite** - Lightweight database for trivia and facts data
- **In-Memory Caching** - High-performance caching for API responses

## 🛠️ Development

### Development Workflow

```bash
# Build the container
./dev.sh build

# Start development environment
./dev.sh start

# View logs
./dev.sh logs

# Restart the bot
./dev.sh restart

# Stop the bot
./dev.sh stop
```

### Code Standards

- **Python Style**: Follow PEP 8 guidelines
- **Logging**: Use `logger.info()`, `logger.error()` instead of `print()`
- **Type Hints**: Use type hints where appropriate
- **f-strings**: Use f-strings for string formatting
- **Async/Await**: Properly handle asynchronous operations
- **Import Style**: Prefer importing from main modules over relative imports

### Testing

#### Run All Tests

```bash
# Run tests inside Docker container
docker-compose exec goobie-bot python -m pytest tests/

# Or use the test script
./tests/run_tests.sh
```

#### Cache Testing

```bash
# Run all Docker cache tests
./scripts/test-docker-cache.sh

# Run simple cache tests
python tests/test_cache_simple.py

# Run cache tests in Docker
docker run --rm -v "$(pwd):/app" -w /app goobie-bot:latest python tests/test_cache_docker.py
```

#### Trivia Testing

```bash
# Test trivia system
./scripts/test-trivia-docker.sh

# Manual trivia trigger
./scripts/manual-trigger-trivia.sh
```

#### Facts Testing

```bash
# Test facts system
./scripts/test_facts_docker.sh

# Test individual components
python scripts/test_facts.py
```

### Adding New Features

1. **New Teams**: Add team data to the appropriate API modules
2. **New Commands**: Add slash commands in the `commands/` directory
3. **New APIs**: Create new modules in the `api/` directory
4. **New Processors**: Add data processing logic in `api/processors/`

## 🐳 Docker Deployment

### Development Environment

```bash
# Build and start with live reloading
docker-compose up -d

# View logs
docker-compose logs -f goobie-bot

# Stop
docker-compose down
```

### Production Environment

```bash
# Use production configuration
docker-compose -f docker-compose.prod.yml up -d

# View production logs
docker-compose -f docker-compose.prod.yml logs -f
```

### Docker Commands

```bash
# Build the image
docker build -t goobie-bot .

# Run the container
docker run -d --name goobie-bot --env-file .env goobie-bot

# View logs
docker logs goobie-bot

# Execute commands in container
docker exec -it goobie-bot /bin/bash
```

## 📊 Performance & Monitoring

### Caching System

The bot implements an intelligent caching system to optimize API calls:

- **Cache Duration**: 5 minutes for game data, 1 hour for team data
- **Memory Management**: Automatic cleanup of expired entries
- **Performance Metrics**: Track cache hit rates and response times

### Rate Limiting

- **ESPN API**: No official rate limits, but respectful usage
- **TheSportsDB API**: 30 requests per minute (free tier)
- **Discord API**: Respects Discord's rate limits

### Logging

The bot uses structured logging with the following levels:

- `INFO`: General information and status updates
- `WARNING`: Non-critical issues
- `ERROR`: Error conditions that don't stop the bot
- `CRITICAL`: Critical errors that may stop the bot

## 🔧 Configuration

### Environment Variables

| Variable                          | Description                      | Required | Default |
| --------------------------------- | -------------------------------- | -------- | ------- |
| `DISCORD_TOKEN`                   | Discord bot token                | ✅ Yes   | -       |
| `WEEKLY_NOTIFICATIONS_CHANNEL_ID` | Channel for weekly notifications | ❌ No    | -       |
| `TRIVIA_CHANNEL_ID`               | Channel for daily trivia         | ❌ No    | -       |
| `FACTS_CHANNEL_ID`                | Channel for daily facts          | ❌ No    | -       |
| `ADMIN_USER_IDS`                  | Admin user IDs (comma-separated) | ❌ No    | -       |

### Bot Permissions

The bot requires the following Discord permissions:

- **Send Messages** - Post messages and embeds
- **Use Slash Commands** - Execute slash commands
- **Embed Links** - Create rich embeds
- **Attach Files** - Upload images and files
- **Read Message History** - Access message history for context

## 🚀 Roadmap

### ✅ Completed Features

- [x] **LA Sports Expansion** - Support for Galaxy, Lakers, Dodgers, and Rams
- [x] **Weekly Notifications** - Automatic weekly match notifications
- [x] **Daily Trivia System** - Interactive trivia with scoring and leaderboards
- [x] **Daily Facts System** - Automated daily sports facts
- [x] **Rich Discord Embeds** - Beautiful embeds with team branding
- [x] **Docker Containerization** - Full Docker support with ARM compatibility
- [x] **Caching System** - Intelligent API response caching
- [x] **Comprehensive Testing** - Full test suite with Docker integration

### 🔄 In Progress

- [ ] **Los Angeles Kings Support** - NHL team integration
- [ ] **Enhanced Error Handling** - Improved error recovery and user feedback

### 📋 Planned Features

- [ ] **Live Score Updates** - Real-time score updates during matches
- [ ] **Player Statistics** - Individual player stats and information
- [ ] **Match Predictions** - AI-powered match outcome predictions
- [ ] **Customizable Alerts** - User-defined match notifications
- [ ] **Multi-Team Support** - Support for other MLS teams
- [ ] **Mobile Optimization** - Enhanced mobile Discord experience
- [ ] **Analytics Dashboard** - Bot usage analytics and insights

## 🤝 Contributing

We welcome contributions from the community! Here's how to get started:

### Getting Started

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Make** your changes following our code standards
4. **Test** your changes thoroughly
5. **Commit** your changes with conventional commits
6. **Push** to your branch (`git push origin feature/amazing-feature`)
7. **Open** a Pull Request

### Commit Message Format

We use [Conventional Commits](https://www.conventionalcommits.org/):

```
type(scope): description

feat(api): add new team support
fix(bot): resolve command error
docs(readme): update installation guide
chore(deps): update dependencies
test(trivia): add trivia system tests
```

### Development Guidelines

- Follow PEP 8 style guidelines
- Use type hints where appropriate
- Write comprehensive tests for new features
- Update documentation for new features
- Use meaningful variable and function names
- Handle errors gracefully with proper logging

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **ESPN** for providing comprehensive sports data
- **TheSportsDB** for team logos and venue information
- **Discord.py** community for the excellent library
- **LA Sports Teams** for being amazing to support! ⚽🏀⚾🏈

## 📞 Support

Having issues? Here's how to get help:

### Troubleshooting

1. **Check the logs**: `./dev.sh logs` or `docker logs goobie-bot`
2. **Restart the bot**: `./dev.sh restart`
3. **Verify configuration**: Check your `.env` file
4. **Test connectivity**: Ensure bot has proper Discord permissions

### Getting Help

1. **Check the documentation** in the `docs/` directory
2. **Search existing issues** on GitHub
3. **Open a new issue** with detailed information
4. **Join our Discord** server (coming soon!)

### Common Issues

- **Bot not responding**: Check Discord token and permissions
- **Commands not syncing**: Use `!sync` command or restart bot
- **Trivia not posting**: Verify `TRIVIA_CHANNEL_ID` is set correctly
- **Facts not posting**: Verify `FACTS_CHANNEL_ID` is set correctly

---

**Made with ⚽🏀⚾🏈 and ❤️ for LA sports fans**

_Go Galaxy! Go Lakers! Go Dodgers! Go Rams! 🌟_
