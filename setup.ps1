# Claude Code Starter Kit — Windows Setup
# Run: powershell -ExecutionPolicy Bypass -File setup.ps1

$ErrorActionPreference = "Stop"
$kit = $PSScriptRoot
$claude_home = "$env:USERPROFILE\.claude"
$desktop_config = "$env:APPDATA\Claude\claude_desktop_config.json"

Write-Host "Claude Code Starter Kit Setup" -ForegroundColor Cyan
Write-Host "=============================="

# 1. Ask for project folder
Write-Host ""
$project = Read-Host "Project folder (absolute path, default: current directory)"
if ([string]::IsNullOrWhiteSpace($project)) { $project = (Get-Location).Path }
if (-not (Test-Path $project)) { New-Item -ItemType Directory -Path $project -Force | Out-Null }
Write-Host "Project: $project"

# 2. Check Python + Node
Write-Host ""
Write-Host "Checking prereqs..."
$py_ok  = $null -ne (Get-Command python -ErrorAction SilentlyContinue)
$npm_ok = $null -ne (Get-Command npm    -ErrorAction SilentlyContinue)
$git_ok = $null -ne (Get-Command git    -ErrorAction SilentlyContinue)

if (-not $py_ok)  { throw "Python not found. Install Python 3.11+ from python.org" }
if (-not $npm_ok) { throw "npm not found. Install Node.js 18+ from nodejs.org" }
if (-not $git_ok) { throw "git not found. Install Git for Windows." }
Write-Host "  python: ok" -ForegroundColor Green
Write-Host "  npm:    ok" -ForegroundColor Green
Write-Host "  git:    ok" -ForegroundColor Green

# 3. Install Python deps
Write-Host ""
Write-Host "Installing Python deps (ChromaDB + sentence-transformers)..." -ForegroundColor Yellow
python -m pip install --quiet chromadb sentence-transformers

# 4. Install MCP servers globally
Write-Host ""
Write-Host "Installing MCP servers (memory + sequential-thinking)..." -ForegroundColor Yellow
npm install -g @modelcontextprotocol/server-memory @modelcontextprotocol/server-sequential-thinking zod

# 5. Copy hooks + skills to ~/.claude/
Write-Host ""
Write-Host "Installing hooks and skills to $claude_home" -ForegroundColor Yellow
New-Item -ItemType Directory -Path "$claude_home\hooks" -Force | Out-Null
New-Item -ItemType Directory -Path "$claude_home\skills" -Force | Out-Null
Copy-Item "$kit\.claude-template\hooks\*" "$claude_home\hooks\" -Force
Copy-Item "$kit\.claude-template\skills\*" "$claude_home\skills\" -Recurse -Force
Write-Host "  hooks: $((Get-ChildItem "$claude_home\hooks\*.py").Count) files" -ForegroundColor Green
Write-Host "  skills: $((Get-ChildItem "$claude_home\skills" -Directory).Count) skills" -ForegroundColor Green

# 6. Register hooks in settings.local.json (merge-safe)
Write-Host ""
Write-Host "Registering hooks in Claude Code settings..." -ForegroundColor Yellow
$settings_file = "$claude_home\settings.local.json"
if (Test-Path $settings_file) {
    $settings = Get-Content $settings_file -Raw | ConvertFrom-Json
} else {
    $settings = [PSCustomObject]@{ permissions = [PSCustomObject]@{ allow = @() } }
}
# Merge hooks config without overwriting existing hooks
$hooks_json = @"
{
  "PreToolUse": [
    { "matcher": "Bash", "hooks": [{ "type": "command", "command": "python \"$claude_home\\hooks\\block_long_bash.py\"", "timeout": 5 }] }
  ],
  "PostToolUse": [
    { "matcher": "Write|Edit", "hooks": [
      { "type": "command", "command": "python \"$claude_home\\hooks\\auto_format_python.py\"", "timeout": 15 },
      { "type": "command", "command": "python \"$claude_home\\hooks\\log_session_activity.py\"", "timeout": 5 }
    ]}
  ]
}
"@
$settings | Add-Member -NotePropertyName hooks -NotePropertyValue ($hooks_json | ConvertFrom-Json) -Force
$settings | ConvertTo-Json -Depth 10 | Set-Content $settings_file -Encoding UTF8
Write-Host "  hooks registered" -ForegroundColor Green

# 7. Configure MCP servers in Claude Desktop config
Write-Host ""
Write-Host "Configuring MCP servers in Claude Desktop..." -ForegroundColor Yellow
$mcp_dir = Split-Path $desktop_config -Parent
if (-not (Test-Path $mcp_dir)) { New-Item -ItemType Directory -Path $mcp_dir -Force | Out-Null }

