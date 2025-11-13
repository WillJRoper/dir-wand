# WAND Documentation

**WAND: WAND Automates Nested Directories**

Welcome to the WAND documentation. This comprehensive guide covers everything you need to know about using WAND to create and manage complex directory structures efficiently.

## What is WAND?

WAND is a Python CLI tool designed to automate the creation of large numbers of directories from a single template and execute commands globally throughout every directory. It's particularly useful for:

- Running many simulations with different parameters
- Performance testing across multiple configurations
- Scientific experiments requiring identical directory structures
- Batch processing tasks with variable inputs
- Any scenario requiring systematic directory creation with parameterized content

## Key Features

- **Template-based directory creation**: Define a single template and generate hundreds or thousands of copies
- **Placeholder system**: Use `{placeholder}` syntax in file paths and file contents
- **Multiple value input methods**: Ranges, lists, or files containing values
- **Swapfile support**: YAML-based configuration for complex placeholder combinations
- **Command execution**: Run commands in each created directory automatically
- **Concurrent execution**: Commands run on parallel threads for efficiency
- **Preserves file properties**: Correctly handles executables, softlinks, permissions, and binary files
- **Silent mode**: Suppress output for use in scripts and automation

## Quick Start

### Installation

```bash
pip install dir-wand
```

### Basic Usage

Create a template directory with placeholders:

```bash
mkdir template_{num}
echo "Run number: {num}" > template_{num}/config.txt
```

Generate copies with different values:

```bash
dir-wand --template template_{num} --num 0-2
```

This creates `template_0/`, `template_1/`, and `template_2/` with the placeholder replaced in file names and contents.

## Documentation Structure

### User Guides
- [Getting Started](guides/getting-started.md) - Installation and first steps
- [Working with Templates](guides/templates.md) - Creating and using templates
- [Placeholder System](guides/placeholders.md) - Understanding placeholders and swaps
- [Swapfiles](guides/swapfiles.md) - Using YAML swapfiles for complex scenarios
- [Command Execution](guides/commands.md) - Running commands in directories

### API Reference
- [Template Class](api/template.md) - Core template functionality
- [Directory Class](api/directory.md) - Directory tree representation
- [File Class](api/file.md) - File handling and copying
- [Parser Class](api/parser.md) - Command-line argument parsing
- [CommandRunner Class](api/command_runner.md) - Command execution system
- [Logger Class](api/logger.md) - Logging and reporting
- [Swapfile Module](api/swapfile.md) - Swapfile generation
- [Utils Module](api/utils.md) - Utility functions

### Examples
- [Basic Examples](examples/basic.md) - Simple use cases
- [Scientific Computing](examples/scientific.md) - Simulation workflows
- [Data Processing](examples/data-processing.md) - Batch data processing
- [Testing and CI/CD](examples/testing.md) - Automated testing scenarios

### Developer Documentation
- [Architecture Overview](developer/architecture.md) - System design and components
- [Contributing Guide](developer/contributing.md) - How to contribute to WAND
- [Development Setup](developer/setup.md) - Setting up a development environment

## Support and Community

- **GitHub Repository**: [WillJRoper/dir-wand](https://github.com/WillJRoper/dir-wand)
- **Issue Tracker**: [GitHub Issues](https://github.com/WillJRoper/dir-wand/issues)
- **PyPI Package**: [dir-wand](https://pypi.org/project/dir-wand/)

## License

WAND is licensed under the GNU General Public License v3.0. See the [LICENSE](../LICENSE) file for details.
