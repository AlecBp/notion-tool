#!/bin/bash
# Installation script for notion-tool
# Run: ./install.sh

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python version
PYTHON_CMD=""
for cmd in python3 python; do
    if command -v $cmd &> /dev/null; then
        version=$($cmd --version 2>&1 | awk '{print $2}')
        major=$(echo $version | cut -d. -f1)
        if [ "$major" -ge 3 ]; then
            PYTHON_CMD=$cmd
            break
        fi
    fi
done

if [ -z "$PYTHON_CMD" ]; then
    echo -e "${RED}Error: Python 3+ is required but not found.${NC}"
    exit 1
fi

PYTHON_VERSION=$($PYTHON_CMD --version 2>&1)
echo -e "${GREEN}Found:${NC} $PYTHON_VERSION"

# Determine install location
INSTALL_DIR="$HOME/.local/bin"
mkdir -p "$INSTALL_DIR"

# Create virtual environment
echo "Creating virtual environment..."
VENV_DIR="$HOME/.notion-tool/venv"
$PYTHON_CMD -m venv "$VENV_DIR"

# Activate and install
echo "Installing dependencies..."
source "$VENV_DIR/bin/activate"
pip install --upgrade pip
pip install -e "$(dirname "$0")"

# Create symlink to the CLI tool
TARGET="$VENV_DIR/bin/notion-tool"
LINK="$INSTALL_DIR/notion-tool"

# Remove existing symlink if it exists
if [ -L "$LINK" ]; then
    rm "$LINK"
fi

ln -s "$TARGET" "$LINK"
echo -e "${GREEN}Created symlink:${NC} $LINK -> $TARGET"

# Add to PATH
SHELL_CONFIG=""
case "$SHELL" in
    */zsh)
        SHELL_CONFIG="$HOME/.zshenv"
        ;;
    */bash)
        if [ -f "$HOME/.bashrc" ]; then
            SHELL_CONFIG="$HOME/.bashrc"
        elif [ -f "$HOME/.bash_profile" ]; then
            SHELL_CONFIG="$HOME/.bash_profile"
        fi
        ;;
    *)
        SHELL_CONFIG="$HOME/.profile"
        ;;
esac

PATH_LINE='export PATH="$HOME/.local/bin:$PATH"'

if ! grep -q "\.local/bin" "$SHELL_CONFIG" 2>/dev/null; then
    echo "" >> "$SHELL_CONFIG"
    echo "# Added by notion-tool installer" >> "$SHELL_CONFIG"
    echo "$PATH_LINE" >> "$SHELL_CONFIG"
    echo -e "${GREEN}Added $INSTALL_DIR to PATH in $SHELL_CONFIG${NC}"
else
    echo -e "${YELLOW}$INSTALL_DIR is already in your PATH${NC}"
fi

echo ""
echo -e "${GREEN}Installation complete!${NC}"
echo ""
echo "To use notion-tool:"
echo "  1. Run: source $SHELL_CONFIG"
echo "  2. Or open a new terminal"
echo ""
echo "Then verify:"
echo "  notion-tool --help"
echo ""
echo "NOTE: Make sure NOTION_API_KEY is set in your environment:"
echo "  export NOTION_API_KEY=\"your-api-key\""
