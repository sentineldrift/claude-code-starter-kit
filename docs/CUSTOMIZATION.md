# Customization — Adapt The Kit To Your Domain

The kit ships with generic skills. Your domain needs specific ones. Here's how to add them.

## Adding A Custom Skill

Skills live in `~/.claude/skills/<skill-name>/SKILL.md`. Example:

```markdown
---
name: code-review
description: Review a pull request for bugs, style issues, and missing tests. Triggers when user says "review PR", "check this code", or pastes a diff.
---

# Code Review Workflow

## Steps

### Step 1: Read the diff
Use the Bash tool to run `git diff origin/main...HEAD`

### Step 2: Check each file
For each modified file:
- Run the project's linter
- Check tests exist
- Look for security issues

### Step 3: Summarize
Group findings by severity. Produce a markdown comment ready to paste in GitHub.
```

Claude will auto-suggest this skill when you say matching phrases from the `description` field.

## Common Domain Adaptations

### Software Engineering
- `code-review` — automated PR review
- `test-gap-finder` — identify untested functions
- `refactor-plan` — propose structural improvements

### Data Science / ML
- `feature-analysis` — correlation, Cohen's d, mutual information
- `experiment-tracker` — log runs with hyperparameters and metrics
- `dataset-audit` — missing values, outliers, leakage checks

### Trading (example — from the source project)
- `strategy-autopsy` — parse trade log, compute MAE/MFE, find skip rules
- `orderflow-scan` — score live signals 0-100
- `prop-firm-check` — DD/ruin/target validation

### Writing / Research
- `paper-summary` — extract key claims + methodology
- `citation-check` — verify references exist
- `draft-critique` — structural feedback on prose

## Skill Patterns That Work

1. **Specific triggers.** Don't write "helps with code." Write "triggers when user says 'run autopsy' or pastes a trade log CSV."
2. **Concrete steps.** Numbered, with exact commands or tool calls.
3. **Reference files.** Point to scripts/data the skill needs.
4. **Output format.** Tell Claude what format to return results in.

## Adapting Hooks

Hooks in `~/.claude/hooks/` run at specific tool-use events. Customize based on your environment:

### For Node.js projects
Replace `auto_format_python.py` with:
```python
# auto_format_js.py
import json, sys, subprocess
data = json.load(sys.stdin)
if data.get("tool_name") not in ("Write", "Edit"): sys.exit(0)
path = data.get("tool_input", {}).get("file_path", "")
if path.endswith((".js", ".ts", ".jsx", ".tsx")):
    subprocess.run(["npx", "prettier", "--write", path], capture_output=True, timeout=15)
```

### For Rust projects
```python
# auto_rustfmt.py
import json, sys, subprocess
data = json.load(sys.stdin)
if data.get("tool_name") not in ("Write", "Edit"): sys.exit(0)
path = data.get("tool_input", {}).get("file_path", "")
if path.endswith(".rs"):
    subprocess.run(["rustfmt", path], capture_output=True, timeout=15)
```

### For backup-before-edit
Useful for critical config files, SQL migrations, etc:
```python
# backup_before_edit.py
import json, sys, shutil, os
from datetime import datetime
data = json.load(sys.stdin)
if data.get("tool_name") not in ("Edit", "Write"): sys.exit(0)
path = data.get("tool_input", {}).get("file_path", "")
# Customize: which file patterns deserve backups?
if any(x in path for x in [".env", "database.yml", "migrations/"]):
    if os.path.exists(path):
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup = path + f".bak_{ts}"
        shutil.copy2(path, backup)
```

Register new hooks by editing `~/.claude/settings.local.json`:
```json
{
  "hooks": {
    "PostToolUse": [{
      "matcher": "Write|Edit",
      "hooks": [{"type": "command", "command": "python ~/.claude/hooks/my_hook.py", "timeout": 15}]
    }]
  }
}
```

## Seeding The Knowledge Graph

After setup, pre-populate your project knowledge with a one-time prompt:

> *"Use `mcp__memory__create_entities` to add these project entities: [Project_X], [Key_Technology_A], [Main_Goal], [Primary_Constraint]. Then use `mcp__memory__create_relations` to connect them: Project_X -> uses -> Key_Technology_A, Project_X -> targets -> Main_Goal, Project_X -> limited_by -> Primary_Constraint."*

That 60 seconds of upfront work gives you a queryable knowledge graph that persists forever.

## RAG Tuning

Default `local_rag_server.py` indexes:
- `*.md` anywhere
- `*.py`, `*.js`, `*.ts`, `*.go`, `*.rs`, `*.java` in `scripts/` and `src/`
- Skips: `.git`, `node_modules`, `__pycache__`, `.venv`

To customize, edit the top of `local_rag_server.py`:
```python
DOC_DIRS = ["docs", "notes", "wiki"]  # your doc directories
CODE_DIRS = ["src", "lib", "packages"]
SKIP_DIRS = {".git", "node_modules", "dist", "build"}
```

Re-run `python scripts/local_rag_server.py index` after changes.

## Sharing Your Customizations

If you build useful skills/hooks for your domain, consider:
1. Adding them to a `contrib/` folder in the kit
2. Opening a PR to the kit repo
3. Publishing your own derivative kit (e.g., `claude-code-starter-kit-rust`)

The community benefits when domain expertise is shared.
