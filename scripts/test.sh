#!/bin/bash
# Test script

set -e

echo "🧪 Running tests..."

# Run pytest with coverage
pytest tests/ -v --cov=app --cov-report=html --cov-report=term-missing

echo "\n✅ Tests completed!"
echo "📊 Coverage report: htmlcov/index.html"
