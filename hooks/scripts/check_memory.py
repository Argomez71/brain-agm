#!/usr/bin/env python3
"""
Hook de revisión automática para brain-agm.

Se ejecuta en PostToolUse y verifica si han pasado 15+ minutos desde la última revisión.
Si sí, sugiere al agente que revise si hay algo importante que guardar.

Este hook NO guarda automáticamente, solo SUGIERE al agente que revise.
"""

import json
import sys
import os
from pathlib import Path
from datetime import datetime, timedelta


def get_last_check_file():
    """Obtener ruta del archivo .last_check"""
    if sys.platform == 'win32':
        home = Path(os.environ.get('USERPROFILE', os.path.expanduser('~')))
    else:
        home = Path.home()

    check_file = home / '.claude' / 'skills' / 'brain-agm' / '.last_check'
    return check_file


def should_check():
    """Determinar si es momento de revisar (15+ minutos desde última revisión)"""
    check_file = get_last_check_file()

    if not check_file.exists():
        return True

    try:
        with open(check_file, 'r') as f:
            last_check_str = f.read().strip()
            last_check = datetime.fromisoformat(last_check_str)

        # Verificar si han pasado 15+ minutos
        now = datetime.now()
        elapsed = now - last_check
        return elapsed >= timedelta(minutes=15)
    except Exception:
        # Si hay error leyendo, asumir que sí hay que revisar
        return True


def update_last_check():
    """Actualizar timestamp de última revisión"""
    check_file = get_last_check_file()

    # Crear directorio si no existe
    check_file.parent.mkdir(parents=True, exist_ok=True)

    # Escribir timestamp actual
    now = datetime.now()
    with open(check_file, 'w') as f:
        f.write(now.isoformat())


def analyze_context(input_data):
    """
    Analizar el contexto de la herramienta ejecutada para detectar momentos importantes.

    Args:
        input_data (dict): Datos del hook

    Returns:
        bool: True si detecta algo importante
    """
    tool_name = input_data.get('tool_name', '')

    # Detectar si se cerró un plan
    if 'plan' in tool_name.lower() or 'exit' in tool_name.lower():
        return True

    # Detectar si se hicieron cambios significativos
    if tool_name in ['Edit', 'Write', 'MultiEdit']:
        # Si se editaron múltiples archivos o archivos importantes
        file_path = input_data.get('file_path', '')
        if any(pattern in file_path for pattern in ['.md', 'config', 'README']):
            return True

    # Detectar git commits
    if tool_name == 'Bash' or tool_name == 'PowerShell':
        command = input_data.get('command', '')
        if 'git commit' in command or 'git push' in command:
            return True

    return False


def main():
    """Entry point del hook"""
    try:
        # Leer input desde stdin
        input_data = json.load(sys.stdin)

        # Verificar si es momento de revisar
        if not should_check():
            # No han pasado 15 minutos, no hacer nada
            sys.exit(0)

        # Analizar si hay algo importante
        is_important = analyze_context(input_data)

        if is_important:
            # Actualizar timestamp
            update_last_check()

            # Sugerir al agente que revise
            message = {
                "systemMessage": """
🧠 brain-agm: Han pasado 15+ minutos desde la última revisión de memoria.

Considera si hay algo importante que guardar:
- ¿Se completó o cerró un plan?
- ¿Se tomó una decisión técnica importante?
- ¿Se resolvió un problema complejo?

Si hay algo importante, guárdalo en memoria con el formato apropiado.
                """.strip()
            }

            print(json.dumps(message), file=sys.stdout)
        else:
            # Hay actividad pero no parece importante, esperar más
            pass

        sys.exit(0)

    except Exception as e:
        # En caso de error, no bloquear el flujo
        error_msg = {"systemMessage": f"brain-agm hook error: {e}"}
        print(json.dumps(error_msg), file=sys.stdout)
        sys.exit(0)


if __name__ == '__main__':
    main()
