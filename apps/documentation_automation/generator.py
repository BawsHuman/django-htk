"""
Generator - orchestrates README generation using Claude API
"""

import os
import logging
from .detector import find_directories_without_readme
from .analyzer import extract_similar_readmes, analyze_directory, format_analysis_for_claude

logger = logging.getLogger(__name__)


class ReadmeGenerator:
    """Generate README files using Claude API"""

    def __init__(self, api_key, model='claude-opus-4-1-20250805'):
        """
        Initialize the generator.

        Args:
            api_key: Anthropic API key
            model: Claude model to use
        """
        self.api_key = api_key
        self.model = model
        self.client = None

        # Try to import and initialize anthropic
        try:
            import anthropic
            self.client = anthropic.Anthropic(api_key=api_key)
        except ImportError:
            logger.warning("anthropic library not installed")

    def generate_for_missing_directories(self, root_path, max_count=10, dry_run=False):
        """
        Generate README files for all directories missing them.

        Args:
            root_path: Root directory to scan
            max_count: Maximum directories to process
            dry_run: If True, only show what would be generated

        Returns:
            Dictionary with results
        """
        result = {
            'success': True,
            'generated': [],
            'failed': [],
            'skipped': [],
        }

        # Find directories without README
        missing_dirs = find_directories_without_readme(root_path)
        missing_dirs = missing_dirs[:max_count]

        logger.info(f"Found {len(missing_dirs)} directories without README")

        for directory in missing_dirs:
            gen_result = self.generate_for_directory(directory, dry_run=dry_run)

            if gen_result['success']:
                result['generated'].append(directory)
            else:
                result['failed'].append({
                    'directory': directory,
                    'error': gen_result.get('error'),
                })

        return result

    def generate_for_directory(self, directory_path, dry_run=False):
        """
        Generate README for a specific directory.

        Args:
            directory_path: Path to the directory
            dry_run: If True, only show what would be generated, don't write

        Returns:
            Dictionary with result
        """
        result = {
            'success': False,
            'directory': directory_path,
            'content': None,
            'error': None,
        }

        try:
            if not self.client:
                result['error'] = 'Claude API not configured'
                return result

            # Extract similar READMEs
            root_path = self._find_root(directory_path)
            examples = extract_similar_readmes(root_path, directory_path, max_count=3)

            # Analyze directory
            analysis = analyze_directory(directory_path)

            # Format for Claude
            prompt = self._build_prompt(analysis, examples)

            # Generate with Claude
            logger.info(f"Generating README for {directory_path}")
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            content = response.content[0].text

            if not dry_run:
                # Write to file
                readme_path = os.path.join(directory_path, 'README.md')
                with open(readme_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                logger.info(f"Wrote README to {readme_path}")

            result['success'] = True
            result['content'] = content

        except Exception as e:
            logger.error(f"Error generating README for {directory_path}: {e}")
            result['error'] = str(e)

        return result

    @staticmethod
    def _build_prompt(analysis, examples):
        """Build the Claude prompt"""
        prompt_parts = [
            "Generate a professional README.md file for this directory.",
            "Match the structure and style of the provided examples.\n",
        ]

        # Add examples
        if examples:
            prompt_parts.append("=== EXAMPLE READMEs (match this style and structure) ===\n")
            for path, content in examples:
                dir_name = os.path.basename(path)
                prompt_parts.append(f"\nExample from {dir_name}:")
                prompt_parts.append(content[:1200])  # First 1200 chars
                prompt_parts.append("\n" + "-" * 50)

        # Add analysis
        prompt_parts.append("\n\n=== DIRECTORY TO DOCUMENT ===\n")
        prompt_parts.append(f"Directory: {analysis['name']}\n")
        prompt_parts.append(f"Type: {analysis['directory_type']}\n")

        if analysis['docstring']:
            prompt_parts.append(f"\nPurpose/Docstring: {analysis['docstring']}\n")

        if analysis['classes']:
            prompt_parts.append(f"\nKey Classes ({len(analysis['classes'])}):\n")
            for cls in analysis['classes'][:8]:
                prompt_parts.append(f"  - {cls['name']}")
                if cls['doc']:
                    doc_short = cls['doc'].split('\n')[0][:80]
                    prompt_parts.append(f": {doc_short}")
                prompt_parts.append("\n")

        if analysis['functions']:
            prompt_parts.append(f"\nKey Functions ({len(analysis['functions'])}):\n")
            for func in analysis['functions'][:8]:
                prompt_parts.append(f"  - {func['name']}()")
                if func['doc']:
                    doc_short = func['doc'].split('\n')[0][:80]
                    prompt_parts.append(f": {doc_short}")
                prompt_parts.append("\n")

        prompt_parts.append(f"\nTotal Python files: {len(analysis['python_files'])}\n")

        prompt_parts.append(
            "\nGenerate only the README.md content. "
            "Use the examples as a reference for structure and style. "
            "Include: Purpose, Key Components, Usage, and Related Modules sections."
        )

        return ''.join(prompt_parts)

    @staticmethod
    def _find_root(directory_path):
        """Find the repository root (where .git is or parent of scan start)"""
        current = directory_path
        while current != '/':
            if os.path.isdir(os.path.join(current, '.git')):
                return current
            parent = os.path.dirname(current)
            if parent == current:
                break
            current = parent
        return os.path.dirname(directory_path)
