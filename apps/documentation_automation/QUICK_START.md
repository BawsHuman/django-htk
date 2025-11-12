# Auto README Generation - Quick Start (Manual)

Simple README generation using Claude API. Learns from existing README files and generates new ones for directories missing them.

## ⚡ 2-Minute Setup

### 1. Add to Settings

```python
# settings.py

INSTALLED_APPS = [
    # ...
    'htk.apps.documentation_automation',
]

DOCUMENTATION_AUTOMATION = {
    'BATCH_SIZE': 10,  # Process 10 directories per run
}
```

### 2. Set API Key

```bash
export CLAUDE_API_KEY='sk-ant-...'
```

## 📝 Commands to Generate READMEs

### Generate for All Missing READMEs

```bash
python manage.py generate_readmes --batch 10
```

Finds and generates READMEs for up to 10 directories missing them.

### Generate for Specific Directory

```bash
python manage.py generate_readmes --directory htk/apps/accounts
```

### Preview First (Dry Run)

```bash
python manage.py generate_readmes --batch 5 --dry-run
```

Shows what would be generated without writing files.

### Show Content Preview

```bash
python manage.py generate_readmes --batch 2 --verbose
```

Displays preview of generated README content.

## 🐍 Python API

```python
from htk.apps.documentation_automation.generator import ReadmeGenerator

gen = ReadmeGenerator(api_key='sk-ant-...')

# Generate for all missing (up to 10)
result = gen.generate_for_missing_directories(
    root_path='/path/to/htk',
    max_count=10
)

# Generate for one directory
result = gen.generate_for_directory('path/to/new_directory')

print(f"Generated: {result['success']}")
print(f"Content: {result['content'][:200]}")
```

## How It Works

1. **Finds** directories without README.md
2. **Learns** from 3 similar existing READMEs in parent/sibling directories
3. **Analyzes** target directory (classes, functions, purpose)
4. **Generates** using Claude based on examples + analysis
5. **Writes** to `directory/README.md`

## Features

✅ Learns from your existing README structure and style
✅ Analyzes actual code (not just placeholders)
✅ Uses Claude API for intelligent generation
✅ Depth-first approach (matches existing patterns)
✅ Manual on-demand generation
✅ Dry-run mode to preview before writing

## Cost

- **Per README**: $0.01-0.02
- **10 directories**: ~$0.10-0.20
- **Monthly**: ~$4-8

## Files

- `detector.py` - Find missing READMEs
- `analyzer.py` - Learn from examples, analyze code
- `generator.py` - Generate with Claude
- `management/commands/generate_readmes.py` - CLI command

## Next Steps

1. ✅ Set CLAUDE_API_KEY environment variable
2. ✅ Add to INSTALLED_APPS
3. ✅ Run command: `python manage.py generate_readmes --batch 10`
4. ✅ Check generated files

---

See `htk/apps/documentation_automation/README.md` for detailed documentation.
