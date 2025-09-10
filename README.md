# 🤖 Goobie-Bot

> **The Ultimate Discord Bot for Sports Statistics**  
> _Built with ❤️ for LA Galaxy fans and sports enthusiasts_

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![Discord.py](https://img.shields.io/badge/Discord.py-2.3.2-7289da.svg)](https://discordpy.readthedocs.io/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ed.svg)](https://docker.com)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

<div align="center">
  <img src="https://raw.githubusercontent.com/kay-rey/goobie-bot/main/assets/images/goobiebotla.png" alt="Goobie-Bot LA Skyline Logo" width="200" height="200">
</div>

## 🌟 What is Goobie-Bot?

Goobie-Bot is a powerful Discord bot that brings real-time sports statistics and game information directly to your Discord server! Currently supporting **LA Galaxy** soccer, **Lakers** basketball, **Dodgers** baseball, and **Rams** football, with plans to expand to other LA-based teams like the **Kings**. Designed to scale for any team or sport.

### ✨ Features

- 🏆 **Real-time Game Data** - Get upcoming matches for LA Galaxy, Lakers, Dodgers, and Rams
- 🎨 **Rich Embeds** - Beautiful Discord embeds with team logos, stadium images, and match details
- ⚡ **Lightning Fast** - Optimized API calls and caching for instant responses
- 🐳 **Docker Ready** - Containerized for easy deployment on any platform
- 🏗️ **Modular Architecture** - Clean, scalable codebase ready for expansion
- 🔄 **Auto-sync Commands** - Slash commands that automatically sync with Discord

## 🚀 Quick Start

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/install/)
- A Discord Bot Token ([How to get one](https://discord.com/developers/applications))

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/goobie-bot.git
cd goobie-bot
```

### 2. Set Up Environment

Create a `.env` file in the project root:

```bash
# Discord Bot Configuration
DISCORD_TOKEN=your_discord_bot_token_here
```

### 3. Run with Docker

```bash
# Development mode (with live reloading)
./dev.sh build
./dev.sh start

# Or use docker-compose directly
docker-compose up -d
```

### 4. Invite Your Bot

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Select your bot application
3. Go to OAuth2 → URL Generator
4. Select "bot" and "applications.commands" scopes
5. Copy the generated URL and invite the bot to your server

## 🎮 Commands

### `/ping`

Test the bot's responsiveness and connection status.

### `/nextgame`

Get the next upcoming game for any LA team (Galaxy, Dodgers, Lakers, Rams) with:

- 📅 Match date and time (converted to Pacific Time)
- 🏟️ Venue information and stadium image
- 🏆 Team logos and match details
- 📊 Competition information

### `/weekly`

Get a comprehensive weekly schedule for all LA teams (Dodgers, Lakers, Galaxy, Rams) with:

- 📅 All matches for the current week (Monday to Sunday)
- 🏟️ Venue information for each match
- ⚾🏀⚽🏈 Team-specific colors and emojis
- 🕐 Automatic weekly notifications every Monday at 1pm PT

## 🏗️ Architecture

Goobie-Bot is built with a modular, scalable architecture:

```
goobie-bot/
├── 🤖 bot.py                 # Main Discord bot application
├── 📁 api/                   # API integration layer
│   ├── espn/                 # ESPN API functions
│   │   ├── games.py          # Game data fetching
│   │   └── teams.py          # Team information
│   ├── sportsdb/             # TheSportsDB API functions
│   │   ├── teams.py          # Team data and logos
│   │   └── venues.py         # Venue information
│   └── processors/           # Data processing
│       └── game_processor.py # Game data processing & embeds
├── 🐳 Dockerfile             # Container configuration
├── 🐙 docker-compose.yml     # Development environment
├── 🚀 dev.sh                 # Development helper script
└── 📋 requirements.txt       # Python dependencies
```

### 🔌 API Integrations

- **ESPN API** - Real-time game data and match information
- **TheSportsDB** - Team logos, stadium images, and detailed team data

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

### Adding New Features

1. **New Teams**: Add team data to the appropriate API modules
   - **LA Teams**: Lakers, Dodgers, Rams, Kings
   - **Other Teams**: Any team from any sport
2. **New Commands**: Add slash commands in `bot.py`
3. **New APIs**: Create new modules in the `api/` directory
4. **New Processors**: Add data processing logic in `api/processors/`

## 🐳 Docker Deployment

### Development

```bash
# Build and start with live reloading
docker-compose up -d

# View logs
docker-compose logs -f goobie-bot

# Stop
docker-compose down
```

### Production (Raspberry Pi)

```bash
# Use production configuration
docker-compose -f docker-compose.prod.yml up -d
```

## 📊 API Rate Limits

- **ESPN API**: No official rate limits, but be respectful
- **TheSportsDB**: 30 requests per minute (free tier)

## 🔧 Configuration

### Environment Variables

| Variable                          | Description                                         | Required |
| --------------------------------- | --------------------------------------------------- | -------- |
| `DISCORD_TOKEN`                   | Discord bot token                                   | ✅ Yes   |
| `WEEKLY_NOTIFICATIONS_CHANNEL_ID` | Channel ID for weekly notifications (Monday 1pm PT) | ❌ No    |

### Bot Permissions

The bot requires the following Discord permissions:

- Send Messages
- Use Slash Commands
- Embed Links
- Attach Files

## 🧪 Testing

```bash
# Run tests inside Docker container
docker-compose exec goobie-bot python -m pytest tests/

# Or use the test script
./tests/run_tests.sh
```

## 🚀 Future Roadmap

- [x] **LA Sports Expansion** - Add support for other LA-based teams:
  - 🏀 **Los Angeles Lakers** (NBA) ✅
  - ⚾ **Los Angeles Dodgers** (MLB) ✅
  - 🏈 **Los Angeles Rams** (NFL) ✅
  - 🏒 **Los Angeles Kings** (NHL)
- [x] **Weekly Notifications** - Automatic weekly match notifications ✅
- [ ] **Multi-Team Support** - Add support for other MLS teams
- [ ] **Live Scores** - Real-time score updates during matches
- [ ] **Player Statistics** - Individual player stats and information
- [ ] **Match Predictions** - AI-powered match outcome predictions
- [ ] **Customizable Alerts** - User-defined match notifications
- [ ] **Additional Sports** - Expand beyond soccer to other sports

## 🤝 Contributing

We welcome contributions! Here's how to get started:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Commit Message Format

We use [Conventional Commits](https://www.conventionalcommits.org/):

```
type(scope): description

feat(api): add new team support
fix(bot): resolve command error
docs(readme): update installation guide
```

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **ESPN** for providing comprehensive sports data
- **TheSportsDB** for team logos and venue information
- **Discord.py** community for the excellent library
- **LA Galaxy** for being an amazing team to support! ⚽

## 📞 Support

Having issues? Here's how to get help:

1. **Check the logs**: `./dev.sh logs`
2. **Restart the bot**: `./dev.sh restart`
3. **Open an issue** on GitHub
4. **Join our Discord** server (coming soon!)

---

**Made with ⚽ and ❤️ for the beautiful game**

_Go Galaxy! 🌟_
