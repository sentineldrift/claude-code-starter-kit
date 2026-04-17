# Integrations — Telegram, Gmail, GitHub Setup

Detailed walkthroughs for each integration the kit supports.

## Telegram (recommended)

### Why Telegram
- Instant delivery (no SMTP daily quotas)
- Works on every phone
- Can send text + images + files
- Free forever

### Setup

1. Open Telegram — app or https://web.telegram.org
2. Search for **@BotFather** and start a chat
3. Send: `/newbot`
4. Give a display name: `MyProject Alerts`
5. Give a username ending in `_bot`: `myproject_alerts_bot`
6. BotFather replies with a token:
   ```
   1234567890:AAH-xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```
   **Copy this token.**

### Get your chat_id

1. In Telegram, find your new bot and send it any message (e.g. "hi")
2. Open in a browser:
   ```
   https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates
   ```
3. You'll see JSON with `"chat":{"id":123456789,...}`
4. **Copy that ID number.**

### Configure

Edit `.claude/secrets.json`:
```json
{
  "telegram_bot_token": "1234567890:AAH-xxxxxxxxxxx",
  "telegram_chat_id": "123456789"
}
```

### Test
```
python scripts/notify.py test
```

You should get a "TradingAI test notification" in Telegram.

## Gmail SMTP (optional)

### Why Gmail
- Good for longer reports / documents
- Native email client support
- Familiar interface

### Gotchas
- **Cannot use regular password** for SMTP
- Requires 2-Step Verification first
- Then requires an App Password (16-char code)
- Daily quota: ~500 messages/day (will lock you out if exceeded)

### Setup

1. Enable 2FA: https://myaccount.google.com/signinoptions/twosv
2. Create App Password: https://myaccount.google.com/apppasswords
   - App name: `ClaudeCode`
   - Copy the 16-char code Google generates (e.g., `abcd efgh ijkl mnop`)

### Configure

Edit `.claude/secrets.json`:
```json
{
  "gmail_address": "you@gmail.com",
  "gmail_app_password": "abcdefghijklmnop",
  "gmail_to_address": "you@gmail.com"
}
```

### Rate limit protection
The kit's `notify.py` defaults to **Telegram only** for automated alerts. Gmail is reserved for explicit on-demand use to avoid burning the daily quota:

```python
from scripts.notify import notify
notify("short alert", priority="high")                       # -> Telegram only
notify("long report", priority="high", channels=["email"])   # -> Gmail only
notify("urgent", priority="critical", channels=["telegram","email"])  # -> both
```

## GitHub Auto-Commit

### Personal Access Token

1. Go to https://github.com/settings/tokens/new
2. Note: `Claude Code Starter Kit`
3. Expiration: 90 days
4. Scopes: ✅ `repo` (full control of private repos)
5. Generate, copy `ghp_...`

### Configure

Edit `.claude/secrets.json`:
```json
{
  "github_pat": "ghp_xxxxxxxxxxxxxxxxxxxx",
  "github_username": "your_username"
}
```

### GitHub CLI (recommended for first-time repo creation)

The kit doesn't install `gh` automatically. To create repos from the command line:

Windows (if winget works):
```
winget install GitHub.cli
```

Manual Windows:
Download https://github.com/cli/cli/releases/latest (gh_windows_amd64.zip), extract, add to PATH.

Auth:
```
echo "ghp_YOUR_TOKEN" | gh auth login --with-token
```

### Auto-commit usage

```
python scripts/auto_commit.py "message here"
```

Stages all changes, commits with your message (falls back to timestamp if omitted), and pushes to origin.

## Webhook / Slack / Discord (not included)

Pattern if you want to add:
1. Get the webhook URL for the service
2. Save it in `secrets.json` as e.g. `slack_webhook_url`
3. Extend `notify.py`:

```python
def send_slack(message, secrets):
    import urllib.request, json
    url = secrets.get("slack_webhook_url")
    if not url: return False
    try:
        data = json.dumps({"text": message}).encode()
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.status == 200
    except Exception:
        return False
```

4. Add to the channel dispatch logic inside `notify()`.

## Anthropic API (for a two-way Telegram bot)

If you want Claude to actually **reply** to your Telegram messages (not just send alerts), you need a polling loop that:
1. Calls `getUpdates` every N seconds
2. When a new message arrives, sends it to the Anthropic API with your knowledge graph as context
3. Posts the response back via `sendMessage`

This costs API usage fees (~$3-15/day at typical chat volume). Not included in the kit because:
- Cowork (Anthropic's remote agent) does this better and it's already bundled with Claude Code
- The kit is designed to be API-key-free by default

If you want it anyway, the pattern is in `contrib/telegram_two_way_bot.py` (not shipped — you'd add it).

## Windows-Specific Notes

- All scripts use forward slashes internally (Git Bash / WSL compatible) but also work with Windows paths
- Python `python` vs `python3` — use whatever your PATH resolves; setup detects and picks
- `winget` not universally available; setup falls back to gentle warnings

## macOS-Specific Notes

- Gatekeeper may block first run of shell scripts; `chmod +x setup.sh` if needed
- Homebrew installation of dependencies is recommended: `brew install python node git`

## Linux-Specific Notes

- Most distributions have Python 3 + git pre-installed
- `curl` required for manual npm install
- If running headless: Telegram works, Gmail works, you won't have a Claude Desktop UI — use Claude Code CLI instead
