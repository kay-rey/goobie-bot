#!/bin/bash

# Development script for goobie-bot
# This script helps manage the bot in development mode

case "$1" in
    "start")
        echo "🚀 Starting goobie-bot in development mode..."
        docker-compose up -d
        echo "✅ Bot started! Check logs with: ./dev.sh logs"
        ;;
    "stop")
        echo "🛑 Stopping goobie-bot..."
        docker-compose down
        echo "✅ Bot stopped!"
        ;;
    "restart")
        echo "🔄 Restarting goobie-bot..."
        docker-compose restart
        echo "✅ Bot restarted!"
        ;;
    "logs")
        echo "📋 Showing bot logs (Ctrl+C to exit)..."
        docker-compose logs -f
        ;;
    "build")
        echo "🔨 Building goobie-bot..."
        docker-compose build
        echo "✅ Bot built!"
        ;;
    "shell")
        echo "🐚 Opening shell in bot container..."
        docker-compose exec goobie-bot /bin/bash
        ;;
    "status")
        echo "📊 Bot status:"
        docker-compose ps
        ;;
    *)
        echo "🤖 Goobie-Bot Development Helper"
        echo ""
        echo "Usage: ./dev.sh [command]"
        echo ""
        echo "Commands:"
        echo "  start    - Start the bot in development mode"
        echo "  stop     - Stop the bot"
        echo "  restart  - Restart the bot"
        echo "  logs     - Show bot logs (live)"
        echo "  build    - Rebuild the bot image"
        echo "  shell    - Open shell in bot container"
        echo "  status   - Show bot status"
        echo ""
        echo "Development mode includes:"
        echo "  - Live code reloading (volume mounting)"
        echo "  - Automatic restarts on container failure"
        echo "  - Easy log viewing"
        ;;
esac
