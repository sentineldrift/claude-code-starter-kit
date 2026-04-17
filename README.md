# Claude Code Starter Kit

**The infrastructure you wish you had on Day 1.**

Turn Claude Code into a persistent, self-improving research partner in 30 minutes.
This kit packages two weeks of learning into a one-command setup.

## What You Get

| Layer | What It Does | Without It |
|-------|-------------|------------|
| **Knowledge Graph (MCP)** | Claude remembers everything across sessions | Starts brain-dead every time |
| **RAG Semantic Search** | Fuzzy search across all your docs + code | Re-reads giant markdown files |
| **Sequential Thinking (MCP)** | Forced step-by-step reasoning on hard problems | Skips steps, makes mistakes |
| **Hooks** | Blocks UI-crashing commands, auto-formats code, logs activity | UI freezes, inconsistent style |
| **Skills** | `/autopsy`, `/parallel-factory`, `/auto-research` — reusable workflows | Rebuilds same workflow every time |
| **Notifications** | Telegram + Gmail alerts from your scripts | No awareness when away from keyboard |
| **Auto-commit** | Push to GitHub after each change with one command | Manual git wrangling |
| **Session Memory** | Daily summaries of what Claude did | Lost context after restart |

## Quick Start (30 min)

### Prereqs
- Windows 10/11 (PowerShell) or macOS/Linux (bash)
- Python 3.11+ installed
- Node.js 18+ (for MCP servers)
- GitHub account + [personal access token with `repo` scope](https://github.com/settings/tokens/new)

### Install

```powershell
# Clone this kit into your project folder (or next to it)
git clone https://github.com/sentineldrift/claude-code-starter-kit.git
cd claude-code-starter-kit

# Run the setup — interactive, asks about your project
powershell -ExecutionPolicy Bypass -File setup.ps1
```

Or on macOS/Linux:
```bash
git clone https://github.com/sentineldrift/claude-code-starter-kit.git
cd claude-code-starter-kit
bash setup.sh
```

### What the setup does

1. Installs MCP servers (memory, sequential-thinking) via npm
2. Installs Python deps (ChromaDB, sentence-transformers)
3. Copies hooks to `~/.claude/hooks/`
4. Copies skills to `~/.claude/skills/`
5. Registers hooks in `~/.claude/settings.local.json`
6. Configures MCP servers in Claude Desktop config
7. Creates `.claude/` folder in your project with:
   - `secrets_template.json` (copy to `secrets.json` and fill in)
   - Empty memory graph seed file
8. Drops a `CLAUDE.md` starter at the top of your project
9. (Optional) Initializes git repo + pushes to GitHub

### After setup

Restart Claude Code. You'll see:
- New MCP tools available (`mcp__memory__*`, `mcp__sequential_thinking__*`)
- Skills loaded (ask "what skills are available")
- Hooks active (long bash commands now blocked automatically)

## What's In The Box

```
claude-code-starter-kit/
├── README.md                      # You are here
├── setup.ps1                      # Windows setup
├── setup.sh                       # Mac/Linux setup
├── requirements.txt               # Python deps
│
├── .claude-template/              # Gets copied to ~/.claude/
│   ├── hooks/
│   │   ├── block_long_bash.py         # Prevents UI-crashing permission dialogs
│   │   ├── auto_format_python.py      # Auto-black on every edit
│   │   └── log_session_activity.py    # Feeds the self-improving loop
│   └── skills/
│       ├── auto-research-loop/        # Self-improving experiment proposer
│       └── parallel-subagent-factory/ # Multi-agent worktree fan-out
│
├── scripts/                       # Universal tools (copied to your project/scripts/)
│   ├── notify.py                  # Unified Telegram + Gmail + log
│   ├── auto_commit.py             # One-command commit + push
│   ├── session_memory.py          # Daily activity summaries
│   └── local_rag_server.py        # Semantic search over your project
│
└── docs/
    ├── ARCHITECTURE.md            # Why each piece exists
    ├── DAY1_CHECKLIST.md          # Recommended order of operations
    ├── CUSTOMIZATION.md           # How to adapt skills to your domain
    └── INTEGRATIONS.md            # Telegram, Gmail, GitHub setup
```

## Philosophy

Most new Claude Code users spend their first week:
1. Re-explaining context every session
2. Reading giant markdown files Claude forgot
3. Typing long bash commands that crash the UI
4. Building the same workflow three different ways
5. Losing work because nothing persisted

This kit makes that week one command.

## Who This Is For

- Anyone starting a new Claude Code project (any domain)
- Developers who want agentic workflows that remember
- Researchers drowning in their own notes
- Quant/trading folks (domain-specific skills in `.claude-template/skills/trading-addon/`)
- Teams onboarding devs to Claude Code

## Credits

Built by [@sentineldrift](https://github.com/sentineldrift) — distilled from 2 weeks of trial and error on a systematic futures trading project. Open sourced so you don't have to repeat the journey.

## License

MIT — use it, fork it, improve it.
