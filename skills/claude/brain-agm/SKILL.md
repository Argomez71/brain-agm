---
name: brain-agm
description: Sistema de memoria compartida entre sesiones. Se activa cuando 1) Usuario pregunta sobre trabajo anterior del proyecto actual, 2) Se completa/cierra un plan, 3) Se toma una decisión importante, 4) Usuario pide explícitamente guardar en memoria, 5) Cada 15 minutos (via hook) para revisar si hay algo nuevo. Busca y carga memorias relevantes del proyecto actual. Solo busca en otros proyectos cuando el usuario lo pide explícitamente.
version: 1.0.0
tools: Bash, PowerShell, Read, Write
---

# brain-agm: Sistema de Memoria Compartida

Sistema para retener información importante entre sesiones de Claude Code. Las memorias se guardan en `~/Documents/brain-agm/[proyecto]/` y son accesibles desde cualquier sesión e IDE.

## Cuándo Activarse

### Guardar Memoria (Automático)

**Siempre guardar cuando**:
- Se completa o cierra un plan
- Se toma una decisión técnica no obvia
- Se resuelve un problema complejo
- Usuario dice explícitamente: "guarda esto en memoria", "recuerda esto", "anota esto"

**Qué guardar**:
- **Planes**: Guardar con contexto completo - qué se implementó, archivos modificados, decisiones tomadas
- **Decisiones**: Guardar con el por qué - contexto, alternativas consideradas, razón de la elección, trade-offs
- **Problemas**: Guardar con la solución - síntoma, causa raíz, solución aplicada, prevención futura
- **User requests**: Cualquier cosa que el usuario pida explícitamente recordar

### Buscar Memoria (Automático)

**Buscar cuando**:
- Usuario pregunta sobre trabajo anterior: "qué hicimos con X", "por qué decidimos Y", "cómo resolvimos Z"
- Pregunta sugiere contexto de sesión anterior del mismo proyecto
- Usuario dice: "busca en memoria", "qué recuerdas sobre X"

**Alcance de búsqueda**:
- **Default**: SOLO proyecto actual (NO usar `--all-projects`)
- **Cross-project**: Solo cuando usuario dice explícitamente "busca en otros proyectos" o menciona un proyecto específico (usar `--all-projects`)

## Formato de Memoria

Toda memoria debe tener esta estructura:

```markdown
## Breve descripción
[1-2 líneas de resumen ejecutivo]

## El qué
[Qué se hizo, decidió o resolvió - concreto y específico]
- Archivos modificados con líneas si es relevante
- Comandos ejecutados si aplica
- Código o configuración clave

## El por qué
**Contexto**: [Situación que llevó a esto]

**Decisiones clave**:
1. [Decisión 1 con su razón]
2. [Decisión 2 con su razón]

**Trade-offs**:
- [Pro y contra de la decisión]
- [Alternativas descartadas y por qué]

## Referencias (opcional)
- PR: #123
- Documentación: docs/file.md
- Memorias relacionadas: [título de otra memoria]
```

## Comandos

### Guardar Memoria

```bash
# Windows (PowerShell)
python ~/.claude/skills/brain-agm/scripts/save_memory.py `
  --project [nombre] `
  --type [plan|decision|problem|user-request] `
  --title "titulo-descriptivo" `
  --content [ruta-archivo-temporal]

# Mac/Linux (Bash)
python ~/.claude/skills/brain-agm/scripts/save_memory.py \
  --project [nombre] \
  --type [plan|decision|problem|user-request] \
  --title "titulo-descriptivo" \
  --content [ruta-archivo-temporal]
```

**Importante**: El archivo temporal debe contener SOLO el contenido (sin frontmatter). El script agrega el frontmatter automáticamente.

### Buscar Memoria

```bash
# Buscar en proyecto actual (DEFAULT)
python ~/.claude/skills/brain-agm/scripts/search_memory.py \
  --project [nombre] \
  --query "texto a buscar"

# Buscar en todos los proyectos (SOLO cuando usuario lo pida)
python ~/.claude/skills/brain-agm/scripts/search_memory.py \
  --all-projects \
  --query "texto a buscar"
```

## Workflow: Guardar

1. **Detectar momento importante** (plan cerrado, decisión tomada, problema resuelto, user request)

2. **Crear archivo temporal** con el contenido:
   ```bash
   # Windows
   $content = @"
   ## Breve descripción
   [...]
   
   ## El qué
   [...]
   
   ## El por qué
   [...]
   "@
   
   $tempFile = "$env:TEMP\memory-$(Get-Date -Format 'yyyyMMdd-HHmmss').md"
   $content | Out-File -FilePath $tempFile -Encoding utf8
   ```

3. **Ejecutar script de guardado**:
   ```bash
   python ~/.claude/skills/brain-agm/scripts/save_memory.py \
     --type [tipo apropiado] \
     --title "titulo-descriptivo" \
     --content $tempFile \
     --tags "tag1,tag2"  # Opcional
   ```

4. **Confirmar al usuario**:
   ```
   ✓ Guardé esto en memoria: [título]
   Ubicación: ~/Documents/brain-agm/[proyecto]/[archivo].md
   Tipo: [tipo]
   ```

## Workflow: Buscar

1. **Detectar pregunta sobre trabajo anterior**
   - Palabras clave: "qué hicimos", "por qué decidimos", "cómo resolvimos", "recuerdas"
   - Contexto: Usuario pregunta por algo que no está en archivos actuales

2. **Determinar alcance**:
   - **Proyecto actual**: No menciona otros proyectos → NO usar `--all-projects`
   - **Cross-project**: Dice "en otros proyectos" o menciona proyecto específico → usar `--all-projects`

