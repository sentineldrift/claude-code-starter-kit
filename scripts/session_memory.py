"""
Session Memory - Cross-session learning loop.

Reads session activity logs and the knowledge graph, produces a compact summary
of what was learned each day, stores it persistently for the next session to read.

Call: python scripts/session_memory.py summarize
      python scripts/session_memory.py latest
      python scripts/session_memory.py stats
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime, timedelta
from collections import Counter, defaultdict

BASE = Path(r"C:\Users\Administrator\Desktop\TradingAI")
LOG_DIR = BASE / ".claude" / "session_logs"
MEM_FILE = BASE / ".claude" / "session_memory.jsonl"


def load_logs(days_back: int = 7):
    """Load session activity from last N days."""
    events = []
    cutoff = datetime.now() - timedelta(days=days_back)
    if not LOG_DIR.exists():
        return events
    for log_file in sorted(LOG_DIR.glob("*.jsonl")):
        try:
            day_str = log_file.stem
            day = datetime.strptime(day_str, "%Y-%m-%d")
            if day < cutoff:
                continue
            with open(log_file, encoding="utf-8") as f:
                for line in f:
                    try:
                        events.append(json.loads(line))
                    except Exception:
                        continue
        except Exception:
            continue
    return events


def summarize_day(target_date: str = None):
    """Summarize session activity for a specific day."""
    if target_date is None:
        target_date = datetime.now().strftime("%Y-%m-%d")
    log_file = LOG_DIR / f"{target_date}.jsonl"
    if not log_file.exists():
        print(f"No logs for {target_date}")
        return None

    events = []
    with open(log_file, encoding="utf-8") as f:
        for line in f:
            try:
                events.append(json.loads(line))
            except Exception:
                continue

    # Tool usage breakdown
    tools = Counter(e.get("tool", "") for e in events)

    # Files touched
    files_touched = set()
    for e in events:
        if e.get("tool") in ("Write", "Edit") and e.get("path"):
            files_touched.add(e["path"])

    # Scripts run
    scripts_run = []
    for e in events:
        if e.get("tool") == "Bash" and "python" in e.get("cmd_head", "").lower():
            scripts_run.append(e["cmd_head"])

    # Results files produced (check by looking for new files in results/)
    results_dir = BASE / "results"
    results_files = []
    if results_dir.exists():
        day = datetime.strptime(target_date, "%Y-%m-%d")
        for p in results_dir.rglob("*"):
            if p.is_file():
                try:
                    mtime = datetime.fromtimestamp(p.stat().st_mtime)
                    if mtime.date() == day.date():
                        results_files.append(str(p.relative_to(BASE)))
                except Exception:
                    continue

    summary = {
        "date": target_date,
        "total_events": len(events),
        "tool_breakdown": dict(tools),
        "files_touched_count": len(files_touched),
        "files_touched": list(files_touched)[:30],
        "scripts_run": scripts_run[:20],
        "results_produced": results_files[:30],
        "generated_at": datetime.now().isoformat(),
    }

    # Append to persistent memory file
    MEM_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(MEM_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(summary) + "\n")

    return summary


def show_latest():
    """Show the most recent session memory."""
    if not MEM_FILE.exists():
        print("No session memory yet. Run: python scripts/session_memory.py summarize")
        return
    with open(MEM_FILE, encoding="utf-8") as f:
        lines = f.readlines()
    if not lines:
        print("Empty session memory")
        return
    latest = json.loads(lines[-1])
    print(f"=== Session Memory: {latest['date']} ===")
    print(f"Total events: {latest['total_events']}")
    print(f"Tool breakdown: {latest['tool_breakdown']}")
    print(f"Files touched: {latest['files_touched_count']}")
    print(f"Scripts run: {len(latest['scripts_run'])}")
    print(f"Results produced: {len(latest['results_produced'])}")
    if latest.get("results_produced"):
        print("Top results files:")
        for p in latest["results_produced"][:10]:
            print(f"  - {p}")


def show_stats():
    """Show cumulative stats across all session memories."""
    if not MEM_FILE.exists():
        print("No session memory yet")
        return
    summaries = []
    with open(MEM_FILE, encoding="utf-8") as f:
        for line in f:
            try:
                summaries.append(json.loads(line))
            except Exception:
                continue

    total_events = sum(s["total_events"] for s in summaries)
    total_files = sum(s["files_touched_count"] for s in summaries)
    total_results = sum(len(s.get("results_produced", [])) for s in summaries)

    print(f"=== Cumulative Session Stats ===")
    print(f"Days recorded: {len(summaries)}")
    print(f"Total events: {total_events}")
    print(f"Total files touched: {total_files}")
    print(f"Total results produced: {total_results}")
    if summaries:
        print(f"Date range: {summaries[0]['date']} → {summaries[-1]['date']}")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "latest"
    if cmd == "summarize":
        date = sys.argv[2] if len(sys.argv) > 2 else None
        s = summarize_day(date)
        if s:
            print(json.dumps(s, indent=2))
    elif cmd == "latest":
        show_latest()
    elif cmd == "stats":
        show_stats()
    else:
        print(f"Unknown command: {cmd}. Use: summarize [DATE] | latest | stats")
