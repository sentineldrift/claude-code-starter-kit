#!/usr/bin/env python3
"""
Hook: Append session activity to a daily log for the self-improving loop to analyze.
"""
import json, sys, os
from datetime import datetime

LOG_DIR = r"C:\Users\Administrator\Desktop\TradingAI\.claude\session_logs"

try:
    data = json.load(sys.stdin)
    os.makedirs(LOG_DIR, exist_ok=True)
    day = datetime.now().strftime("%Y-%m-%d")
    log_path = os.path.join(LOG_DIR, f"{day}.jsonl")
    event = {
        "ts": datetime.now().isoformat(),
        "hook": data.get("hook_event_name", ""),
        "tool": data.get("tool_name", ""),
        "ok": True,
    }
    # Add minimal tool-specific context
    ti = data.get("tool_input", {})
    if data.get("tool_name") == "Bash":
        event["cmd_head"] = str(ti.get("command", ""))[:80]
    elif data.get("tool_name") in ("Write", "Edit"):
        event["path"] = ti.get("file_path", "")
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(event) + "\n")
except Exception:
    pass
sys.exit(0)
