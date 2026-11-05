# ============================================================
# brain-agm: Sistema de memoria compartida
# Instalado: 2026-11-05
# Versión: 1.0.0
# ============================================================

# Sistema brain-agm para Windsurf/Devin

Sistema de memoria compartida entre sesiones. Guarda automáticamente planes, decisiones y problemas en `~/Documents/brain-agm/[proyecto]/`.

## Cuándo Guardar

- Completas un plan
- Tomas una decisión técnica importante
- Resuelves un problema complejo
- Usuario dice: "guarda esto en memoria"

## Cuándo Buscar

- Usuario pregunta sobre trabajo anterior del proyecto actual
- Usuario dice: "busca en memoria", "qué hicimos con X"
- **Solo busca en otros proyectos** cuando usuario lo pida explícitamente

## Comandos Principales

**Guardar**:
```bash
python ~/.codeium/windsurf/skills/brain-agm/scripts/save_memory.py \
  --type [plan|decision|problem|user-request] \
  --title "titulo" \
  --content [archivo-temporal]
```

**Buscar** (proyecto actual):
```bash
python ~/.codeium/windsurf/skills/brain-agm/scripts/search_memory.py \
  --query "texto"
```

**Buscar** (todos los proyectos - solo cuando usuario lo pida):
```bash
python ~/.codeium/windsurf/skills/brain-agm/scripts/search_memory.py \
  --all-projects \
  --query "texto"
```

## Formato de Memoria

Toda memoria debe tener:
- **Breve descripción**: 1-2 líneas
- **El qué**: Específico con archivos/líneas
- **El por qué**: Contexto, decisiones, trade-offs

## Reglas

- Búsquedas SOLO en proyecto actual por defecto
- Mostrar siempre al usuario qué se encontró/guardó
- No guardar información sensible (credenciales, API keys)

# ============================================================
# Fin de brain-agm
# ============================================================
