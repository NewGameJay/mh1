#!/bin/bash
#
# MH1 Quick Install Script
#
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/marketerhire/mh1/main/install.sh | bash
#
# Or manually:
#   git clone https://github.com/marketerhire/mh1.git ~/.mh1
#   cd ~/.mh1 && ./install.sh
#

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

MH1_DIR="${MH1_DIR:-$HOME/.mh1}"
MH1_REPO="https://github.com/NewGameJay/mh1.git"

echo -e "${CYAN}"
echo "    ███╗   ███╗██╗  ██╗     ██╗"
echo "    ████╗ ████║██║  ██║    ███║"
echo "    ██╔████╔██║███████║    ╚██║"
echo "    ██║╚██╔╝██║██╔══██║     ██║"
echo "    ██║ ╚═╝ ██║██║  ██║     ██║"
echo "    ╚═╝     ╚═╝╚═╝  ╚═╝     ╚═╝"
echo -e "${NC}"
echo "    MH1 Installer"
echo ""

# Check if running from within MH1 directory
if [ -f "./mh1" ] && [ -d "./skills" ]; then
    echo -e "${CYAN}Installing from current directory...${NC}"
    MH1_DIR="$(pwd)"
else
    # Clone if not exists
    if [ -d "$MH1_DIR" ]; then
        echo -e "${YELLOW}MH1 already exists at $MH1_DIR${NC}"
        read -p "Update existing installation? [Y/n]: " choice
        choice=${choice:-Y}
        if [[ "$choice" =~ ^[Yy] ]]; then
            echo "Updating..."
            cd "$MH1_DIR" && git pull
        fi
    else
        echo -e "${CYAN}Cloning MH1 to $MH1_DIR...${NC}"
        git clone --depth 1 "$MH1_REPO" "$MH1_DIR"
    fi
fi

cd "$MH1_DIR"

# Create virtual environment
echo -e "${CYAN}Setting up Python environment...${NC}"
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi

# Install dependencies
echo "Installing dependencies..."
.venv/bin/pip install -q --upgrade pip
.venv/bin/pip install -q pyyaml firebase-admin

# Make mh1 executable
chmod +x mh1

# Create symlink in user bin
USER_BIN="$HOME/.local/bin"
mkdir -p "$USER_BIN"

if [ -L "$USER_BIN/mh1" ]; then
    rm "$USER_BIN/mh1"
fi
ln -s "$MH1_DIR/mh1" "$USER_BIN/mh1"

echo ""
echo -e "${GREEN}✓ MH1 installed successfully!${NC}"
echo ""
echo "Location: $MH1_DIR"
echo ""

# Check if ~/.local/bin is in PATH
if [[ ":$PATH:" != *":$USER_BIN:"* ]]; then
    echo -e "${YELLOW}Add this to your ~/.zshrc or ~/.bashrc:${NC}"
    echo ""
    echo "  export PATH=\"\$HOME/.local/bin:\$PATH\""
    echo ""
    echo "Then restart your terminal or run: source ~/.zshrc"
    echo ""
fi

echo "Run 'mh1' to start!"
echo ""
