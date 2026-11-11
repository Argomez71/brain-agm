#!/usr/bin/env python3
"""
Shared utilities for brain-agm.
Functions to detect the project, validate memories and search text.
"""

import os
import sys
import re
from pathlib import Path
from datetime import datetime


def get_project_name():
    """
    Get the current project name from the working directory.

    Returns:
        str: Project name (current directory name)
    """
    cwd = os.getcwd()
    project_name = os.path.basename(cwd)

    # Clean the name so it can be used as a folder name
    project_name = re.sub(r'[^\w\s-]', '', project_name)
    project_name = re.sub(r'[-\s]+', '-', project_name)

    return project_name.lower()


def get_memory_dir(project=None):
    """
    Get the memory directory path.

    Args:
        project (str, optional): Project name. If not given, uses the current project.

    Returns:
        Path: Path to the project's memory directory
    """
    if project is None:
        project = get_project_name()

    # Detect OS and use the appropriate path
    if sys.platform == 'win32':
        home = Path(os.environ.get('USERPROFILE', os.path.expanduser('~')))
    else:
        home = Path.home()

    memory_base = home / 'Documents' / 'brain-agm'
    memory_dir = memory_base / project

    return memory_dir


def ensure_memory_dir(project=None):
    """
    Make sure the memory directory exists, creating it if needed.

    Args:
        project (str, optional): Project name

    Returns:
        Path: Path to the memory directory
    """
    memory_dir = get_memory_dir(project)
    memory_dir.mkdir(parents=True, exist_ok=True)
    return memory_dir


def validate_frontmatter(content):
    """
    Validate that the content has valid frontmatter.

    Args:
        content (str): Content of the memory file

    Returns:
        tuple: (bool, str) - (is_valid, error_message)
    """
    lines = content.strip().split('\n')

    # Must start with ---
    if not lines or lines[0].strip() != '---':
        return False, "Frontmatter must start with '---'"

    # Find the closing frontmatter delimiter
    end_idx = -1
    for i in range(1, len(lines)):
        if lines[i].strip() == '---':
            end_idx = i
            break

    if end_idx == -1:
        return False, "Frontmatter is not closed with '---'"

    # Validate required frontmatter fields
    frontmatter = '\n'.join(lines[1:end_idx])
    required_fields = ['title:', 'date:', 'project:', 'type:']

    for field in required_fields:
        if field not in frontmatter:
            return False, f"Required field '{field.rstrip(':')}' not found in frontmatter"

    return True, ""


def parse_memory(file_path):
    """
    Parse a memory file.

    Args:
        file_path (Path or str): Path to the memory file

    Returns:
        dict: Dictionary with 'frontmatter' (dict) and 'content' (str).
              Returns None if the file does not exist or is invalid.
    """
    file_path = Path(file_path)

    if not file_path.exists():
        return None

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading file: {e}", file=sys.stderr)
        return None

    lines = content.split('\n')

    # Look for frontmatter
    if not lines or lines[0].strip() != '---':
        return None

    end_idx = -1
    for i in range(1, len(lines)):
        if lines[i].strip() == '---':
            end_idx = i
            break

    if end_idx == -1:
        return None

    # Parse frontmatter (simple key: value)
    frontmatter = {}
    for line in lines[1:end_idx]:
        if ':' in line:
            key, value = line.split(':', 1)
            frontmatter[key.strip()] = value.strip()

    # Content after the frontmatter
    body = '\n'.join(lines[end_idx + 1:])

    return {
        'frontmatter': frontmatter,
        'content': body.strip()
    }


def search_text(query, text):
    """
    Simple case-insensitive text search.

    Args:
        query (str): Text to search for
        text (str): Text to search in

    Returns:
        tuple: (bool, list) - (found, list of matching lines)
    """
    query_lower = query.lower()
    text_lower = text.lower()

    if query_lower not in text_lower:
        return False, []

    # Find the lines that contain the query
    lines = text.split('\n')
    matching_lines = []

    for i, line in enumerate(lines):
        if query_lower in line.lower():
            matching_lines.append((i + 1, line.strip()))

    return True, matching_lines


def create_slug(title):
    """
    Create a slug from a title.

    Args:
        title (str): Title to convert

    Returns:
        str: Slug (kebab-case, without special characters)
    """
    # Convert to lowercase
    slug = title.lower()

    # Remove special characters
    slug = re.sub(r'[^\w\s-]', '', slug)

    # Replace spaces and repeated hyphens with a single hyphen
    slug = re.sub(r'[-\s]+', '-', slug)

    # Remove leading and trailing hyphens
    slug = slug.strip('-')

    return slug


def get_timestamp():
    """
    Get the current timestamp in ISO 8601 format.

    Returns:
        str: Timestamp (e.g., "2026-11-05T14:30:00")
    """
    return datetime.now().strftime('%Y-%m-%dT%H:%M:%S')


def get_date():
    """
    Get the current date in YYYY-MM-DD format.

    Returns:
        str: Date (e.g., "2026-11-05")
    """
    return datetime.now().strftime('%Y-%m-%d')


if __name__ == '__main__':
    # Basic checks
    print(f"Current project: {get_project_name()}")
    print(f"Memory directory: {get_memory_dir()}")
    print(f"Slug for 'OAuth 2.0 Implementation': {create_slug('OAuth 2.0 Implementation')}")
    print(f"Current date: {get_date()}")
