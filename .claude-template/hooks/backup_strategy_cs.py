#!/usr/bin/env python3
"""
Hook: Back up NinjaScript .cs files before modification.
Creates a timestamped copy in bak_strategies/ next to the original.
"""
import json, sys, shutil, os
from datetime import datetime

try:
    data = json.load(sys.stdin)
    tool = data.get("tool_name", "")
    if tool not in ("Edit", "Write"):
        sys.exit(0)
    path = data.get("tool_input", {}).get("file_path", "")
    if not path.endswith(".cs"):
        sys.exit(0)
    if "NinjaTrader" not in path and "Strategies" not in path:
        sys.exit(0)
    if not os.path.exists(path):
        sys.exit(0)
    # CRITICAL: store backups OUTSIDE any NinjaTrader Strategies/Indicators folder.
    # NinjaTrader scans ALL .cs files under bin/Custom for compilation - if we put
    # backups in a subfolder there, they cause duplicate-class compile errors.
    # Use the user's Desktop\TradingAI\strategies_backups\ instead (outside NT8 scan).
    backup_root = os.path.expanduser(r"~\Desktop\TradingAI\strategies_backups")
    os.makedirs(backup_root, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    # Use .bak extension (not .cs) so even if this WAS under NT8 Custom, it'd be ignored.
    name = os.path.basename(path).replace(".cs", f"_{ts}.bak")
    shutil.copy2(path, os.path.join(backup_root, name))
except Exception:
    pass
sys.exit(0)
