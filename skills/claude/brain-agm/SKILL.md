---
name: brain-agm
description: Shared memory system across sessions. Activates when 1) User asks about previous work in current project, 2) A plan is completed/closed, 3) An important decision is made, 4) User explicitly asks to save to memory, 5) Every 15 minutes (via hook) to review if there's something new. Searches and loads relevant memories from current project. Only searches other projects when user explicitly requests it.
version: 1.0.0
tools: Bash, PowerShell, Read, Write
---

# brain-agm: Shared Memory System

System for retaining important information across Claude Code sessions. Memories are saved in `~/Documents/brain-agm/[project]/` and are accessible from any session and IDE.

## When to Activate

### Save Memory (Automatic)

**Always save when**:
- A plan is completed or closed
- A non-obvious technical decision is made
- A complex problem is solved
- User explicitly says: "save this to memory", "remember this", "note this"

**What to save**:
- **Plans**: Save with complete context - what was implemented, modified files, decisions made
- **Decisions**: Save with the why - context, alternatives considered, reason for choice, trade-offs
- **Problems**: Save with solution - symptom, root cause, applied solution, future prevention
- **User requests**: Anything user explicitly asks to remember

### Search Memory (Automatic)

**Search when**:
- User asks about previous work: "what did we do with X", "why did we decide Y", "how did we solve Z"
- Question suggests context from previous session of same project
- User says: "search memory", "what do you remember about X"

**Search scope**:
- **Default**: ONLY current project (do NOT use `--all-projects`)
- **Cross-project**: Only when user explicitly says "search in other projects" or mentions a specific project (use `--all-projects`)

## Memory Format

Every memory must have this structure:

```markdown
## Brief description
[1-2 lines executive summary - what was done/decided/solved]

## What
[Specific concrete description of what was done, decided or solved]
- Modified files with lines if relevant
- Executed commands if applicable
- Changed configuration if applicable
- Key code if applicable

## Why

**Context**: [Situation that led to this - the problem or need]

**Key decisions**:
1. [Decision 1 with its reason]
2. [Decision 2 with its reason]
3. [Decision 3 with its reason]

**Trade-offs**:
- [Pro and con of the decision]
- [Discarded alternatives and why]

## References (optional)
- PR: #123
- Documentation: docs/file.md
- Related memories: [title of other memory]
```

## Commands

### Save Memory

```bash
# Windows (PowerShell)
python ~/.claude/skills/brain-agm/scripts/save_memory.py `
  --project [name] `
  --type [plan|decision|problem|user-request] `
  --title "descriptive-title" `
  --content [temp-file-path]

# Mac/Linux (Bash)
python ~/.claude/skills/brain-agm/scripts/save_memory.py \
  --project [name] \
  --type [plan|decision|problem|user-request] \
  --title "descriptive-title" \
  --content [temp-file-path]
```

**Important**: The temp file must contain ONLY the content (without frontmatter). The script adds frontmatter automatically.

### Search Memory

```bash
# Search in current project (DEFAULT)
python ~/.claude/skills/brain-agm/scripts/search_memory.py \
  --project [name] \
  --query "text to search"

# Search in all projects (ONLY when user requests it)
python ~/.claude/skills/brain-agm/scripts/search_memory.py \
  --all-projects \
  --query "text to search"
```

## Workflow: Save

1. **Detect important moment** (plan closed, decision made, problem solved, user request)

2. **Create temp file** with content:
   ```bash
   # Windows
   $content = @"
   ## Brief description
   [...]
   
   ## What
   [...]
   
   ## Why
   [...]
   "@
   
   $tempFile = "$env:TEMP\memory-$(Get-Date -Format 'yyyyMMdd-HHmmss').md"
   $content | Out-File -FilePath $tempFile -Encoding utf8
   ```

3. **Execute save script**:
   ```bash
   python ~/.claude/skills/brain-agm/scripts/save_memory.py \
     --type [appropriate-type] \
     --title "descriptive-title" \
     --content $tempFile \
     --tags "tag1,tag2"  # Optional
   ```

4. **Confirm to user**:
   ```
   ✓ Saved to memory: [title]
   Location: ~/Documents/brain-agm/[project]/[file].md
   Type: [type]
   ```

## Workflow: Search

1. **Detect question about previous work**
   - Keywords: "what did we do", "why did we decide", "how did we solve", "remember"
   - Context: User asks about something not in current files

2. **Determine scope**:
   - **Current project**: Doesn't mention other projects → do NOT use `--all-projects`
   - **Cross-project**: Says "in other projects" or mentions specific project → use `--all-projects`

