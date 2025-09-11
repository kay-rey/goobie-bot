#!/bin/bash
# Docker Cache Testing Script for goobie-bot
# This script runs cache tests inside the Docker container

echo "🐳 Goobie-Bot Docker Cache Testing"
echo "=================================="
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Error: Docker is not running"
    exit 1
fi

# Check if the container exists
if ! docker ps -a --format "table {{.Names}}" | grep -q "goobie-bot"; then
    echo "❌ Error: goobie-bot container not found"
    echo "Please run 'docker-compose up -d' first to create the container"
    exit 1
fi

echo "🔧 Running cache tests inside Docker container..."
echo ""

# Run the simple cache test inside the container
echo "1️⃣ Running Simple Cache Tests..."
docker exec goobie-bot python tests/test_cache_simple.py
SIMPLE_EXIT_CODE=$?

echo ""
echo "2️⃣ Running Cache Performance Tests..."
docker exec goobie-bot python tests/test_cache_performance.py
PERFORMANCE_EXIT_CODE=$?

echo ""
echo "3️⃣ Running Comprehensive Cache Tests..."
docker exec goobie-bot python tests/test_cache.py
COMPREHENSIVE_EXIT_CODE=$?

echo ""
echo "📊 Docker Test Summary"
echo "====================="

if [ $SIMPLE_EXIT_CODE -eq 0 ]; then
    echo "✅ Simple Cache Tests: PASSED"
else
    echo "❌ Simple Cache Tests: FAILED"
fi

if [ $PERFORMANCE_EXIT_CODE -eq 0 ]; then
    echo "✅ Cache Performance Tests: PASSED"
else
    echo "❌ Cache Performance Tests: FAILED"
fi

if [ $COMPREHENSIVE_EXIT_CODE -eq 0 ]; then
    echo "✅ Comprehensive Cache Tests: PASSED"
else
    echo "❌ Comprehensive Cache Tests: FAILED"
fi

# Overall result
if [ $SIMPLE_EXIT_CODE -eq 0 ] && [ $PERFORMANCE_EXIT_CODE -eq 0 ] && [ $COMPREHENSIVE_EXIT_CODE -eq 0 ]; then
    echo ""
    echo "🎉 All Docker cache tests passed!"
    echo "Cache implementation is working correctly in Docker environment."
    exit 0
else
    echo ""
    echo "⚠️ Some Docker cache tests failed!"
    echo "Please check the output above for details."
    exit 1
fi
