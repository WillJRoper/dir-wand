# Contributing to WAND

Thank you for your interest in contributing to WAND! This guide will help you get started.

## Code of Conduct

Be respectful, inclusive, and constructive in all interactions.

## How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported in [Issues](https://github.com/WillJRoper/dir-wand/issues)
2. If not, create a new issue with:
   - Clear title and description
   - Steps to reproduce
   - Expected vs actual behavior
   - WAND version (`pip show dir-wand`)
   - Python version
   - Operating system

**Example:**

```markdown
## Bug: Placeholder not replaced in binary files

**Description:**
Placeholders in PNG files are not being replaced.

**Steps to Reproduce:**
1. Create template with image_{num}.png
2. Run: dir-wand --template image_{num} --num 0-5
3. Observe that {num} remains in filename

**Expected:**
File named image_0.png, image_1.png, etc.

**Actual:**
File remains named image_{num}.png

**Environment:**
- WAND version: 1.0.0
- Python: 3.10.5
- OS: Ubuntu 22.04
```

### Suggesting Features

1. Check [existing issues](https://github.com/WillJRoper/dir-wand/issues) for similar requests
2. Create a new issue with:
   - Clear use case
   - Proposed solution (if you have one)
   - Why this benefits WAND users

### Contributing Code

#### 1. Fork and Clone

```bash
# Fork on GitHub, then:
git clone https://github.com/YOUR_USERNAME/dir-wand.git
cd dir-wand
```

#### 2. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

#### 3. Set Up Development Environment

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

#### 4. Make Changes

Follow the [Development Guidelines](#development-guidelines) below.

#### 5. Test Your Changes

```bash
# Run linter
ruff check src/

# Format code
ruff format src/

# Test manually
dir-wand --template test_{num} --num 0-2
```

#### 6. Commit Your Changes

```bash
git add .
git commit -m "Add feature: brief description"
```

**Commit Message Guidelines:**

- Use imperative mood ("Add feature" not "Added feature")
- First line: brief summary (50 chars max)
- Blank line, then detailed description if needed

**Examples:**

```
Add support for JSON swapfiles

Extend swapfile parsing to support JSON format in addition to YAML.
This allows users to use either format based on preference.
```

```
Fix placeholder replacement in softlinks

Symbolic links were incorrectly having their targets modified.
Now symlinks are preserved correctly as per the original implementation.
```

#### 7. Push and Create Pull Request

```bash
git push origin feature/your-feature-name
```

Then create a pull request on GitHub.

## Development Guidelines

### Code Style

WAND uses [Ruff](https://github.com/astral-sh/ruff) for linting and formatting.

**Configuration:** See `[tool.ruff]` in `pyproject.toml`

**Run Ruff:**

```bash
# Check for issues
ruff check src/

# Auto-fix issues
ruff check --fix src/

# Format code
ruff format src/
```

**Key Style Points:**

- Line length: 79 characters (PEP-8)
- Indentation: 4 spaces
- Quotes: Double quotes for strings
- Imports: Alphabetically sorted

### Documentation

All public functions, classes, and modules should have docstrings.

**Function Docstring Format:**

```python
def swap_in_str(string, **swaps):
    """
    Replace placeholders in a string with their corresponding values.

    Args:
        string (str): The string containing placeholders in {name} format.
        **swaps: Keyword arguments mapping placeholder names to values.

    Returns:
        str: The string with all placeholders replaced.

    Raises:
        ValueError: If required placeholders are missing from swaps.

    Example:
        >>> swap_in_str("exp_{num}", num=42)
        'exp_42'
    ```python
"""
    # Implementation
```

**Class Docstring Format:**

```python
class Directory:
    """
    A class for defining the directory.

    A directory is a tree structure containing files and other directories.

    Attributes:
        path (str): The path to the directory.
        children (list): A list of child directories.
        files (list): A list of files in the directory.
    """
```

### Testing

While WAND doesn't currently have a formal test suite, manual testing is important:

**Test Checklist:**

- [ ] Basic functionality works
- [ ] Edge cases handled
- [ ] Error messages are clear
- [ ] No regressions in existing features

**Manual Test Examples:**

```bash
# Basic template copying
mkdir test_{num}
echo "{num}" > test_{num}/file.txt
dir-wand --template test_{num} --num 0-5

# Multiple placeholders
dir-wand --template exp_{id}_{seed} --id 0-2 --seed 42-44

# Command execution
dir-wand --template job_{id} --id 0-3 --run "cd job_{id} && ls"

# Swapfiles
cat > test.yaml << EOF
num:
  range: 0-5
EOF
dir-wand --template test_{num} --swapfile test.yaml

# Edge cases
dir-wand --template test --num   # Should error
dir-wand --template test_{a}_{b} --a 0-2 --b 0-3  # Should error (mismatch)
```

### Project Structure

```
dir-wand/
├── src/
│   └── dir_wand/
│       ├── main.py          # Entry point
│       ├── parser.py        # Argument parsing
│       ├── template.py      # Template controller
│       ├── directory.py     # Directory tree
│       ├── file.py          # File handling
│       ├── command_runner.py # Command execution
│       ├── logger.py        # Logging/reporting
│       ├── swapfile.py      # Swapfile generation
│       ├── utils.py         # Utilities
│       └── art.py           # ASCII art
├── docs/                    # Documentation (MkDocs)
├── pyproject.toml          # Project configuration
├── README.md               # Project README
└── LICENSE                 # GPL-3.0 license
```

### Adding New Features

When adding a new feature:

1. **Consider the API:**
   - Is it backward compatible?
   - Does it fit WAND's design philosophy?
   - Is the interface intuitive?

2. **Update documentation:**
   - Add to relevant user guide
   - Update API reference
   - Add examples if appropriate

3. **Consider edge cases:**
   - What if inputs are invalid?
   - What if files don't exist?
   - What about empty inputs?

**Example: Adding a new value format**

If adding support for arithmetic sequences:

```python
# In parser.py
def parse_swaps(**swaps):
    for key, value in swaps.items():
        # Existing checks...

        # New: arithmetic sequence
        elif ":" in value and "-" in value:
            # Format: start-end:step
            parts = value.split(":")
            range_part, step = parts[0], int(parts[1])
            start, end = map(int, range_part.split("-"))
            swaps[key] = list(range(start, end + 1, step))
```

Then:

- Update `parser.md` documentation
- Add example to user guide
- Test edge cases

## Pull Request Process

1. **Ensure your PR:**
   - Has a clear title and description
   - References any related issues
   - Passes Ruff checks
   - Doesn't break existing functionality

2. **PR Description Template:**

   ```markdown
   ## Description
   Brief description of changes

   ## Motivation
   Why is this change needed?

   ## Changes
   - Change 1
   - Change 2

   ## Testing
   How was this tested?

   ## Checklist
   - [ ] Code follows style guidelines
   - [ ] Documentation updated
   - [ ] Manually tested
   - [ ] No breaking changes (or documented if unavoidable)
   ```

3. **Review Process:**
   - Maintainers will review your PR
   - Address any feedback
   - Once approved, PR will be merged

## Development Workflow

```bash
# 1. Start with latest main
git checkout main
git pull upstream main

# 2. Create feature branch
git checkout -b feature/new-feature

# 3. Make changes
# ... edit files ...

# 4. Run checks
ruff check src/
ruff format src/

# 5. Test manually
dir-wand --template test_{num} --num 0-2

# 6. Commit
git add .
git commit -m "Add new feature"

# 7. Push and create PR
git push origin feature/new-feature
```

## Release Process

(For maintainers)

1. Update version in `pyproject.toml`
2. Update changelog
3. Create git tag:
   ```bash
   git tag -a v1.x.x -m "Release v1.x.x"
   git push origin v1.x.x
   ```
4. Build and upload to PyPI:
   ```bash
   python -m build
   python -m twine upload dist/*
   ```

## Questions?

- **General questions:** Open a [Discussion](https://github.com/WillJRoper/dir-wand/discussions)
- **Bugs:** Open an [Issue](https://github.com/WillJRoper/dir-wand/issues)
- **Security:** Email the maintainer directly

## License

By contributing, you agree that your contributions will be licensed under the GNU General Public License v3.0.