$npm_bin = "$env:APPDATA\npm"
$memory_bin = "$npm_bin\mcp-server-memory.cmd"
$seqthink_bin = "$npm_bin\mcp-server-sequential-thinking.cmd"
$memory_file = "$project\.claude\memory_graph.json"

if (Test-Path $desktop_config) {
    $dc = Get-Content $desktop_config -Raw | ConvertFrom-Json
    if (-not $dc.mcpServers) { $dc | Add-Member -NotePropertyName mcpServers -NotePropertyValue ([PSCustomObject]@{}) -Force }
} else {
    $dc = [PSCustomObject]@{ mcpServers = [PSCustomObject]@{} }
}
$dc.mcpServers | Add-Member -NotePropertyName memory -NotePropertyValue ([PSCustomObject]@{
    command = $memory_bin
    env = [PSCustomObject]@{ MEMORY_FILE_PATH = $memory_file }
}) -Force
$dc.mcpServers | Add-Member -NotePropertyName "sequential-thinking" -NotePropertyValue ([PSCustomObject]@{
    command = $seqthink_bin
}) -Force
$dc | ConvertTo-Json -Depth 10 | Set-Content $desktop_config -Encoding UTF8
Write-Host "  mcp: memory + sequential-thinking registered" -ForegroundColor Green

# 8. Set up project .claude folder
Write-Host ""
Write-Host "Setting up project .claude folder..." -ForegroundColor Yellow
New-Item -ItemType Directory -Path "$project\.claude" -Force | Out-Null
New-Item -ItemType Directory -Path "$project\scripts" -Force | Out-Null

# Copy universal scripts
Copy-Item "$kit\scripts\*" "$project\scripts\" -Force

# Secrets template
$secrets_template = @"
{
  "_comment": "Copy this file to secrets.json and fill in real values. secrets.json is gitignored.",
  "telegram_bot_token": "PASTE_BOT_TOKEN_FROM_BOTFATHER",
  "telegram_chat_id": "PASTE_YOUR_CHAT_ID",
  "gmail_address": "you@gmail.com",
  "gmail_app_password": "PASTE_16_CHAR_APP_PASSWORD",
  "gmail_to_address": "you@gmail.com",
  "github_pat": "ghp_...",
  "github_username": "your_username"
}
"@
Set-Content "$project\.claude\secrets_template.json" -Value $secrets_template -Encoding UTF8

# CLAUDE.md template
$claude_md = @"
# Project Context for Claude

## What this project does
(Describe the project purpose here.)

## Key technology stack
(List languages, frameworks, runtimes.)

## Critical rules
1. (Add project-specific rules Claude must follow.)
2. (E.g., coding style, testing requirements, commit conventions.)

## File structure
- ``scripts/`` — utilities and automation
- ``docs/`` — reference documentation
- ``.claude/`` — memory graph, RAG index, secrets (gitignored)

## Useful commands
``````
python scripts/auto_commit.py "message"   # commit + push
python scripts/local_rag_server.py index   # reindex docs
python scripts/local_rag_server.py search "query"
python scripts/session_memory.py latest
``````

## Skills available
- ``auto-research-loop`` — propose next experiments based on session logs
- ``parallel-subagent-factory`` — spawn multiple subagents in isolated worktrees

## Knowledge graph
Stored at ``.claude/memory_graph.json``. Query via ``mcp__memory__*`` tools.
"@
if (-not (Test-Path "$project\CLAUDE.md")) {
    Set-Content "$project\CLAUDE.md" -Value $claude_md -Encoding UTF8
    Write-Host "  CLAUDE.md created" -ForegroundColor Green
} else {
    Write-Host "  CLAUDE.md already exists (not overwritten)" -ForegroundColor Yellow
}

# 9. Gitignore
$gi_additions = @"

# Claude Code starter kit additions
.claude/memory_graph.json
.claude/rag_chroma_db/
.claude/session_logs/
.claude/session_memory.jsonl
.claude/secrets.json
.claude/notifications.log
"@
if (Test-Path "$project\.gitignore") {
    Add-Content "$project\.gitignore" -Value $gi_additions
} else {
    Set-Content "$project\.gitignore" -Value $gi_additions.Trim() -Encoding UTF8
}
Write-Host "  .gitignore updated" -ForegroundColor Green

Write-Host ""
Write-Host "================ SETUP COMPLETE ================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:"
Write-Host "  1. Edit $project\CLAUDE.md with your project context"
Write-Host "  2. Copy $project\.claude\secrets_template.json to secrets.json and fill in credentials"
Write-Host "  3. RESTART CLAUDE CODE (fully quit, then reopen)"
Write-Host "  4. After restart, index your docs:"
Write-Host "       cd $project"
Write-Host "       python scripts\local_rag_server.py index"
Write-Host ""
Write-Host "  5. Test the knowledge graph: ask Claude 'what do you remember about this project'"
Write-Host ""
