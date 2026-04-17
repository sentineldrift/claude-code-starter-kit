#!/usr/bin/env bash
# Claude Code Starter Kit - macOS/Linux setup
# Run: bash setup.sh

set -e
KIT="$(cd "$(dirname "$0")" && pwd)"
CLAUDE_HOME="$HOME/.claude"

echo "Claude Code Starter Kit Setup"
echo "=============================="

# 1. Project folder
echo ""
read -p "Project folder (absolute path, default: current directory): " PROJECT
PROJECT=${PROJECT:-$(pwd)}
mkdir -p "$PROJECT"
echo "Project: $PROJECT"

# 2. Check prereqs
echo ""
echo "Checking prereqs..."
command -v python3 >/dev/null 2>&1 || { echo "Python 3 required"; exit 1; }
command -v npm >/dev/null 2>&1 || { echo "Node.js/npm required"; exit 1; }
command -v git >/dev/null 2>&1 || { echo "git required"; exit 1; }
echo "  python: ok"
echo "  npm:    ok"
echo "  git:    ok"

# 3. Python deps
echo ""
echo "Installing Python deps..."
python3 -m pip install --quiet chromadb sentence-transformers

# 4. MCP servers
echo ""
echo "Installing MCP servers..."
npm install -g @modelcontextprotocol/server-memory @modelcontextprotocol/server-sequential-thinking zod

# 5. Hooks + skills
echo ""
echo "Installing hooks and skills to $CLAUDE_HOME"
mkdir -p "$CLAUDE_HOME/hooks" "$CLAUDE_HOME/skills"
cp -f "$KIT/.claude-template/hooks/"*.py "$CLAUDE_HOME/hooks/"
cp -rf "$KIT/.claude-template/skills/"* "$CLAUDE_HOME/skills/"
echo "  hooks: $(ls "$CLAUDE_HOME/hooks/"*.py 2>/dev/null | wc -l) files"
echo "  skills: $(ls -d "$CLAUDE_HOME/skills/"*/ 2>/dev/null | wc -l) skills"

# 6. Settings with hooks (merge-safe via Python)
echo ""
echo "Registering hooks..."
python3 - <<PYEOF
import json, os
from pathlib import Path

settings_file = Path(os.path.expanduser("~/.claude/settings.local.json"))
hook_dir = str(Path(os.path.expanduser("~/.claude/hooks")))

if settings_file.exists():
    s = json.loads(settings_file.read_text())
else:
    s = {"permissions": {"allow": []}}

s["hooks"] = {
    "PreToolUse": [
        {"matcher": "Bash", "hooks": [
            {"type": "command", "command": f'python3 "{hook_dir}/block_long_bash.py"', "timeout": 5}
        ]}
    ],
    "PostToolUse": [
        {"matcher": "Write|Edit", "hooks": [
            {"type": "command", "command": f'python3 "{hook_dir}/auto_format_python.py"', "timeout": 15},
            {"type": "command", "command": f'python3 "{hook_dir}/log_session_activity.py"', "timeout": 5}
        ]}
    ]
}
settings_file.write_text(json.dumps(s, indent=2))
print("  hooks registered")
PYEOF

# 7. MCP Desktop config
echo ""
echo "Configuring MCP servers..."
DC_DIR="$HOME/Library/Application Support/Claude"
[ "$(uname)" = "Linux" ] && DC_DIR="$HOME/.config/Claude"
mkdir -p "$DC_DIR"
DC="$DC_DIR/claude_desktop_config.json"

python3 - <<PYEOF
import json, os
from pathlib import Path

dc = Path("$DC")
memory_file = Path("$PROJECT/.claude/memory_graph.json")

if dc.exists():
    c = json.loads(dc.read_text())
else:
    c = {"mcpServers": {}}
if "mcpServers" not in c:
    c["mcpServers"] = {}

c["mcpServers"]["memory"] = {
    "command": "mcp-server-memory",
    "env": {"MEMORY_FILE_PATH": str(memory_file)}
}
c["mcpServers"]["sequential-thinking"] = {
    "command": "mcp-server-sequential-thinking"
}
dc.write_text(json.dumps(c, indent=2))
print("  mcp: memory + sequential-thinking registered")
PYEOF

# 8. Project .claude folder + scripts + templates
echo ""
echo "Setting up project ..."
mkdir -p "$PROJECT/.claude" "$PROJECT/scripts"
cp -f "$KIT/scripts/"*.py "$PROJECT/scripts/"

cat > "$PROJECT/.claude/secrets_template.json" <<'JSON'
{
  "_comment": "Copy to secrets.json and fill in. secrets.json is gitignored.",
  "telegram_bot_token": "PASTE_BOT_TOKEN_FROM_BOTFATHER",
  "telegram_chat_id": "PASTE_YOUR_CHAT_ID",
  "gmail_address": "you@gmail.com",
  "gmail_app_password": "PASTE_16_CHAR_APP_PASSWORD",
  "gmail_to_address": "you@gmail.com",
  "github_pat": "ghp_...",
  "github_username": "your_username"
}
JSON

if [ ! -f "$PROJECT/CLAUDE.md" ]; then
cat > "$PROJECT/CLAUDE.md" <<'MD'
# Project Context for Claude

## What this project does
(Describe the project purpose here.)

## Critical rules
1. (Add project-specific rules Claude must follow.)

## Skills available
- `auto-research-loop` - propose next experiments
- `parallel-subagent-factory` - spawn concurrent subagents

## Knowledge graph at .claude/memory_graph.json
MD
  echo "  CLAUDE.md created"
else
  echo "  CLAUDE.md exists (not overwritten)"
fi

cat >> "$PROJECT/.gitignore" <<'GI'

# Claude Code starter kit additions
.claude/memory_graph.json
.claude/rag_chroma_db/
.claude/session_logs/
.claude/session_memory.jsonl
.claude/secrets.json
.claude/notifications.log
GI

echo ""
echo "================ SETUP COMPLETE ================"
echo ""
echo "Next steps:"
echo "  1. Edit $PROJECT/CLAUDE.md with your project context"
echo "  2. Copy $PROJECT/.claude/secrets_template.json to secrets.json and fill in credentials"
echo "  3. RESTART CLAUDE CODE fully"
echo "  4. After restart: cd $PROJECT && python3 scripts/local_rag_server.py index"
echo ""
