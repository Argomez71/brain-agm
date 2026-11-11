#!/usr/bin/env python3
"""
Script to save memories in brain-agm.

Usage:
    python save_memory.py --project <name> --type <type> --title <title> --content <file>

Example:
    python save_memory.py --project api-backend --type decision --title "oauth-implementation" --content /tmp/memory.md
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
    ensure_memory_dir,
    validate_frontmatter,
    create_slug,
    get_date,
    get_timestamp
)


def save_memory(project, memory_type, title, content_file, tags=None):
    """
    Save a memory in the system.

    Args:
        project (str): Project name
        memory_type (str): Memory type (plan|decision|problem|user-request)
        title (str): Memory title
        content_file (str): Path to the file with the content
        tags (list, optional): List of tags

    Returns:
        dict: Result with success, file_path and message
    """
    # Validate type
    valid_types = ['plan', 'decision', 'problem', 'user-request']
    if memory_type not in valid_types:
        return {
            'success': False,
            'message': f"Invalid type. Must be one of: {', '.join(valid_types)}"
        }

    # Read content
    content_path = Path(content_file)
    if not content_path.exists():
        return {
            'success': False,
            'message': f"Content file not found: {content_file}"
        }

    try:
        with open(content_path, 'r', encoding='utf-8') as f:
            content_body = f.read()
    except Exception as e:
        return {
            'success': False,
            'message': f"Error reading content file: {e}"
        }

    # Create slug from title
    slug = create_slug(title)
    if not slug:
        return {
            'success': False,
            'message': "Invalid title (could not create slug)"
        }

    # Make sure the directory exists
    memory_dir = ensure_memory_dir(project)

    # Create a unique file name
    timestamp = get_timestamp().replace(':', '-').replace('T', '_')
    filename = f"{slug}_{timestamp}.md"
    file_path = memory_dir / filename

    # Build frontmatter
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

    # Combine frontmatter + content
    full_content = frontmatter + content_body

    # Validate format
    is_valid, error_msg = validate_frontmatter(full_content)
    if not is_valid:
        return {
            'success': False,
            'message': f"Format validation failed: {error_msg}"
        }

    # Write file
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(full_content)
    except Exception as e:
        return {
            'success': False,
            'message': f"Error writing file: {e}"
        }

    return {
        'success': True,
        'file_path': str(file_path),
        'project': project,
        'title': slug,
        'message': f"Memory saved successfully at {file_path}"
    }


def main():
    parser = argparse.ArgumentParser(
        description='Save a memory in brain-agm',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Example:
  python save_memory.py --project api-backend --type decision \\
    --title "OAuth Implementation" --content /tmp/memory-content.md

Valid types: plan, decision, problem, user-request
        """
    )

    parser.add_argument(
        '--project',
        type=str,
        default=None,
        help='Project name (default: detected from the current directory)'
    )

    parser.add_argument(
        '--type',
        type=str,
        required=True,
        choices=['plan', 'decision', 'problem', 'user-request'],
        help='Memory type'
    )

    parser.add_argument(
        '--title',
        type=str,
        required=True,
        help='Memory title'
    )

    parser.add_argument(
        '--content',
        type=str,
        required=True,
        help='Path to the file with the memory content'
    )

    parser.add_argument(
        '--tags',
        type=str,
        default=None,
        help='Comma-separated tags (e.g. "auth,oauth,security")'
    )

    args = parser.parse_args()

    # Detect the project if not specified
    project = args.project if args.project else get_project_name()

    # Parse tags
    tags = args.tags.split(',') if args.tags else None
    if tags:
        tags = [tag.strip() for tag in tags]

    # Save memory
    result = save_memory(
        project=project,
        memory_type=args.type,
        title=args.title,
        content_file=args.content,
        tags=tags
    )

    # Print result as JSON
    print(json.dumps(result, indent=2))

    # Exit code
    sys.exit(0 if result['success'] else 1)


if __name__ == '__main__':
    main()
