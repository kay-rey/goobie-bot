# Docker Cache Testing Guide

This guide explains how to test the cache functionality in the Docker environment for goobie-bot.

## Overview

The bot runs in a Docker container, so we need to ensure our cache implementation works correctly in that environment. We've created several testing approaches:

1. **Docker-specific tests** - Tests designed specifically for containerized environment
2. **Docker integration tests** - Tests that run inside the actual Docker container
3. **Docker Compose tests** - Tests using docker-compose for orchestration

## Quick Start

### Run All Docker Cache Tests

```bash
./test-docker-cache.sh
```

This will:

- Build the Docker image
- Run all cache tests inside Docker containers
- Clean up test containers
- Provide a comprehensive summary

### Run Individual Tests

#### 1. Docker-specific Cache Tests

```bash
docker run --rm -v "$(pwd):/app" -w /app goobie-bot:latest python tests/test_cache_docker.py
```

#### 2. Simple Cache Tests in Docker

```bash
docker run --rm -v "$(pwd):/app" -w /app goobie-bot:latest python tests/test_cache_simple.py
```

#### 3. Performance Tests in Docker

```bash
docker run --rm -v "$(pwd):/app" -w /app goobie-bot:latest python tests/test_cache_performance.py
```

#### 4. Using Docker Compose

```bash
docker-compose -f docker-compose.test.yml up --build
```

## Test Files

### `tests/test_cache_docker.py`

Docker-specific cache tests that:

- Test basic cache operations in containerized environment
- Verify TTL functionality
- Test concurrent operations
- Simulate API integration
- Check Docker environment specifics

### `tests/test_cache_simple.py`

Lightweight cache tests that work in any environment:

- Basic set/get/delete operations
- Cache miss scenarios
- Performance testing
- Key generation testing

### `tests/test_cache_performance.py`

Performance-focused tests:

- Realistic workload simulation
- Speedup calculations
- Stress testing
- Mixed workload scenarios

## Docker Commands

### Build the Image

```bash
docker build -t goobie-bot:latest .
```

### Run the Bot

```bash
docker-compose up -d
```

### Run Tests in Running Container

```bash
# If the bot is already running
docker exec goobie-bot python tests/test_cache_docker.py
```

### View Bot Logs

```bash
docker-compose logs -f goobie-bot
```

### Stop the Bot

```bash
docker-compose down
```

## Testing Scenarios

### 1. Basic Functionality

- ✅ Set and retrieve cache values
- ✅ Handle cache misses
- ✅ Delete cache entries
- ✅ Track cache statistics

### 2. TTL (Time To Live)

- ✅ Different TTL durations for different data types
- ✅ Automatic expiration
- ✅ Manual cleanup of expired entries

### 3. Concurrency

- ✅ Multiple simultaneous cache operations
- ✅ Thread-safe access
- ✅ Race condition handling

### 4. Integration

- ✅ API call simulation with caching
- ✅ Cache key generation
- ✅ Real-world usage patterns

### 5. Docker Environment

- ✅ Container-specific features
- ✅ Volume mounting
- ✅ Environment variables
- ✅ Resource constraints

## Expected Results

When all tests pass, you should see:

```
🎉 All Docker cache tests passed!
Cache implementation is working correctly in Docker environment.
```

### Performance Expectations

- **Hit Rate**: 70%+ for repeated requests
- **Speedup**: 10x+ faster for cached vs uncached requests
- **Concurrency**: 95%+ success rate under concurrent load
- **Memory**: Efficient memory usage with TTL cleanup

## Troubleshooting

### Common Issues

1. **Docker not running**

   ```
   ❌ Error: Docker is not running
   ```

   Solution: Start Docker Desktop or Docker daemon

2. **Container not found**

   ```
   ❌ Error: goobie-bot container not found
   ```

   Solution: Run `docker-compose up -d` first

3. **Permission denied**

   ```
   ❌ Error: Permission denied
   ```

   Solution: Make scripts executable with `chmod +x *.sh`

4. **Import errors**
   ```
   ❌ Error: Failed to import cache module
   ```
   Solution: Ensure you're in the correct directory and Python path is set

### Debug Mode

Run tests with verbose output:

```bash
docker run --rm -v "$(pwd):/app" -w /app -e LOG_LEVEL=DEBUG goobie-bot:latest python tests/test_cache_docker.py
```

### View Container Logs

```bash
docker logs goobie-bot-test
```

## Cache Configuration

The cache is configured with different TTL durations:

- **Game Data**: 1 hour (frequently changing)
- **Team Logos**: 6 months (rarely changing)
- **Venue Data**: 6 months (rarely changing)
- **Team Metadata**: 12 hours (moderately changing)
- **Team Names**: 6 months (rarely changing)

## Monitoring

### View Cache Statistics

Use the Discord command `/cache stats` to see:

- Hit rate percentage
- Total requests
- Cache entries
- Performance metrics

### Clear Cache

Use `/cache clear` to clear all cache entries or `/cache cleanup` to remove expired entries.

## Development

### Adding New Tests

1. Create test functions in the appropriate test file
2. Add them to the test suite in `main()`
3. Update this documentation

### Modifying Cache Behavior

1. Update `api/cache.py`
2. Run tests to verify changes
3. Test in Docker environment
4. Update documentation

## Production Considerations

- Cache runs in memory (not persistent across container restarts)
- TTL cleanup runs every 5 minutes
- Monitor memory usage in production
- Consider Redis for distributed caching if needed
- Use `/cache stats` to monitor performance
