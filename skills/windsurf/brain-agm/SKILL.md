---
name: brain-agm
description: Shared memory system across sessions for Windsurf/Devin. Activates when user asks about previous work in current project, completes a plan, makes an important decision, or explicitly asks to save to memory. Searches and loads relevant memories from current project. Only searches other projects when user explicitly requests it.
---

# brain-agm: Shared Memory System

System for retaining important information across Devin/Windsurf sessions. Memories are saved in `~/Documents/brain-agm/[project]/` and are accessible from any session and IDE.

## When to Use

### Save Memory

Saves automatically when:
- You complete or close a plan
- You make an important technical decision
- You solve a complex problem
- User says: "save this to memory", "remember this"

### Search Memory

Searches when:
- User asks about previous work in current project
- User says: "search memory", "what did we do with X"
- **Only search in other projects** when user explicitly says "search in other projects"

## Commands

### Save

```bash
# 1. Create temp file with content (without frontmatter)
# 2. Execute script
python ~/.codeium/windsurf/skills/brain-agm/scripts/save_memory.py \
  --project [name] \
  --type [plan|decision|problem|user-request] \
  --title "descriptive-title" \
  --content [temp-file]
```

### Search

```bash
# Current project (default)
python ~/.codeium/windsurf/skills/brain-agm/scripts/search_memory.py \
  --project [name] \
  --query "text"

# All projects (only when user requests it)
python ~/.codeium/windsurf/skills/brain-agm/scripts/search_memory.py \
  --all-projects \
  --query "text"
```

## Memory Format

```markdown
## Brief description
[1-2 lines]

## What
[What was done - specific with files/lines]

## Why
**Context**: [Situation]
**Key decisions**: [List]
**Trade-offs**: [Pros and cons]
```

## Notes

- Searches are ONLY current project by default
- Always show user what was found/saved
- Don't save sensitive information

ChaChau !!!
