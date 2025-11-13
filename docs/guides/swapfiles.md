# Swapfiles

Swapfiles are YAML files that define placeholder values for complex scenarios. This guide explains how to create and use swapfiles effectively.

## What is a Swapfile?

A swapfile is a YAML file that specifies replacement values for placeholders. It's useful when:

- You have many placeholders
- You need to document the values
- You want to reuse the same values across multiple runs
- You need all combinations of values
- You want version-controlled configurations

## Basic Swapfile Format

```yaml
placeholder_name:
  list:
    - value1
    - value2
    - value3
```

### Example

```yaml
# swapfile.yaml
experiment_id:
  list:
    - 0
    - 1
    - 2

condition:
  list:
    - control
    - treatment
    - placebo
```

Usage:

```bash
dir-wand --template exp_{experiment_id}_{condition} --swapfile swapfile.yaml
```

## Swapfile Value Types

### List Format

Explicit list of values:

```yaml
model:
  list:
    - resnet50
    - vgg16
    - inception
    - transformer
```

### Range Format

Inclusive integer range:

```yaml
seed:
  range: 100-200  # Creates 101 values: 100, 101, ..., 200
```

### File Reference

Load values from an external file:

```yaml
experiment_ids:
  file: /path/to/ids.txt
```

Where `ids.txt` contains one value per line:

```
exp_001
exp_002
exp_003
```

## Using Swapfiles

### Basic Usage

```bash
dir-wand --template template_{num} --swapfile config.yaml
```

### With Additional Arguments

You can combine swapfile with command-line arguments:

```bash
dir-wand --template exp_{num} --swapfile config.yaml --run "python run.py"
```

### Swapfile Only

```bash
# No --template means run commands in existing directories
dir-wand --run "cd exp_{num} && python analyze.py" --swapfile config.yaml
```

## Creating Swapfiles

### Manual Creation

Create a YAML file with your values:

```yaml
# experiment_config.yaml
num:
  range: 0-9

scenario:
  list:
    - baseline
    - treatment

seed:
  list:
    - 42
    - 43
    - 44
    - 45
    - 46
    - 47
    - 48
    - 49
    - 50
    - 51
```

### Automatic Generation

Generate all combinations using WAND:

```bash
dir-wand --swapfile output.yaml --num 0-2 -condition A B C
```

This creates a swapfile with all 9 combinations (3 × 3):

```yaml
condition:
  list:
  - A
  - A
  - A
  - B
  - B
  - B
  - C
  - C
  - C
num:
  list:
  - 0
  - 1
  - 2
  - 0
  - 1
  - 2
  - 0
  - 1
  - 2
```

## Advanced Swapfile Patterns

### Machine Learning Hyperparameter Grid

```yaml
# ml_grid.yaml
model_architecture:
  list:
    - resnet50
    - vgg16
    - inception_v3

learning_rate:
  list:
    - 0.0001
    - 0.001
    - 0.01
    - 0.1

batch_size:
  range: 16-64  # 16, 32, 48, 64 (steps of 1)

optimizer:
  list:
    - adam
    - sgd
    - rmsprop
```

```bash
# First create all combinations
dir-wand --swapfile all_combos.yaml \
  --model resnet vgg inception \
  --lr 0.0001 0.001 0.01 0.1 \
  --batch 16 32 48 64 \
  --opt adam sgd rmsprop

# Then use the swapfile
# This creates 3 × 4 × 4 × 3 = 144 experiments!
dir-wand --template ml_exp_{model}_{lr}_{batch}_{opt} --swapfile all_combos.yaml
```

### Scientific Simulation Suite

```yaml
# simulation_suite.yaml
model_variant:
  list:
    - standard
    - enhanced
    - experimental

initial_condition:
  file: /data/initial_conditions.txt

timesteps:
  range: 1000-10000

output_frequency:
  list:
    - 10
    - 50
    - 100

random_seed:
  range: 0-99
```

### Testing Matrix

```yaml
# test_matrix.yaml
browser:
  list:
    - chrome
    - firefox
    - safari
    - edge

platform:
  list:
    - linux
    - macos
    - windows

test_suite:
  list:
    - unit
    - integration
    - e2e
```

## Swapfile Best Practices

### 1. Document Your Swapfile

Add comments explaining the purpose:

```yaml
# Hyperparameter search configuration
# Last updated: 2024-01-15
# Total combinations: 48 (3 models × 4 LRs × 4 batch sizes)

model:
  list:
    - resnet50    # Baseline model
    - vgg16       # Comparison
    - inception   # High-capacity option

learning_rate:
  list: [0.0001, 0.001, 0.01, 0.1]

batch_size:
  range: 16-64
```

### 2. Use Consistent Naming

