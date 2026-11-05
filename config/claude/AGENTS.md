# ============================================================
# brain-agm: Shared Memory System
# Installed: 2026-11-05
# Version: 1.0.0
# ============================================================

# brain-agm System

This system automatically saves memory across sessions so you don't lose context when opening new Claude Code sessions.

## What It Saves

- **Plans** executed or closed
- **Decisions** important technical
- **Problems** found and solved
- **Anything** you explicitly ask to save

Memories are saved in `~/Documents/brain-agm/[project]/` in Markdown format and are accessible from any session and IDE.

## When to Use brain-agm

### Save Memory

Saves automatically when:
- You complete or close a plan
- You make a non-obvious technical decision
- You solve a complex problem
- User says: "save this to memory", "remember this", "note this"

### Search Memory

Searches automatically when:
- User asks about previous work in current project
- You detect question refers to past decision in same project
- User says: "search memory", "what did we do with X", "why did we decide Y"

**Important**: Searches ONLY in current project by default. Only use `--all-projects` when user explicitly says "search in other projects" or mentions a specific project.

### Update Memory

Updates when:
- A plan or decision changes
- User corrects saved information
- Details are added to something already saved

## Memory Format

Every memory must include:

**Brief description**: 1-2 lines summary  
**What**: What was done, decided or solved (concrete, with file/line references if applicable)  
**Why**: Context, reason, trade-offs of the decision

Example:
```markdown
## Brief description
OAuth 2.0 implementation with Google and Microsoft

## What
Implemented OAuth 2.0 flow:
- Files: src/auth/oauth.py:45-120
- Endpoints: /auth/login, /auth/callback, /auth/logout
- Providers: Google, Microsoft

## Why
**Context**: Client requires SSO for security policy

**Key decisions**:
1. authlib over python-oauth2 - better PKCE support
2. Redis for tokens - automatic TTL

**Trade-offs**:
- More complex but required by policy
```

## Commands

**Save** (create temp file first with content):
```powershell
# Windows
python ~/.claude/skills/brain-agm/scripts/save_memory.py `
  --project [name] `
  --type [plan|decision|problem|user-request] `
  --title "descriptive-title" `
  --content [temp-file-path] `
  --tags "tag1,tag2"  # Optional

# Mac/Linux
python ~/.claude/skills/brain-agm/scripts/save_memory.py \
  --project [name] \
  --type [plan|decision|problem|user-request] \
  --title "descriptive-title" \
  --content [temp-file-path] \
  --tags "tag1,tag2"
```

**Search in current project**:
```bash
python ~/.claude/skills/brain-agm/scripts/search_memory.py \
  --project [name] \
  --query "text to search"
```

**Search in all projects** (only when user requests it):
```bash
python ~/.claude/skills/brain-agm/scripts/search_memory.py \
  --all-projects \
  --query "text to search"
```

## Quick Workflow

### Save:
1. Detect important moment
2. Create temp file with content (without frontmatter)
3. Execute save_memory.py
4. Confirm to user: "✓ Saved to memory: [title]"

### Search:
1. Detect question about previous work
2. Execute search_memory.py (without `--all-projects` by default)
3. Read found memory files
4. Respond using content: "Found X memory(ies): [titles]"

## Notes

- **Project auto-detected** from current folder name
- **Searches are ONLY current project by default** - `--all-projects` requires explicit request
- **Always show user** what memories were found/saved
- **Make explicit references** to used memories ("according to memory from [date]")
- **Don't save sensitive information** - no credentials, API keys, PII

# ============================================================
# End of brain-agm
# ============================================================
