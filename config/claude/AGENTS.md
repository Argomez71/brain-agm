# ============================================================
# brain-agm: Sistema de memoria compartida
# Instalado: 2026-11-05
# Versión: 1.0.0
# ============================================================

# Sistema brain-agm

Este sistema guarda automáticamente memoria entre sesiones para que no pierdas contexto al abrir nuevas sesiones de Claude Code.

## Qué Guarda

- **Planes** ejecutados o cerrados
- **Decisiones** técnicas importantes
- **Problemas** encontrados y resueltos
- **Cualquier cosa** que pidas explícitamente guardar

Las memorias se guardan en `~/Documents/brain-agm/[proyecto]/` en formato Markdown y son accesibles desde cualquier sesión e IDE.

## Cuándo Usar brain-agm

### Guardar Memoria

Guarda automáticamente cuando:
- Completas o cierras un plan
- Tomas una decisión técnica no obvia
- Resuelves un problema complejo
- El usuario dice: "guarda esto en memoria", "recuerda esto", "anota esto"

### Buscar Memoria

Busca automáticamente cuando:
- El usuario pregunta sobre trabajo anterior del proyecto actual
- Detectas que la pregunta se refiere a una decisión pasada del mismo proyecto
- El usuario dice: "busca en memoria", "qué hicimos con X", "por qué decidimos Y"

**Importante**: Busca SOLO en el proyecto actual por defecto. Solo usa `--all-projects` cuando el usuario diga explícitamente "busca en otros proyectos" o mencione un proyecto específico.

### Actualizar Memoria

Actualiza cuando:
- Un plan o decisión cambia
- El usuario corrige información guardada
- Se agregan detalles a algo ya guardado

## Formato de Memoria

Toda memoria debe incluir:

**Breve descripción**: 1-2 líneas de resumen  
**El qué**: Qué se hizo, decidió o resolvió (concreto, con referencias a archivos/líneas si aplica)  
**El por qué**: Contexto, razón, trade-offs de la decisión

Ejemplo:
```markdown
## Breve descripción
Implementación OAuth 2.0 con Google y Microsoft

## El qué
Se implementó flujo OAuth 2.0:
- Archivos: src/auth/oauth.py:45-120
- Endpoints: /auth/login, /auth/callback, /auth/logout
- Providers: Google, Microsoft

## El por qué
**Contexto**: Cliente requiere SSO para política de seguridad

**Decisiones clave**:
1. authlib sobre python-oauth2 - mejor soporte PKCE
2. Redis para tokens - TTL automático

**Trade-offs**:
- Más complejo pero requerido por política
```

## Comandos

**Guardar** (crear archivo temporal primero con el contenido):
```powershell
# Windows
python ~/.claude/skills/brain-agm/scripts/save_memory.py `
  --project [nombre] `
  --type [plan|decision|problem|user-request] `
  --title "titulo-descriptivo" `
  --content [ruta-archivo-temporal] `
  --tags "tag1,tag2"  # Opcional

# Mac/Linux
python ~/.claude/skills/brain-agm/scripts/save_memory.py \
  --project [nombre] \
  --type [plan|decision|problem|user-request] \
  --title "titulo-descriptivo" \
  --content [ruta-archivo-temporal] \
  --tags "tag1,tag2"
```

**Buscar en proyecto actual**:
```bash
python ~/.claude/skills/brain-agm/scripts/search_memory.py \
  --project [nombre] \
  --query "texto a buscar"
```

**Buscar en todos los proyectos** (solo cuando usuario lo pida):
```bash
python ~/.claude/skills/brain-agm/scripts/search_memory.py \
  --all-projects \
  --query "texto a buscar"
```

## Workflow Rápido

### Guardar:
1. Detectar momento importante
2. Crear archivo temporal con contenido (sin frontmatter)
3. Ejecutar save_memory.py
4. Confirmar al usuario: "✓ Guardé esto en memoria: [título]"

### Buscar:
1. Detectar pregunta sobre trabajo anterior
2. Ejecutar search_memory.py (sin `--all-projects` por defecto)
3. Leer archivos de memorias encontradas
4. Responder usando el contenido: "Encontré X memoria(s): [títulos]"

## Notas

- **Proyecto detectado automáticamente** del nombre de carpeta actual
- **Búsquedas son SOLO proyecto actual por defecto** - `--all-projects` requiere request explícito
- **Siempre mostrar al usuario** qué memorias se encontraron/guardaron
- **Hacer referencia explícita** a las memorias usadas ("según memoria de [fecha]")
- **No guardar información sensible** - sin credenciales, API keys, PII

# ============================================================
# Fin de brain-agm
# ============================================================
