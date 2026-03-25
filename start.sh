#!/bin/bash
# Quick start script for OpenClaw AI + AI Employee

set -e

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AI_EMPLOYEE_DIR="$REPO_DIR/ai-employee"

echo "================================================"
echo "OpenClaw AI + AI Employee"
echo "Quick Start"
echo "================================================"

# Check if virtual environment exists
if [ ! -d "$REPO_DIR/venv" ]; then
    echo "Error: Virtual environment not found."
    echo "Please run setup.sh first:"
    echo "  ./setup.sh"
    exit 1
fi

# Activate virtual environment
source "$REPO_DIR/venv/bin/activate"

# Check if JWT secret is set
if [ -z "$JWT_SECRET_KEY" ]; then
    # Try loading from .env
    if [ -f "$REPO_DIR/.env" ]; then
        set -a
        source "$REPO_DIR/.env"
        set +a
    fi
fi

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

# Export AI_HOME so the AI Employee bots know where to find their files
export AI_HOME="$AI_EMPLOYEE_DIR"

# ── Start OpenClaw API server (background) ────────────────────────────────────
echo ""
echo "Starting OpenClaw AI API server (port 8000)..."
mkdir -p "$REPO_DIR/logs"
nohup python3 "$REPO_DIR/main.py" >> "$REPO_DIR/logs/openclaw.log" 2>&1 &
OPENCLAW_PID=$!
echo "$OPENCLAW_PID" > "$REPO_DIR/logs/openclaw.pid"
echo "✓ OpenClaw API server started (pid=$OPENCLAW_PID)"
echo "  → API: http://127.0.0.1:8000"
echo "  → Docs: http://127.0.0.1:8000/docs (debug mode only)"

# ── Start AI Employee bots ─────────────────────────────────────────────────────
echo ""
echo "Starting AI Employee bots..."
mkdir -p "$AI_EMPLOYEE_DIR/logs" "$AI_EMPLOYEE_DIR/run" "$AI_EMPLOYEE_DIR/state"

# Set PYTHON to the venv python so bots use the correct environment
export PYTHON="$REPO_DIR/venv/bin/python3"

# Override python3 for bots by prepending venv bin to PATH
export PATH="$REPO_DIR/venv/bin:$PATH"

AI_EMPLOYEE_BIN="$AI_EMPLOYEE_DIR/runtime/bin/ai-employee"
if [ -x "$AI_EMPLOYEE_BIN" ]; then
    "$AI_EMPLOYEE_BIN" start --all >> "$AI_EMPLOYEE_DIR/logs/startup.log" 2>&1 || true
    echo "✓ AI Employee bots started"
    echo "  → Problem Solver UI: http://127.0.0.1:8787"
else
    echo "⚠️  AI Employee bin not found at $AI_EMPLOYEE_BIN"
fi

echo ""
echo "================================================"
echo "All services started!"
echo "================================================"
echo ""
echo "  OpenClaw API:      http://127.0.0.1:8000"
echo "  Problem Solver UI: http://127.0.0.1:8787"
echo "  Health check:      http://127.0.0.1:8000/health"
echo ""
echo "Logs:"
echo "  OpenClaw: $REPO_DIR/logs/openclaw.log"
echo "  Bots:     $AI_EMPLOYEE_DIR/logs/"
echo ""
echo "Press Ctrl+C to stop all services."
echo ""

# Cleanup function
cleanup() {
    echo ""
    echo "Stopping all services..."
    # Stop AI Employee bots
    if [ -x "$AI_EMPLOYEE_BIN" ]; then
        "$AI_EMPLOYEE_BIN" stop --all >/dev/null 2>&1 || true
    fi
    # Stop OpenClaw API
    if [ -f "$REPO_DIR/logs/openclaw.pid" ]; then
        kill "$(cat "$REPO_DIR/logs/openclaw.pid")" 2>/dev/null || true
        rm -f "$REPO_DIR/logs/openclaw.pid"
    fi
    echo "✓ All services stopped."
}

trap cleanup EXIT INT TERM

# Wait indefinitely (keep services running)
wait $OPENCLAW_PID 2>/dev/null || true

