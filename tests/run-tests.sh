#!/bin/bash

# Benin Salary Calculator API - Test Runner

echo "🧪 Running tests for Benin Salary Calculator API..."

# Change to project root directory
cd "$(dirname "$0")/.."

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Install test dependencies
pip install -r dev-requirements.txt

echo ""
echo "📋 Running linting..."
flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
flake8 . --count --exit-zero --max-complexity=10 --max-line-length=120 --statistics

echo ""
echo "🔒 Running security check..."
bandit -r . -f json || true

echo ""
echo "🧪 Running tests..."
pytest tests/test_main.py -v --cov=main --cov-report=term-missing

echo ""
echo "✅ All tests completed!"