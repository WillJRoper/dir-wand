# Development Setup

This guide will help you set up a development environment for WAND.

## Prerequisites

- Python 3.8 or higher
- Git
- pip
- Virtual environment tool (venv, virtualenv, or conda)

## Quick Start

```bash
# Clone repository
git clone https://github.com/WillJRoper/dir-wand.git
cd dir-wand

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode with dev dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install

# Verify installation
dir-wand --help
```

## Detailed Setup

### 1. Clone the Repository

```bash
# HTTPS
git clone https://github.com/WillJRoper/dir-wand.git

# or SSH
git clone git@github.com:WillJRoper/dir-wand.git

cd dir-wand
```

### 2. Create Virtual Environment

Using venv:

```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
```

Using conda:

```bash
conda create -n dir-wand python=3.10
conda activate dir-wand
```

### 3. Install Dependencies

**Development installation:**

```bash
pip install -e ".[dev]"
```

This installs:

- WAND in editable mode (changes reflect immediately)
- Runtime dependencies (pyyaml)
- Development dependencies (ruff)

**Manual installation:**

```bash
# Install WAND in editable mode
pip install -e .

# Install development tools
pip install ruff pre-commit
```

### 4. Configure Pre-commit Hooks

```bash
# Install hooks
pre-commit install

# Test hooks
pre-commit run --all-files
```

Pre-commit will now run Ruff on every commit.

### 5. Verify Installation

```bash
# Check WAND is installed
which dir-wand  # Should show path in your venv

# Check version
pip show dir-wand

# Test basic functionality
mkdir test_{num}
echo "{num}" > test_{num}/file.txt
dir-wand --template test_{num} --num 0-2
```

## Development Tools

### Ruff

Linter and formatter for Python code.

**Configuration:** `pyproject.toml` under `[tool.ruff]`

**Usage:**

```bash
# Check for issues
ruff check src/

# Auto-fix issues
ruff check --fix src/

# Format code
ruff format src/

# Check specific file
ruff check src/dir_wand/template.py
```

### Pre-commit

Runs checks before each commit.

**Configuration:** `.pre-commit-config.yaml` (create if needed)

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.3.0
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
```

**Usage:**

```bash
# Install hooks
pre-commit install

# Run manually
pre-commit run --all-files

# Update hooks
pre-commit autoupdate
```

## Project Structure

```
dir-wand/
├── src/
│   └── dir_wand/          # Source code
│       ├── __init__.py
│       ├── main.py         # Entry point
│       ├── parser.py
│       ├── template.py
│       ├── directory.py
│       ├── file.py
│       ├── command_runner.py
│       ├── logger.py
│       ├── swapfile.py
│       ├── utils.py
│       └── art.py
├── docs/                   # Documentation (MkDocs)
│   ├── index.md
│   ├── api/
│   ├── guides/
│   ├── examples/
│   └── developer/
├── pyproject.toml          # Project configuration
├── LICENSE
├── README.md
└── mkdocs.yml             # Documentation config
```

## Documentation Development

### MkDocs

Documentation is built with MkDocs Material.

**Install dependencies:**

```bash
pip install mkdocs-material mkdocstrings[python] pymdown-extensions
```

**Local development:**

```bash
# Serve documentation locally
mkdocs serve

# Open http://127.0.0.1:8000 in browser
# Auto-reloads on changes
```

**Build documentation:**

```bash
# Build static site
mkdocs build

# Output in site/ directory
```

**Deploy documentation:**

```bash
# Deploy to GitHub Pages
mkdocs gh-deploy
```

## Testing

### Manual Testing

Create test templates and run WAND:

```bash
# Create test directory
mkdir -p test_env/template_{num}
echo "Test {num}" > test_env/template_{num}/file.txt

cd test_env

# Test basic functionality
dir-wand --template template_{num} --num 0-5

# Test multiple placeholders
dir-wand --template exp_{id}_{seed} --id 0-2 --seed 42-44

# Test commands
dir-wand --template job_{id} --id 0-3 --run "echo 'Job {id}'"

# Test swapfiles
cat > test.yaml << EOF
num:
  range: 0-5
EOF
dir-wand --template template_{num} --swapfile test.yaml

# Clean up
cd ..
rm -rf test_env
```

### Testing Checklist

When testing changes:

- [ ] Basic template copying works
- [ ] Multiple placeholders work
- [ ] Swapfiles work
- [ ] Command execution works
- [ ] Edge cases handled (empty directories, binary files, symlinks)
- [ ] Error messages are clear
- [ ] Silent mode works
- [ ] Help text is accurate

## Common Development Tasks

### Adding a New Feature

1. **Create branch:**
   ```bash
   git checkout -b feature/new-feature
   ```

2. **Implement feature:**
   - Edit appropriate module in `src/dir_wand/`
   - Follow code style guidelines

3. **Update documentation:**
   - Add to relevant files in `docs/`
   - Update API reference if needed

4. **Test:**
   ```bash
   ruff check src/
   # Manual testing
   ```

5. **Commit:**
   ```bash
   git add .
   git commit -m "Add feature: description"
   ```

### Debugging

**Print debugging:**

```python
# In source code
print(f"DEBUG: variable = {variable}", file=sys.stderr)
```

**Run with Python debugger:**

```bash
python -m pdb -m dir_wand.main --template test_{num} --num 0-2
```

**Check logs:**

```bash
# With logging enabled
dir-wand --template test_{num} --num 0-2 2>&1 | tee debug.log
```

### Updating Dependencies

```bash
# Update all dependencies
pip install --upgrade -e ".[dev]"

# Update specific package
pip install --upgrade ruff

# List installed packages
pip list
```

## Troubleshooting

### Import Errors

```bash
# Ensure WAND is installed in editable mode
pip install -e .

# Verify import works
python -c "from dir_wand import main"
```

### Ruff Not Found

```bash
# Install ruff
pip install ruff

# Verify installation
ruff --version
```

### Pre-commit Issues

```bash
# Reinstall hooks
pre-commit uninstall
pre-commit install

# Clear cache
pre-commit clean
```

### Module Not Found

```bash
# Check PYTHONPATH
echo $PYTHONPATH

# Reinstall in editable mode
pip uninstall dir-wand
pip install -e .
```

## IDE Setup

### VS Code

**Recommended extensions:**

- Python (Microsoft)
- Ruff (Astral Software)

**Settings (`.vscode/settings.json`):**

```json
{
  "python.linting.enabled": true,
  "python.linting.ruffEnabled": true,
  "python.formatting.provider": "none",
  "[python]": {
    "editor.defaultFormatter": "charliermarsh.ruff",
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
      "source.organizeImports": true
    }
  },
  "python.analysis.typeCheckingMode": "basic"
}
```

### PyCharm

**Setup:**

1. Open project directory
2. Configure Python interpreter (point to venv)
3. Enable Ruff:
   - Settings → Tools → External Tools → Add Ruff
   - Command: `ruff check --fix $FilePath$`

## Next Steps

- Read the [Architecture Overview](architecture.md)
- Review [Contributing Guidelines](contributing.md)
- Check out the [API Reference](../api/template.md)

## Getting Help

- **Issues:** [GitHub Issues](https://github.com/WillJRoper/dir-wand/issues)
- **Discussions:** [GitHub Discussions](https://github.com/WillJRoper/dir-wand/discussions)
