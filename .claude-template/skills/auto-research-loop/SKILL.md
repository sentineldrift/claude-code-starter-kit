---
name: auto-research-loop
description: Self-improving research loop. Analyzes session activity logs, identifies patterns of success/failure, proposes and executes next experiments. Triggers when user says "what should we try next", "self-improve", "analyze what worked", or when a strategy analysis plateaus. Runs periodically to generate research recommendations.
---

# Auto-Research Self-Improving Loop

## What This Skill Does

This is a meta-skill that makes Claude smarter over time by analyzing its own work.

Every time Claude writes/edits a file or runs a bash command, it's logged via the `log_session_activity.py` hook to `TradingAI/.claude/session_logs/YYYY-MM-DD.jsonl`. This skill reads those logs, identifies patterns, and proposes next experiments.

## When to Invoke

- User asks "what should we try next?"
- User asks "what worked and what didn't?"
- User says "self-improve" or "auto-research"
- After completing a batch of backtests
- When a strategy analysis appears to plateau
- Weekly/periodically for compound improvement

## Workflow

### Step 1: Load Recent Activity
Read the last 3-7 days of logs from `TradingAI/.claude/session_logs/`:
- Count tool uses per type (Write, Edit, Bash)
- Extract file paths that were modified
- Identify bash commands that ran Python scripts

### Step 2: Identify Success Signals
Look at what produced results files in `TradingAI/results/`:
- Which scripts were run most recently?
- Which produced new markdown reports or CSVs?
- What patterns of analysis worked (orderflow correlation, Monte Carlo, skip rules)?

### Step 3: Identify Gaps
- Which strategies haven't been through V2 doctrine yet?
- Which analysis types haven't been run on certain strategies?
- What questions came up in conversation but weren't answered?

### Step 4: Query the Knowledge Graph
Use `mcp__memory__search_nodes` to find:
- Strategies marked as "pending" or "not yet tested"
- Doctrines not yet applied to specific strategies
- Recent findings that suggest follow-up work

### Step 5: Query RAG for Context
Use `python scripts/tradingai_rag_server.py search "<topic>"` to find related past work.

### Step 6: Propose Experiments
Generate 3-5 concrete next experiments, each with:
- **Hypothesis**: What we expect to learn
- **Method**: Exact script/command to run
- **Success criteria**: What outcome validates the hypothesis
- **Expected duration**: Time investment
- **Expected lift**: Approximate monetary or quality improvement

### Step 7: Rank by Expected Value
Order experiments by (expected_lift × probability_of_success) / time_cost.

### Step 8: Present to User
Output a concise ranked list. Let user pick. Execute the chosen experiment.

### Step 9: Record Outcome
After experiment completes, add observation to the knowledge graph:
- What was tried
- What the result was
- Whether it validated or refuted the hypothesis
- What to try next

## Reference Files

- Session logs: `C:\Users\Administrator\Desktop\TradingAI\.claude\session_logs\`
- Results directory: `C:\Users\Administrator\Desktop\TradingAI\results\`
- Scripts directory: `C:\Users\Administrator\Desktop\TradingAI\scripts\`
- Knowledge graph: Use `mcp__memory__*` tools
- RAG search: `python scripts/tradingai_rag_server.py search "query"`

## Example Output

```
Based on session activity over the last 7 days, I've identified 5 next experiments
ranked by expected value:

1. **Apply V2 doctrine to Titan Wraith MK6** (expected lift: +$30K trapped profit)
   - Run: python scripts/v2_doctrine_analysis.py --strategy Titan_Wraith
   - Hypothesis: DailyProfitLimit is throttling; raising it unlocks trapped profit
   - Success: Net profit increases by >$15K on backtest
   - Duration: 30 min

2. **Run orderflow correlation on Chaos Dominator** (expected lift: +20% WR)
   ...
```
