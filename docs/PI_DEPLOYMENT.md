# Raspberry Pi Deployment Guide

## Quick Start

Your goobie-bot is now **Pi-optimized by default**! No separate files needed.

### 1. Deploy on Pi

```bash
# Build for ARM64
docker build --platform linux/arm64 -t goobie-bot .

# Run with Pi optimizations
docker run -d \
  --name goobie-bot \
  --platform linux/arm64 \
  --env-file .env \
  -e PI_MODE=true \
  -e MEMORY_LIMIT_MB=512 \
  -e CACHE_SIZE_LIMIT=100 \
  --restart unless-stopped \
  goobie-bot
```

### 2. Or use Docker Compose

```yaml
# docker-compose.yml
version: "3.8"
services:
  goobie-bot:
    build: .
    platform: linux/arm64
    container_name: goobie-bot
    env_file: .env
    environment:
      - PI_MODE=true
      - MEMORY_LIMIT_MB=512
      - CACHE_SIZE_LIMIT=100
    restart: unless-stopped
```

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

# Memory limit in MB (default: 512)
MEMORY_LIMIT_MB=512

# Cache size limit (default: 100)
CACHE_SIZE_LIMIT=100

# Log level (default: INFO)
LOG_LEVEL=INFO
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

| Pi Model   | Memory Usage | Status       |
| ---------- | ------------ | ------------ |
| Pi 4 (4GB) | ~150-200MB   | ✅ Excellent |
| Pi 4 (2GB) | ~100-150MB   | ✅ Great     |
| Pi 3 (1GB) | ~80-120MB    | ✅ Good      |

## That's It!

Your bot now automatically optimizes itself for Pi when `PI_MODE=true` is set. No separate files needed! 🍓🤖
