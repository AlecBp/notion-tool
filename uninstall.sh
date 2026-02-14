#!/bin/bash
# Uninstallation script for notion-tool
# Run: ./uninstall.sh

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

VENV_DIR="$HOME/.notion-tool/venv"
SYMLINK="$HOME/.local/bin/notion-tool"

echo "Uninstalling notion-tool..."

# Remove symlink
if [ -L "$SYMLINK" ]; then
    rm "$SYMLINK"
    echo -e "${GREEN}Removed symlink:${NC} $SYMLINK"
else
    echo -e "${YELLOW}Symlink not found:${NC} $SYMLINK"
fi

# Remove virtual environment
if [ -d "$VENV_DIR" ]; then
    rm -rf "$VENV_DIR"
    echo -e "${GREEN}Removed virtual environment:${NC} $VENV_DIR"
else
    echo -e "${YELLOW}Virtual environment not found:${NC} $VENV_DIR"
fi

# Clean up empty directory
if [ -d "$HOME/.notion-tool" ] && [ -z "$(ls -A $HOME/.notion-tool 2>/dev/null)" ]; then
    rmdir "$HOME/.notion-tool"
    echo -e "${GREEN}Removed empty directory:${NC} $HOME/.notion-tool"
fi

echo ""
echo -e "${GREEN}Uninstallation complete!${NC}"
echo ""
echo "Note: Your NOTION_API_KEY environment variable and PATH changes"
echo "in your shell config remain unchanged (for safety)."
