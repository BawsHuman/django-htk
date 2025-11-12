"""
Simple README detector - finds directories without README.md files
"""

import os


def find_directories_without_readme(root_path, max_depth=4, ignore_patterns=None):
    """
    Find all directories missing README.md files.

    Args:
        root_path: Root directory to scan
        max_depth: Maximum directory depth to scan
        ignore_patterns: List of patterns to ignore (default: migrations, __pycache__, .git, etc)

    Returns:
        List of directory paths that need README.md files
    """
    if ignore_patterns is None:
        ignore_patterns = [
            'migrations', '__pycache__', '.git', '.venv', 'venv',
            'node_modules', 'build', 'dist', '.egg-info', '.pytest_cache'
        ]

    missing_readme_dirs = []

    def should_ignore(path):
        for pattern in ignore_patterns:
            if pattern in path:
                return True
        return False

    def is_code_directory(directory):
        """Check if directory contains Python code"""
        try:
            for item in os.listdir(directory):
                if item.endswith('.py'):
                    return True
        except (PermissionError, OSError):
            pass
        return False

    def scan(directory, depth):
        if depth > max_depth or should_ignore(directory):
            return

        # Check if README exists
        readme_path = os.path.join(directory, 'README.md')
        if os.path.isdir(directory) and not os.path.isfile(readme_path):
            if is_code_directory(directory):
                missing_readme_dirs.append(directory)

        # Scan subdirectories
        try:
            for item in os.listdir(directory):
                if not item.startswith('.'):
                    item_path = os.path.join(directory, item)
                    if os.path.isdir(item_path):
                        scan(item_path, depth + 1)
        except (PermissionError, OSError):
            pass

    scan(root_path, 0)
    return sorted(missing_readme_dirs)
