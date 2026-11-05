# brain-agm: Shared Memory System

Shared memory system across sessions for Claude Code and Devin/Windsurf. Automatically saves plans, decisions, and solved problems so you don't lose context when opening new sessions.

## Problem It Solves

When working with AI across different sessions, the agent doesn't remember what you did in previous sessions. You have to:
- Repeat context every time
- Manually document everything important
- Search through your commit/PR history

**brain-agm** solves this by automatically saving important information in a shared location that all IDEs can read.

## Features

- ✅ **Automatic memory** - Saves plans, decisions, and problems without asking
- ✅ **Smart search** - Agent finds relevant memories when you ask
- ✅ **Cross-IDE** - Works in Claude Code and Devin/Windsurf
- ✅ **Simple** - Just Markdown files, no database
- ✅ **Portable** - Share memories between machines by copying `~/Documents/brain-agm/`

## Installation

### Requirements

- Python 3.7+ installed
- Claude Code or Devin/Windsurf installed
- PowerShell 5.1+ (Windows) or Bash 4+ (Mac/Linux)

### Windows

```powershell
cd C:\AI_Projects\brain-agm
.\install.ps1
```

### Mac/Linux

```bash
cd ~/ai_projects/brain-agm
chmod +x install.sh
./install.sh
```

## What It Installs

The installation script:

1. ✅ Creates `~/Documents/brain-agm/` for storing memories
2. ✅ Copies skill to `~/.claude/skills/brain-agm/` (Claude)
3. ✅ Copies skill to `~/.codeium/windsurf/skills/brain-agm/` (Devin)
4. ✅ Adds configuration to `~/.claude/AGENTS.md` and `~/.claude/CLAUDE.md`
5. ✅ Adds configuration to `~/.codeium/windsurf/AGENTS.md`

**Important**: Does NOT overwrite existing files, appends brain-agm content at the end.

## Usage

### Automatic

The system works automatically:

**Saves memory when**:
- You complete a plan
- You make an important technical decision
- You solve a complex problem
- You say: "save this to memory"

**Searches memory when**:
- You ask: "what did we do with X", "why did we decide Y"
- You reference something from previous sessions

### Manual

#### Save a memory

```bash
# 1. Create file with content
cat > /tmp/memory.md << 'EOF'
## Brief description
OAuth authentication implementation

## What
- Implemented OAuth 2.0 with Google and Microsoft
- Files: src/auth/oauth.py
- Endpoints: /auth/login, /auth/callback

## Why
Client requires corporate SSO for security
EOF

# 2. Save
python ~/.claude/skills/brain-agm/scripts/save_memory.py \
  --type decision \
  --title "OAuth Implementation" \
  --content /tmp/memory.md
```

#### Search memories

```bash
# Search in current project
python ~/.claude/skills/brain-agm/scripts/search_memory.py \
  --query "oauth"

# Search in all projects
python ~/.claude/skills/brain-agm/scripts/search_memory.py \
  --all-projects \
  --query "authentication"
```

## Memory Structure

Memories are saved in: `~/Documents/brain-agm/[project]/`

Each memory is a Markdown file:

```markdown
---
title: oauth-implementation
date: 2026-11-05
project: api-backend
type: decision
status: completed
tags: ["auth", "oauth", "security"]
---

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

## Memory Types

- **plan**: Executed or closed plans
- **decision**: Important technical decisions
- **problem**: Solved problems with their solution
- **user-request**: Anything you explicitly ask to save

## Examples

### Example 1: Question about previous work

**You**: "Why did we use Redis for OAuth tokens?"

**Claude**:
```
Found decision in memory:

📝 OAuth Implementation (2026-11-05)

We decided to use Redis for tokens because:
1. Automatic TTL - expires in 7 days without manual logic
2. Low volume - less than 10k users
3. Simple and reliable

The alternative was using the main DB, but Redis eliminates complexity with automatic TTL.
```

### Example 2: Search across projects

**You**: "Search in other projects for how we handled rate limiting"

**Claude**:
```
Found 2 memories in other projects:

