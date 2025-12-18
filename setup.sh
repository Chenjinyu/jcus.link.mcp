#!/bin/bash

# Quick Start Script for MCP Resume Server
# This script sets up the development environment

set -e  # Exit on error

echo "🚀 MCP Resume Server - Quick Start Setup"
echo "========================================"
echo ""

# Check Python version
echo "📋 Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "   Found Python $python_version"

# Create virtual environment
echo ""
echo "🔧 Creating virtual environment..."
if [ -d "venv" ]; then
    echo "   Virtual environment already exists"
else
    python3 -m venv venv
    echo "   ✅ Virtual environment created"
fi

# Activate virtual environment
echo ""
echo "🔌 Activating virtual environment..."
source venv/bin/activate
echo "   ✅ Virtual environment activated"

# Upgrade pip
echo ""
echo "⬆️  Upgrading pip..."
pip install --upgrade pip > /dev/null 2>&1
echo "   ✅ Pip upgraded"

# Install dependencies
echo ""
echo "📦 Installing dependencies..."
pip install -r requirements.txt > /dev/null 2>&1
echo "   ✅ Dependencies installed"

# Create .env file if it doesn't exist
echo ""
echo "⚙️  Setting up configuration..."
if [ -f ".env" ]; then
    echo "   .env file already exists"
else
    cp .env.example .env
    echo "   ✅ Created .env file from template"
    echo "   ⚠️  Please edit .env with your API keys!"
fi

# Create necessary directories
echo ""
echo "📁 Creating directories..."
mkdir -p logs
mkdir -p data
echo "   ✅ Directories created"

echo ""
echo "✨ Setup complete!"
echo ""
echo "📝 Next steps:"
echo "   1. Edit .env file with your API keys:"
echo "      - LLM_API_KEY=your_anthropic_or_openai_key"
echo ""
echo "   2. Run the server:"
echo "      python -m src.main"
echo "      # or with auto-reload:"
echo "      uvicorn src.main:app --reload"
echo ""
echo "   3. Test the server:"
echo "      curl http://localhost:8000/health"
echo ""
echo "📚 Documentation:"
echo "   - README.md          - Full documentation"
echo "   - MIGRATION_GUIDE.md - Architecture details"
echo "   - PROJECT_STRUCTURE.md - Structure overview"
echo ""
echo "Happy coding! 🎉"