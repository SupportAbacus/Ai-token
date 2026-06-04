#!/usr/bin/env bash
set -e

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BIN_DIR="$HOME/.local/bin"
CC_DIR="$HOME/.cai"
INSTALL_LIB="$CC_DIR/lib"

mkdir -p "$BIN_DIR" "$INSTALL_LIB"

# Copy modules to a stable location so imports always work
cp "$REPO_DIR/cai" "$INSTALL_LIB/cai"
cp "$REPO_DIR/classifier.py" "$INSTALL_LIB/classifier.py"
cp "$REPO_DIR/logger.py" "$INSTALL_LIB/logger.py"
chmod +x "$INSTALL_LIB/cai"

# Write a shim to ~/.local/bin/cai that calls the installed copy
cat > "$BIN_DIR/cai" << 'SHIM'
#!/usr/bin/env bash
exec python3 "$HOME/.cai/lib/cai" "$@"
SHIM
chmod +x "$BIN_DIR/cai"

# Add ~/.local/bin to PATH if not already present
for RC in "$HOME/.bashrc" "$HOME/.zshrc"; do
    if [ -f "$RC" ] && ! grep -q '\.local/bin' "$RC"; then
        echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$RC"
        echo "  Added ~/.local/bin to PATH in $RC — run: source $RC"
    fi
done

echo "✓ cai installed to $BIN_DIR/cai"
echo ""
echo "  Quick test:"
echo "    cai --dry-run \"check apache logs for errors\"   → Haiku"
echo "    cai --dry-run \"write RCA report for incident\"  → Sonnet"
echo "    cai --stats"
