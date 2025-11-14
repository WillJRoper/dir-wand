# Programmatic API Reference

WAND provides a clean Python API for use in scripts and applications, in addition to the command-line interface.

## Overview

The programmatic API allows you to:

- Create directories from templates
- Execute commands in directories
- Generate and load swapfiles
- Create template structures programmatically
- Integrate WAND into larger applications

## Quick Start

```python
from dir_wand import create_directories

# Create 10 experiment directories
create_directories(
    template="experiment_{num}",
    output_dir="/data/experiments",
    num=range(10)
)
```

## Module: `dir_wand.api`

### High-Level Functions

#### `create_directories()`

Create multiple directories from a template with placeholder replacement.

```python
create_directories(
    template: Union[str, Path],
    output_dir: Union[str, Path] = ".",
    run_command: Optional[str] = None,
    silent: bool = False,
    **placeholders: Union[List[Any], range]
) -> Dict[str, int]
```

**Parameters:**

- `template` (str | Path): Path to the template directory. Can contain placeholders (e.g., `"experiment_{num}"`).
- `output_dir` (str | Path): Directory where copies will be created. Defaults to current directory.
- `run_command` (str, optional): Command to execute in each created directory. Can contain placeholders.
- `silent` (bool): If True, suppress all output. Defaults to False.
- `**placeholders`: Keyword arguments where keys are placeholder names and values are lists/ranges of replacement values. All lists must have the same length.

**Returns:**

Dictionary with statistics:

- `"directories"`: Number of directories created
- `"files"`: Number of files created
- `"commands"`: Number of commands executed
- `"swaps"`: Number of placeholder replacements made

**Raises:**

- `ValueError`: If placeholder value lists have different lengths
- `FileNotFoundError`: If template directory doesn't exist

**Examples:**

```python
# Simple sequential directories
from dir_wand import create_directories

create_directories(
    template="exp_{num}",
    num=range(10)
)

# Multiple placeholders
create_directories(
    template="sim_{scenario}_{seed}",
    output_dir="/simulations",
    scenario=["baseline", "treatment", "control"],
    seed=[100, 200, 300]
)

# With command execution
create_directories(
    template="job_{id}",
    id=[1, 2, 3, 4, 5],
    run_command="cd job_{id} && python process.py"
)

# Silent mode
stats = create_directories(
    template="test_{num}",
    num=range(100),
    silent=True
)
print(f"Created {stats['directories']} directories")
```

#### `run_commands()`

Execute a command multiple times with different placeholder values.

```python
run_commands(
    command: str,
    silent: bool = False,
    **placeholders: Union[List[Any], range]
) -> Dict[str, int]
```

**Parameters:**

- `command` (str): Command to execute. Can contain placeholders (e.g., `"cd exp_{num} && python analyze.py"`).
- `silent` (bool): If True, suppress all output. Defaults to False.
- `**placeholders`: Keyword arguments mapping placeholder names to value lists/ranges.

**Returns:**

Dictionary with statistics:

- `"commands"`: Number of commands executed
- `"swaps"`: Number of placeholder replacements made

**Raises:**

- `ValueError`: If placeholder value lists have different lengths

**Examples:**

```python
from dir_wand import run_commands

# Run analysis in existing directories
run_commands(
    "cd exp_{num} && python analyze.py",
    num=range(10)
)

# Clean up temporary files
run_commands(
    "cd job_{id} && rm -f *.tmp",
    id=[1, 2, 3, 4, 5]
)

# Collect results
stats = run_commands(
    "cp exp_{num}/results.csv collected/results_{num}.csv",
    num=range(100),
    silent=True
)
print(f"Collected {stats['commands']} results")
```

#### `generate_swapfile()`

Generate a YAML swapfile with all combinations of placeholder values.

```python
generate_swapfile(
    output_path: Union[str, Path],
    **placeholders: Union[List[Any], range]
) -> int
```

**Parameters:**

- `output_path` (str | Path): Path where the swapfile will be written.
- `**placeholders`: Keyword arguments mapping placeholder names to value lists/ranges.

**Returns:**

Number of combinations generated.

**Examples:**

```python
from dir_wand import generate_swapfile

# Generate all combinations
num_combos = generate_swapfile(
    "experiments.yaml",
    num=range(3),
    condition=["A", "B", "C"]
)
print(f"Generated {num_combos} combinations")  # 9

# Use with create_directories
from dir_wand import load_swapfile, create_directories

swaps = load_swapfile("experiments.yaml")
create_directories(
    "exp_{num}_{condition}",
    **swaps
)
```

#### `load_swapfile()`

Load placeholder values from a YAML swapfile.

```python
load_swapfile(
    swapfile_path: Union[str, Path]
) -> Dict[str, List[Any]]
```

**Parameters:**

- `swapfile_path` (str | Path): Path to the YAML swapfile.

**Returns:**

Dictionary mapping placeholder names to lists of values.

**Raises:**

- `FileNotFoundError`: If swapfile doesn't exist
- `yaml.YAMLError`: If swapfile has invalid YAML syntax

**Examples:**

```python
from dir_wand import load_swapfile, create_directories

# Load swapfile
swaps = load_swapfile("config.yaml")

# Use the values
create_directories(
    "exp_{num}_{condition}",
    **swaps
)
```

#### `create_template_structure()`

Create a template directory structure programmatically.

```python
create_template_structure(
    template_path: Union[str, Path],
    directories: Optional[List[str]] = None,
    files: Optional[Dict[str, str]] = None,
) -> None
```

**Parameters:**

