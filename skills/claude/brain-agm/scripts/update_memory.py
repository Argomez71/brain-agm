#!/usr/bin/env python3
"""
Script para actualizar memorias existentes en brain-agm.

Uso:
    python update_memory.py --project <nombre> --file <archivo> [opciones]

Ejemplo:
    python update_memory.py --project api-backend --file oauth-impl.md --status archived
    python update_memory.py --project api-backend --file oauth-impl.md --content /tmp/update.md --append
"""

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime

# Importar utilidades
import os
script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

from utils import (
    get_project_name,
    get_memory_dir,
    parse_memory,
    validate_frontmatter
)


def update_memory(project, filename, new_title=None, new_status=None,
                  content_file=None, append=False, new_tags=None):
    """
    Actualizar una memoria existente.

    Args:
        project (str): Nombre del proyecto
        filename (str): Nombre del archivo de memoria
        new_title (str, optional): Nuevo título
        new_status (str, optional): Nuevo status
        content_file (str, optional): Archivo con nuevo contenido
        append (bool): Si True, agregar contenido en lugar de reemplazar
        new_tags (list, optional): Nuevos tags

    Returns:
        dict: Resultado con success, file_path y message
    """
    memory_dir = get_memory_dir(project)
    file_path = memory_dir / filename

    # Verificar que el archivo existe
    if not file_path.exists():
        return {
            'success': False,
            'message': f"Archivo no encontrado: {file_path}"
        }

    # Leer memoria existente
    memory = parse_memory(file_path)
    if not memory:
        return {
            'success': False,
            'message': f"No se pudo parsear memoria: {file_path}"
        }

    frontmatter = memory['frontmatter']
    content = memory['content']

    # Actualizar frontmatter
    updated = False

    if new_title:
        frontmatter['title'] = new_title
        updated = True

    if new_status:
        valid_statuses = ['completed', 'in-progress', 'archived']
        if new_status not in valid_statuses:
            return {
                'success': False,
                'message': f"Status inválido. Debe ser uno de: {', '.join(valid_statuses)}"
            }
        frontmatter['status'] = new_status
        updated = True

    if new_tags:
        frontmatter['tags'] = json.dumps(new_tags)
        updated = True

    # Actualizar contenido
    if content_file:
        content_path = Path(content_file)
        if not content_path.exists():
            return {
                'success': False,
                'message': f"Archivo de contenido no encontrado: {content_file}"
            }

        try:
            with open(content_path, 'r', encoding='utf-8') as f:
                new_content = f.read()
        except Exception as e:
            return {
                'success': False,
                'message': f"Error leyendo contenido: {e}"
            }

        if append:
            # Agregar nota de actualización
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            content = f"{content}\n\n---\n**Actualizado**: {timestamp}\n\n{new_content}"
        else:
            content = new_content

        updated = True

    if not updated:
        return {
            'success': False,
            'message': "No se especificaron cambios para actualizar"
        }

    # Construir nuevo archivo
    frontmatter_lines = ['---']
    for key, value in frontmatter.items():
        frontmatter_lines.append(f"{key}: {value}")
    frontmatter_lines.append('---')
    frontmatter_text = '\n'.join(frontmatter_lines)

    full_content = f"{frontmatter_text}\n\n{content}"

    # Validar formato
    is_valid, error_msg = validate_frontmatter(full_content)
    if not is_valid:
        return {
            'success': False,
            'message': f"Validación falló: {error_msg}"
        }

    # Crear backup
    backup_path = file_path.with_suffix('.md.backup')
    try:
        import shutil
        shutil.copy2(file_path, backup_path)
    except Exception as e:
        return {
            'success': False,
            'message': f"Error creando backup: {e}"
        }

    # Escribir archivo actualizado
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(full_content)
    except Exception as e:
        # Restaurar backup si falla
        try:
            import shutil
            shutil.copy2(backup_path, file_path)
        except:
            pass
        return {
            'success': False,
            'message': f"Error escribiendo archivo: {e}"
        }

    # Eliminar backup si todo salió bien
    try:
        backup_path.unlink()
    except:
        pass

    return {
        'success': True,
        'file_path': str(file_path),
        'project': project,
        'updated_fields': [
            k for k in ['title', 'status', 'tags', 'content']
            if (k == 'title' and new_title) or
               (k == 'status' and new_status) or
               (k == 'tags' and new_tags) or
               (k == 'content' and content_file)
        ],
        'message': f"Memoria actualizada exitosamente: {file_path}"
    }


def main():
    parser = argparse.ArgumentParser(
        description='Actualizar una memoria existente en brain-agm',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  # Cambiar status a archived
  python update_memory.py --project api-backend --file oauth-impl.md --status archived

  # Actualizar contenido (reemplazar)
  python update_memory.py --project api-backend --file oauth-impl.md --content /tmp/update.md

  # Agregar contenido
  python update_memory.py --project api-backend --file oauth-impl.md --content /tmp/update.md --append

  # Cambiar título y tags
  python update_memory.py --project api-backend --file oauth-impl.md \\
    --title "new-title" --tags "tag1,tag2"
        """
    )

    parser.add_argument(
        '--project',
        type=str,
        default=None,
        help='Nombre del proyecto (default: detectado del directorio actual)'
    )

    parser.add_argument(
        '--file',
        type=str,
        required=True,
        help='Nombre del archivo de memoria a actualizar'
    )

    parser.add_argument(
        '--title',
        type=str,
        default=None,
        help='Nuevo título'
    )

    parser.add_argument(
        '--status',
        type=str,
        choices=['completed', 'in-progress', 'archived'],
        default=None,
        help='Nuevo status'
    )

    parser.add_argument(
        '--content',
        type=str,
        default=None,
        help='Ruta a archivo con nuevo contenido'
    )

    parser.add_argument(
        '--append',
        action='store_true',
        help='Agregar contenido en lugar de reemplazar'
    )

    parser.add_argument(
        '--tags',
        type=str,
        default=None,
        help='Nuevos tags separados por coma'
    )

    args = parser.parse_args()

    # Detectar proyecto si no se especificó
    project = args.project if args.project else get_project_name()

    # Parsear tags
    tags = args.tags.split(',') if args.tags else None
    if tags:
        tags = [tag.strip() for tag in tags]

    # Actualizar memoria
    result = update_memory(
        project=project,
        filename=args.file,
        new_title=args.title,
        new_status=args.status,
        content_file=args.content,
        append=args.append,
        new_tags=tags
    )

    # Imprimir resultado como JSON
    print(json.dumps(result, indent=2))

    # Exit code
    sys.exit(0 if result['success'] else 1)


if __name__ == '__main__':
    main()
