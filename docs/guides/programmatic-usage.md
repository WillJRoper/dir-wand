# Programmatic Usage Guide

WAND can be used as a Python library in your scripts and applications, not just as a command-line tool.

## Why Use the Programmatic API?

- **Integration**: Incorporate WAND into larger workflows
- **Flexibility**: Dynamic parameter generation based on runtime data
- **Automation**: Build custom experiment managers and batch processors
- **Type Safety**: Full type hints for IDE support
- **Simplicity**: Cleaner than subprocess calls to the CLI

## Installation

The programmatic API is included with WAND:

```bash
pip install dir-wand
```

## Basic Usage

### Creating Directories

```python
from dir_wand import create_directories

# Create 10 experiment directories
stats = create_directories(
    template="experiment_{num}",
    output_dir="/data/experiments",
    num=range(10)
)

print(f"Created {stats['directories']} directories")
print(f"Created {stats['files']} files")
```

### Running Commands

```python
from dir_wand import run_commands

# Run analysis in existing directories
stats = run_commands(
    "cd exp_{num} && python analyze.py",
    num=range(10)
)

print(f"Executed {stats['commands']} commands")
```

### Working with Swapfiles

```python
from dir_wand import generate_swapfile, load_swapfile, create_directories

# Generate all combinations
num_combos = generate_swapfile(
    "experiments.yaml",
    model=["resnet", "vgg"],
    lr=[0.001, 0.01, 0.1]
)

print(f"Generated {num_combos} combinations")

# Load and use
swaps = load_swapfile("experiments.yaml")
create_directories("exp_{model}_{lr}", **swaps)
```

## Complete Example

Here's a complete workflow for running machine learning experiments:

```python
#!/usr/bin/env python3
"""Machine learning experiment workflow."""

from pathlib import Path
from dir_wand import (
    create_template_structure,
    create_directories,
    run_commands,
)

# Step 1: Create template
create_template_structure(
    "ml_exp_{model}_{lr}",
    directories=["data", "checkpoints", "logs"],
    files={
        "config.yaml": """
model: {model}
learning_rate: {lr}
batch_size: 32
epochs: 100
""",
        "train.py": """
#!/usr/bin/env python3
# Training script here
import yaml

with open('config.yaml') as f:
    config = yaml.safe_load(f)

print(f"Training {config['model']} with lr={config['learning_rate']}")
"""
    }
)

# Step 2: Create experiments
models = ["resnet50", "vgg16", "inception"]
learning_rates = [0.001, 0.01, 0.1]

stats = create_directories(
    template="ml_exp_{model}_{lr}",
    output_dir="/experiments",
    model=models,
    lr=learning_rates,
    run_command="cd ml_exp_{model}_{lr} && python train.py"
)

print(f"Created {stats['directories']} experiments")
print(f"Launched {stats['commands']} training jobs")

# Step 3: Collect results (after training completes)
run_commands(
    "cp ml_exp_{model}_{lr}/checkpoints/best.pth results/{model}_{lr}.pth",
    model=models,
    lr=learning_rates
)
```

## Comparison: CLI vs Programmatic API

### CLI Approach

```bash
#!/bin/bash
dir-wand --template exp_{num} --num 0-99 --run "python run.py"
```

### Programmatic Approach

```python
from dir_wand import create_directories

create_directories(
    template="exp_{num}",
    num=range(100),
    run_command="python run.py"
)
```

**Advantages of Programmatic API:**

- Dynamic parameter generation
- Error handling with try/except
- Integration with other Python libraries
- Access to statistics
- Type checking and IDE autocomplete

## Integration Patterns

### Pattern 1: Dynamic Parameters from Data

```python
import pandas as pd
from dir_wand import create_directories

# Load experimental design
design = pd.read_csv("design.csv")

# Create directories dynamically
create_directories(
    template="exp_{treatment}_{replicate}",
    treatment=design["treatment"].tolist(),
    replicate=design["replicate"].tolist()
)
```

### Pattern 2: Class-Based Experiment Manager

```python
from dir_wand import create_directories, run_commands
from pathlib import Path

class ExperimentManager:
    def __init__(self, base_dir: str):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def create_experiments(self, experiment_ids):
        """Create experiment directories."""
        return create_directories(
            template=str(self.base_dir / "exp_{id}"),
            id=experiment_ids
        )

    def run_all(self, experiment_ids):
        """Run all experiments."""
        return run_commands(
            f"cd {self.base_dir}/exp_{{id}} && python run.py",
            id=experiment_ids
        )

# Usage
manager = ExperimentManager("/data/experiments")
manager.create_experiments(range(100))
manager.run_all(range(100))
```

### Pattern 3: Conditional Logic

```python
from dir_wand import create_directories

def setup_experiments(config):
    """Set up experiments based on configuration."""
    if config["mode"] == "full":
        # Full grid search
        num_experiments = 100
    else:
        # Quick test
        num_experiments = 10

    return create_directories(
        template="exp_{id}",
        id=range(num_experiments),
        run_command=config.get("command", "python run.py")
    )

config = {"mode": "full", "command": "python train.py"}
stats = setup_experiments(config)
```

### Pattern 4: Error Handling

