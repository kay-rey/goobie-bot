#!/bin/bash
# Cache Testing Runner for goobie-bot
# This script runs all cache tests and provides a summary

echo "🧪 Goobie-Bot Cache Testing Suite"
echo "=================================="
echo ""

# Check if we're in the right directory
if [ ! -f "bot.py" ]; then
    echo "❌ Error: Please run this script from the goobie-bot root directory"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Error: Virtual environment not found. Please run 'python -m venv venv' first"
    exit 1
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies if needed
echo "📦 Checking dependencies..."
pip install -q -r requirements.txt

echo ""
echo "🚀 Running Cache Tests..."
echo "========================="
echo ""

# Run comprehensive cache tests
echo "1️⃣ Running Comprehensive Cache Tests..."
python tests/test_cache.py
COMPREHENSIVE_EXIT_CODE=$?

echo ""
echo "2️⃣ Running Cache Performance Tests..."
python tests/test_cache_performance.py
PERFORMANCE_EXIT_CODE=$?

echo ""
echo "📊 Test Summary"
echo "==============="

if [ $COMPREHENSIVE_EXIT_CODE -eq 0 ]; then
    echo "✅ Comprehensive Cache Tests: PASSED"
else
    echo "❌ Comprehensive Cache Tests: FAILED"
fi

if [ $PERFORMANCE_EXIT_CODE -eq 0 ]; then
    echo "✅ Cache Performance Tests: PASSED"
else
    echo "❌ Cache Performance Tests: FAILED"
fi

# Overall result
if [ $COMPREHENSIVE_EXIT_CODE -eq 0 ] && [ $PERFORMANCE_EXIT_CODE -eq 0 ]; then
    echo ""
    echo "🎉 All cache tests passed!"
    echo "Cache implementation is working correctly."
    exit 0
else
    echo ""
    echo "⚠️ Some cache tests failed!"
    echo "Please check the output above for details."
    exit 1
fi
