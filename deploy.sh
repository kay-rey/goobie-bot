#!/bin/bash

# Goobie Bot Deployment Script
# This script handles the complete deployment process for the Raspberry Pi

set -e  # Exit on any error

echo "🚀 Starting goobie-bot deployment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the right directory
if [ ! -f "docker-compose.prod.yml" ]; then
    print_error "docker-compose.prod.yml not found. Please run this script from the goobie-bot directory."
    exit 1
fi

# Navigate to bot directory (in case we're not already there)
cd "$(dirname "$0")"
print_status "Working directory: $(pwd)"

# Pull latest changes
print_status "📥 Pulling latest changes from GitHub..."
if git pull origin main; then
    print_success "Git pull completed"
else
    print_warning "Git pull failed or no changes available"
fi

# Stop current bot
print_status "🛑 Stopping current bot containers..."
if docker-compose -f docker-compose.prod.yml down; then
    print_success "Bot stopped successfully"
else
    print_warning "No running containers to stop"
fi

# Remove old images to force rebuild
print_status "🧹 Cleaning up old images..."
docker rmi goobie-bot 2>/dev/null || true
docker rmi goobie-bot:latest 2>/dev/null || true
docker system prune -f --volumes 2>/dev/null || true

# Build the image
print_status "🔨 Building bot image for ARMv7 (Pi 2)..."
if docker build --platform linux/arm/v7 -t goobie-bot .; then
    print_success "Image built successfully"
else
    print_error "Image build failed"
    exit 1
fi

# Start the bot
print_status "🚀 Starting bot with optimized settings..."
if docker-compose -f docker-compose.prod.yml up -d; then
    print_success "Bot started successfully"
else
    print_error "Failed to start bot"
    exit 1
fi

# Wait for bot to start
print_status "⏳ Waiting for bot to initialize..."
sleep 15

# Check bot status
print_status "✅ Checking bot status..."
echo ""
echo "📊 Container Status:"
docker ps | grep goobie-bot-prod || print_warning "Bot container not found in running containers"

echo ""
echo "📋 Recent Logs (last 20 lines):"
docker logs goobie-bot-prod --tail 20 2>/dev/null || print_warning "Could not retrieve logs"

echo ""
echo "💾 Resource Usage:"
docker stats goobie-bot-prod --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}" 2>/dev/null || print_warning "Could not retrieve resource stats"

# Test resource monitoring
print_status "🔍 Testing resource monitoring..."
if docker exec goobie-bot-prod python -c "
from config import resource_monitor
mem = resource_monitor.get_memory_usage()
cpu = resource_monitor.get_cpu_usage()
print(f'Memory: {mem[\"percent\"]:.1f}% ({mem[\"used_mb\"]:.1f}MB used)')
print(f'CPU: {cpu:.1f}%')
print(f'Available: {mem[\"available_mb\"]:.1f}MB')
" 2>/dev/null; then
    print_success "Resource monitoring working"
else
    print_warning "Resource monitoring test failed"
fi

echo ""
print_success "🎉 Deployment complete!"
print_status "Bot is running with optimized settings:"
print_status "  • Memory limit: 768MB (75% of Pi's 1GB RAM)"
print_status "  • CPU limit: 2 cores (50% of quad-core)"
print_status "  • Cache size: 100 entries"
print_status "  • Log level: INFO"
echo ""
print_status "To check logs: docker logs goobie-bot-prod -f"
print_status "To stop bot: docker-compose -f docker-compose.prod.yml down"
print_status "To restart: ./deploy.sh"
