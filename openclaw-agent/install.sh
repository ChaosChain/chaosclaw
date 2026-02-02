#!/bin/bash
# ChaosClaw OpenClaw Agent Installer
# This script sets up ChaosClaw as an OpenClaw agent

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OPENCLAW_AGENTS_DIR="${HOME}/.openclaw/agents"
AGENT_NAME="chaosclaw"

echo "🦞 ChaosClaw OpenClaw Agent Installer"
echo "======================================"
echo ""

# Check if OpenClaw is installed
if ! command -v openclaw &> /dev/null; then
    echo "❌ OpenClaw is not installed."
    echo ""
    echo "Install OpenClaw first:"
    echo "  curl -fsSL https://openclaw.ai/install.sh | bash"
    echo ""
    exit 1
fi

echo "✅ OpenClaw is installed"

# Check if ChaosChain skill is installed
if ! clawhub list 2>/dev/null | grep -q "chaoschain"; then
    echo ""
    echo "⚠️  ChaosChain skill not found. Installing..."
    clawhub install chaoschain
    echo "✅ ChaosChain skill installed"
else
    echo "✅ ChaosChain skill is installed"
fi

# Create agent directory
echo ""
echo "📁 Setting up agent directory..."
mkdir -p "${OPENCLAW_AGENTS_DIR}/${AGENT_NAME}"

# Copy or symlink agent files
if [ "$1" == "--dev" ]; then
    echo "🔗 Creating symlinks (development mode)..."
    ln -sf "${SCRIPT_DIR}/SOUL.md" "${OPENCLAW_AGENTS_DIR}/${AGENT_NAME}/SOUL.md"
    ln -sf "${SCRIPT_DIR}/config.json" "${OPENCLAW_AGENTS_DIR}/${AGENT_NAME}/config.json"
else
    echo "📄 Copying agent files..."
    cp "${SCRIPT_DIR}/SOUL.md" "${OPENCLAW_AGENTS_DIR}/${AGENT_NAME}/SOUL.md"
    cp "${SCRIPT_DIR}/config.json" "${OPENCLAW_AGENTS_DIR}/${AGENT_NAME}/config.json"
fi

echo "✅ Agent files installed"

# Verify installation
echo ""
echo "🔍 Verifying installation..."
if [ -f "${OPENCLAW_AGENTS_DIR}/${AGENT_NAME}/SOUL.md" ] && \
   [ -f "${OPENCLAW_AGENTS_DIR}/${AGENT_NAME}/config.json" ]; then
    echo "✅ ChaosClaw agent installed successfully!"
else
    echo "❌ Installation verification failed"
    exit 1
fi

echo ""
echo "======================================"
echo "🦞 ChaosClaw is ready!"
echo "======================================"
echo ""
echo "To test ChaosClaw:"
echo ""
echo "  1. Make sure the gateway is running:"
echo "     openclaw gateway"
echo ""
echo "  2. Send a test message:"
echo "     openclaw message send --agent chaosclaw --message \"Hey, can you verify agent 540?\""
echo ""
echo "  3. Or interact via your configured channels (WhatsApp/Telegram/Discord)"
echo ""
echo "For more info: ${SCRIPT_DIR}/README.md"
echo ""
