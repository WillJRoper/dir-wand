"""WAND: WAND Automates Nested Directories.

A Python CLI and library for creating large numbers of directories from a
single template and executing commands globally throughout every directory.

Programmatic API:
    >>> from dir_wand import create_directories
    >>> create_directories(
    ...     template="experiment_{num}",
    ...     output_dir="/data/experiments",
    ...     num=range(10)
    ... )

    >>> from dir_wand import run_commands
    >>> run_commands(
    ...     "cd exp_{num} && python analyze.py",
    ...     num=range(10)
    ... )

For CLI usage:
    $ dir-wand --template experiment_{num} --num 0-9

See documentation at: https://willjroper.github.io/dir-wand/
"""

# High-level API
from dir_wand.api import (
    create_directories,
    create_swapfile,
    create_template_structure,
    execute_commands,
    generate_swapfile,
    load_swapfile,
    make_directories,
    run_commands,
)

# Core classes for advanced usage
from dir_wand.command_runner import CommandRunner
from dir_wand.directory import Directory
from dir_wand.file import File
from dir_wand.logger import Logger
from dir_wand.template import Template

# Version info (set by setuptools_scm)
try:
    from dir_wand._version import version as __version__
except ImportError:
    __version__ = "unknown"

__all__ = [
    # High-level API (recommended)
    "create_directories",
    "run_commands",
    "generate_swapfile",
    "load_swapfile",
    "create_template_structure",
    # Aliases
    "make_directories",
    "execute_commands",
    "create_swapfile",
    # Core classes (advanced usage)
    "Template",
    "Directory",
    "File",
    "CommandRunner",
    "Logger",
    # Version
    "__version__",
]