1. api-gateway: "Rate Limiting with Redis" (2026-10-15)
   - Sliding window algorithm
   - 100 req/min per user

2. webhooks-service: "Rate Limiting Webhooks" (2026-09-20)
   - Token bucket algorithm
   - Different limits per tier

Want me to read any in detail?
```

## Verification

Test that installation worked:

```bash
# 1. Verify scripts installed
python ~/.claude/skills/brain-agm/scripts/save_memory.py --help

# 2. Save test memory
echo "## Brief description
brain-agm test

## What
Installed shared memory system

## Why
To test it works" > /tmp/test.md

python ~/.claude/skills/brain-agm/scripts/save_memory.py \
  --project test \
  --type user-request \
  --title "Test" \
  --content /tmp/test.md

# 3. Search for memory
python ~/.claude/skills/brain-agm/scripts/search_memory.py \
  --project test \
  --query "test"

# 4. Verify saved file
ls ~/Documents/brain-agm/test/
```

## Uninstallation

```powershell
# Windows
.\uninstall.ps1

# Mac/Linux
./uninstall.sh
```

**Note**: By default does NOT delete saved memories in `~/Documents/brain-agm/`. The script asks if you want to delete them.

## Troubleshooting

### Script doesn't find Python

```bash
# Verify Python installed
python --version  # or python3 --version

# Install Python if missing
# Windows: https://www.python.org/downloads/
# Mac: brew install python3
# Linux: sudo apt install python3
```

### Skill doesn't activate in Claude

1. Verify skill is installed:
   ```bash
   ls ~/.claude/skills/brain-agm/
   ```

2. Verify CLAUDE.md references AGENTS.md:
   ```bash
   cat ~/.claude/CLAUDE.md
   ```

3. Restart Claude Code

### Doesn't find memories

- Verify correct project: project name is current folder name
- Verify exists: `ls ~/Documents/brain-agm/[project]/`
- Try with `--all-projects` if searching in another project

## Project Structure

```
brain-agm/
├── README.md                       # This file
├── install.ps1                     # Windows installer
├── install.sh                      # Mac/Linux installer (TODO)
├── uninstall.ps1                   # Windows uninstaller (TODO)
├── uninstall.sh                    # Mac/Linux uninstaller (TODO)
│
├── skills/                         # Skills for each IDE
│   ├── claude/brain-agm/
│   │   ├── SKILL.md                # Skill definition for Claude
│   │   └── scripts/
│   │       ├── __init__.py
│   │       ├── utils.py            # Shared functions
│   │       ├── save_memory.py      # Save memories
│   │       └── search_memory.py    # Search memories
│   │
│   └── windsurf/brain-agm/
│       └── SKILL.md                # Skill for Devin
│
├── config/                         # Global configuration
│   ├── claude/
│   │   ├── CLAUDE.md               # Claude global config
│   │   └── AGENTS.md               # brain-agm rules
│   └── windsurf/
│       └── AGENTS.md               # Devin rules
│
├── hooks/                          # Hooks
│   ├── claude/hooks.json
│   └── scripts/check_memory.py
│
└── templates/
    └── memory_template.md          # Template
```

## Roadmap

- [x] Basic Python scripts
- [x] Claude skill
- [x] Claude global configuration
- [x] Windows installation script
- [ ] update_memory.py script
- [ ] Devin/Windsurf skill
- [ ] 15-minute review hook
- [ ] Mac/Linux scripts
- [ ] Uninstallation scripts
- [ ] Automated tests

## Contributing

This project is designed to be shared with the team. If you have improvements:

1. Test locally
2. Document the change
3. Share the updated code

## License

Internal use for Improving. Do not distribute outside the organization.

## Support

For issues or questions:
- Review Troubleshooting section above
- Contact Global IT Services team
- Create issue in internal repo (if applicable)

---

**Version**: 1.0.0  
**Last updated**: 2026-11-05  
**Author**: Armando Gómez (armando.gomez@improving.com)
