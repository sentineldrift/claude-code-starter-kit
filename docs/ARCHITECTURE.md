# Architecture — Why Each Piece Exists

## The Problem This Kit Solves

Every new Claude Code user hits the same walls:

1. **Amnesia.** Claude starts fresh every session. You re-explain context.
2. **Context bloat.** Claude reads giant markdown files trying to remember what was done.
3. **UI crashes.** Long bash commands trigger permission dialogs that don't scroll.
4. **Reinventing workflows.** Same "run X analysis on Y" gets built three different ways.
5. **No feedback loop.** No way to ask "what should we try next based on what worked."
6. **Data loss.** Knowledge stored only in conversation = lost when chat ends.

## The Four-Layer Solution

### Layer 1: Memory (Knowledge Graph)
- **MCP server:** `@modelcontextprotocol/server-memory`
- **Storage:** `.claude/memory_graph.json` (JSONL file, local-first)
- **What it stores:** entities (strategies, findings, tools) with observations and relations
- **Why it beats markdown:** queryable. Ask "what do I know about X" and the graph returns X's facts + everything X is connected to. No linear file scan.

### Layer 2: Semantic Search (RAG)
- **Storage:** ChromaDB vector database + sentence-transformers embeddings
- **Index:** every markdown file + every code file in the project
- **What it enables:** fuzzy text search across your entire project. "What's safest for the eval" returns the 5 most relevant passages, even if that phrase is never written verbatim.

### Layer 3: Step-by-Step Reasoning
- **MCP server:** `@modelcontextprotocol/server-sequential-thinking`
- **What it does:** forces Claude to write out numbered reasoning steps for complex decisions before acting
- **When it matters:** multi-step engineering problems where skipping steps produces bugs

### Layer 4: Determinism (Hooks + Skills)
- **Hooks:** run automatically on events (every bash command, every file write). Fast, no AI required.
- **Skills:** reusable workflows that fire on specific language patterns (`autopsy`, `run in parallel`, etc.)

Hooks enforce guardrails. Skills codify workflows.

## Information Flow

```
┌─────────────────────────────────────────┐
│           USER (you)                     │
└─────────────────┬───────────────────────┘
                  │ prompt
                  ▼
┌─────────────────────────────────────────┐
│         CLAUDE CODE (reasoning)          │
│                                          │
│    ◆ reads CLAUDE.md at start            │
│    ◆ queries memory graph (MCP)          │
│    ◆ queries RAG for fuzzy context       │
│    ◆ can request sequential thinking MCP │
└─┬──────────────┬──────────────┬─────────┘
  │              │              │
  ▼              ▼              ▼
┌─────┐   ┌──────────┐   ┌────────────┐
│ bash │──▶│  Hooks   │   │ Notifies   │
│write│   │(deterministic│   │ Telegram/  │
│edit │   │ python)  │   │ Gmail      │
└─────┘   └──────────┘   └────────────┘
              │
              ▼
        (e.g., block_long_bash rejects
         UI-crashing commands before
         they hit the permission UI)
```

## Why This Order Matters

Install the infrastructure FIRST. Then start the project.

If you start the project first (like most people), you spend weeks learning the hard way that:
- You lose context on every session restart (should have built memory first)
- You blow through your Gmail daily quota on alerts (should have set up Telegram tier logic)
- You lost 2 hours to NinjaTrader crashes (should have built backup hooks)
- You forgot which of your 500 strategies you already analyzed (should have built the tracking)

The kit collapses that learning curve to one command.

## What's NOT Included (by design)

- Domain-specific skills (trading, legal, medical) — adapt the generic skills to your domain
- API integrations beyond Telegram/Gmail — plug in what you need
- CI/CD automation — that's a separate concern
- Model training data — this is a Claude Code harness, not an ML platform

## Extending The Kit

Add your own skills in `~/.claude/skills/<your-skill>/SKILL.md`:

```markdown
---
name: my-custom-workflow
description: Triggers when user says X. Runs Y. Use this for Z.
---

# My Custom Workflow

## Steps
1. Query knowledge graph for ...
2. Run script X
3. Summarize
```

Claude will auto-suggest the skill when the user's prompt matches the description.