3. **Execute search**:
   ```bash
   python ~/.claude/skills/brain-agm/scripts/search_memory.py \
     --project brain-agm \
     --query "oauth"
   ```

4. **Process results**:
   - Read the complete file of most relevant memories
   - Load context into conversation

5. **Respond to user**:
   ```
   Found [N] related memory(ies) in [project]:
   
   1. [Title] (date: [date], type: [type])
      File: [path]
      
      [Summary of what was found]
   
   [Use content to answer original question]
   ```

## Examples

### Example 1: Save Completed Plan

**Situation**: Just completed OAuth implementation plan.

**Action**:
```powershell
$content = @"
## Brief description
OAuth 2.0 authentication implementation with Google and Microsoft

## What
Implemented OAuth 2.0 flow:
- Files: src/auth/oauth.py:45-120, src/config/providers.py:12-30
- Endpoints: /auth/login, /auth/callback, /auth/logout
- Providers: Google OAuth, Microsoft Azure AD
- Storage: Redis with 7-day TTL

## Why
**Context**: Client requires corporate SSO for security policy

**Key decisions**:
1. authlib over python-oauth2 - better PKCE support
2. Redis for tokens - automatic TTL, low volume (<10k users)
3. No refresh tokens this phase - client prefers re-auth every 7 days

**Trade-offs**:
- More complex than local auth but required by policy
- External service dependency mitigated with retry logic
"@

$tempFile = "$env:TEMP\memory-oauth.md"
$content | Out-File -FilePath $tempFile -Encoding utf8

python ~/.claude/skills/brain-agm/scripts/save_memory.py `
  --type plan `
  --title "OAuth 2.0 Implementation" `
  --content $tempFile `
  --tags "auth,oauth,security"
```

**Response to user**:
```
✓ Saved completed plan to memory: oauth-2-0-implementation
Location: ~/Documents/brain-agm/api-backend/oauth-2-0-implementation_2026-11-05_14-30-00.md
Type: plan
```

### Example 2: Search Previous Decision

**Situation**: User asks "why do we use Redis for tokens?"

**Detection**: Question about past technical decision

**Action**:
```bash
python ~/.claude/skills/brain-agm/scripts/search_memory.py \
  --project api-backend \
  --query "redis tokens"
```

**Response**:
```json
{
  "success": true,
  "count": 1,
  "results": [{
    "title": "oauth-2-0-implementation",
    "date": "2026-11-05",
    "type": "plan",
    "snippet": "Redis for tokens - automatic TTL, low volume"
  }]
}
```

**Read complete memory** and respond:
```
Found the decision in memory:

📝 OAuth 2.0 Implementation (2026-11-05)

We decided to use Redis for tokens because:
1. Automatic TTL - tokens expire in 7 days without manual logic
2. Low volume - less than 10k users, Redis handles this easily
3. Simple and reliable - less code to write and maintain

The alternative was using the main database, but we preferred Redis because automatic TTL eliminates complexity.
```

### Example 3: Cross-Project Search

**Situation**: User asks "search in other projects how we handled rate limiting"

**Detection**: User explicitly says "in other projects"

**Action**:
```bash
python ~/.claude/skills/brain-agm/scripts/search_memory.py \
  --all-projects \
  --query "rate limiting"
```

**Response**:
```
Found 2 memories in other projects about rate limiting:

1. api-gateway: "Rate Limiting Implementation with Redis" (2026-10-15)
   - Used Redis with sliding window
   - 100 req/min per user

2. webhooks-service: "Rate Limiting for Webhooks" (2026-09-20)
   - Token bucket algorithm
   - Different limits per client tier

Want me to read any in detail?
```

## Important Notes

1. **Always show user what was saved/found** - be transparent about memory usage

2. **Make explicit references** - say "according to memory from [date]" so user knows where information comes from

3. **Project is auto-detected** from current folder name, but can be specified with `--project`

4. **Searches are ONLY current project by default** - using `--all-projects` requires user to explicitly request it

5. **Don't save sensitive information** - no credentials, API keys, PII

6. **Validate before saving** - script validates format, but review that content is useful

7. **Tags help organize** - use relevant tags when saving (optional but recommended)

## Troubleshooting

### Script fails with "module not found"
- Verify Python is in PATH
- Verify scripts are in `~/.claude/skills/brain-agm/scripts/`

### Doesn't find memories
- Verify correct project: `--project [name]`
- Verify exists: `~/Documents/brain-agm/[project]/`
- Try with `--all-projects` if searching in another project

### Memory doesn't save
- Verify temp file exists
- Verify write permissions in `~/Documents/brain-agm/`
- Review content format (must have "## Brief description", "## What", "## Why" sections)

ChaChau !!!
