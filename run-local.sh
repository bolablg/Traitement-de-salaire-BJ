#!/bin/bash

# Benin Salary Calculator API - Local Development Server

echo "🇧🇯 Starting Benin Salary Calculator API locally..."

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

# Check for service account file
if [ ! -f "intelytix-sa.json" ]; then
    echo "⚠️  Warning: Service account file 'intelytix-sa.json' not found"
    echo "   Google Sheets logging will not work"
    echo "   Please add your service account key file"
    echo ""
fi

echo "🚀 Starting local server on http://localhost:8080"
echo "📝 Test with:"
echo "   curl -X POST http://localhost:8080 -H 'Content-Type: application/json' -d '{\"brut\": 500000}'"
echo ""

# Start the Functions Framework
functions-framework --target=main --debug --port=8080