```python
from dir_wand import create_directories
import logging

logging.basicConfig(level=logging.INFO)

def safe_create_directories(**kwargs):
    """Create directories with error handling."""
    try:
        stats = create_directories(**kwargs)
        logging.info(f"Successfully created {stats['directories']} directories")
        return stats
    except ValueError as e:
        logging.error(f"Configuration error: {e}")
        raise
    except FileNotFoundError as e:
        logging.error(f"Template not found: {e}")
        raise
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        raise

# Usage
stats = safe_create_directories(
    template="exp_{num}",
    num=range(10)
)
```

## Advanced Features

### Silent Mode

Suppress all output for use in scripts:

```python
from dir_wand import create_directories

# No console output
stats = create_directories(
    template="test_{num}",
    num=range(1000),
    silent=True
)

# But you still get statistics
if stats["directories"] == 1000:
    print("All directories created successfully")
```

### Creating Templates Programmatically

```python
from dir_wand import create_template_structure

def make_simulation_template(template_name):
    """Create a simulation template."""
    create_template_structure(
        template_name,
        directories=[
            "input",
            "output",
            "logs",
            "checkpoints"
        ],
        files={
            "config.yaml": """
simulation:
  name: {name}
  seed: {seed}
  steps: 1000
""",
            "run.sh": """#!/bin/bash
set -e
echo "Running {name}"
python simulate.py --config config.yaml
""",
            "README.md": "# Simulation {name}\n\nSeed: {seed}\n"
        }
    )

make_simulation_template("sim_{name}_{seed}")
```

### Type Hints for Better IDE Support

```python
from typing import List, Dict
from dir_wand import create_directories

def batch_process(
    file_ids: List[int],
    output_dir: str
) -> Dict[str, int]:
    """Process files in batch.

    Args:
        file_ids: List of file IDs to process.
        output_dir: Output directory path.

    Returns:
        Statistics dictionary.
    """
    return create_directories(
        template="batch_{id}",
        output_dir=output_dir,
        id=file_ids,
        run_command="cd batch_{id} && python process.py"
    )
```

## Common Use Cases

### 1. Scientific Simulations

```python
from dir_wand import generate_swapfile, load_swapfile, create_directories

# Generate parameter grid
generate_swapfile(
    "sim_params.yaml",
    temperature=range(273, 374, 10),  # 273K to 373K
    pressure=[1e5, 2e5, 5e5, 1e6],
    seed=range(42, 52)  # 10 replicates
)

# Run simulations
params = load_swapfile("sim_params.yaml")
create_directories(
    "sim_{temperature}_{pressure}_{seed}",
    output_dir="/simulations",
    **params,
    run_command="cd sim_{temperature}_{pressure}_{seed} && ./simulate"
)
```

### 2. Data Processing Pipeline

```python
from dir_wand import create_directories, run_commands

# Stage 1: Prepare
create_directories(
    "batch_{id}",
    id=range(1000),
    run_command="cd batch_{id} && python prepare.py"
)

# Stage 2: Process
run_commands(
    "cd batch_{id} && python process.py",
    id=range(1000)
)

# Stage 3: Collect
run_commands(
    "cp batch_{id}/output.csv results/batch_{id}.csv",
    id=range(1000)
)
```

### 3. Testing Matrix

```python
from dir_wand import create_directories

browsers = ["chrome", "firefox", "safari", "edge"]
platforms = ["linux", "macos", "windows", "windows"]

create_directories(
    "test_{browser}_{platform}",
    output_dir="/tests",
    browser=browsers,
    platform=platforms,
    run_command="cd test_{browser}_{platform} && pytest"
)
```

## Best Practices

### 1. Use Context Managers for Cleanup

```python
from dir_wand import create_directories
import shutil
from contextlib import contextmanager

@contextmanager
def temporary_experiments(num_experiments):
    """Create temporary experiment directories."""
    stats = create_directories(
        "temp_exp_{id}",
        id=range(num_experiments),
        silent=True
    )

    try:
        yield stats
    finally:
        # Cleanup
        for i in range(num_experiments):
            shutil.rmtree(f"temp_exp_{i}", ignore_errors=True)

# Usage
with temporary_experiments(10) as stats:
    # Do work with the directories
    print(f"Working with {stats['directories']} directories")
# Automatically cleaned up
```

### 2. Validate Parameters

```python
from dir_wand import create_directories

def validated_create(template, ids):
    """Create directories with parameter validation."""
    # Validate
    if not isinstance(ids, (list, range)):
        raise TypeError("ids must be a list or range")

    if isinstance(ids, list) and not all(isinstance(i, int) for i in ids):
        raise ValueError("All IDs must be integers")

    # Create
    return create_directories(template=template, id=ids)
```

### 3. Log Operations

```python
import logging
from dir_wand import create_directories

logging.basicConfig(level=logging.INFO)

def logged_create(**kwargs):
    """Create directories with logging."""
    logging.info(f"Creating directories with template: {kwargs.get('template')}")

    stats = create_directories(**kwargs)

    logging.info(f"Created {stats['directories']} directories")
    logging.info(f"Executed {stats.get('commands', 0)} commands")

    return stats
```

## See Also

- [API Reference](../api/api.md) - Complete API documentation
- [Examples Directory](https://github.com/WillJRoper/dir-wand/tree/main/examples) - Example scripts
- [Basic Examples](../examples/basic.md) - Usage examples
- [CLI Guide](getting-started.md) - Command-line interface
