#!/usr/bin/env bash
set -e

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BIN_DIR="$HOME/.local/bin"
CAI_DIR="$HOME/.cai"
INSTALL_LIB="$CAI_DIR/lib"

mkdir -p "$BIN_DIR" "$INSTALL_LIB"

# Save real claude path (resolve symlinks) BEFORE we shadow it
# Skip if already saved — prevents overwriting with our own wrapper path on re-install
if [ ! -f "$CAI_DIR/real_claude" ]; then
    REAL_CLAUDE=$(readlink -f "$(which claude 2>/dev/null)" 2>/dev/null || which claude 2>/dev/null || echo "")
    if [ -z "$REAL_CLAUDE" ] || [ ! -f "$REAL_CLAUDE" ]; then
        echo "Error: claude not found in PATH. Install Claude Code CLI first."
        exit 1
    fi
    echo "$REAL_CLAUDE" > "$CAI_DIR/real_claude"
    echo "  Real claude saved: $REAL_CLAUDE"
fi

# Copy router + modules to stable location
cp "$REPO_DIR/claude" "$INSTALL_LIB/claude"
cp "$REPO_DIR/classifier.py" "$INSTALL_LIB/classifier.py"
cp "$REPO_DIR/logger.py" "$INSTALL_LIB/logger.py"
chmod +x "$INSTALL_LIB/claude"

# Write shim to ~/.local/bin/claude
# Use rm -f first to avoid "Text file busy" when claude is currently running
rm -f "$BIN_DIR/claude"
cat > "$BIN_DIR/claude" << 'SHIM'
#!/usr/bin/env bash
exec python3 "$HOME/.cai/lib/claude" "$@"
SHIM
chmod +x "$BIN_DIR/claude"

# Ensure ~/.local/bin is first in PATH
for RC in "$HOME/.bashrc" "$HOME/.zshrc"; do
    if [ -f "$RC" ] && ! grep -q 'local/bin.*PATH\|PATH.*local/bin' "$RC"; then
        echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$RC"
        echo "  Added ~/.local/bin to PATH in $RC — run: source $RC"
    fi
done

echo "✓ claude router installed to $BIN_DIR/claude"
echo ""
echo "  Usage (unchanged — just type claude as normal):"
echo "    claude \"check apache logs for errors\"   → auto-routes to Haiku"
echo "    claude \"write RCA report for incident\"  → auto-routes to Sonnet"
echo "    claude --stats                           → 7-day usage summary"
echo "    claude --dry-run \"your task\"            → preview routing"
echo "    claude --model sonnet \"task\"            → manual override"
