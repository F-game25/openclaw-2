#!/bin/bash
# Setup script for OpenClaw AI - Private & Secure

set -e

echo "================================================"
echo "OpenClaw AI - Private & Secure Edition"
echo "Setup Script"
echo "================================================"
echo ""

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Found Python $python_version"

# Check if Python 3.8+
required_version="3.8"
if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "✗ Error: Python 3.8 or higher required"
    exit 1
fi

# Create virtual environment
echo ""
echo "Creating virtual environment..."
python3 -m venv venv
echo "✓ Virtual environment created"

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate
echo "✓ Virtual environment activated"

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip > /dev/null
echo "✓ pip upgraded"

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt
echo "✓ Dependencies installed"

# Create necessary directories
echo ""
echo "Creating directories..."
mkdir -p data logs
echo "✓ Directories created"

# Setup configuration
echo ""
if [ ! -f "config.local.yml" ]; then
    echo "Creating local configuration..."
    cp config.yml config.local.yml
    echo "✓ config.local.yml created"
    echo ""
    echo "⚠️  IMPORTANT: Edit config.local.yml and change the JWT secret key!"
else
    echo "⚠️  config.local.yml already exists, skipping..."
fi

# Setup environment file
echo ""
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cp .env.example .env
    echo "✓ .env created"
    echo ""
    echo "⚠️  IMPORTANT: Edit .env and add your JWT secret key!"
else
    echo "⚠️  .env already exists, skipping..."
fi

# Generate secure JWT secret
echo ""
echo "Generating secure JWT secret..."
jwt_secret=$(python3 -c "import secrets; print(secrets.token_hex(32))")
echo ""
echo "=============================================="
echo "Your generated JWT secret (save this):"
echo "$jwt_secret"
echo "=============================================="
echo ""
echo "Add this to .env file as:"
echo "JWT_SECRET_KEY=$jwt_secret"
echo ""

# Set secure permissions
echo "Setting secure file permissions..."
chmod 700 data logs
chmod 600 .env 2>/dev/null || true
chmod 600 config.local.yml 2>/dev/null || true
echo "✓ Permissions set"

echo ""
echo "================================================"
echo "Setup complete!"
echo "================================================"
echo ""
echo "Next steps:"
echo "1. Edit .env and add the JWT secret above"
echo "2. Review config.local.yml and adjust settings"
echo "3. Run: python main.py"
echo ""
echo "For security best practices, see SECURITY.md"
echo ""
