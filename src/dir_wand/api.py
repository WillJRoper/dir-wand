"""Programmatic API for WAND.

This module provides a clean Python API for using WAND functionality
programmatically, without going through the command-line interface.

Example:
    Basic usage:

    >>> from dir_wand import create_directories
    >>> create_directories(
    ...     template="experiment_{num}",
    ...     output_dir="/data/experiments",
    ...     num=range(10)
    ... )

    With commands:

    >>> create_directories(
    ...     template="job_{id}",
    ...     output_dir="/jobs",
    ...     id=[1, 2, 3],
    ...     run_command="cd job_{id} && python run.py"
    ... )
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from dir_wand.logger import Logger
from dir_wand.swapfile import make_swapfile as _make_swapfile


def create_directories(
    template: Union[str, Path],
    output_dir: Union[str, Path] = ".",
    run_command: Optional[str] = None,
    silent: bool = False,
    **placeholders: Union[List[Any], range]
) -> Dict[str, int]:
    """
    Create multiple directories from a template with placeholder replacement.

    This is the main programmatic entry point for WAND. It creates copies of
    a template directory, replacing placeholders with provided values.

    Args:
        template: Path to the template directory. Can contain placeholders
            in the directory name (e.g., "experiment_{num}").
        output_dir: Directory where copies will be created. Defaults to
            current directory.
        run_command: Optional command to execute in each created directory.
            Can contain placeholders that will be replaced.
        silent: If True, suppress all output.
        **placeholders: Keyword arguments where keys are placeholder names
            and values are lists/ranges of replacement values. All lists must
            have the same length.

    Returns:
        Dictionary with statistics:
            - "directories": Number of directories created
            - "files": Number of files created
            - "commands": Number of commands executed
            - "swaps": Number of placeholder replacements made

    Raises:
        ValueError: If placeholder value lists have different lengths.
        FileNotFoundError: If template directory doesn't exist.

    Examples:
        Create simple sequential directories:

        >>> create_directories(
        ...     template="exp_{num}",
        ...     num=range(10)
        ... )

        Create with multiple placeholders:

        >>> create_directories(
        ...     template="sim_{scenario}_{seed}",
        ...     output_dir="/data/simulations",
        ...     scenario=["baseline", "treatment", "control"],
        ...     seed=[100, 200, 300]
        ... )

        Create and run commands:

        >>> create_directories(
        ...     template="job_{id}",
        ...     id=[1, 2, 3, 4, 5],
        ...     run_command="cd job_{id} && python process.py"
        ... )

        Suppress output:

        >>> create_directories(
        ...     template="test_{num}",
        ...     num=range(100),
        ...     silent=True
        ... )
    """
    # Delay imports to ensure Logger is set up first
    from dir_wand.template import Template

    # Set up logger
    logger = Logger(silent=silent)

    # Convert paths to strings
    template = str(template)
    output_dir = str(output_dir)

    # Convert placeholders to lists
    swaps = {}
    for key, value in placeholders.items():
        if isinstance(value, range):
            swaps[key] = list(value)
        elif isinstance(value, (list, tuple)):
            swaps[key] = list(value)
        else:
            # Single value - wrap in list
            swaps[key] = [value]

    # Validate all swaps have same length
    lengths = {key: len(value) for key, value in swaps.items()}
    unique_lengths = set(lengths.values())
    if len(unique_lengths) > 1:
        raise ValueError(
            f"All placeholder lists must have the same length. Got: {lengths}"
        )

    # Create template
    template_obj = Template(template, run=run_command, **swaps)

    # Print info if not silent
    if not silent:
        print(template_obj)
        print()
        print("Template structure:")
        print(template_obj.directory)

    # Make copies
    template_obj.make_copies(output_dir)

    # Get statistics
    stats = {
        "directories": logger.counts.get("directory", 0),
        "files": logger.counts.get("file", 0),
        "commands": logger.counts.get("command", 0),
        "swaps": sum(logger.swap_counts.values()),
    }

    # Report if not silent
    if not silent:
        logger.report()

    return stats


def run_commands(
    command: str,
    silent: bool = False,
    **placeholders: Union[List[Any], range]
) -> Dict[str, int]:
    """
    Run a command in existing directories with placeholder replacement.

    This function executes a command multiple times with different placeholder
    values, useful for running operations in existing directory structures.

    Args:
        command: Command to execute. Can contain placeholders (e.g.,
            "cd exp_{num} && python analyze.py").
        silent: If True, suppress all output.
        **placeholders: Keyword arguments where keys are placeholder names
            and values are lists/ranges of replacement values.

    Returns:
        Dictionary with statistics:
            - "commands": Number of commands executed
            - "swaps": Number of placeholder replacements made

    Raises:
        ValueError: If placeholder value lists have different lengths.

    Examples:
        Run analysis in existing directories:

        >>> run_commands(
        ...     "cd exp_{num} && python analyze.py",
        ...     num=range(10)
        ... )

        Clean up temporary files:

        >>> run_commands(
        ...     "cd job_{id} && rm -f *.tmp",
        ...     id=[1, 2, 3, 4, 5]
        ... )

        Collect results:

        >>> run_commands(
        ...     "cp exp_{num}/results.csv collected/results_{num}.csv",
        ...     num=range(100)
        ... )
    """
    # Delay import
    from dir_wand.command_runner import CommandRunner

    # Set up logger
    logger = Logger(silent=silent)

    # Convert placeholders to lists
    swaps = {}
    for key, value in placeholders.items():
        if isinstance(value, range):
            swaps[key] = list(value)
        elif isinstance(value, (list, tuple)):
            swaps[key] = list(value)
        else:
            swaps[key] = [value]

    # Validate all swaps have same length
    lengths = {key: len(value) for key, value in swaps.items()}
    unique_lengths = set(lengths.values())
    if len(unique_lengths) > 1:
        raise ValueError(
            f"All placeholder lists must have the same length. Got: {lengths}"
        )

    # Create command runner
    runner = CommandRunner(command)

    # Run commands for all swaps
    runner.run_command_for_all_swaps(**swaps)

    # Get statistics
    stats = {
        "commands": logger.counts.get("command", 0),
        "swaps": sum(logger.swap_counts.values()),
    }

    # Report if not silent
    if not silent:
        logger.report()

    return stats


def generate_swapfile(
    output_path: Union[str, Path],
    **placeholders: Union[List[Any], range]
) -> int:
    """
    Generate a YAML swapfile with all combinations of placeholder values.

    This function creates all possible combinations of the provided placeholder
    values and saves them to a YAML file in swapfile format.

    Args:
        output_path: Path where the swapfile will be written.
        **placeholders: Keyword arguments where keys are placeholder names
            and values are lists/ranges of possible values.

    Returns:
        Number of combinations generated.

    Examples:
        Generate all combinations:

        >>> generate_swapfile(
        ...     "experiments.yaml",
        ...     num=range(3),
        ...     condition=["A", "B", "C"]
        ... )
        9

        Use with create_directories:

        >>> from dir_wand import generate_swapfile, load_swapfile
        >>> generate_swapfile(
        ...     "config.yaml",
        ...     model=["resnet", "vgg"],
        ...     lr=[0.001, 0.01, 0.1]
        ... )
        >>> swaps = load_swapfile("config.yaml")
        >>> create_directories(
        ...     "exp_{model}_{lr}",
        ...     **swaps
        ... )
    """
    # Convert paths
    output_path = str(output_path)

    # Convert placeholders to lists
    swaps = {}
    for key, value in placeholders.items():
        if isinstance(value, range):
            swaps[key] = list(value)
        elif isinstance(value, (list, tuple)):
            swaps[key] = list(value)
        else:
            swaps[key] = [value]

    # Generate swapfile
    _make_swapfile(output_path, swaps)

    # Calculate number of combinations
    if swaps:
        num_combinations = len(list(swaps.values())[0])
    else:
        num_combinations = 0

    return num_combinations


def load_swapfile(swapfile_path: Union[str, Path]) -> Dict[str, List[Any]]:
    """
    Load placeholder values from a YAML swapfile.

    Args:
        swapfile_path: Path to the YAML swapfile.

    Returns:
        Dictionary mapping placeholder names to lists of values.

    Raises:
        FileNotFoundError: If swapfile doesn't exist.
        yaml.YAMLError: If swapfile has invalid YAML syntax.

    Example:
        >>> swaps = load_swapfile("config.yaml")
        >>> create_directories(
        ...     "exp_{num}_{condition}",
        ...     **swaps
        ... )
    """
    from dir_wand.parser import parse_swapfile

    return parse_swapfile(str(swapfile_path))


def create_template_structure(
    template_path: Union[str, Path],
    directories: Optional[List[str]] = None,
    files: Optional[Dict[str, str]] = None,
) -> None:
    """
    Create a template directory structure programmatically.

    This is a convenience function for creating template directories from
    Python code rather than manually.

    Args:
        template_path: Path where the template will be created.
        directories: List of directory paths to create within the template.
        files: Dictionary mapping file paths to their contents.

    Example:
        >>> create_template_structure(
        ...     "experiment_{num}",
        ...     directories=["data", "results", "logs"],
        ...     files={
        ...         "config.yaml": "experiment_id: {num}\\nseed: {seed}\\n",
        ...         "run.sh": "#!/bin/bash\\necho 'Running {num}'\\n"
        ...     }
        ... )
    """
    import os

    template_path = Path(template_path)

    # Create root directory
    template_path.mkdir(parents=True, exist_ok=True)

    # Create subdirectories
    if directories:
        for dir_path in directories:
            (template_path / dir_path).mkdir(parents=True, exist_ok=True)

    # Create files
    if files:
        for file_path, content in files.items():
            file_full_path = template_path / file_path
            file_full_path.parent.mkdir(parents=True, exist_ok=True)
            file_full_path.write_text(content)

            # Make executable if it's a script
            if file_path.endswith((".sh", ".py", ".bash")):
                os.chmod(file_full_path, 0o755)


# Convenience aliases
make_directories = create_directories
execute_commands = run_commands
create_swapfile = generate_swapfile
