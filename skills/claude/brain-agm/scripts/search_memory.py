#!/usr/bin/env python3
"""
Script to search brain-agm memories.

Usage:
    python search_memory.py --project <name> --query <text>
    python search_memory.py --all-projects --query <text>

Example:
    python search_memory.py --project api-backend --query "oauth"
    python search_memory.py --all-projects --query "authentication"
"""

import argparse
import json
import sys
from pathlib import Path

# Import utilities
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
    Search memories in a specific project.

    Args:
        project (str): Project name
        query (str): Text to search for
        limit (int): Maximum number of results
        memory_type (str, optional): Filter by type

    Returns:
        list: List of memories found
    """
    memory_dir = get_memory_dir(project)

    if not memory_dir.exists():
        return []

    results = []

    # Search all .md files
    for file_path in memory_dir.glob('*.md'):
        memory = parse_memory(file_path)

        if not memory:
            continue

        frontmatter = memory['frontmatter']
        content = memory['content']

        # Filter by type if specified
        if memory_type and frontmatter.get('type', '') != memory_type:
            continue

        # Search the title
        title = frontmatter.get('title', '')
        title_match = query.lower() in title.lower()

        # Search the content
        content_match, matching_lines = search_text(query, content)

        if title_match or content_match:
            # Build snippet
            if matching_lines:
                snippet_lines = matching_lines[:3]  # First 3 matching lines
                snippet = '\n'.join([f"  L{line_num}: {line}" for line_num, line in snippet_lines])
            else:
                # If it only matched the title, show the first content lines
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
                'relevance': 2 if title_match else 1  # Higher relevance for title matches
            }

            results.append(result)

    # Sort by relevance (descending)
    results.sort(key=lambda x: x['relevance'], reverse=True)

    # Limit results
    return results[:limit]


def search_all_projects(query, limit=5, memory_type=None):
    """
    Search memories across all projects.

    Args:
        query (str): Text to search for
        limit (int): Maximum number of results
        memory_type (str, optional): Filter by type

    Returns:
        list: List of memories found
    """
    # Detect OS and get the base path
    if sys.platform == 'win32':
        home = Path(os.environ.get('USERPROFILE', os.path.expanduser('~')))
    else:
        home = Path.home()

    memory_base = home / 'Documents' / 'brain-agm'

    if not memory_base.exists():
        return []

    all_results = []

    # Search each project
    for project_dir in memory_base.iterdir():
        if project_dir.is_dir():
            project_name = project_dir.name
            project_results = search_in_project(project_name, query, limit, memory_type)
            all_results.extend(project_results)

    # Sort by relevance
    all_results.sort(key=lambda x: x['relevance'], reverse=True)

    # Limit results
    return all_results[:limit]


def main():
    parser = argparse.ArgumentParser(
        description='Search brain-agm memories',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Search the current project
  python search_memory.py --query "oauth"

  # Search a specific project
  python search_memory.py --project api-backend --query "authentication"

  # Search all projects
  python search_memory.py --all-projects --query "decision"

  # Search only decisions
  python search_memory.py --query "auth" --type decision
        """
    )

    parser.add_argument(
        '--project',
        type=str,
        default=None,
        help='Project name (default: detected from the current directory)'
    )

    parser.add_argument(
        '--all-projects',
        action='store_true',
        help='Search all projects (use ONLY when the user explicitly asks)'
    )

    parser.add_argument(
        '--query',
        type=str,
        required=True,
        help='Text to search for'
    )

    parser.add_argument(
        '--limit',
        type=int,
        default=5,
        help='Maximum number of results (default: 5)'
    )

    parser.add_argument(
        '--type',
        type=str,
        choices=['plan', 'decision', 'problem', 'user-request'],
        default=None,
        help='Filter by memory type'
    )

    args = parser.parse_args()

    # Search
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

    # Build response
    response = {
        'success': True,
        'query': args.query,
        'count': len(results),
        'results': results
    }

    # Print result as JSON
    print(json.dumps(response, indent=2))

    sys.exit(0)


if __name__ == '__main__':
    main()
