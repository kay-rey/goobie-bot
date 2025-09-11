#!/bin/bash
# Comprehensive Docker Cache Testing Script for goobie-bot

echo "🐳 Goobie-Bot Docker Cache Testing Suite"
echo "========================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    local status=$1
    local message=$2
    case $status in
        "SUCCESS")
            echo -e "${GREEN}✅ $message${NC}"
            ;;
        "ERROR")
            echo -e "${RED}❌ $message${NC}"
            ;;
        "WARNING")
            echo -e "${YELLOW}⚠️ $message${NC}"
            ;;
        "INFO")
            echo -e "${BLUE}ℹ️ $message${NC}"
            ;;
    esac
}

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    print_status "ERROR" "Docker is not running"
    exit 1
fi

print_status "INFO" "Docker is running"

# Check if we're in the right directory
if [ ! -f "Dockerfile" ] || [ ! -f "docker-compose.yml" ]; then
    print_status "ERROR" "Please run this script from the goobie-bot root directory"
    exit 1
fi

print_status "INFO" "Found Docker configuration files"

# Build the Docker image if it doesn't exist or is outdated
echo ""
print_status "INFO" "Building Docker image..."
if docker build -t goobie-bot:latest . > /dev/null 2>&1; then
    print_status "SUCCESS" "Docker image built successfully"
else
    print_status "ERROR" "Failed to build Docker image"
    exit 1
fi

# Stop any existing test containers
echo ""
print_status "INFO" "Cleaning up existing test containers..."
docker stop goobie-bot-test 2>/dev/null || true
docker rm goobie-bot-test 2>/dev/null || true

# Run the Docker-specific cache tests
echo ""
print_status "INFO" "Running Docker-specific cache tests..."
if docker run --rm --name goobie-bot-test -v "$(pwd):/app" -w /app goobie-bot:latest python tests/test_cache_docker.py; then
    print_status "SUCCESS" "Docker-specific cache tests passed"
    DOCKER_SPECIFIC_EXIT_CODE=0
else
    print_status "ERROR" "Docker-specific cache tests failed"
    DOCKER_SPECIFIC_EXIT_CODE=1
fi

# Run simple cache tests in Docker
echo ""
print_status "INFO" "Running simple cache tests in Docker..."
if docker run --rm --name goobie-bot-simple-test -v "$(pwd):/app" -w /app goobie-bot:latest python tests/test_cache_simple.py; then
    print_status "SUCCESS" "Simple cache tests passed in Docker"
    SIMPLE_EXIT_CODE=0
else
    print_status "ERROR" "Simple cache tests failed in Docker"
    SIMPLE_EXIT_CODE=1
fi

# Run performance tests in Docker
echo ""
print_status "INFO" "Running cache performance tests in Docker..."
if docker run --rm --name goobie-bot-perf-test -v "$(pwd):/app" -w /app goobie-bot:latest python tests/test_cache_performance.py; then
    print_status "SUCCESS" "Cache performance tests passed in Docker"
    PERFORMANCE_EXIT_CODE=0
else
    print_status "ERROR" "Cache performance tests failed in Docker"
    PERFORMANCE_EXIT_CODE=1
fi

# Test with docker-compose
echo ""
print_status "INFO" "Testing with docker-compose..."
if docker-compose -f docker-compose.test.yml up --build --abort-on-container-exit; then
    print_status "SUCCESS" "Docker-compose test passed"
    COMPOSE_EXIT_CODE=0
else
    print_status "ERROR" "Docker-compose test failed"
    COMPOSE_EXIT_CODE=1
fi

# Clean up
echo ""
print_status "INFO" "Cleaning up test containers..."
docker stop goobie-bot-test goobie-bot-simple-test goobie-bot-perf-test 2>/dev/null || true
docker rm goobie-bot-test goobie-bot-simple-test goobie-bot-perf-test 2>/dev/null || true

# Print summary
echo ""
echo "========================================"
print_status "INFO" "DOCKER TEST SUMMARY"
echo "========================================"

if [ $DOCKER_SPECIFIC_EXIT_CODE -eq 0 ]; then
    print_status "SUCCESS" "Docker-specific cache tests: PASSED"
else
    print_status "ERROR" "Docker-specific cache tests: FAILED"
fi

if [ $SIMPLE_EXIT_CODE -eq 0 ]; then
    print_status "SUCCESS" "Simple cache tests in Docker: PASSED"
else
    print_status "ERROR" "Simple cache tests in Docker: FAILED"
fi

if [ $PERFORMANCE_EXIT_CODE -eq 0 ]; then
    print_status "SUCCESS" "Cache performance tests in Docker: PASSED"
else
    print_status "ERROR" "Cache performance tests in Docker: FAILED"
fi

if [ $COMPOSE_EXIT_CODE -eq 0 ]; then
    print_status "SUCCESS" "Docker-compose test: PASSED"
else
    print_status "ERROR" "Docker-compose test: FAILED"
fi

# Overall result
TOTAL_FAILED=$((DOCKER_SPECIFIC_EXIT_CODE + SIMPLE_EXIT_CODE + PERFORMANCE_EXIT_CODE + COMPOSE_EXIT_CODE))

if [ $TOTAL_FAILED -eq 0 ]; then
    echo ""
    print_status "SUCCESS" "All Docker cache tests passed!"
    print_status "INFO" "Cache implementation is working correctly in Docker environment."
    echo ""
    print_status "INFO" "You can now run the bot with: docker-compose up -d"
    exit 0
else
    echo ""
    print_status "ERROR" "$TOTAL_FAILED Docker cache test(s) failed!"
    print_status "WARNING" "Please check the output above for details."
    exit 1
fi
