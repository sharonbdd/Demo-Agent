#!/bin/bash
# OpenClaude v2.0 Linux Build Script

set -e

# 1. Build the JS bundle
echo "Building JS bundle..."
bun run build

# 2. Compile the CLI binary for Linux
echo "Compiling Linux CLI binary..."
mkdir -p dist/openclaude-linux
bun build --compile --target=bun-linux-x64 ./src/entrypoints/cli.tsx --outfile dist/openclaude-linux/openclaude

# 3. Instructions for the ACP Bridge
echo "--------------------------------------------------"
echo "CLI binary created at: dist/openclaude-linux/openclaude"
echo ""
echo "To build the ACP Bridge for Linux (ELF binaries):"
echo "Run the following on your Linux machine:"
echo "  pip install pyinstaller agent-client-protocol"
echo "  python3 -m PyInstaller --onefile scripts/openclaude_acp_bridge.py --distpath dist/openclaude-linux --name openclaude-acp-modes"
echo "  python3 -m PyInstaller --onefile scripts/openclaude_acp_low.py --distpath dist/openclaude-linux --name openclaude-acp-low"
echo "  python3 -m PyInstaller --onefile scripts/openclaude_acp_high.py --distpath dist/openclaude-linux --name openclaude-acp-high"
echo "--------------------------------------------------"