```yaml
# Good: clear, consistent names
experiment_id:
  range: 0-99

random_seed:
  range: 42-142

# Less clear
e:
  range: 0-99

r:
  range: 42-142
```

### 3. Version Control Swapfiles

```bash
git add swapfiles/
git commit -m "Add experiment configuration swapfile"
```

Benefits:

- Track changes to experimental parameters
- Reproduce old experiments
- Share configurations with collaborators

### 4. Organize by Project

```
swapfiles/
├── ml_experiments/
│   ├── grid_search.yaml
│   └── random_search.yaml
├── simulations/
│   ├── baseline.yaml
│   └── sensitivity_analysis.yaml
└── testing/
    └── test_matrix.yaml
```

### 5. Validate Before Large Runs

Test with a subset first:

```yaml
# test_swapfile.yaml
num:
  range: 0-2  # Just 3 values for testing

model:
  list:
    - resnet50  # Just one model
```

```bash
# Test with small swapfile
dir-wand --template exp_{num}_{model} --swapfile test_swapfile.yaml

# If it works, use full swapfile
dir-wand --template exp_{num}_{model} --swapfile full_swapfile.yaml
```

## Combining Methods

### Swapfile + Command Line

Swapfile values take precedence:

```yaml
# config.yaml
num:
  range: 0-5
```

```bash
# num from swapfile (0-5), seed from command line
dir-wand --template exp_{num}_{seed} \
  --swapfile config.yaml \
  --seed 100-105
```

### Multiple Swapfiles

You can't use multiple swapfiles directly, but you can combine them manually:

```yaml
# combined.yaml
# From experiment_config.yaml:
experiment_id:
  range: 0-99

# From model_config.yaml:
model_name:
  list:
    - resnet
    - vgg

# From data_config.yaml:
dataset:
  list:
    - cifar10
    - imagenet
```

## Swapfile Templates

### Minimal Template

```yaml
placeholder_name:
  list:
    - value1
    - value2
```

### Complete Template

```yaml
# Project: [Project Name]
# Purpose: [Description]
# Author: [Your Name]
# Date: [YYYY-MM-DD]
# Total combinations: [Calculate n1 × n2 × ...]

placeholder1:
  list:
    - value1
    - value2

placeholder2:
  range: start-end

placeholder3:
  file: /path/to/values.txt

# Add more placeholders as needed
```

## Troubleshooting

### Invalid YAML Syntax

**Error:** `yaml.scanner.ScannerError`

**Causes:**

- Incorrect indentation (YAML uses spaces, not tabs)
- Missing colons
- Invalid characters

**Solution:**

```yaml
# Wrong: tabs used for indentation
num:
→list:  # Tab character
→→- 1

# Correct: spaces for indentation
num:
  list:  # 2 spaces
    - 1  # 4 spaces
```

### File Not Found

**Error:** `FileNotFoundError`

**Causes:**

- Swapfile path is incorrect
- Referenced file in `file:` doesn't exist

**Solutions:**

```bash
# Use absolute path
dir-wand --swapfile /full/path/to/swapfile.yaml

# Or relative to current directory
dir-wand --swapfile ./configs/swapfile.yaml

# Check referenced files exist
cat /path/to/values.txt  # Should display file contents
```

### Mismatched Lengths

**Error:** `ValueError: All swaps must have the same number of elements`

**Cause:** Different placeholders have different numbers of values

**Solution:**

Ensure all placeholders have the same count:

```yaml
# Wrong: 3 values vs 2 values
num:
  list: [1, 2, 3]
letter:
  list: [a, b]

# Correct: both have 3 values
num:
  list: [1, 2, 3]
letter:
  list: [a, b, c]
```

## Examples

### Create All Combinations

```bash
# Generate all combinations of two parameters
dir-wand --swapfile combos.yaml --x 1-3 --y 10-12

# Results in 9 combinations in combos.yaml
# Then use it
dir-wand --template exp_{x}_{y} --swapfile combos.yaml
```

### Reusable Configuration

```yaml
# base_config.yaml - reusable across projects
random_seed:
  range: 42-51  # 10 seeds for statistical significance

num_iterations:
  list:
    - 100
    - 500
    - 1000
    - 5000
```

### Incremental Experiments

```yaml
# experiment_v1.yaml
model:
  list: [resnet50]

# experiment_v2.yaml
model:
  list: [resnet50, vgg16]

# experiment_v3.yaml
model:
  list: [resnet50, vgg16, inception, transformer]
```

## See Also

- [Placeholder System](placeholders.md) - Understanding placeholders
- [Templates Guide](templates.md) - Creating templates
- [Swapfile API](../api/swapfile.md) - Technical details
- [Examples](../examples/scientific.md) - Real-world swapfile usage
