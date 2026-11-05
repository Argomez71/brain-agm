# brain-agm: Sistema de Memoria Compartida

Sistema de memoria compartida entre sesiones para Claude Code y Devin/Windsurf. Guarda automáticamente planes, decisiones y problemas resueltos para que no pierdas contexto al abrir nuevas sesiones.

## Problema que Resuelve

Cuando trabajas con IA en diferentes sesiones, el agente no recuerda lo que hicieron en sesiones anteriores. Tienes que:
- Repetir contexto cada vez
- Documentar manualmente todo lo importante
- Buscar en tu historial de commits/PRs

**brain-agm** resuelve esto guardando automáticamente información importante en una ubicación compartida que todos los IDEs pueden leer.

## Características

- ✅ **Memoria automática** - Guarda planes, decisiones y problemas sin que lo pidas
- ✅ **Búsqueda inteligente** - El agente encuentra memorias relevantes cuando preguntas
- ✅ **Cross-IDE** - Funciona en Claude Code y Devin/Windsurf
- ✅ **Simple** - Solo archivos Markdown, sin base de datos
- ✅ **Portable** - Comparte memorias entre máquinas copiando `~/Documents/brain-agm/`

## Instalación

### Requisitos

- Python 3.7+ instalado
- Claude Code o Devin/Windsurf instalado
- PowerShell 5.1+ (Windows) o Bash 4+ (Mac/Linux)

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

## Qué Instala

El script de instalación:

1. ✅ Crea `~/Documents/brain-agm/` para guardar memorias
2. ✅ Copia el skill a `~/.claude/skills/brain-agm/` (Claude)
3. ✅ Copia el skill a `~/.codeium/windsurf/skills/brain-agm/` (Devin)
4. ✅ Agrega configuración a `~/.claude/AGENTS.md` y `~/.claude/CLAUDE.md`
5. ✅ Agrega configuración a `~/.codeium/windsurf/AGENTS.md`

**Importante**: NO sobreescribe archivos existentes, agrega el contenido de brain-agm al final.

## Uso

### Automático

El sistema funciona automáticamente:

**Guarda memoria cuando**:
- Completas un plan
- Tomas una decisión técnica importante
- Resuelves un problema complejo
- Dices: "guarda esto en memoria"

**Busca memoria cuando**:
- Preguntas: "qué hicimos con X", "por qué decidimos Y"
- Referencias algo de sesiones anteriores

### Manual

#### Guardar una memoria

```bash
# 1. Crear archivo con el contenido
cat > /tmp/memory.md << 'EOF'
## Breve descripción
Implementación de autenticación OAuth

## El qué
- Implementamos OAuth 2.0 con Google y Microsoft
- Archivos: src/auth/oauth.py
- Endpoints: /auth/login, /auth/callback

## El por qué
Cliente requiere SSO corporativo para seguridad
EOF

# 2. Guardar
python ~/.claude/skills/brain-agm/scripts/save_memory.py \
  --type decision \
  --title "OAuth Implementation" \
  --content /tmp/memory.md
```

#### Buscar memorias

```bash
# Buscar en proyecto actual
python ~/.claude/skills/brain-agm/scripts/search_memory.py \
  --query "oauth"

# Buscar en todos los proyectos
python ~/.claude/skills/brain-agm/scripts/search_memory.py \
  --all-projects \
  --query "autenticación"
```

## Estructura de Memorias

Las memorias se guardan en: `~/Documents/brain-agm/[proyecto]/`

Cada memoria es un archivo Markdown:

```markdown
---
title: oauth-implementation
date: 2026-11-05
project: api-backend
type: decision
status: completed
tags: ["auth", "oauth", "security"]
---

## Breve descripción
Implementación de OAuth 2.0 con Google y Microsoft

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

## Tipos de Memoria

- **plan**: Planes ejecutados o cerrados
- **decision**: Decisiones técnicas importantes
- **problem**: Problemas resueltos con su solución
- **user-request**: Cualquier cosa que pidas guardar explícitamente

## Ejemplos

### Ejemplo 1: Pregunta sobre trabajo anterior

**Tú**: "Por qué usamos Redis para los tokens de OAuth?"

**Claude**:
```
Encontré la decisión en memoria:

📝 OAuth Implementation (2026-11-05)

Decidimos usar Redis para tokens por:
1. TTL automático - expiran en 7 días sin lógica manual
2. Volumen bajo - menos de 10k usuarios
3. Simple y confiable

La alternativa era usar la DB principal, pero Redis elimina complejidad con el TTL automático.
```

### Ejemplo 2: Buscar en otros proyectos

**Tú**: "Busca en otros proyectos cómo manejamos rate limiting"

**Claude**:
```
Encontré 2 memorias en otros proyectos:

1. api-gateway: "Rate Limiting con Redis" (2026-10-15)
   - Sliding window algorithm
   - 100 req/min por usuario

2. webhooks-service: "Rate Limiting Webhooks" (2026-09-20)
   - Token bucket algorithm
   - Diferentes límites por tier

¿Quieres que lea alguna en detalle?
```

## Verificación

Probar que la instalación funcionó:

```bash
# 1. Verificar scripts instalados
python ~/.claude/skills/brain-agm/scripts/save_memory.py --help

# 2. Guardar memoria de prueba
echo "## Breve descripción
Prueba de brain-agm

## El qué
Instalé el sistema de memoria compartida

## El por qué
Para probar que funciona" > /tmp/test.md

python ~/.claude/skills/brain-agm/scripts/save_memory.py \
  --project test \
  --type user-request \
  --title "Prueba" \
  --content /tmp/test.md

# 3. Buscar la memoria
python ~/.claude/skills/brain-agm/scripts/search_memory.py \
  --project test \
  --query "prueba"

# 4. Verificar archivo guardado
ls ~/Documents/brain-agm/test/
```

## Desinstalación

```powershell
# Windows
.\uninstall.ps1

# Mac/Linux
./uninstall.sh
```

**Nota**: Por defecto NO borra las memorias guardadas en `~/Documents/brain-agm/`. El script pregunta si quieres eliminarlas.

## Troubleshooting

### Script no encuentra Python

```bash
# Verificar Python instalado
python --version  # o python3 --version

# Instalar Python si falta
# Windows: https://www.python.org/downloads/
# Mac: brew install python3
# Linux: sudo apt install python3
```

### Skill no se activa en Claude

1. Verificar que el skill está instalado:
   ```bash
   ls ~/.claude/skills/brain-agm/
   ```

2. Verificar que CLAUDE.md referencia a AGENTS.md:
   ```bash
   cat ~/.claude/CLAUDE.md
   ```

3. Reiniciar Claude Code

### No encuentra memorias

- Verificar proyecto correcto: el nombre del proyecto es el nombre de la carpeta actual
- Verificar que existe: `ls ~/Documents/brain-agm/[proyecto]/`
- Probar con `--all-projects` si buscas en otro proyecto

## Estructura del Proyecto

```
brain-agm/
├── README.md                       # Este archivo
├── install.ps1                     # Instalador Windows
├── install.sh                      # Instalador Mac/Linux (TODO)
├── uninstall.ps1                   # Desinstalador Windows (TODO)
├── uninstall.sh                    # Desinstalador Mac/Linux (TODO)
│
├── skills/                         # Skills para cada IDE
│   ├── claude/brain-agm/
│   │   ├── SKILL.md                # Definición del skill para Claude
│   │   └── scripts/
│   │       ├── __init__.py
│   │       ├── utils.py            # Funciones compartidas
│   │       ├── save_memory.py      # Guardar memorias
│   │       └── search_memory.py    # Buscar memorias
│   │
│   └── windsurf/brain-agm/
│       └── SKILL.md                # Skill para Devin (TODO)
│
├── config/                         # Configuración global
│   ├── claude/
│   │   ├── CLAUDE.md               # Config global Claude
│   │   └── AGENTS.md               # Reglas brain-agm
│   └── windsurf/
│       └── AGENTS.md               # Reglas Devin (TODO)
│
├── hooks/                          # Hooks (TODO)
│   ├── claude/hooks.json
│   └── scripts/check_memory.py
│
└── templates/
    └── memory_template.md          # Template (TODO)
```

## Roadmap

- [x] Scripts Python básicos
- [x] Skill para Claude
- [x] Configuración global Claude
- [x] Script de instalación Windows
- [ ] Script update_memory.py
- [ ] Skill para Devin/Windsurf
- [ ] Hook de revisión cada 15 min
- [ ] Scripts Mac/Linux
- [ ] Scripts de desinstalación
- [ ] Tests automatizados

## Contribuir

Este proyecto está diseñado para compartirse con el equipo. Si tienes mejoras:

1. Probar localmente
2. Documentar el cambio
3. Compartir el código actualizado

## Licencia

Uso interno de Improving. No distribuir fuera de la organización.

## Soporte

Para problemas o preguntas:
- Revisar sección Troubleshooting arriba
- Contactar al equipo de Global IT Services
- Crear issue en el repo interno (si aplica)

---

**Versión**: 1.0.0  
**Última actualización**: 2026-11-05  
**Autor**: Armando Gómez (armando.gomez@improving.com)
