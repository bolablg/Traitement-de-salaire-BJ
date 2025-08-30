#!/bin/bash

# Benin Salary Calculator API - Local Development Server

echo "🇧🇯 Starting Benin Salary Calculator API locally..."

# Change to project root directory
cd "$(dirname "$0")/.."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r dev-requirements.txt

# Check for service account file using SA_KEY_PATH environment variable
if [ -z "$SA_KEY_PATH" ]; then
    echo "⚠️  Warning: SA_KEY_PATH environment variable not set"
    echo "   Google Sheets logging will not work"
    echo "   Please set SA_KEY_PATH in your .env file"
    echo ""
elif [ ! -f "$SA_KEY_PATH" ]; then
    echo "⚠️  Warning: Service account file '$SA_KEY_PATH' not found"
    echo "   Google Sheets logging will not work"
    echo "   Please check the SA_KEY_PATH in your .env file"
    echo ""
fi

# Load environment variables from .env if it exists
if [ -f ".env" ]; then
    echo "Loading environment variables from .env..."
    set -a
    source .env
    set +a
fi

echo "🚀 Starting local server on http://localhost:8080"
echo "📝 Test with:"
echo "   curl -X POST http://localhost:8080 -H 'Content-Type: application/json' -d '{\"brut\": 500000}'"
echo ""

# Start the Functions Framework
functions-framework --target=main --debug --port=8080