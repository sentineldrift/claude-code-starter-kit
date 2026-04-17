"""
Auto-commit helper. Stages all changes, commits with a message, and pushes to origin.
Uses the PAT from secrets.json for non-interactive auth.

Usage:
    python scripts/auto_commit.py "commit message here"
    python scripts/auto_commit.py  # uses default message with timestamp
"""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

BASE = Path(r"C:\Users\Administrator\Desktop\TradingAI")
SECRETS = BASE / ".claude" / "secrets.json"


def run(cmd, cwd=None):
    """Run a command, return (returncode, stdout, stderr)."""
    r = subprocess.run(cmd, cwd=cwd or BASE, capture_output=True, text=True)
    return r.returncode, r.stdout.strip(), r.stderr.strip()


def main():
    message = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else \
        f"Auto-commit: {datetime.now().strftime('%Y-%m-%d %H:%M')}"

    # Check for changes
    rc, out, _ = run(["git", "status", "--porcelain"])
    if rc != 0:
        print("Not a git repo")
        sys.exit(1)
    if not out:
        print("No changes to commit")
        return

    print(f"Changes detected:\n{out[:500]}{'...' if len(out) > 500 else ''}")

    # Stage everything
    run(["git", "add", "-A"])

    # Commit
    rc, out, err = run(["git", "commit", "-m", message])
    if rc != 0:
        print(f"Commit failed: {err}")
        sys.exit(1)
    print(f"Committed: {out.splitlines()[0] if out else message}")

    # Push
    rc, out, err = run(["git", "push", "origin", "main"])
    if rc != 0:
        print(f"Push failed: {err}")
        sys.exit(1)
    print("Pushed to origin/main")

    # Optional notify
    try:
        sys.path.insert(0, str(BASE / "scripts"))
        from notify import notify
        notify(f"📦 Auto-commit pushed: {message}", priority="low")
    except Exception:
        pass


if __name__ == "__main__":
    main()
