#!/usr/bin/env python3
"""
Script para buscar en memorias de brain-agm.

Uso:
    python search_memory.py --project <nombre> --query <texto>
    python search_memory.py --all-projects --query <texto>

Ejemplo:
    python search_memory.py --project api-backend --query "oauth"
    python search_memory.py --all-projects --query "autenticación"
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
    get_memory_dir,
    parse_memory,
    search_text
)


def search_in_project(project, query, limit=5, memory_type=None):
    """
    Buscar memorias en un proyecto específico.

    Args:
        project (str): Nombre del proyecto
        query (str): Texto a buscar
        limit (int): Número máximo de resultados
        memory_type (str, optional): Filtrar por tipo

    Returns:
        list: Lista de memorias encontradas
    """
    memory_dir = get_memory_dir(project)

    if not memory_dir.exists():
        return []

    results = []

    # Buscar en todos los archivos .md
    for file_path in memory_dir.glob('*.md'):
        memory = parse_memory(file_path)

        if not memory:
            continue

        frontmatter = memory['frontmatter']
        content = memory['content']

        # Filtrar por tipo si se especificó
        if memory_type and frontmatter.get('type', '') != memory_type:
            continue

        # Buscar en título
        title = frontmatter.get('title', '')
        title_match = query.lower() in title.lower()

        # Buscar en contenido
        content_match, matching_lines = search_text(query, content)

        if title_match or content_match:
            # Crear snippet
            if matching_lines:
                snippet_lines = matching_lines[:3]  # Primeras 3 líneas coincidentes
                snippet = '\n'.join([f"  L{line_num}: {line}" for line_num, line in snippet_lines])
            else:
                # Si solo coincidió en título, mostrar primeras líneas del contenido
                content_lines = content.split('\n')[:3]
                snippet = '\n'.join([f"  {line}" for line in content_lines if line.strip()])

            result = {
                'project': project,
                'file': file_path.name,
                'path': str(file_path),
                'title': title,
                'date': frontmatter.get('date', ''),
                'type': frontmatter.get('type', ''),
                'status': frontmatter.get('status', ''),
                'snippet': snippet,
                'relevance': 2 if title_match else 1  # Mayor relevancia si coincide en título
            }

            results.append(result)

    # Ordenar por relevancia (descendente)
    results.sort(key=lambda x: x['relevance'], reverse=True)

    # Limitar resultados
    return results[:limit]


def search_all_projects(query, limit=5, memory_type=None):
    """
    Buscar memorias en todos los proyectos.

    Args:
        query (str): Texto a buscar
        limit (int): Número máximo de resultados
        memory_type (str, optional): Filtrar por tipo

    Returns:
        list: Lista de memorias encontradas
    """
    # Detectar OS y obtener ruta base
    if sys.platform == 'win32':
        home = Path(os.environ.get('USERPROFILE', os.path.expanduser('~')))
    else:
        home = Path.home()

    memory_base = home / 'Documents' / 'brain-agm'

    if not memory_base.exists():
        return []

    all_results = []

    # Buscar en cada proyecto
    for project_dir in memory_base.iterdir():
        if project_dir.is_dir():
            project_name = project_dir.name
            project_results = search_in_project(project_name, query, limit, memory_type)
            all_results.extend(project_results)

    # Ordenar por relevancia
    all_results.sort(key=lambda x: x['relevance'], reverse=True)

    # Limitar resultados
    return all_results[:limit]


def main():
    parser = argparse.ArgumentParser(
        description='Buscar en memorias de brain-agm',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  # Buscar en proyecto actual
  python search_memory.py --query "oauth"

  # Buscar en proyecto específico
  python search_memory.py --project api-backend --query "autenticación"

  # Buscar en todos los proyectos
  python search_memory.py --all-projects --query "decisión"

  # Buscar solo decisiones
  python search_memory.py --query "auth" --type decision
        """
    )

    parser.add_argument(
        '--project',
        type=str,
        default=None,
        help='Nombre del proyecto (default: detectado del directorio actual)'
    )

    parser.add_argument(
        '--all-projects',
        action='store_true',
        help='Buscar en todos los proyectos (usar SOLO cuando usuario lo pida explícitamente)'
    )

    parser.add_argument(
        '--query',
        type=str,
        required=True,
        help='Texto a buscar'
    )

    parser.add_argument(
        '--limit',
        type=int,
        default=5,
        help='Número máximo de resultados (default: 5)'
    )

    parser.add_argument(
        '--type',
        type=str,
        choices=['plan', 'decision', 'problem', 'user-request'],
        default=None,
        help='Filtrar por tipo de memoria'
    )

    args = parser.parse_args()

    # Buscar
    if args.all_projects:
        results = search_all_projects(
            query=args.query,
            limit=args.limit,
            memory_type=args.type
        )
    else:
        project = args.project if args.project else get_project_name()
        results = search_in_project(
            project=project,
            query=args.query,
            limit=args.limit,
            memory_type=args.type
        )

    # Preparar respuesta
    response = {
        'success': True,
        'query': args.query,
        'count': len(results),
        'results': results
    }

    # Imprimir resultado como JSON
    print(json.dumps(response, indent=2))

    sys.exit(0)


if __name__ == '__main__':
    main()
