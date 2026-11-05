# ============================================================
# brain-agm: Shared Memory System
# Installed: 2026-11-05
# Version: 1.0.0
# ============================================================

# brain-agm System for Windsurf/Devin

Shared memory system across sessions. Automatically saves plans, decisions and problems in `~/Documents/brain-agm/[project]/`.

## When to Save

- You complete a plan
- You make an important technical decision
- You solve a complex problem
- User says: "save this to memory"

## When to Search

- User asks about previous work in current project
- User says: "search memory", "what did we do with X"
- **Only search in other projects** when user explicitly requests it

## Main Commands

**Save**:
```bash
python ~/.codeium/windsurf/skills/brain-agm/scripts/save_memory.py \
  --type [plan|decision|problem|user-request] \
  --title "title" \
  --content [temp-file]
```

**Search** (current project):
```bash
python ~/.codeium/windsurf/skills/brain-agm/scripts/search_memory.py \
  --query "text"
```

**Search** (all projects - only when user requests it):
```bash
python ~/.codeium/windsurf/skills/brain-agm/scripts/search_memory.py \
  --all-projects \
  --query "text"
```

## Memory Format

Every memory must have:
- **Brief description**: 1-2 lines
- **What**: Specific with files/lines
- **Why**: Context, decisions, trade-offs

## Rules

- Searches ONLY in current project by default
- Always show user what was found/saved
- Don't save sensitive information (credentials, API keys)

# ============================================================
# End of brain-agm
# ============================================================
