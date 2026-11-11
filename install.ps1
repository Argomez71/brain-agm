#!/usr/bin/env pwsh
<#
.SYNOPSIS
    brain-agm installer for Windows/Mac/Linux

.DESCRIPTION
    Installs the brain-agm shared memory system:
    - Creates the memory directory in ~/Documents/brain-agm/
    - Copies the skill to Claude (~/.claude/skills/brain-agm/)
    - Copies the skill to Windsurf (~/.codeium/windsurf/skills/brain-agm/)
    - Adds configuration to AGENTS.md and CLAUDE.md (without overwriting)
    - Registers the automatic review hook in ~/.claude/settings.json

.PARAMETER Verbose
    Shows detailed information during installation

.EXAMPLE
    .\install.ps1
    .\install.ps1 -Verbose
#>

[CmdletBinding()]
param(
    [switch]$VerboseMode
)

# Output colors
function Write-Success { param($msg) Write-Host "✓ $msg" -ForegroundColor Green }
function Write-Info { param($msg) Write-Host "→ $msg" -ForegroundColor Cyan }
function Write-Warning { param($msg) Write-Host "⚠ $msg" -ForegroundColor Yellow }
function Write-ErrorMsg { param($msg) Write-Host "✗ $msg" -ForegroundColor Red }

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  brain-agm: Shared Memory System" -ForegroundColor Cyan
Write-Host "  Installer v1.0.0" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# 1. Check that Python is installed
Write-Info "Checking Python..."
$pythonCmd = $null
foreach ($cmd in @('python', 'python3')) {
    try {
        $version = & $cmd --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            $pythonCmd = $cmd
            Write-Success "Python found: $version"
            break
        }
    } catch {}
}

if (-not $pythonCmd) {
    Write-ErrorMsg "Python not found. Install Python 3.7+ from https://www.python.org/downloads/"
    exit 1
}

# 2. Detect paths based on the OS
Write-Info "Detecting operating system..."
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
Write-Success "System: $os"
Write-Success "Home: $homeDir"

# Important paths
$memoryBase = Join-Path $homeDir "Documents" "brain-agm"
$claudeSkills = Join-Path $homeDir ".claude" "skills" "brain-agm"
$claudeAgents = Join-Path $homeDir ".claude" "AGENTS.md"
$claudeMd = Join-Path $homeDir ".claude" "CLAUDE.md"
$windsurfSkills = Join-Path $homeDir ".codeium" "windsurf" "skills" "brain-agm"
$windsurfAgents = Join-Path $homeDir ".codeium" "windsurf" "AGENTS.md"

$projectRoot = $PSScriptRoot

# 3. Create the memory directory
Write-Info "Creating memory directory..."
if (Test-Path $memoryBase) {
    Write-Success "Directory already exists: $memoryBase"
} else {
    New-Item -ItemType Directory -Force -Path $memoryBase | Out-Null
    Write-Success "Created: $memoryBase"
}

# 4. Copy the skill to Claude
Write-Info "Installing skill for Claude Code..."
$sourceSkill = Join-Path $projectRoot "skills" "claude" "brain-agm"
if (Test-Path $sourceSkill) {
    # Create the parent directory if it does not exist
    $claudeSkillsParent = Split-Path $claudeSkills -Parent
    if (-not (Test-Path $claudeSkillsParent)) {
        New-Item -ItemType Directory -Force -Path $claudeSkillsParent | Out-Null
    }

    # Copy skill
    Copy-Item -Path $sourceSkill -Destination $claudeSkills -Recurse -Force
    Write-Success "Skill copied to: $claudeSkills"

    # Verify that the scripts work
    $testScript = Join-Path $claudeSkills "scripts" "save_memory.py"
    if (Test-Path $testScript) {
        try {
            & $pythonCmd $testScript --help | Out-Null
            if ($LASTEXITCODE -eq 0) {
                Write-Success "Python scripts verified"
            }
        } catch {
            Write-Warning "Could not verify Python scripts"
        }
    }
} else {
    Write-ErrorMsg "Claude skill not found at: $sourceSkill"
}

