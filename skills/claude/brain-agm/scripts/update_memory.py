#!/usr/bin/env python3
"""
Script to update existing memories in brain-agm.

Usage:
    python update_memory.py --project <name> --file <file> [options]

Example:
    python update_memory.py --project api-backend --file oauth-impl.md --status archived
    python update_memory.py --project api-backend --file oauth-impl.md --content /tmp/update.md --append
"""

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime

# Import utilities
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
    Update an existing memory.

    Args:
        project (str): Project name
        filename (str): Memory file name
        new_title (str, optional): New title
        new_status (str, optional): New status
        content_file (str, optional): File with the new content
        append (bool): If True, append content instead of replacing it
        new_tags (list, optional): New tags

    Returns:
        dict: Result with success, file_path and message
    """
    memory_dir = get_memory_dir(project)
    file_path = memory_dir / filename

    # Check that the file exists
    if not file_path.exists():
        return {
            'success': False,
            'message': f"File not found: {file_path}"
        }

    # Read existing memory
    memory = parse_memory(file_path)
    if not memory:
        return {
            'success': False,
            'message': f"Could not parse memory: {file_path}"
        }

    frontmatter = memory['frontmatter']
    content = memory['content']

    # Update frontmatter
    updated = False

    if new_title:
        frontmatter['title'] = new_title
        updated = True

    if new_status:
        valid_statuses = ['completed', 'in-progress', 'archived']
        if new_status not in valid_statuses:
            return {
                'success': False,
                'message': f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
            }
        frontmatter['status'] = new_status
        updated = True

    if new_tags:
        frontmatter['tags'] = json.dumps(new_tags)
        updated = True

    # Update content
    if content_file:
        content_path = Path(content_file)
        if not content_path.exists():
            return {
                'success': False,
                'message': f"Content file not found: {content_file}"
            }

        try:
            with open(content_path, 'r', encoding='utf-8') as f:
                new_content = f.read()
        except Exception as e:
            return {
                'success': False,
                'message': f"Error reading content: {e}"
            }

        if append:
            # Add an update note
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            content = f"{content}\n\n---\n**Updated**: {timestamp}\n\n{new_content}"
        else:
            content = new_content

        updated = True

    if not updated:
        return {
            'success': False,
            'message': "No changes specified to update"
        }

    # Build the new file
    frontmatter_lines = ['---']
    for key, value in frontmatter.items():
        frontmatter_lines.append(f"{key}: {value}")
    frontmatter_lines.append('---')
    frontmatter_text = '\n'.join(frontmatter_lines)

    full_content = f"{frontmatter_text}\n\n{content}"

    # Validate format
    is_valid, error_msg = validate_frontmatter(full_content)
    if not is_valid:
        return {
            'success': False,
            'message': f"Validation failed: {error_msg}"
        }

    # Create backup
    backup_path = file_path.with_suffix('.md.backup')
    try:
        import shutil
        shutil.copy2(file_path, backup_path)
    except Exception as e:
        return {
            'success': False,
            'message': f"Error creating backup: {e}"
        }

    # Write updated file
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(full_content)
    except Exception as e:
        # Restore backup if writing fails
        try:
            import shutil
            shutil.copy2(backup_path, file_path)
        except:
            pass
        return {
            'success': False,
            'message': f"Error writing file: {e}"
        }

    # Delete backup if everything went well
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
        'message': f"Memory updated successfully: {file_path}"
    }


def main():
    parser = argparse.ArgumentParser(
        description='Update an existing memory in brain-agm',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Change status to archived
  python update_memory.py --project api-backend --file oauth-impl.md --status archived

  # Update content (replace)
  python update_memory.py --project api-backend --file oauth-impl.md --content /tmp/update.md

  # Append content
  python update_memory.py --project api-backend --file oauth-impl.md --content /tmp/update.md --append

  # Change title and tags
  python update_memory.py --project api-backend --file oauth-impl.md \\
    --title "new-title" --tags "tag1,tag2"
        """
    )

    parser.add_argument(
        '--project',
        type=str,
        default=None,
        help='Project name (default: detected from the current directory)'
    )

    parser.add_argument(
        '--file',
        type=str,
        required=True,
        help='Name of the memory file to update'
    )

    parser.add_argument(
        '--title',
        type=str,
        default=None,
        help='New title'
    )

    parser.add_argument(
        '--status',
        type=str,
        choices=['completed', 'in-progress', 'archived'],
        default=None,
        help='New status'
    )

    parser.add_argument(
        '--content',
        type=str,
        default=None,
        help='Path to a file with the new content'
    )

    parser.add_argument(
        '--append',
        action='store_true',
        help='Append content instead of replacing it'
    )

    parser.add_argument(
        '--tags',
        type=str,
        default=None,
        help='New comma-separated tags'
    )

    args = parser.parse_args()

    # Detect the project if not specified
    project = args.project if args.project else get_project_name()

    # Parse tags
    tags = args.tags.split(',') if args.tags else None
    if tags:
        tags = [tag.strip() for tag in tags]

    # Update memory
    result = update_memory(
        project=project,
        filename=args.file,
        new_title=args.title,
        new_status=args.status,
        content_file=args.content,
        append=args.append,
        new_tags=tags
    )

    # Print result as JSON
    print(json.dumps(result, indent=2))

    # Exit code
    sys.exit(0 if result['success'] else 1)


if __name__ == '__main__':
    main()
