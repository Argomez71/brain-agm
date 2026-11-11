# On-demand memory across Claude Code sessions

## Problem

When a new session opens, the agent has no access to what was done in previous sessions. Within the same session everything works well.

## Discarded options

All options that load context at startup were discarded because they consume context from the first message, even when it is not needed:

- CLAUDE.md with accumulated history or decisions.
- Automatic memory in files, which is loaded at startup.
- Session notes imported from CLAUDE.md.
- Resuming sessions with `claude --continue` or `claude --resume`, because it only restores one full conversation and does not allow querying several past sessions from a new one.

## Chosen approach

On-demand retrieval. A local search script indexes Claude Code transcripts, which are stored as JSONL files in `%USERPROFILE%\.claude\projects\`. When the user asks about past work, the agent runs the script with the Bash tool, gets the relevant excerpts with date and session, and uses them to answer.

Startup cost: zero, because the script is not loaded into context until it is used. It only adds one line to CLAUDE.md that says when to use it.

## Pending items before building it

1. Confirm the exact JSONL format on this machine, because the path and structure may change depending on the Claude Code version.
2. Check with Improving's data policy whether indexing transcripts is acceptable. If sessions contain client data, credentials, PII or cryptographic material, they must be reviewed or anonymized before being processed with AI. The index stays on the machine, but the policy applies to the content.
3. Choose the script language (PowerShell or Python) based on what is installed.

## Project status

- The project folder was renamed from `engram-agm` to `brain-agm`.
- The current session works in `C:\ai_projects\brain-agm`, and its transcript is in `%USERPROFILE%\.claude\projects\C--ai-projects-brain-agm\`.
- Pending: delete the empty folder `C:\ai_projects\engram-agm` and the previous session copy in `%USERPROFILE%\.claude\projects\C--ai-projects-engram-agm\`. The tool blocked the deletion, so it must be done manually.


## Plan for building the global memory tool

The idea is to share memory from one session to another across different IDEs or CLIs. Within a session, the agent should be able to:

- If a plan was executed or closed, save it to memory.
- When important decisions are made, save them to memory, with the why and the purpose.
- When the agent finds a problem and makes an important decision while working, save that too.
- If the user explicitly asks to save something to memory, do it as well.
- Every 15 minutes, the agent should ask itself whether there is anything new that should be saved.
- Saved memories must be updatable, in case a plan or decision changed.

Storage structure:

- On every Windows or Mac computer, create a folder named brain-agm in Documents, where all memories will be stored. The location can vary, but it must be a path that always exists and where the brain-agm folder can always be created. Recommend the best location for each OS.
- When a chat session with any brain-agm agent opens, it must create a folder inside brain-agm named after the project we are working on, taken from the name of the folder we are in.
- Inside a project, all memories must be saved with a title, the date, and in this format: a) Brief description, b) What and why.

Retrieval:

- In a chat session, the agent must detect when the user asks a question that implies prior work or an important past decision. If brain-agm may have related memory, the agent must search it, load related memories into the current conversation context, and show the user what it found, always referencing the memory it recovered.
- The user can explicitly ask to search memory for the current project or even for another project.

Constraints:

- The user is not very technical, so the tool must be as simple as possible, while working globally on the machine for any project or session.
- It must work for Claude and for Devin/Windsurf. For Claude, a CLAUDE.md file can reference AGENTS.md, where this tool is defined: how it works, what it is for, and when to use it, so the agent knows it exists at session start. A skill or MCP may also be needed to read or save memories, and the same files will need to exist for Devin/Windsurf.
- All project files live in `C:\AI_Projects\brain-agm`, because the project will be shared with colleagues who can install it if useful. It needs an installation and configuration script, and a second script to remove the tool. Keep it as simple as possible.
- AGENTS.md can be global in each IDE configuration folder, at the same level as CLAUDE.md. Claude must reference AGENTS.md.
- Do not use IDE-specific mechanisms to save memories. It must be a simple mechanism that works in any IDE, and memories must be stored in the folder specified above. Ideas from existing features can be borrowed.
- Check whether Claude global skills exist and investigate them.