# 5. Copy the skill to Windsurf (if installed)
Write-Info "Checking Windsurf/Devin..."
$windsurfBase = Join-Path $homeDir ".codeium" "windsurf"
if (Test-Path $windsurfBase) {
    Write-Info "Windsurf found, installing skill..."
    $sourceWindsurf = Join-Path $projectRoot "skills" "windsurf" "brain-agm"

    if (Test-Path $sourceWindsurf) {
        $windsurfSkillsParent = Split-Path $windsurfSkills -Parent
        if (-not (Test-Path $windsurfSkillsParent)) {
            New-Item -ItemType Directory -Force -Path $windsurfSkillsParent | Out-Null
        }
        Copy-Item -Path $sourceWindsurf -Destination $windsurfSkills -Recurse -Force
        Write-Success "Skill copied to: $windsurfSkills"
    } else {
        Write-Warning "Windsurf skill not available yet (TODO)"
    }
} else {
    Write-Warning "Windsurf not found, skipping..."
}

# 6. Handle the global Claude AGENTS.md (do NOT overwrite)
Write-Info "Configuring global AGENTS.md for Claude..."
$agentsContent = Get-Content (Join-Path $projectRoot "config" "claude" "AGENTS.md") -Raw

if (Test-Path $claudeAgents) {
    # File exists, check whether it already has brain-agm
    $existing = Get-Content $claudeAgents -Raw
    if ($existing -match "brain-agm: (Sistema de memoria compartida|Shared Memory System)") {
        Write-Warning "AGENTS.md already contains brain-agm, skipping..."
    } else {
        # Append to the end, with a backup
        $backup = "$claudeAgents.backup-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
        Copy-Item $claudeAgents $backup
        Write-Success "Backup created: $backup"

        Add-Content -Path $claudeAgents -Value "`n`n$agentsContent"
        Write-Success "brain-agm added to existing AGENTS.md"
    }
} else {
    # Create new
    $claudeDir = Split-Path $claudeAgents -Parent
    if (-not (Test-Path $claudeDir)) {
        New-Item -ItemType Directory -Force -Path $claudeDir | Out-Null
    }
    Set-Content -Path $claudeAgents -Value $agentsContent
    Write-Success "AGENTS.md created: $claudeAgents"
}

# 7. Handle the global CLAUDE.md (do NOT overwrite)
Write-Info "Configuring global CLAUDE.md for Claude..."
$claudeMdContent = Get-Content (Join-Path $projectRoot "config" "claude" "CLAUDE.md") -Raw

if (Test-Path $claudeMd) {
    # File exists, check whether it already references AGENTS.md
    $existing = Get-Content $claudeMd -Raw

    if ($existing -match "brain-agm") {
        Write-Warning "CLAUDE.md already contains brain-agm, skipping..."
    } elseif ($existing -match "@.*AGENTS\.md") {
        Write-Success "CLAUDE.md already references AGENTS.md"
    } else {
        # Add a reference to AGENTS.md
        $backup = "$claudeMd.backup-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
        Copy-Item $claudeMd $backup
        Write-Success "Backup created: $backup"

        # Append to the end
        Add-Content -Path $claudeMd -Value "`n`n$claudeMdContent"
        Write-Success "brain-agm added to existing CLAUDE.md"
    }
} else {
    # Create new
    Set-Content -Path $claudeMd -Value $claudeMdContent
    Write-Success "CLAUDE.md created: $claudeMd"
}

