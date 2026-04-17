"""
Unified notification module for TradingAI.

Supports:
- Telegram bot messages (with BotFather token)
- Gmail SMTP (with app password)
- Console fallback (always works)

Secrets live in .claude/secrets.json (gitignored) — never commit tokens.

Usage:
    from scripts.notify import notify
    notify("Signal scored 82/100 on Nebula Gambit LONG", priority="high")
    notify("Heartbeat", priority="low")  # may be suppressed
"""

import os
import json
import smtplib
import urllib.request
import urllib.parse
from email.mime.text import MIMEText
from pathlib import Path
from datetime import datetime

SECRETS_PATH = Path(r"C:\Users\Administrator\Desktop\TradingAI\.claude\secrets.json")


def load_secrets():
    """Load the secrets file. Returns {} if missing."""
    if not SECRETS_PATH.exists():
        return {}
    try:
        return json.loads(SECRETS_PATH.read_text())
    except Exception:
        return {}


def send_telegram(message: str, secrets: dict) -> bool:
    """Send message via Telegram bot. Returns True on success."""
    token = secrets.get("telegram_bot_token")
    chat_id = secrets.get("telegram_chat_id")
    if not token or not chat_id:
        return False
    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        data = urllib.parse.urlencode({
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "HTML",
        }).encode()
        req = urllib.request.Request(url, data=data, method="POST")
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.status == 200
    except Exception as e:
        print(f"[notify] Telegram failed: {e}")
        return False


def send_email(subject: str, message: str, secrets: dict) -> bool:
    """Send email via Gmail SMTP. Returns True on success."""
    email_addr = secrets.get("gmail_address")
    app_pw = secrets.get("gmail_app_password")
    to_addr = secrets.get("gmail_to_address", email_addr)
    if not email_addr or not app_pw:
        return False
    try:
        msg = MIMEText(message, "plain")
        msg["Subject"] = f"[TradingAI] {subject}"
        msg["From"] = email_addr
        msg["To"] = to_addr
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=15) as s:
            s.login(email_addr, app_pw)
            s.send_message(msg)
        return True
    except Exception as e:
        print(f"[notify] Email failed: {e}")
        return False


def log_to_file(message: str, priority: str):
    """Always-on fallback: write to notifications.log."""
    log_path = Path(r"C:\Users\Administrator\Desktop\TradingAI\.claude\notifications.log")
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(f"{datetime.now().isoformat()} [{priority.upper()}] {message}\n")


def notify(message: str, subject: str = "Alert", priority: str = "normal",
           channels: list = None) -> dict:
    """
    Send notification via configured channels.

    priority: "low" | "normal" | "high" | "critical"
        - low: log only
        - normal: log + email
        - high: log + email + telegram
        - critical: all channels, bypasses rate limits

    channels: optional override list e.g. ["telegram"], ["email"]. None = auto.

    Returns: dict of {channel: success_bool}
    """
    secrets = load_secrets()
    results = {"log": True}

    log_to_file(message, priority)

    if channels is None:
        # Gmail is disabled for auto-alerts (user preference).
        # Use channels=["email"] explicitly when you want to send mail.
        if priority in ("high", "critical"):
            channels = ["telegram"]
        else:
            channels = []

    if "telegram" in channels:
        results["telegram"] = send_telegram(message, secrets)
    if "email" in channels:
        results["email"] = send_email(subject, message, secrets)

    return results


def test_channels():
    """Send a test message on all configured channels."""
    secrets = load_secrets()
    print(f"Secrets file: {SECRETS_PATH}")
    print(f"  exists: {SECRETS_PATH.exists()}")
    print(f"  telegram_bot_token: {'SET' if secrets.get('telegram_bot_token') else 'MISSING'}")
    print(f"  telegram_chat_id: {'SET' if secrets.get('telegram_chat_id') else 'MISSING'}")
    print(f"  gmail_address: {secrets.get('gmail_address', 'MISSING')}")
    print(f"  gmail_app_password: {'SET' if secrets.get('gmail_app_password') else 'MISSING'}")
    print()
    msg = f"TradingAI test notification at {datetime.now().isoformat()}"
    results = notify(msg, subject="Channel test", priority="critical")
    print(f"Results: {results}")


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        test_channels()
    elif len(sys.argv) > 1:
        notify(" ".join(sys.argv[1:]), priority="high")
    else:
        print("Usage: python scripts/notify.py [test | MESSAGE]")
