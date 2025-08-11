#!/bin/bash

# SmartBot Pro Setup and Run Script

echo "🤖 SmartBot Pro Setup Script"
echo "=============================="

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ first."
    exit 1
fi

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
echo "🔗 Activating virtual environment..."
source .venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Check which version to run
if [ "$1" = "--legacy" ]; then
    echo "🚀 Starting SmartBot Pro (Legacy Version)..."
    streamlit run app.py --server.port 8502
else
    echo "🚀 Starting SmartBot Pro (Modular Version)..."
    streamlit run main.py --server.port 8502
fi