3. **Ejecutar búsqueda**:
   ```bash
   python ~/.claude/skills/brain-agm/scripts/search_memory.py \
     --project brain-agm \
     --query "oauth"
   ```

4. **Procesar resultados**:
   - Leer el archivo completo de las memorias más relevantes
   - Cargar contexto en la conversación

5. **Responder al usuario**:
   ```
   Encontré [N] memoria(s) relacionada(s) en [proyecto]:
   
   1. [Título] (fecha: [fecha], tipo: [tipo])
      Archivo: [ruta]
      
      [Resumen de lo encontrado]
   
   [Usar el contenido para responder la pregunta original]
   ```

## Ejemplos

### Ejemplo 1: Guardar Plan Completado

**Situación**: Acabas de completar un plan de implementación de OAuth.

**Acción**:
```powershell
$content = @"
## Breve descripción
Implementación de autenticación OAuth 2.0 con Google y Microsoft

## El qué
Se implementó flujo OAuth 2.0:
- Archivos: src/auth/oauth.py:45-120, src/config/providers.py:12-30
- Endpoints: /auth/login, /auth/callback, /auth/logout
- Providers: Google OAuth, Microsoft Azure AD
- Storage: Redis con TTL de 7 días

## El por qué
**Contexto**: Cliente requiere SSO corporativo para cumplir política de seguridad

**Decisiones clave**:
1. authlib sobre python-oauth2 - mejor soporte PKCE
2. Redis para tokens - TTL automático, bajo volumen (<10k users)
3. No refresh tokens esta fase - cliente prefiere re-auth cada 7 días

**Trade-offs**:
- Más complejo que auth local pero requerido por política
- Dependencia servicios externos mitigada con retry logic
"@

$tempFile = "$env:TEMP\memory-oauth.md"
$content | Out-File -FilePath $tempFile -Encoding utf8

python ~/.claude/skills/brain-agm/scripts/save_memory.py `
  --type plan `
  --title "Implementación OAuth 2.0" `
  --content $tempFile `
  --tags "auth,oauth,security"
```

**Respuesta al usuario**:
```
✓ Guardé el plan completado en memoria: implementación-oauth-2-0
Ubicación: ~/Documents/brain-agm/api-backend/implementación-oauth-2-0_2026-11-05_14-30-00.md
Tipo: plan
```

### Ejemplo 2: Buscar Decisión Anterior

**Situación**: Usuario pregunta "por qué usamos Redis para los tokens?"

**Detección**: Pregunta sobre decisión técnica pasada

**Acción**:
```bash
python ~/.claude/skills/brain-agm/scripts/search_memory.py \
  --project api-backend \
  --query "redis tokens"
```

**Respuesta**:
```json
{
  "success": true,
  "count": 1,
  "results": [{
    "title": "implementación-oauth-2-0",
    "date": "2026-11-05",
    "type": "plan",
    "snippet": "Redis para tokens - TTL automático, bajo volumen"
  }]
}
```

**Leer memoria completa** y responder:
```
Encontré la decisión en memoria:

📝 Implementación OAuth 2.0 (2026-11-05)

Decidimos usar Redis para tokens por:
1. TTL automático - los tokens expiran en 7 días sin lógica manual
2. Volumen bajo - menos de 10k usuarios, Redis maneja esto fácilmente
3. Simple y confiable - menos código que escribir y mantener

La alternativa era usar la base de datos principal, pero preferimos Redis porque el TTL automático elimina complejidad.
```

### Ejemplo 3: Búsqueda Cross-Project

**Situación**: Usuario pregunta "busca en otros proyectos cómo manejamos rate limiting"

**Detección**: Usuario dice explícitamente "en otros proyectos"

**Acción**:
```bash
python ~/.claude/skills/brain-agm/scripts/search_memory.py \
  --all-projects \
  --query "rate limiting"
```

**Respuesta**:
```
Encontré 2 memorias en otros proyectos sobre rate limiting:

1. api-gateway: "Implementación Rate Limiting con Redis" (2026-10-15)
   - Usaron Redis con sliding window
   - 100 req/min por usuario

2. webhooks-service: "Rate Limiting para Webhooks" (2026-09-20)
   - Token bucket algorithm
   - Diferentes límites por tier de cliente

¿Quieres que lea alguna en detalle?
```

## Notas Importantes

1. **Siempre mostrar al usuario qué se guardó/encontró** - ser transparente sobre el uso de memoria

2. **Hacer referencia explícita** - decir "según la memoria de [fecha]" para que el usuario sepa de dónde viene la información

3. **El proyecto se detecta automáticamente** del nombre de la carpeta actual, pero puede especificarse con `--project`

4. **Búsquedas son SOLO proyecto actual por defecto** - usar `--all-projects` requiere que el usuario lo pida explícitamente

5. **No guardar información sensible** - sin credenciales, API keys, PII

6. **Validar antes de guardar** - el script valida formato, pero revisar que el contenido sea útil

7. **Tags ayudan a organizar** - usar tags relevantes al guardar (opcional pero recomendado)

## Troubleshooting

### Script falla con "module not found"
- Verificar que Python esté en PATH
- Verificar que los scripts estén en `~/.claude/skills/brain-agm/scripts/`

### No encuentra memorias
- Verificar que el proyecto sea correcto: `--project [nombre]`
- Verificar que exista `~/Documents/brain-agm/[proyecto]/`
- Probar con `--all-projects` si buscas en otro proyecto

### Memoria no se guarda
- Verificar que el archivo temporal existe
- Verificar permisos de escritura en `~/Documents/brain-agm/`
- Revisar formato del contenido (debe tener secciones "## Breve descripción", "## El qué", "## El por qué")

ChaChau !!!
