---
name: parallel-backtest-factory
description: Run multiple backtest or strategy analysis tasks in parallel using isolated git worktrees. Each subagent gets its own worktree, works independently, and reports back. Triggers when user says "run in parallel", "batch backtest", "fan out to agents", "factory run", or any time 3+ strategies need the same analysis.
---

# Parallel Backtest Factory

## What This Skill Does

Enables true parallelism for backtest and analysis tasks. Instead of running 10 strategies sequentially (slow), it spawns 10 isolated worktree subagents that work concurrently, each writing to their own branch, then merging results back.

## When to Invoke

- "Run backtest on all 10 strategies in parallel"
- "Fan out to agents for X tasks"
- "Factory run"
- "Batch this across all strategies"
- When completing the same analysis on 3+ strategies

## Workflow

### Step 1: Plan the Fan-Out
Use the Agent tool with `isolation: "worktree"` to spawn ONE subagent per task.
For our TradingAI project, common fan-outs:
- 1 agent per strategy (up to ~15 at once)
- 1 agent per orderflow feature
- 1 agent per time regime (month/week)

### Step 2: Spawn Agents in a Single Message
CRITICAL: Send all Agent tool calls in ONE message to run concurrently.

```
Multiple Agent() calls in same message with:
  - description: "Backtest Savage Warrior V2" (unique per agent)
  - isolation: "worktree"
  - prompt: self-contained with file paths, exact script to run
  - subagent_type: "general-purpose"
```

### Step 3: Standard Task Template
Each subagent should:
1. Navigate to its worktree copy
2. Run the assigned Python script with specific args
3. Write results to `results/factory/<agent_id>/` (not main results/)
4. Report back with metrics summary

### Step 4: Collect and Aggregate
After all agents report back (this happens automatically when they finish):
1. Read each agent's result file
2. Aggregate into a master report
3. Rank by metric of interest
4. Write to `results/factory_run_<timestamp>/master_report.md`

### Step 5: Cleanup
Worktrees with no changes auto-delete. Merge any useful branches manually if needed.

## Example Fan-Out

```
# Single message with 10 concurrent agents:

Agent(description="V2 backtest SW",    isolation="worktree", prompt="Run V2 analysis on Savage Warrior...")
Agent(description="V2 backtest MAV",   isolation="worktree", prompt="Run V2 analysis on Maverick...")
Agent(description="V2 backtest FURY",  isolation="worktree", prompt="Run V2 analysis on Fury...")
Agent(description="V2 backtest NEB",   isolation="worktree", prompt="Run V2 analysis on Nebula...")
Agent(description="V2 backtest QT",    isolation="worktree", prompt="Run V2 analysis on Quantum Tactic...")
Agent(description="V2 backtest TW",    isolation="worktree", prompt="Run V2 analysis on Titan Wraith...")
Agent(description="V2 backtest AC",    isolation="worktree", prompt="Run V2 analysis on Aggressive Conqueror...")
Agent(description="V2 backtest LR",    isolation="worktree", prompt="Run V2 analysis on Lightning Retribution...")
Agent(description="V2 backtest AP3",   isolation="worktree", prompt="Run V2 analysis on Apex Predator V3...")
Agent(description="V2 backtest TH",    isolation="worktree", prompt="Run V2 analysis on Thunder Havoc...")

# 10 agents work in parallel, each in isolated worktree
# Total time ≈ slowest single agent (not sum of all)
```

## Self-Contained Prompt Template

Each agent's prompt MUST include:
1. Absolute paths to required files
2. Exact Python command to run
3. Expected output location
4. Report format expectations

```
You are running a V2 doctrine analysis on <STRATEGY_NAME>.

Required files:
- Trade log: <FULL_PATH>
- Orderflow data: C:\Users\Administrator\Desktop\TradingAI\footprint_data\MNQ\_combined_2026-04-14\bars.csv
- Analysis script: C:\Users\Administrator\Desktop\TradingAI\scripts\v2_doctrine_analysis.py

Steps:
1. cd C:\Users\Administrator\Desktop\TradingAI
2. python scripts/v2_doctrine_analysis.py --strategy <STRATEGY_NAME> --trade-log <PATH>
3. Read the output from results/v2_doctrine_<STRATEGY_NAME>/
4. Report back with: V1 net, V2 net, lift %, Apex 50K pass/fail, any anomalies

Report under 200 words.
```

## Critical Gotchas

- Agents starting together but not communicating with each other
- Each writes to its OWN directory to avoid collisions
- Main session aggregates after all finish
- For interactive strategies (NinjaTrader), this pattern does NOT work - must be Python-based
