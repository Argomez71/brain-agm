#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Instalador de brain-agm para Windows/Mac/Linux

.DESCRIPTION
    Instala el sistema de memoria compartida brain-agm:
    - Crea directorio de memorias en ~/Documents/brain-agm/
    - Copia skills a Claude (~/.claude/skills/brain-agm/)
    - Copia skills a Windsurf (~/.codeium/windsurf/skills/brain-agm/)
    - Agrega configuración a AGENTS.md y CLAUDE.md (sin sobreescribir)

.PARAMETER Verbose
    Muestra información detallada durante la instalación

.EXAMPLE
    .\install.ps1
    .\install.ps1 -Verbose
#>

[CmdletBinding()]
param(
    [switch]$VerboseMode
)

# Colores para output
function Write-Success { param($msg) Write-Host "✓ $msg" -ForegroundColor Green }
function Write-Info { param($msg) Write-Host "→ $msg" -ForegroundColor Cyan }
function Write-Warning { param($msg) Write-Host "⚠ $msg" -ForegroundColor Yellow }
function Write-ErrorMsg { param($msg) Write-Host "✗ $msg" -ForegroundColor Red }

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  brain-agm: Sistema de Memoria Compartida" -ForegroundColor Cyan
Write-Host "  Instalador v1.0.0" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# 1. Verificar Python instalado
Write-Info "Verificando Python..."
$pythonCmd = $null
foreach ($cmd in @('python', 'python3')) {
    try {
        $version = & $cmd --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            $pythonCmd = $cmd
            Write-Success "Python encontrado: $version"
            break
        }
    } catch {}
}

if (-not $pythonCmd) {
    Write-ErrorMsg "Python no encontrado. Instala Python 3.7+ desde https://www.python.org/downloads/"
    exit 1
}

# 2. Detectar rutas según OS
Write-Info "Detectando sistema operativo..."
if ($IsWindows -or $env:OS -match "Windows") {
    $homeDir = $env:USERPROFILE
    $os = "Windows"
} else {
    $homeDir = $env:HOME
    if ($IsMacOS) {
        $os = "macOS"
    } else {
        $os = "Linux"
    }
}
Write-Success "Sistema: $os"
Write-Success "Home: $homeDir"

# Rutas importantes
$memoryBase = Join-Path $homeDir "Documents\brain-agm"
$claudeSkills = Join-Path $homeDir ".claude\skills\brain-agm"
$claudeAgents = Join-Path $homeDir ".claude\AGENTS.md"
$claudeMd = Join-Path $homeDir ".claude\CLAUDE.md"
$windsurfSkills = Join-Path $homeDir ".codeium\windsurf\skills\brain-agm"
$windsurfAgents = Join-Path $homeDir ".codeium\windsurf\AGENTS.md"

$projectRoot = $PSScriptRoot

# 3. Crear directorio de memorias
Write-Info "Creando directorio de memorias..."
if (Test-Path $memoryBase) {
    Write-Success "Directorio ya existe: $memoryBase"
} else {
    New-Item -ItemType Directory -Force -Path $memoryBase | Out-Null
    Write-Success "Creado: $memoryBase"
}

# 4. Copiar skills a Claude
Write-Info "Instalando skill para Claude Code..."
$sourceSkill = Join-Path $projectRoot "skills\claude\brain-agm"
if (Test-Path $sourceSkill) {
    # Crear directorio padre si no existe
    $claudeSkillsParent = Split-Path $claudeSkills -Parent
    if (-not (Test-Path $claudeSkillsParent)) {
        New-Item -ItemType Directory -Force -Path $claudeSkillsParent | Out-Null
    }

    # Copiar skill
    Copy-Item -Path $sourceSkill -Destination $claudeSkills -Recurse -Force
    Write-Success "Skill copiado a: $claudeSkills"

    # Verificar que los scripts funcionan
    $testScript = Join-Path $claudeSkills "scripts\save_memory.py"
    if (Test-Path $testScript) {
        try {
            & $pythonCmd $testScript --help | Out-Null
            if ($LASTEXITCODE -eq 0) {
                Write-Success "Scripts Python verificados"
            }
        } catch {
            Write-Warning "No se pudo verificar scripts Python"
        }
    }
} else {
    Write-ErrorMsg "No se encontró skill de Claude en: $sourceSkill"
}

# 5. Copiar skills a Windsurf (si existe)
Write-Info "Verificando Windsurf/Devin..."
$windsurfBase = Join-Path $homeDir ".codeium\windsurf"
if (Test-Path $windsurfBase) {
    Write-Info "Windsurf encontrado, instalando skill..."
    $sourceWindsurf = Join-Path $projectRoot "skills\windsurf\brain-agm"

    if (Test-Path $sourceWindsurf) {
        $windsurfSkillsParent = Split-Path $windsurfSkills -Parent
        if (-not (Test-Path $windsurfSkillsParent)) {
            New-Item -ItemType Directory -Force -Path $windsurfSkillsParent | Out-Null
        }
        Copy-Item -Path $sourceWindsurf -Destination $windsurfSkills -Recurse -Force
        Write-Success "Skill copiado a: $windsurfSkills"
    } else {
        Write-Warning "Skill de Windsurf no disponible todavía (TODO)"
    }
} else {
    Write-Warning "Windsurf no encontrado, omitiendo..."
}

# 6. Manejar AGENTS.md de Claude (NO sobreescribir)
Write-Info "Configurando AGENTS.md global para Claude..."
$agentsContent = Get-Content (Join-Path $projectRoot "config\claude\AGENTS.md") -Raw

