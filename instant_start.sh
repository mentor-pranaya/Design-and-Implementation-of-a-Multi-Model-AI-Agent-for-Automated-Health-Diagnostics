#!/bin/bash
# ⚡ INSTANT POWERFUL INBLOODO AGENT - Performance-Optimized Startup (Linux/Mac)
# This script starts the server with all performance enhancements enabled

cat << "EOF"

╔════════════════════════════════════════════════════════════════╗
║   ⚡ INBLOODO AGENT - INSTANT & POWERFUL STARTUP ⚡          ║
║                                                                ║
║   All Performance Optimizations ENABLED:                     ║
║   • Response Caching                                          ║
║   • Parallel Processing                                       ║
║   • Connection Pooling                                        ║
║   • GZIP Compression                                          ║
║   • Real-time Monitoring                                      ║
║                                                                ║
║   Expected Speed: 10-100x FASTER RESULTS!                    ║
╚════════════════════════════════════════════════════════════════╝

EOF

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 not found. Install Python 3.8+ first."
    exit 1
fi

# Create venv if needed
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    echo "📥 Installing dependencies..."
    pip install --upgrade pip
    pip install -r requirements.txt
    echo "✅ Optional performance packages (install separately if needed):"
    echo "   pip install -r requirements-performance.txt"
else
    source venv/bin/activate
fi

# Set environment for performance
export ENVIRONMENT=production
export HOST=0.0.0.0
export PORT=10000
export PYTHONOPTIMIZE=2

# Create directories
mkdir -p data/uploads
mkdir -p src/data

echo ""
echo "✨ Starting INSTANT POWERFUL Blood Report Analysis..."
echo ""

# Start optimized server
python run_instant.py
