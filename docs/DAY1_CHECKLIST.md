# Day 1 Checklist

Follow this order for a new Claude Code project. Takes ~45 minutes total.

## Phase 1 — Prereqs (10 min, one-time per machine)

- [ ] Install Python 3.11+ from python.org
- [ ] Install Node.js 18+ from nodejs.org
- [ ] Install Git from git-scm.com
- [ ] Install Claude Code desktop from https://claude.com/code
- [ ] Create a GitHub account (free tier is fine)
- [ ] Create a GitHub Personal Access Token at https://github.com/settings/tokens/new
  - Scopes: ✅ `repo` (full control)
  - Expiration: 90 days
  - Save the `ghp_...` token somewhere safe

## Phase 2 — Run The Setup (5 min)

```
git clone https://github.com/sentineldrift/claude-code-starter-kit.git
cd claude-code-starter-kit

# Windows
powershell -ExecutionPolicy Bypass -File setup.ps1

# Mac/Linux
bash setup.sh
```

When prompted, give it the path to your project folder. If it doesn't exist, the script creates it.

- [ ] Setup script completes with no errors
- [ ] Fully quit Claude Code (from task manager if needed) and reopen
- [ ] Open your project folder in Claude Code

## Phase 3 — Configure Secrets (10 min)

1. Copy `.claude/secrets_template.json` to `.claude/secrets.json`
2. Fill in the credentials you want:

### Telegram bot (recommended — fastest alerts)

- [ ] Open Telegram app or https://web.telegram.org
- [ ] Search for `@BotFather`, send `/newbot`
- [ ] Pick a display name + username ending in `_bot`
- [ ] BotFather gives you a token like `1234567890:AAH...` — paste as `telegram_bot_token`
- [ ] Send any message to your new bot
- [ ] Visit `https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates`
- [ ] Find the `"chat":{"id":...}` value — paste as `telegram_chat_id`

### Gmail SMTP (optional — for reports, not spam)

- [ ] Enable 2-Step Verification on your Google account
- [ ] Create an App Password at https://myaccount.google.com/apppasswords
- [ ] 16-char code goes in `gmail_app_password`

### GitHub (for auto-commit + auto-push)

- [ ] PAT from Phase 1 step goes in `github_pat`

## Phase 4 — First Real Use (10 min)

### Test Telegram
```
cd my-project
python scripts/notify.py test
```
- [ ] Get a message in Telegram

### Index your docs
```
python scripts/local_rag_server.py index
```
- [ ] See "Indexing complete" with N doc chunks

### Test semantic search
```
python scripts/local_rag_server.py search "what is this project about"
```
- [ ] See relevant passages from your CLAUDE.md / docs

### Test the knowledge graph
Ask Claude:
> *"Use mcp__memory__read_graph to show me what's in the knowledge graph"*

- [ ] Empty graph returned (expected — it's day 1)

### Populate the graph (as you work)
Ask Claude:
> *"Create an entity for this project in the memory graph with these observations: [list the key facts about your project]"*

- [ ] Entity created — now persists across sessions

## Phase 5 — Write CLAUDE.md (10 min)

Edit the generated CLAUDE.md at the top of your project. Include:

- [ ] One-paragraph description of the project
- [ ] Critical rules Claude must follow (style, safety, testing)
- [ ] File structure summary
- [ ] Useful commands (how to run tests, build, etc.)
- [ ] Any domain-specific vocabulary

Save it. Claude reads this file at the start of every session automatically.

## You're Done — Now Start The Real Work

From this point forward, every conversation:
1. Claude reads CLAUDE.md automatically
2. Claude queries the memory graph when you ask "what do you know about X"
3. Claude searches the RAG when you ask fuzzy questions
4. Hooks run silently on every tool call
5. You can invoke skills with plain English ("run autopsy on X", "fan out to agents")
6. `python scripts/auto_commit.py "msg"` pushes after any meaningful change

## Troubleshooting

### "MCP tools not available after restart"
- Fully quit Claude Code (Task Manager on Windows, force quit on Mac)
- Check `~/.claude_desktop_config.json` or equivalent has the server entries
- Verify `npm list -g` shows the MCP packages

### "Hooks don't seem to fire"
- Check `~/.claude/settings.local.json` has the `hooks` section
- Try the `/hooks` command in Claude to reload
- Settings watcher only watches folders that had a settings file at launch time

### "Telegram test fails"
- Verify `secrets.json` has real values (not the `PASTE_...` placeholders)
- Message your bot at least once before running getUpdates
- Bot token format: `<digits>:<alphanumeric>`

### "Gmail test fails: 5.7.8 BadCredentials"
- You used your regular password instead of an App Password
- App passwords only work with 2FA enabled
- Copy the 16-char code without spaces
