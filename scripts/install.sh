#!/bin/bash

# ADK Agent Scaffold Installer
# This script installs the adk_scaffold command to your system

set -e

echo "🚀 ADK Agent Scaffold Installer"
echo "==============================="

# Default installation directory
INSTALL_DIR="/usr/local/bin"
SCRIPT_NAME="adk_scaffold"

# Check if user wants custom installation directory
if [ "$1" ]; then
    INSTALL_DIR="$1"
fi

echo "📍 Installation directory: $INSTALL_DIR"

# Check if directory exists and is writable
if [ ! -d "$INSTALL_DIR" ]; then
    echo "❌ Directory $INSTALL_DIR does not exist"
    echo "💡 Try: sudo mkdir -p $INSTALL_DIR"
    exit 1
fi

if [ ! -w "$INSTALL_DIR" ]; then
    echo "❌ No write permission to $INSTALL_DIR"
    echo "💡 Try running with sudo: sudo ./install.sh"
    exit 1
fi

# Download the script
echo "📥 Downloading adk_scaffold.sh..."
curl -s -o "$INSTALL_DIR/$SCRIPT_NAME" https://raw.githubusercontent.com/VENKATESHWARAN-R/adk_scaffold/main/scripts/adk_scaffold.sh

# Make it executable
chmod +x "$INSTALL_DIR/$SCRIPT_NAME"

echo "✅ Installation complete!"
echo ""
echo "🎯 You can now use 'adk_scaffold' from anywhere:"
echo "   adk_scaffold my_awesome_agent"
echo ""
echo "📍 Installed to: $INSTALL_DIR/$SCRIPT_NAME"

# Check if directory is in PATH
if ! echo "$PATH" | grep -q "$INSTALL_DIR"; then
    echo ""
    echo "⚠️  Warning: $INSTALL_DIR is not in your PATH"
    echo "💡 Add this to your ~/.zshrc or ~/.bashrc:"
    echo "   export PATH=\"\$PATH:$INSTALL_DIR\""
fi