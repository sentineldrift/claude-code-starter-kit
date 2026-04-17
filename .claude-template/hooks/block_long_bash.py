#!/usr/bin/env python3
"""
Hook: Block bash commands over 500 chars to prevent UI crash from massive permission dialogs.
Runs on PreToolUse for Bash tool.
"""
import json, sys

try:
    data = json.load(sys.stdin)
    if data.get("tool_name") != "Bash":
        sys.exit(0)
    cmd = data.get("tool_input", {}).get("command", "")
    if len(cmd) > 500:
        print(
            "ERROR: Bash command is {} chars (max 500). "
            "Write the script to a file first, then run with a short command.".format(len(cmd)),
            file=sys.stderr,
        )
        sys.exit(2)  # exit 2 = block the tool use
except Exception:
    pass
sys.exit(0)
