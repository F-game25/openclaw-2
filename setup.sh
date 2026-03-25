#!/bin/bash
# Setup script for AI Employee + OpenClaw 2

set -e

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OPENCLAW2_DIR="$REPO_DIR/openclaw2"

echo "================================================"
echo "AI Employee + OpenClaw 2"
echo "Setup Script"
echo "================================================"
echo ""

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Found Python $python_version"

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

source "$REPO_DIR/venv/bin/activate"
pip install --upgrade pip -q

# Install OpenClaw 2 dependencies
echo ""
echo "Installing OpenClaw 2 dependencies..."
pip install -r "$OPENCLAW2_DIR/requirements.txt" -q
echo "✓ OpenClaw 2 dependencies installed"

# Create runtime directories
echo ""
echo "Creating runtime directories..."
mkdir -p "$REPO_DIR/run" "$REPO_DIR/state" "$REPO_DIR/workspace"
mkdir -p "$OPENCLAW2_DIR/data" "$OPENCLAW2_DIR/logs"
echo "✓ Directories created"

# Setup OpenClaw 2 config
echo ""
if [ ! -f "$OPENCLAW2_DIR/config.local.yml" ]; then
    cp "$OPENCLAW2_DIR/config.yml" "$OPENCLAW2_DIR/config.local.yml"
    echo "✓ openclaw2/config.local.yml created — edit it to set your JWT secret"
else
    echo "⚠️  openclaw2/config.local.yml already exists, skipping"
fi

# Setup .env
echo ""
if [ ! -f "$OPENCLAW2_DIR/.env" ]; then
    cp "$OPENCLAW2_DIR/.env.example" "$OPENCLAW2_DIR/.env"
    echo "✓ openclaw2/.env created"
else
    echo "⚠️  openclaw2/.env already exists, skipping"
fi

# Generate JWT secret
jwt_secret=$(python3 -c "import secrets; print(secrets.token_hex(32))")
echo ""
echo "=============================================="
echo "Generated JWT secret (add to openclaw2/.env):"
echo "JWT_SECRET_KEY=$jwt_secret"
echo "=============================================="

# Set executable permissions on AI Employee scripts
echo ""
echo "Setting script permissions..."
chmod +x "$REPO_DIR/runtime/bin/ai-employee" 2>/dev/null || true
chmod +x "$REPO_DIR/runtime/start.sh" "$REPO_DIR/runtime/stop.sh" 2>/dev/null || true
find "$REPO_DIR/runtime/bots" -name "run.sh" -exec chmod +x {} \; 2>/dev/null || true
echo "✓ Permissions set"

echo ""
echo "================================================"
echo "Setup complete!"
echo "================================================"
echo ""
echo "Next steps:"
echo "1. Add the JWT secret above to openclaw2/.env"
echo "2. (Optional) Add ANTHROPIC_API_KEY / OLLAMA settings to openclaw2/.env"
echo "3. Run: ./start.sh"
echo ""
