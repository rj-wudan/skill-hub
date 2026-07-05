#!/bin/bash
# Install cls-case-weekly-report skill to supported AI coding platforms
set -e

SKILL_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILL_NAME="cls-case-weekly-report"

echo "Installing ${SKILL_NAME} skill..."

# Hermes Agent
if [ -d "$HOME/.hermes" ]; then
    TARGET="$HOME/.hermes/skills/devops/${SKILL_NAME}"
    rm -rf "$TARGET"
    cp -r "$SKILL_DIR" "$TARGET"
    echo "  ✅ Hermes Agent: $TARGET"
else
    echo "  ⬜ Hermes Agent: not found"
fi

# Claude Code
if command -v claude &>/dev/null || [ -d "$HOME/.claude" ]; then
    TARGET="$HOME/.claude/skills/${SKILL_NAME}"
    mkdir -p "$(dirname "$TARGET")"
    rm -rf "$TARGET"
    cp -r "$SKILL_DIR" "$TARGET"
    echo "  ✅ Claude Code: $TARGET"
else
    echo "  ⬜ Claude Code: not found"
fi

# OpenCode
if [ -d "$HOME/.opencode" ]; then
    TARGET="$HOME/.opencode/skills/${SKILL_NAME}"
    mkdir -p "$(dirname "$TARGET")"
    rm -rf "$TARGET"
    cp -r "$SKILL_DIR" "$TARGET"
    echo "  ✅ OpenCode: $TARGET"
else
    echo "  ⬜ OpenCode: not found"
fi

# Cursor
if [ -d "$HOME/.cursor" ]; then
    TARGET="$HOME/.cursor/skills/${SKILL_NAME}"
    mkdir -p "$(dirname "$TARGET")"
    rm -rf "$TARGET"
    cp -r "$SKILL_DIR" "$TARGET"
    echo "  ✅ Cursor: $TARGET"
else
    echo "  ⬜ Cursor: not found"
fi

# Windsurf
if [ -d "$HOME/.windsurf" ]; then
    TARGET="$HOME/.windsurf/skills/${SKILL_NAME}"
    mkdir -p "$(dirname "$TARGET")"
    rm -rf "$TARGET"
    cp -r "$SKILL_DIR" "$TARGET"
    echo "  ✅ Windsurf: $TARGET"
else
    echo "  ⬜ Windsurf: not found"
fi

# GitHub Copilot (VS Code extension)
if [ -d "$HOME/.vscode" ] || [ -d "$HOME/.vscode-insiders" ]; then
    for BASE in "$HOME/.vscode" "$HOME/.vscode-insiders"; do
        if [ -d "$BASE" ]; then
            TARGET="$BASE/skills/${SKILL_NAME}"
            mkdir -p "$(dirname "$TARGET")"
            rm -rf "$TARGET"
            cp -r "$SKILL_DIR" "$TARGET"
            echo "  ✅ VS Code/Copilot: $TARGET"
        fi
    done
else
    echo "  ⬜ VS Code/Copilot: not found"
fi

# Generic: also copy to current project if inside a git repo
if git rev-parse --git-dir &>/dev/null 2>&1; then
    PROJECT_ROOT="$(git rev-parse --show-toplevel)"
    TARGET="$PROJECT_ROOT/.skills/${SKILL_NAME}"
    mkdir -p "$(dirname "$TARGET")"
    rm -rf "$TARGET"
    cp -r "$SKILL_DIR" "$TARGET"
    echo "  ✅ Project-local: $TARGET"
fi

echo ""
echo "Done! Next steps:"
echo "  1. Edit ${SKILL_NAME}/scripts/generate_report.py to set your Redmine URL, username, and password"
echo "  2. Test: python3 ${SKILL_NAME}/scripts/generate_report.py"
echo "  3. Ask your AI agent: 'generate the weekly Redmine report'"
