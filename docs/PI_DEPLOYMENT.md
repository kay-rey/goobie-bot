# Raspberry Pi Deployment Guide

## Quick Start

Your goobie-bot is now **Pi-optimized by default**! No separate files needed.

### 1. Automatic Deployment (Recommended)

The bot automatically deploys when you push to the main branch:

```bash
# Push changes to GitHub
git add .
git commit -m "feat: update bot"
git push origin main

# GitHub Actions automatically deploys to your Pi!
```

**Setup required:**

- Add GitHub Secrets: `PI_HOST`, `PI_USER`, `PI_SSH_KEY`
- Clone repository on Pi: `git clone https://github.com/kay-rey/goobie-bot.git`

### 2. Manual Deployment

```bash
# Build for ARMv6 (Pi Model B v1.1)
docker build --platform linux/arm/v6 -t goobie-bot .

# Run with Pi optimizations
docker run -d \
  --name goobie-bot \
  --platform linux/arm/v6 \
  --env-file .env \
  -e PI_MODE=true \
  -e MEMORY_LIMIT_MB=256 \
  -e CACHE_SIZE_LIMIT=50 \
  --restart unless-stopped \
  goobie-bot
```

### 3. Docker Compose (Production)

```bash
# Use production configuration
docker-compose -f docker-compose.prod.yml up -d
```

**Production settings:**

- **Platform**: `linux/arm/v6` (Pi Model B v1.1)
- **Memory limit**: 384MB (75% of 512MB RAM)
- **CPU limit**: 0.7 cores
- **Cache limit**: 50 entries
- **Health checks**: Memory monitoring

## Pi-Specific Features

The bot automatically detects Pi mode and enables:

- **Memory monitoring** with `psutil`
- **Resource health checks**
- **Optimized cache TTL** (shorter durations)
- **Memory limits** and eviction
- **Reduced logging** from noisy libraries

## Environment Variables

Add these to your `.env` file for Pi optimization:

```bash
# Pi mode (enables optimizations)
PI_MODE=true

# Memory limit in MB (default: 256 for Pi Model B v1.1)
MEMORY_LIMIT_MB=256

# Cache size limit (default: 50 for Pi Model B v1.1)
CACHE_SIZE_LIMIT=50

# Log level (default: WARNING for Pi)
LOG_LEVEL=WARNING
```

## Monitoring

```bash
# Check container status
docker ps

# View logs
docker logs goobie-bot

# Check memory usage
docker exec goobie-bot python -c "import psutil; print(f'Memory: {psutil.virtual_memory().percent}%')"

# Check cache stats
docker exec goobie-bot python -c "
from api.cache import get_cache_stats
import asyncio
stats = asyncio.run(get_cache_stats())
print(f'Cache hit rate: {stats[\"hit_rate\"]}%')
"
```

## Performance Expectations

| Pi Model                    | Memory Usage   | Status           |
| --------------------------- | -------------- | ---------------- |
| Pi 4 (4GB)                  | ~150-200MB     | ✅ Excellent     |
| Pi 4 (2GB)                  | ~100-150MB     | ✅ Great         |
| Pi 3 (1GB)                  | ~80-120MB      | ✅ Good          |
| **Pi Model B v1.1 (512MB)** | **~200-300MB** | **✅ Optimized** |

## GitHub Actions Setup

### 1. Add GitHub Secrets

Go to your repository → Settings → Secrets and variables → Actions:

- **`PI_HOST`** - Your Pi's IP address (e.g., `192.168.1.100`)
- **`PI_USER`** - Username (usually `pi`)
- **`PI_SSH_KEY`** - Your SSH private key
- **`PI_PORT`** - SSH port (optional, defaults to 22)

### 2. Set up SSH Key

```bash
# On your main computer
ssh-keygen -t rsa -b 4096 -C "your-email@example.com"

# Copy public key to Pi
ssh-copy-id pi@<pi-ip>

# Copy private key to GitHub Secrets
cat ~/.ssh/id_rsa
```

### 3. Clone Repository on Pi

```bash
# On Pi
git clone https://github.com/kay-rey/goobie-bot.git
cd goobie-bot
```

## That's It!

Your bot now automatically optimizes itself for Pi when `PI_MODE=true` is set and deploys automatically via GitHub Actions! 🍓🤖
