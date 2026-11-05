#!/usr/bin/env python3
"""
Utilidades compartidas para brain-agm
Funciones para detectar proyecto, validar memorias y buscar texto.
"""

import os
import sys
import re
from pathlib import Path
from datetime import datetime


def get_project_name():
    """
    Obtener nombre del proyecto actual desde el directorio de trabajo.

    Returns:
        str: Nombre del proyecto (nombre del directorio actual)
    """
    cwd = os.getcwd()
    project_name = os.path.basename(cwd)

    # Limpiar nombre para usar como nombre de carpeta
    project_name = re.sub(r'[^\w\s-]', '', project_name)
    project_name = re.sub(r'[-\s]+', '-', project_name)

    return project_name.lower()


def get_memory_dir(project=None):
    """
    Obtener ruta del directorio de memorias.

    Args:
        project (str, optional): Nombre del proyecto. Si no se especifica, usa el proyecto actual.

    Returns:
        Path: Ruta al directorio de memorias del proyecto
    """
    if project is None:
        project = get_project_name()

    # Detectar OS y usar la ruta apropiada
    if sys.platform == 'win32':
        home = Path(os.environ.get('USERPROFILE', os.path.expanduser('~')))
    else:
        home = Path.home()

    memory_base = home / 'Documents' / 'brain-agm'
    memory_dir = memory_base / project

    return memory_dir


def ensure_memory_dir(project=None):
    """
    Asegurar que el directorio de memorias existe, crearlo si no.

    Args:
        project (str, optional): Nombre del proyecto

    Returns:
        Path: Ruta al directorio de memorias
    """
    memory_dir = get_memory_dir(project)
    memory_dir.mkdir(parents=True, exist_ok=True)
    return memory_dir


def validate_frontmatter(content):
    """
    Validar que el contenido tiene frontmatter válido.

    Args:
        content (str): Contenido del archivo de memoria

    Returns:
        tuple: (bool, str) - (es_válido, mensaje_error)
    """
    lines = content.strip().split('\n')

    # Debe empezar con ---
    if not lines or lines[0].strip() != '---':
        return False, "Frontmatter debe empezar con '---'"

    # Buscar el cierre del frontmatter
    end_idx = -1
    for i in range(1, len(lines)):
        if lines[i].strip() == '---':
            end_idx = i
            break

    if end_idx == -1:
        return False, "Frontmatter no está cerrado con '---'"

    # Validar campos requeridos en frontmatter
    frontmatter = '\n'.join(lines[1:end_idx])
    required_fields = ['title:', 'date:', 'project:', 'type:']

    for field in required_fields:
        if field not in frontmatter:
            return False, f"Campo requerido '{field.rstrip(':')}' no encontrado en frontmatter"

    return True, ""


def parse_memory(file_path):
    """
    Parsear un archivo de memoria.

    Args:
        file_path (Path or str): Ruta al archivo de memoria

    Returns:
        dict: Diccionario con 'frontmatter' (dict) y 'content' (str)
              Retorna None si el archivo no existe o es inválido
    """
    file_path = Path(file_path)

    if not file_path.exists():
        return None

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error leyendo archivo: {e}", file=sys.stderr)
        return None

    lines = content.split('\n')

    # Buscar frontmatter
    if not lines or lines[0].strip() != '---':
        return None

    end_idx = -1
    for i in range(1, len(lines)):
        if lines[i].strip() == '---':
            end_idx = i
            break

    if end_idx == -1:
        return None

    # Parsear frontmatter (simple key: value)
    frontmatter = {}
    for line in lines[1:end_idx]:
        if ':' in line:
            key, value = line.split(':', 1)
            frontmatter[key.strip()] = value.strip()

    # Contenido después del frontmatter
    body = '\n'.join(lines[end_idx + 1:])

    return {
        'frontmatter': frontmatter,
        'content': body.strip()
    }


def search_text(query, text):
    """
    Buscar texto simple (case-insensitive).

    Args:
        query (str): Texto a buscar
        text (str): Texto donde buscar

    Returns:
        tuple: (bool, list) - (encontrado, lista de líneas coincidentes)
    """
    query_lower = query.lower()
    text_lower = text.lower()

    if query_lower not in text_lower:
        return False, []

    # Encontrar líneas que contienen el query
    lines = text.split('\n')
    matching_lines = []

    for i, line in enumerate(lines):
        if query_lower in line.lower():
            matching_lines.append((i + 1, line.strip()))

    return True, matching_lines


def create_slug(title):
    """
    Crear slug desde un título.

    Args:
        title (str): Título a convertir

    Returns:
        str: Slug (kebab-case, sin caracteres especiales)
    """
    # Convertir a minúsculas
    slug = title.lower()

    # Remover caracteres especiales
    slug = re.sub(r'[^\w\s-]', '', slug)

    # Reemplazar espacios y múltiples guiones con un guion
    slug = re.sub(r'[-\s]+', '-', slug)

    # Remover guiones al inicio y final
    slug = slug.strip('-')

    return slug


def get_timestamp():
    """
    Obtener timestamp actual en formato ISO 8601.

    Returns:
        str: Timestamp (e.g., "2026-11-05T14:30:00")
    """
    return datetime.now().strftime('%Y-%m-%dT%H:%M:%S')


def get_date():
    """
    Obtener fecha actual en formato YYYY-MM-DD.

    Returns:
        str: Fecha (e.g., "2026-11-05")
    """
    return datetime.now().strftime('%Y-%m-%d')


if __name__ == '__main__':
    # Pruebas básicas
    print(f"Proyecto actual: {get_project_name()}")
    print(f"Directorio de memorias: {get_memory_dir()}")
    print(f"Slug de 'Implementación OAuth 2.0': {create_slug('Implementación OAuth 2.0')}")
    print(f"Fecha actual: {get_date()}")
