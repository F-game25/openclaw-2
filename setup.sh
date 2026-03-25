#!/bin/bash
# Setup script for OpenClaw AI + AI Employee (merged)

set -e

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AI_EMPLOYEE_DIR="$REPO_DIR/ai-employee"

echo "================================================"
echo "OpenClaw AI + AI Employee"
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
python3 -m venv "$REPO_DIR/venv"
echo "✓ Virtual environment created"

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source "$REPO_DIR/venv/bin/activate"
echo "✓ Virtual environment activated"

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip > /dev/null
echo "✓ pip upgraded"

# Install all dependencies (OpenClaw + AI Employee)
echo ""
echo "Installing dependencies..."
pip install -r "$REPO_DIR/requirements.txt"
echo "✓ Dependencies installed"

# Create necessary directories
echo ""
echo "Creating directories..."
mkdir -p "$REPO_DIR/data" "$REPO_DIR/logs"
mkdir -p "$AI_EMPLOYEE_DIR/logs" "$AI_EMPLOYEE_DIR/run" "$AI_EMPLOYEE_DIR/state" "$AI_EMPLOYEE_DIR/workspace"
echo "✓ Directories created"

# Setup configuration
echo ""
if [ ! -f "$REPO_DIR/config.local.yml" ]; then
    echo "Creating local configuration..."
    cp "$REPO_DIR/config.yml" "$REPO_DIR/config.local.yml"
    echo "✓ config.local.yml created"
    echo ""
    echo "⚠️  IMPORTANT: Edit config.local.yml and change the JWT secret key!"
else
    echo "⚠️  config.local.yml already exists, skipping..."
fi

# Setup environment file
echo ""
if [ ! -f "$REPO_DIR/.env" ]; then
    echo "Creating .env file..."
    cp "$REPO_DIR/.env.example" "$REPO_DIR/.env"
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
chmod 700 "$REPO_DIR/data" "$REPO_DIR/logs"
chmod 600 "$REPO_DIR/.env" 2>/dev/null || true
chmod 600 "$REPO_DIR/config.local.yml" 2>/dev/null || true
echo "✓ Permissions set"

# Set AI Employee shell scripts executable
echo ""
echo "Setting AI Employee script permissions..."
chmod +x "$AI_EMPLOYEE_DIR/runtime/bin/ai-employee" 2>/dev/null || true
chmod +x "$AI_EMPLOYEE_DIR/runtime/start.sh" 2>/dev/null || true
chmod +x "$AI_EMPLOYEE_DIR/runtime/stop.sh" 2>/dev/null || true
find "$AI_EMPLOYEE_DIR/runtime/bots" -name "run.sh" -exec chmod +x {} \; 2>/dev/null || true
echo "✓ AI Employee scripts are executable"

echo ""
echo "================================================"
echo "Setup complete!"
echo "================================================"
echo ""
echo "Next steps:"
echo "1. Edit .env and add the JWT secret above"
echo "   Also add: ANTHROPIC_API_KEY (optional, for Claude agent)"
echo "2. Review config.local.yml and adjust settings"
echo "3. Run: ./start.sh"
echo ""
echo "For security best practices, see SECURITY.md"
echo ""
