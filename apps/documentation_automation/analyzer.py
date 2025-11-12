"""
Analyzer - learns from existing READMEs and analyzes new directories
"""

import os
import re
import ast


def extract_similar_readmes(root_path, target_directory, max_count=3):
    """
    Find similar README.md files to use as examples.

    Looks for READMEs in parent and sibling directories.

    Args:
        root_path: Root directory
        target_directory: Directory that needs README
        max_count: Maximum examples to return

    Returns:
        List of (directory_path, readme_content) tuples
    """
    examples = []

    # Try parent directory first
    parent = os.path.dirname(target_directory.rstrip('/'))
    if parent and parent != root_path:
        try:
            for item in os.listdir(parent):
                if len(examples) >= max_count:
                    break
                item_path = os.path.join(parent, item)
                readme_path = os.path.join(item_path, 'README.md')
                if os.path.isdir(item_path) and os.path.isfile(readme_path):
                    try:
                        with open(readme_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            if len(content) > 200:  # Only substantial READMEs
                                examples.append((item_path, content))
                    except (UnicodeDecodeError, IOError):
                        pass
        except (PermissionError, OSError):
            pass

    return examples


def analyze_directory(directory_path):
    """
    Analyze a directory to extract relevant information.

    Args:
        directory_path: Path to analyze

    Returns:
        Dictionary with directory information
    """
    analysis = {
        'path': directory_path,
        'name': os.path.basename(directory_path.rstrip('/')),
        'python_files': [],
        'classes': [],
        'functions': [],
        'docstring': None,
        'directory_type': 'generic',
    }

    # Find Python files
    try:
        for root, dirs, files in os.walk(directory_path):
            # Skip common non-code directories
            dirs[:] = [d for d in dirs if d not in ['__pycache__', '.git', 'migrations', 'node_modules']]

            for file in files:
                if file.endswith('.py') and not file.startswith('.'):
                    filepath = os.path.join(root, file)
                    analysis['python_files'].append(filepath)

                    # Analyze this Python file
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            content = f.read()
                            tree = ast.parse(content)

                            # Get module docstring
                            if not analysis['docstring']:
                                analysis['docstring'] = ast.get_docstring(tree)

                            # Extract classes and functions
                            for node in ast.walk(tree):
                                if isinstance(node, ast.ClassDef):
                                    analysis['classes'].append({
                                        'name': node.name,
                                        'doc': ast.get_docstring(node),
                                    })
                                elif isinstance(node, ast.FunctionDef) and node.col_offset == 0:
                                    analysis['functions'].append({
                                        'name': node.name,
                                        'doc': ast.get_docstring(node),
                                    })
                    except (SyntaxError, UnicodeDecodeError):
                        pass

    except (PermissionError, OSError):
        pass

    # Determine directory type
    analysis['directory_type'] = _determine_directory_type(directory_path, analysis)

    # Limit to first 10 of each
    analysis['classes'] = analysis['classes'][:10]
    analysis['functions'] = analysis['functions'][:10]
    analysis['python_files'] = analysis['python_files'][:20]

    return analysis


def _determine_directory_type(directory_path, analysis):
    """Determine what type of directory this is"""
    dir_contents = set()
    try:
        dir_contents = set(os.listdir(directory_path))
    except (PermissionError, OSError):
        pass

    # Check for Django app
    if 'models.py' in dir_contents or 'views.py' in dir_contents:
        return 'django_app'

    # Check for utility
    if 'utils' in directory_path.lower():
        return 'utility'

    # Check for library
    if 'setup.py' in dir_contents or 'pyproject.toml' in dir_contents:
        return 'library'

    # Check for tests
    if 'test' in directory_path.lower() or 'tests.py' in dir_contents:
        return 'test'

    return 'app'


def format_analysis_for_claude(analysis, examples):
    """
    Format analysis and examples for Claude API prompt.

    Args:
        analysis: Directory analysis dictionary
        examples: List of (path, content) tuples of example READMEs

    Returns:
        Formatted string for Claude
    """
    prompt_parts = []

    # Add example READMEs
    if examples:
        prompt_parts.append("=== EXAMPLE READMEs (use similar structure and style) ===\n")
        for i, (path, content) in enumerate(examples, 1):
            prompt_parts.append(f"Example {i} (from {os.path.basename(path)}):")
            prompt_parts.append(content[:1500])  # First 1500 chars
            prompt_parts.append("\n" + "="*50 + "\n")

    # Add directory analysis
    prompt_parts.append("=== DIRECTORY TO DOCUMENT ===\n")
    prompt_parts.append(f"Directory: {analysis['name']}\n")
    prompt_parts.append(f"Type: {analysis['directory_type']}\n")

    if analysis['docstring']:
        prompt_parts.append(f"Module docstring: {analysis['docstring']}\n")

    if analysis['classes']:
        prompt_parts.append(f"\nClasses ({len(analysis['classes'])}):\n")
        for cls in analysis['classes'][:5]:
            prompt_parts.append(f"  - {cls['name']}")
            if cls['doc']:
                prompt_parts.append(f": {cls['doc'][:100]}")
            prompt_parts.append("\n")

    if analysis['functions']:
        prompt_parts.append(f"\nFunctions ({len(analysis['functions'])}):\n")
        for func in analysis['functions'][:5]:
            prompt_parts.append(f"  - {func['name']}()")
            if func['doc']:
                prompt_parts.append(f": {func['doc'][:100]}")
            prompt_parts.append("\n")

    prompt_parts.append(f"\nTotal Python files: {len(analysis['python_files'])}\n")

    return ''.join(prompt_parts)
