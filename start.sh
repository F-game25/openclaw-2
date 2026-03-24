#!/bin/bash
# Quick start script for OpenClaw AI - Private & Secure

set -e

echo "================================================"
echo "OpenClaw AI - Private & Secure Edition"
echo "Quick Start Guide"
echo "================================================"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Error: Virtual environment not found."
    echo "Please run setup.sh first:"
    echo "  ./setup.sh"
    exit 1
fi

# Check if JWT secret is set
if [ -z "$JWT_SECRET_KEY" ]; then
    echo ""
    echo "⚠️  WARNING: JWT_SECRET_KEY environment variable not set"
    echo ""
    echo "Generating a secure JWT secret for this session..."
    export JWT_SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
    echo "JWT_SECRET_KEY=$JWT_SECRET_KEY"
    echo ""
    echo "💡 To persist this key, add it to your .env file:"
    echo "   echo 'JWT_SECRET_KEY=$JWT_SECRET_KEY' >> .env"
    echo ""
fi

# Activate virtual environment and start server
echo "Starting OpenClaw AI server..."
echo ""
source venv/bin/activate
python main.py

