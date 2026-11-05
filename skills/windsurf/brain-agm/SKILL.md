---
name: brain-agm
description: Sistema de memoria compartida entre sesiones para Windsurf/Devin. Se activa cuando el usuario pregunta sobre trabajo anterior del proyecto actual, completa un plan, toma una decisión importante, o pide explícitamente guardar en memoria. Busca y carga memorias relevantes del proyecto actual. Solo busca en otros proyectos cuando el usuario lo pide explícitamente.
---

# brain-agm: Sistema de Memoria Compartida

Sistema para retener información importante entre sesiones de Devin/Windsurf. Las memorias se guardan en `~/Documents/brain-agm/[proyecto]/` y son accesibles desde cualquier sesión e IDE.

## Cuándo Usar

### Guardar Memoria

Guarda automáticamente cuando:
- Completas o cierras un plan
- Tomas una decisión técnica importante
- Resuelves un problema complejo
- El usuario dice: "guarda esto en memoria", "recuerda esto"

### Buscar Memoria

Busca cuando:
- Usuario pregunta sobre trabajo anterior del proyecto actual
- Usuario dice: "busca en memoria", "qué hicimos con X"
- **Solo busca en otros proyectos** cuando usuario dice explícitamente "busca en otros proyectos"

## Comandos

### Guardar

```bash
# 1. Crear archivo temporal con contenido (sin frontmatter)
# 2. Ejecutar script
python ~/.codeium/windsurf/skills/brain-agm/scripts/save_memory.py \
  --project [nombre] \
  --type [plan|decision|problem|user-request] \
  --title "titulo-descriptivo" \
  --content [archivo-temporal]
```

### Buscar

```bash
# Proyecto actual (default)
python ~/.codeium/windsurf/skills/brain-agm/scripts/search_memory.py \
  --project [nombre] \
  --query "texto"

# Todos los proyectos (solo cuando usuario lo pida)
python ~/.codeium/windsurf/skills/brain-agm/scripts/search_memory.py \
  --all-projects \
  --query "texto"
```

## Formato de Memoria

```markdown
## Breve descripción
[1-2 líneas]

## El qué
[Qué se hizo - específico con archivos/líneas]

## El por qué
**Contexto**: [Situación]
**Decisiones clave**: [Lista]
**Trade-offs**: [Pros y contras]
```

## Notas

- Búsquedas son SOLO proyecto actual por defecto
- Siempre mostrar al usuario qué se encontró/guardó
- No guardar información sensible

ChaChau !!!