- `template_path` (str | Path): Path where the template will be created.
- `directories` (List[str], optional): List of directory paths to create within the template.
- `files` (Dict[str, str], optional): Dictionary mapping file paths to their contents.

**Examples:**

```python
from dir_wand import create_template_structure

create_template_structure(
    "experiment_{num}",
    directories=["data", "results", "logs"],
    files={
        "config.yaml": "experiment_id: {num}\nseed: {seed}\n",
        "run.sh": "#!/bin/bash\necho 'Running {num}'\n",
        "README.md": "# Experiment {num}\n"
    }
)
```

### Convenience Aliases

The following aliases are available for convenience:

```python
from dir_wand import (
    make_directories,     # Alias for create_directories
    execute_commands,     # Alias for run_commands
    create_swapfile,      # Alias for generate_swapfile
)
```

## Advanced Usage

### Using Core Classes

For advanced use cases, you can import and use the core classes directly:

```python
from dir_wand import Template, Directory, File, CommandRunner, Logger

# Create template manually
template = Template(
    root="experiment_{num}",
    run="python run.py",
    num=[1, 2, 3]
)

# Make copies
template.make_copies("/output")

# Access statistics
logger = Logger()
print(logger.counts)
```

See individual class documentation for details:

- [Template](template.md)
- [Directory](directory.md)
- [File](file.md)
- [CommandRunner](command_runner.md)
- [Logger](logger.md)

## Integration Patterns

### Pattern 1: Simple Batch Processing

```python
from dir_wand import create_directories

def process_batch(start_id: int, end_id: int):
    """Process a batch of data files."""
    create_directories(
        template="batch_{id}",
        output_dir="/processing",
        id=range(start_id, end_id),
        run_command="cd batch_{id} && python process.py"
    )

# Process 1000 files
process_batch(0, 1000)
```

### Pattern 2: Parameter Grid Search

```python
from dir_wand import generate_swapfile, load_swapfile, create_directories

def run_grid_search(params):
    """Run a hyperparameter grid search."""
    # Generate all combinations
    generate_swapfile("grid.yaml", **params)

    # Load and create experiments
    swaps = load_swapfile("grid.yaml")
    stats = create_directories(
        "exp_{param1}_{param2}",
        **swaps,
        run_command="cd exp_{param1}_{param2} && python train.py"
    )

    return stats

# Run grid search
stats = run_grid_search({
    "param1": [0.001, 0.01, 0.1],
    "param2": [16, 32, 64]
})
```

### Pattern 3: Multi-Stage Workflow

```python
from dir_wand import create_directories, run_commands

class Workflow:
    """Multi-stage data processing workflow."""

    def __init__(self, num_jobs: int):
        self.num_jobs = num_jobs
        self.job_ids = list(range(num_jobs))

    def stage1_prepare(self):
        """Prepare data."""
        create_directories(
            "job_{id}",
            id=self.job_ids,
            run_command="cd job_{id} && python prepare.py"
        )

    def stage2_process(self):
        """Process data."""
        run_commands(
            "cd job_{id} && python process.py",
            id=self.job_ids
        )

    def stage3_analyze(self):
        """Analyze results."""
        run_commands(
            "cd job_{id} && python analyze.py",
            id=self.job_ids
        )

    def run_all(self):
        """Run complete workflow."""
        self.stage1_prepare()
        self.stage2_process()
        self.stage3_analyze()

# Run workflow
workflow = Workflow(num_jobs=100)
workflow.run_all()
```

### Pattern 4: Integration with pandas

```python
import pandas as pd
from dir_wand import create_directories

# Load experimental design
design = pd.read_csv("experiment_design.csv")

# Create directories for each row
create_directories(
    "exp_{treatment}_{replicate}",
    output_dir="/experiments",
    treatment=design["treatment"].tolist(),
    replicate=design["replicate"].tolist(),
    dose=design["dose"].tolist()
)
```

## Type Hints

The API includes full type hints for IDE support:

```python
from typing import List, Dict
from dir_wand import create_directories

def setup_experiments(experiment_ids: List[int]) -> Dict[str, int]:
    """Set up experiment directories."""
    stats = create_directories(
        template="exp_{id}",
        id=experiment_ids
    )
    return stats
```

## Error Handling

```python
from dir_wand import create_directories

try:
    stats = create_directories(
        template="exp_{a}_{b}",
        a=[1, 2, 3],
        b=[10, 20]  # Different length - will raise ValueError
    )
except ValueError as e:
    print(f"Error: {e}")
    # Error: All placeholder lists must have the same length. Got: {'a': 3, 'b': 2}

try:
    stats = create_directories(
        template="/nonexistent/template_{num}",
        num=[1, 2, 3]
    )
except FileNotFoundError as e:
    print(f"Template not found: {e}")
```

## Performance Considerations

- **Silent Mode**: Use `silent=True` for large batches to reduce I/O overhead
- **Ranges**: Use `range()` instead of lists for large sequences (more memory efficient)
- **Commands**: Commands run concurrently on threads; suitable for I/O-bound tasks

```python
# Memory efficient for large ranges
create_directories(
    "job_{id}",
    id=range(10000),  # More efficient than list(range(10000))
    silent=True        # Reduce output overhead
)
```

## See Also

- [Examples](../examples/basic.md) - Real-world usage examples
- [User Guide](../guides/getting-started.md) - Getting started with WAND
- [Template API](template.md) - Template class reference
- [GitHub Examples](https://github.com/WillJRoper/dir-wand/tree/main/examples) - Example scripts
