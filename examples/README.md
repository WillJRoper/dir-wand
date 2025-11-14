# WAND Programmatic API Examples

This directory contains example scripts demonstrating how to use WAND's programmatic Python API.

## Quick Start

```python
from dir_wand import create_directories

# Create directories programmatically
create_directories(
    template="experiment_{num}",
    output_dir="/data/experiments",
    num=range(10)
)
```

## Examples

### basic_usage.py

Demonstrates fundamental API usage:

- Simple directory creation
- Multiple placeholders
- Running commands
- Silent mode
- Using explicit lists

**Run it:**

```bash
python examples/basic_usage.py
```

### scientific_workflow.py

Complete scientific computing workflow:

- Creating templates programmatically
- Generating parameter grids
- Running batch simulations
- Analyzing results
- Collecting and summarizing data

**Run it:**

```bash
python examples/scientific_workflow.py
```

### integration_example.py

Shows integration into a larger application:

- Class-based experiment manager
- Managing ML experiments
- Creating configurations programmatically
- Collecting results

**Run it:**

```bash
python examples/integration_example.py --experiment-id 1
```

## API Reference

### High-Level Functions

#### `create_directories()`

Create multiple directories from a template.

```python
from dir_wand import create_directories

stats = create_directories(
    template="job_{id}",
    output_dir="/jobs",
    id=range(100),
    run_command="cd job_{id} && python process.py"
)

print(f"Created {stats['directories']} directories")
print(f"Executed {stats['commands']} commands")
```

**Parameters:**

- `template`: Path to template directory
- `output_dir`: Where to create copies (default: current directory)
- `run_command`: Optional command to run in each directory
- `silent`: Suppress output (default: False)
- `**placeholders`: Placeholder names and values

**Returns:** Dictionary with statistics

#### `run_commands()`

Run commands in existing directories.

```python
from dir_wand import run_commands

stats = run_commands(
    "cd exp_{num} && python analyze.py",
    num=range(10)
)
```

**Parameters:**

- `command`: Command with placeholders
- `silent`: Suppress output
- `**placeholders`: Placeholder names and values

**Returns:** Dictionary with statistics

#### `generate_swapfile()`

Generate all combinations of parameters.

```python
from dir_wand import generate_swapfile

num_combos = generate_swapfile(
    "experiments.yaml",
    model=["resnet", "vgg"],
    lr=[0.001, 0.01, 0.1]
)

print(f"Generated {num_combos} combinations")
```

#### `load_swapfile()`

Load parameters from a swapfile.

```python
from dir_wand import load_swapfile, create_directories

params = load_swapfile("experiments.yaml")
create_directories(
    "exp_{model}_{lr}",
    **params
)
```

#### `create_template_structure()`

Create template structure programmatically.

```python
from dir_wand import create_template_structure

create_template_structure(
    "project_{id}",
    directories=["src", "tests", "data"],
    files={
        "config.yaml": "project_id: {id}\n",
        "run.sh": "#!/bin/bash\necho 'Project {id}'\n"
    }
)
```

### Advanced Classes

For advanced usage, you can import the core classes:

```python
from dir_wand import Template, Directory, File, CommandRunner

# Create template manually
template = Template(
    "experiment_{num}",
    run="python run.py",
    num=[1, 2, 3]
)

template.make_copies("/output")
```

## Common Patterns

### Pattern 1: Parameter Grid Search

```python
from dir_wand import generate_swapfile, load_swapfile, create_directories

# Generate all combinations
generate_swapfile(
    "grid.yaml",
    param_a=[1, 2, 3],
    param_b=[10, 20, 30]
)

# Use the combinations
params = load_swapfile("grid.yaml")
create_directories("exp_{param_a}_{param_b}", **params)
```

### Pattern 2: Batch Processing

```python
from dir_wand import create_directories

# Process 1000 data files
create_directories(
    template="batch_{id}",
    output_dir="/processing",
    id=range(1000),
    run_command="cd batch_{id} && python process.py data_{id}.csv"
)
```

### Pattern 3: Multi-Stage Workflow

```python
from dir_wand import create_directories, run_commands

# Stage 1: Create and run simulations
create_directories(
    "sim_{id}",
    id=range(100),
    run_command="cd sim_{id} && ./simulate.sh"
)

# Stage 2: Analyze results
run_commands(
    "cd sim_{id} && python analyze.py",
    id=range(100)
)

# Stage 3: Collect results
run_commands(
    "cp sim_{id}/results.csv collected/results_{id}.csv",
    id=range(100)
)
```

### Pattern 4: Integration with pandas

```python
import pandas as pd
from dir_wand import create_directories

# Read experimental design from CSV
design = pd.read_csv("experiment_design.csv")

# Create directories for each row
create_directories(
    "exp_{treatment}_{replicate}",
    treatment=design["treatment"].tolist(),
    replicate=design["replicate"].tolist(),
    dose=design["dose"].tolist()
)
```

## Tips

### Type Hints

The API includes type hints for better IDE support:

```python
from typing import List
from dir_wand import create_directories

def run_batch(ids: List[int]) -> None:
    create_directories(
        template="job_{id}",
        id=ids
    )
```

### Error Handling

```python
from dir_wand import create_directories

try:
    stats = create_directories(
        template="exp_{a}_{b}",
        a=[1, 2, 3],
        b=[10, 20]  # Different length!
    )
except ValueError as e:
    print(f"Error: {e}")
    # Error: All placeholder lists must have the same length
```

### Silent Mode

```python
from dir_wand import create_directories

# No output
stats = create_directories(
    "test_{num}",
    num=range(1000),
    silent=True
)

# But you still get statistics
print(f"Created {stats['directories']} directories quietly")
```

## See Also

- [API Documentation](../docs/api/api.md)
- [User Guide](../docs/guides/getting-started.md)
- [More Examples](../docs/examples/basic.md)
