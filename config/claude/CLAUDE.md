# ============================================================
# brain-agm: Shared Memory System
# Installed: 2026-11-05
# ============================================================

# Claude Code Global Configuration

Read global rules that include brain-agm system:

@~/.claude/AGENTS.md

## Notes about brain-agm

- brain-agm system saves memory across sessions automatically
- Memories are saved in `~/Documents/brain-agm/[project]/`
- brain-agm skill loads automatically from `~/.claude/skills/`
- Each project can have its own AGENTS.md that combines with this global one

## How It Works

When you open any project in Claude Code:
1. This global CLAUDE.md loads first
2. Loads AGENTS.md containing brain-agm instructions
3. brain-agm skill activates automatically when relevant
4. Current project memories are available for query

# ============================================================
# End of brain-agm
# ============================================================
