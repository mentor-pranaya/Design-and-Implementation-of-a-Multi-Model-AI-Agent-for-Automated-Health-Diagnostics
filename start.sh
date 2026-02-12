#!/bin/bash

# INBLOODO AGENT Startup Script
echo "🩺 Starting INBLOODO AGENT..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Check if pip is installed
if ! command -v pip &> /dev/null; then
    echo "❌ pip is not installed. Please install pip."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install/upgrade dependencies
echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create data directories
mkdir -p data/uploads
mkdir -p src/data

# Set environment variables
export ENVIRONMENT=production
export HOST=0.0.0.0
export PORT=${PORT:-10000}
export API_KEY=${API_KEY:-$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")}

echo "🔑 API Key: $API_KEY"
echo "🌐 Starting server on http://$HOST:$PORT"
echo "📊 Health check: http://$HOST:$PORT/health"
echo "🏠 Web interface: http://$HOST:$PORT"

# Start the application
python main.py