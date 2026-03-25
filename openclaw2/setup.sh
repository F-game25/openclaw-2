#!/bin/bash
# OpenClaw 2 standalone setup
# If running as part of AI Employee, use the root-level ./setup.sh instead.

set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Note: For the full AI Employee + OpenClaw 2 stack, run the root ./setup.sh"
echo "This script sets up OpenClaw 2 standalone."
echo ""

python3 -m venv "$SCRIPT_DIR/venv"
source "$SCRIPT_DIR/venv/bin/activate"
pip install --upgrade pip -q
pip install -r "$SCRIPT_DIR/requirements.txt" -q

mkdir -p "$SCRIPT_DIR/data" "$SCRIPT_DIR/logs"

[ ! -f "$SCRIPT_DIR/config.local.yml" ] && cp "$SCRIPT_DIR/config.yml" "$SCRIPT_DIR/config.local.yml"
[ ! -f "$SCRIPT_DIR/.env" ] && cp "$SCRIPT_DIR/.env.example" "$SCRIPT_DIR/.env"

jwt_secret=$(python3 -c "import secrets; print(secrets.token_hex(32))")
echo "Add to openclaw2/.env:  JWT_SECRET_KEY=$jwt_secret"
