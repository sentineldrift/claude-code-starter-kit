#!/usr/bin/env python3
"""
Hook: Auto-format Python files after Write/Edit operations.
Runs on PostToolUse. Silent if formatter unavailable.
"""
import json, sys, subprocess, os

try:
    data = json.load(sys.stdin)
    tool = data.get("tool_name", "")
    if tool not in ("Write", "Edit"):
        sys.exit(0)
    path = data.get("tool_input", {}).get("file_path", "")
    if not path.endswith(".py"):
        sys.exit(0)
    # Try black first, then autopep8, silently skip if neither available
    for cmd in [["black", "--quiet", path], ["python", "-m", "black", "--quiet", path]]:
        try:
            r = subprocess.run(cmd, capture_output=True, timeout=10)
            if r.returncode == 0:
                break
        except Exception:
            continue
except Exception:
    pass
sys.exit(0)
