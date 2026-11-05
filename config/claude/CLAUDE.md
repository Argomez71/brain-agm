# ============================================================
# brain-agm: Sistema de memoria compartida
# Instalado: 2026-11-05
# ============================================================

# Configuración Global de Claude Code

Lee las reglas globales que incluyen el sistema brain-agm:

@~/.claude/AGENTS.md

## Notas sobre brain-agm

- El sistema brain-agm guarda memoria entre sesiones automáticamente
- Las memorias se guardan en `~/Documents/brain-agm/[proyecto]/`
- El skill brain-agm se carga automáticamente desde `~/.claude/skills/`
- Cada proyecto puede tener su propio AGENTS.md que se combina con este global

## Cómo Funciona

Cuando abres cualquier proyecto en Claude Code:
1. Este CLAUDE.md global se carga primero
2. Carga AGENTS.md que contiene las instrucciones de brain-agm
3. El skill brain-agm se activa automáticamente cuando es relevante
4. Las memorias del proyecto actual están disponibles para consulta

# ============================================================
# Fin de brain-agm
# ============================================================