if (Test-Path $claudeAgents) {
    # Archivo existe, verificar si ya tiene brain-agm
    $existing = Get-Content $claudeAgents -Raw
    if ($existing -match "brain-agm: Sistema de memoria compartida") {
        Write-Warning "AGENTS.md ya contiene brain-agm, omitiendo..."
    } else {
        # Agregar al final con backup
        $backup = "$claudeAgents.backup-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
        Copy-Item $claudeAgents $backup
        Write-Success "Backup creado: $backup"

        Add-Content -Path $claudeAgents -Value "`n`n$agentsContent"
        Write-Success "brain-agm agregado a AGENTS.md existente"
    }
} else {
    # Crear nuevo
    $claudeDir = Split-Path $claudeAgents -Parent
    if (-not (Test-Path $claudeDir)) {
        New-Item -ItemType Directory -Force -Path $claudeDir | Out-Null
    }
    Set-Content -Path $claudeAgents -Value $agentsContent
    Write-Success "AGENTS.md creado: $claudeAgents"
}

# 7. Manejar CLAUDE.md global (NO sobreescribir)
Write-Info "Configurando CLAUDE.md global para Claude..."
$claudeMdContent = Get-Content (Join-Path $projectRoot "config\claude\CLAUDE.md") -Raw

if (Test-Path $claudeMd) {
    # Archivo existe, verificar si ya referencia AGENTS.md
    $existing = Get-Content $claudeMd -Raw

    if ($existing -match "brain-agm") {
        Write-Warning "CLAUDE.md ya contiene brain-agm, omitiendo..."
    } elseif ($existing -match "@.*AGENTS\.md") {
        Write-Success "CLAUDE.md ya referencia AGENTS.md"
    } else {
        # Agregar referencia a AGENTS.md si no existe
        $backup = "$claudeMd.backup-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
        Copy-Item $claudeMd $backup
        Write-Success "Backup creado: $backup"

        # Agregar al final
        Add-Content -Path $claudeMd -Value "`n`n$claudeMdContent"
        Write-Success "brain-agm agregado a CLAUDE.md existente"
    }
} else {
    # Crear nuevo
    Set-Content -Path $claudeMd -Value $claudeMdContent
    Write-Success "CLAUDE.md creado: $claudeMd"
}

# 8. Manejar AGENTS.md de Windsurf (si aplica)
if (Test-Path $windsurfBase) {
    Write-Info "Configurando AGENTS.md para Windsurf..."
    $windsurfAgentsSource = Join-Path $projectRoot "config\windsurf\AGENTS.md"

    if (Test-Path $windsurfAgentsSource) {
        $windsurfAgentsContent = Get-Content $windsurfAgentsSource -Raw

        if (Test-Path $windsurfAgents) {
            $existing = Get-Content $windsurfAgents -Raw
            if ($existing -match "brain-agm") {
                Write-Warning "Windsurf AGENTS.md ya contiene brain-agm"
            } else {
                $backup = "$windsurfAgents.backup-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
                Copy-Item $windsurfAgents $backup
                Add-Content -Path $windsurfAgents -Value "`n`n$windsurfAgentsContent"
                Write-Success "brain-agm agregado a Windsurf AGENTS.md"
            }
        } else {
            Set-Content -Path $windsurfAgents -Value $windsurfAgentsContent
            Write-Success "Windsurf AGENTS.md creado"
        }
    } else {
        Write-Warning "Configuración de Windsurf no disponible todavía (TODO)"
    }
}

# 9. Copiar hook check_memory.py
Write-Info "Instalando hook de revisión automática..."
$hookScript = Join-Path $projectRoot "hooks\scripts\check_memory.py"
if (Test-Path $hookScript) {
    $claudeHooksDir = Join-Path $homeDir ".claude\skills\brain-agm\hooks"
    if (-not (Test-Path $claudeHooksDir)) {
        New-Item -ItemType Directory -Force -Path $claudeHooksDir | Out-Null
    }
    Copy-Item -Path $hookScript -Destination $claudeHooksDir -Force
    Write-Success "Hook copiado a: $claudeHooksDir"
} else {
    Write-Warning "Hook script no encontrado"
}

# 10. Resumen de instalación
Write-Host ""
Write-Host "============================================" -ForegroundColor Green
Write-Host "  ✓ Instalación Completada" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
Write-Host ""

Write-Host "Archivos instalados:" -ForegroundColor Cyan
Write-Host "  → Memorias: $memoryBase" -ForegroundColor White
Write-Host "  → Skill Claude: $claudeSkills" -ForegroundColor White
Write-Host "  → Config Claude: $claudeAgents" -ForegroundColor White
Write-Host "  → Config Claude: $claudeMd" -ForegroundColor White

if (Test-Path $windsurfBase) {
    Write-Host "  → Skill Windsurf: $windsurfSkills" -ForegroundColor White
    Write-Host "  → Config Windsurf: $windsurfAgents" -ForegroundColor White
}

Write-Host ""
Write-Host "Próximos pasos:" -ForegroundColor Yellow
Write-Host "  1. Abre una nueva sesión de Claude Code" -ForegroundColor White
Write-Host "  2. Prueba: 'guarda esto en memoria: instalé brain-agm'" -ForegroundColor White
Write-Host "  3. En otra sesión: 'qué instalamos recientemente?'" -ForegroundColor White
Write-Host ""
Write-Host "Ver README.md para más información y troubleshooting" -ForegroundColor Cyan
Write-Host ""