# 8. Handle the Windsurf AGENTS.md (if applicable)
if (Test-Path $windsurfBase) {
    Write-Info "Configuring AGENTS.md for Windsurf..."
    $windsurfAgentsSource = Join-Path $projectRoot "config" "windsurf" "AGENTS.md"

    if (Test-Path $windsurfAgentsSource) {
        $windsurfAgentsContent = Get-Content $windsurfAgentsSource -Raw

        if (Test-Path $windsurfAgents) {
            $existing = Get-Content $windsurfAgents -Raw
            if ($existing -match "brain-agm") {
                Write-Warning "Windsurf AGENTS.md already contains brain-agm"
            } else {
                $backup = "$windsurfAgents.backup-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
                Copy-Item $windsurfAgents $backup
                Add-Content -Path $windsurfAgents -Value "`n`n$windsurfAgentsContent"
                Write-Success "brain-agm added to Windsurf AGENTS.md"
            }
        } else {
            Set-Content -Path $windsurfAgents -Value $windsurfAgentsContent
            Write-Success "Windsurf AGENTS.md created"
        }
    } else {
        Write-Warning "Windsurf configuration not available yet (TODO)"
    }
}

# 9. Copy the check_memory.py hook and register it in Claude's settings.json
Write-Info "Installing automatic review hook..."
$hookScript = Join-Path $projectRoot "hooks" "scripts" "check_memory.py"
if (Test-Path $hookScript) {
    $claudeHooksDir = Join-Path $homeDir ".claude" "skills" "brain-agm" "hooks"
    if (-not (Test-Path $claudeHooksDir)) {
        New-Item -ItemType Directory -Force -Path $claudeHooksDir | Out-Null
    }
    Copy-Item -Path $hookScript -Destination $claudeHooksDir -Force
    Write-Success "Hook copied to: $claudeHooksDir"

    $hookConfig = Get-Content (Join-Path $projectRoot "hooks" "claude" "hooks.json") -Raw | ConvertFrom-Json
    $claudeSettings = Join-Path $homeDir ".claude" "settings.json"
    if (Test-Path $claudeSettings) {
        $settings = Get-Content $claudeSettings -Raw | ConvertFrom-Json
        $backup = "$claudeSettings.backup-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
        Copy-Item $claudeSettings $backup
        Write-Success "Backup created: $backup"
    } else {
        $settings = [pscustomobject]@{}
    }

    if (-not $settings.PSObject.Properties['hooks']) {
        $settings | Add-Member -NotePropertyName hooks -NotePropertyValue ([pscustomobject]@{})
    }
    if (-not $settings.hooks.PSObject.Properties['PostToolUse']) {
        $settings.hooks | Add-Member -NotePropertyName PostToolUse -NotePropertyValue @()
    }

    $registered = @($settings.hooks.PostToolUse) | Where-Object { $_.hooks.command -like '*check_memory.py*' }
    if ($registered) {
        Write-Warning "Hook already registered in settings.json, skipping..."
    } else {
        $settings.hooks.PostToolUse = @($settings.hooks.PostToolUse) + @($hookConfig.hooks.PostToolUse)
        $settings | ConvertTo-Json -Depth 20 | Set-Content -Path $claudeSettings -Encoding UTF8
        Write-Success "Hook registered in settings.json"
    }
} else {
    Write-Warning "Hook script not found"
}

# 10. Installation summary
Write-Host ""
Write-Host "============================================" -ForegroundColor Green
Write-Host "  ✓ Installation Complete" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
Write-Host ""

Write-Host "Installed files:" -ForegroundColor Cyan
Write-Host "  → Memories: $memoryBase" -ForegroundColor White
Write-Host "  → Claude skill: $claudeSkills" -ForegroundColor White
Write-Host "  → Claude config: $claudeAgents" -ForegroundColor White
Write-Host "  → Claude config: $claudeMd" -ForegroundColor White

if (Test-Path $windsurfBase) {
    Write-Host "  → Windsurf skill: $windsurfSkills" -ForegroundColor White
    Write-Host "  → Windsurf config: $windsurfAgents" -ForegroundColor White
}

Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Open a new Claude Code session" -ForegroundColor White
Write-Host "  2. Try: 'remember this: I installed brain-agm'" -ForegroundColor White
Write-Host "  3. In another session: 'what did we install recently?'" -ForegroundColor White
Write-Host ""
Write-Host "See README.md for more information and troubleshooting" -ForegroundColor Cyan
Write-Host ""
