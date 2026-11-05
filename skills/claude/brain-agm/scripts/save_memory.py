#!/usr/bin/env python3
"""
Script para guardar memorias en brain-agm.

Uso:
    python save_memory.py --project <nombre> --type <tipo> --title <titulo> --content <archivo>

Ejemplo:
    python save_memory.py --project api-backend --type decision --title "oauth-implementation" --content /tmp/memory.md
"""

import argparse
import json
import sys
from pathlib import Path

# Importar utilidades
import os
script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

from utils import (
    get_project_name,
    ensure_memory_dir,
    validate_frontmatter,
    create_slug,
    get_date,
    get_timestamp
)


def save_memory(project, memory_type, title, content_file, tags=None):
    """
    Guardar una memoria en el sistema.

    Args:
        project (str): Nombre del proyecto
        memory_type (str): Tipo de memoria (plan|decision|problem|user-request)
        title (str): Título de la memoria
        content_file (str): Ruta al archivo con el contenido
        tags (list, optional): Lista de tags

    Returns:
        dict: Resultado con success, file_path y message
    """
    # Validar tipo
    valid_types = ['plan', 'decision', 'problem', 'user-request']
    if memory_type not in valid_types:
        return {
            'success': False,
            'message': f"Tipo inválido. Debe ser uno de: {', '.join(valid_types)}"
        }

    # Leer contenido
    content_path = Path(content_file)
    if not content_path.exists():
        return {
            'success': False,
            'message': f"Archivo de contenido no encontrado: {content_file}"
        }

    try:
        with open(content_path, 'r', encoding='utf-8') as f:
            content_body = f.read()
    except Exception as e:
        return {
            'success': False,
            'message': f"Error leyendo archivo de contenido: {e}"
        }

    # Crear slug del título
    slug = create_slug(title)
    if not slug:
        return {
            'success': False,
            'message': "Título inválido (no se pudo crear slug)"
        }

    # Asegurar que existe el directorio
    memory_dir = ensure_memory_dir(project)

    # Crear nombre de archivo único
    timestamp = get_timestamp().replace(':', '-').replace('T', '_')
    filename = f"{slug}_{timestamp}.md"
    file_path = memory_dir / filename

    # Construir frontmatter
    date = get_date()
    tags_str = json.dumps(tags) if tags else "[]"

    frontmatter = f"""---
title: {slug}
date: {date}
project: {project}
type: {memory_type}
status: completed
tags: {tags_str}
---

"""

    # Combinar frontmatter + contenido
    full_content = frontmatter + content_body

    # Validar formato
    is_valid, error_msg = validate_frontmatter(full_content)
    if not is_valid:
        return {
            'success': False,
            'message': f"Validación de formato falló: {error_msg}"
        }

    # Escribir archivo
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(full_content)
    except Exception as e:
        return {
            'success': False,
            'message': f"Error escribiendo archivo: {e}"
        }

    return {
        'success': True,
        'file_path': str(file_path),
        'project': project,
        'title': slug,
        'message': f"Memoria guardada exitosamente en {file_path}"
    }


def main():
    parser = argparse.ArgumentParser(
        description='Guardar una memoria en brain-agm',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplo:
  python save_memory.py --project api-backend --type decision \\
    --title "OAuth Implementation" --content /tmp/memory-content.md

Tipos válidos: plan, decision, problem, user-request
        """
    )

    parser.add_argument(
        '--project',
        type=str,
        default=None,
        help='Nombre del proyecto (default: detectado del directorio actual)'
    )

    parser.add_argument(
        '--type',
        type=str,
        required=True,
        choices=['plan', 'decision', 'problem', 'user-request'],
        help='Tipo de memoria'
    )

    parser.add_argument(
        '--title',
        type=str,
        required=True,
        help='Título de la memoria'
    )

    parser.add_argument(
        '--content',
        type=str,
        required=True,
        help='Ruta al archivo con el contenido de la memoria'
    )

    parser.add_argument(
        '--tags',
        type=str,
        default=None,
        help='Tags separados por coma (ej: "auth,oauth,security")'
    )

    args = parser.parse_args()

    # Detectar proyecto si no se especificó
    project = args.project if args.project else get_project_name()

    # Parsear tags
    tags = args.tags.split(',') if args.tags else None
    if tags:
        tags = [tag.strip() for tag in tags]

    # Guardar memoria
    result = save_memory(
        project=project,
        memory_type=args.type,
        title=args.title,
        content_file=args.content,
        tags=tags
    )

    # Imprimir resultado como JSON
    print(json.dumps(result, indent=2))

    # Exit code
    sys.exit(0 if result['success'] else 1)


if __name__ == '__main__':
    main()
