#!/usr/bin/env python3
"""
brain-agm automatic review hook.

Runs on PostToolUse and checks whether 15+ minutes have passed since the last review.
If so, it suggests that the agent check whether there is something important to save.

This hook does NOT save anything automatically; it only SUGGESTS that the agent review.
"""

import json
import sys
import os
from pathlib import Path
from datetime import datetime, timedelta


def get_last_check_file():
    """Get the path of the .last_check file"""
    if sys.platform == 'win32':
        home = Path(os.environ.get('USERPROFILE', os.path.expanduser('~')))
    else:
        home = Path.home()

    check_file = home / '.claude' / 'skills' / 'brain-agm' / '.last_check'
    return check_file


def should_check():
    """Decide whether it is time to review (15+ minutes since the last review)"""
    check_file = get_last_check_file()

    if not check_file.exists():
        return True

    try:
        with open(check_file, 'r') as f:
            last_check_str = f.read().strip()
            last_check = datetime.fromisoformat(last_check_str)

        # Check whether 15+ minutes have passed
        now = datetime.now()
        elapsed = now - last_check
        return elapsed >= timedelta(minutes=15)
    except Exception:
        # If reading fails, assume a review is needed
        return True


def update_last_check():
    """Update the timestamp of the last review"""
    check_file = get_last_check_file()

    # Create the directory if it does not exist
    check_file.parent.mkdir(parents=True, exist_ok=True)

    # Write the current timestamp
    now = datetime.now()
    with open(check_file, 'w') as f:
        f.write(now.isoformat())


def analyze_context(input_data):
    """
    Analyze the context of the executed tool to detect important moments.

    Args:
        input_data (dict): Hook data

    Returns:
        bool: True if something important is detected
    """
    tool_name = input_data.get('tool_name', '')

    # Detect a closed plan
    if 'plan' in tool_name.lower() or 'exit' in tool_name.lower():
        return True

    # Detect significant changes
    if tool_name in ['Edit', 'Write', 'MultiEdit']:
        # If multiple files or important files were edited
        file_path = input_data.get('file_path', '')
        if any(pattern in file_path for pattern in ['.md', 'config', 'README']):
            return True

    # Detect git commits
    if tool_name == 'Bash' or tool_name == 'PowerShell':
        command = input_data.get('command', '')
        if 'git commit' in command or 'git push' in command:
            return True

    return False


def main():
    """Hook entry point"""
    try:
        # Read input from stdin
        input_data = json.load(sys.stdin)

        # Check whether it is time to review
        if not should_check():
            # Less than 15 minutes have passed, do nothing
            sys.exit(0)

        # Check whether there is anything important
        is_important = analyze_context(input_data)

        if is_important:
            # Update timestamp
            update_last_check()

            # Suggest that the agent review
            message = {
                "systemMessage": """
🧠 brain-agm: 15+ minutes have passed since the last memory review.

Consider whether there is anything important to save:
- Was a plan completed or closed?
- Was an important technical decision made?
- Was a complex problem solved?

If there is something important, save it to memory in the appropriate format.
                """.strip()
            }

            print(json.dumps(message), file=sys.stdout)
        else:
            # There is activity but nothing important seems to have happened; wait longer
            pass

        sys.exit(0)

    except Exception as e:
        # On error, do not block the flow
        error_msg = {"systemMessage": f"brain-agm hook error: {e}"}
        print(json.dumps(error_msg), file=sys.stdout)
        sys.exit(0)


if __name__ == '__main__':
    main()
