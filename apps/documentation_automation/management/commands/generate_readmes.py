"""
Management command: Generate README files for directories without them
"""

import os
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from htk.apps.documentation_automation.generator import ReadmeGenerator
from htk.apps.documentation_automation.detector import find_directories_without_readme


class Command(BaseCommand):
    """Generate README.md files for directories missing them"""

    help = 'Generate README.md files for directories without them'

    def add_arguments(self, parser):
        parser.add_argument(
            '--batch',
            type=int,
            default=10,
            help='Number of directories to process (default: 10)'
        )

        parser.add_argument(
            '--directory',
            type=str,
            help='Generate README for a specific directory'
        )

        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be generated without writing files'
        )

        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Show generated content'
        )

    def handle(self, *args, **options):
        """Execute the command"""

        # Get API key
        api_key = os.environ.get('CLAUDE_API_KEY')
        if not api_key:
            config = getattr(settings, 'DOCUMENTATION_AUTOMATION', {})
            api_key = config.get('CLAUDE_API_KEY')

        if not api_key:
            raise CommandError(
                'CLAUDE_API_KEY not found. Set CLAUDE_API_KEY environment variable '
                'or add to DOCUMENTATION_AUTOMATION settings.'
            )

        # Get root path
        config = getattr(settings, 'DOCUMENTATION_AUTOMATION', {})
        root_path = config.get('ROOT_PATH', os.getcwd())

        # Initialize generator
        generator = ReadmeGenerator(api_key=api_key)

        batch_size = options['batch']
        dry_run = options['dry_run']
        verbose = options['verbose']
        target_directory = options['directory']

        if target_directory:
            # Generate for specific directory
            self._generate_single(generator, target_directory, dry_run, verbose)
        else:
            # Generate for all missing
            self._generate_batch(
                generator, root_path, batch_size, dry_run, verbose
            )

    def _generate_single(self, generator, directory_path, dry_run, verbose):
        """Generate for a single directory"""

        self.stdout.write(f'\nGenerating README for: {directory_path}')

        result = generator.generate_for_directory(directory_path, dry_run=dry_run)

        if result['success']:
            self.stdout.write(
                self.style.SUCCESS(f'✓ Successfully generated README')
            )
            if verbose and result['content']:
                self.stdout.write('\n' + '=' * 60)
                self.stdout.write(result['content'][:500] + '...\n')
                self.stdout.write('=' * 60)
        else:
            self.stdout.write(
                self.style.ERROR(f"✗ Error: {result['error']}")
            )

    def _generate_batch(self, generator, root_path, batch_size, dry_run, verbose):
        """Generate for batch of directories"""

        # Find missing
        missing_dirs = find_directories_without_readme(root_path)
        missing_dirs = missing_dirs[:batch_size]

        if not missing_dirs:
            self.stdout.write(self.style.SUCCESS('✓ All directories have README files!'))
            return

        self.stdout.write(
            self.style.WARNING(f'\nFound {len(missing_dirs)} directories without README:\n')
        )

        # Generate for each
        generated = 0
        failed = 0

        for directory in missing_dirs:
            self.stdout.write(f'  Processing: {directory}...')

            result = generator.generate_for_directory(directory, dry_run=dry_run)

            if result['success']:
                self.stdout.write(self.style.SUCCESS('    ✓ Generated'))
                generated += 1
                if verbose and result['content']:
                    self.stdout.write('    Content preview:')
                    for line in result['content'][:300].split('\n')[:5]:
                        self.stdout.write(f'    {line}')
            else:
                self.stdout.write(
                    self.style.ERROR(f"    ✗ Error: {result['error']}")
                )
                failed += 1

        # Summary
        self.stdout.write('\n' + '=' * 60)
        self.stdout.write(f'Generated: {generated}, Failed: {failed}')

        if dry_run:
            self.stdout.write(
                self.style.WARNING('\nNote: This was a dry run. Files were not written.')
            )

        self.stdout.write('=' * 60)
