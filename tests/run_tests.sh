#!/bin/bash
# Test script to run API tests inside Docker container

echo "🤖 Running API tests inside Docker container..."

# Copy test file to container and run it
docker exec goobie-bot python /app/tests/test_apis.py
