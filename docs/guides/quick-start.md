# Quick Start Guide

Get up and running with WAND in minutes.

## 5-Minute Quick Start

### 1. Install WAND

```bash
pip install dir-wand
```

### 2. Create a Template

```bash
mkdir "experiment_{num}"
echo "Run: {num}" > "experiment_{num}/config.txt"
```

### 3. Generate Copies

```bash
dir-wand --template "experiment_{num}" --num 0-9
```

Done! You now have 10 experiment directories.

## Common Use Cases

### Scientific Simulations

```bash
# Create template
mkdir "sim_{scenario}_{seed}"
cat > "sim_{scenario}_{seed}/config.yaml" << 'EOF'
scenario: {scenario}
random_seed: {seed}
output: results_{scenario}_{seed}.csv
EOF

# Generate all combinations
dir-wand --template "sim_{scenario}_{seed}" \
  -scenario baseline treatment control \
  -seed 100 200 300
```

### Batch Data Processing

```bash
# Template with processing script
mkdir "job_{id}"
cat > "job_{id}/process.sh" << 'EOF'
#!/bin/bash
python analyze.py --input data_{id}.csv --output result_{id}.csv
EOF
chmod +x "job_{id}/process.sh"

# Create jobs and run them
dir-wand --template "job_{id}" --id 0-99 \
  --run "cd job_{id} && ./process.sh"
```

### Testing Multiple Configurations

```bash
# Template for different configs
mkdir "test_{browser}_{platform}"
cat > "test_{browser}_{platform}/test_config.json" << 'EOF'
{
  "browser": "{browser}",
  "platform": "{platform}",
  "timeout": 30
}
EOF

# Generate test directories
dir-wand --template "test_{browser}_{platform}" \
  -browser chrome firefox safari \
  -platform linux macos windows
```

## Placeholder Syntax

### In File Names

```
experiment_{num}/config_{num}.yaml
```

### In File Contents

```yaml
# config.yaml
experiment_id: {num}
name: "Experiment {num}"
parameters:
  seed: {seed}
  iterations: {iterations}
```

### In Commands

```bash
dir-wand --template exp_{num} --num 0-5 \
  --run "python run.py --exp {num}"
```

## Value Specification

### Range

```bash
--num 0-99        # 0, 1, 2, ..., 99
--seed 1000-1010  # 1000, 1001, ..., 1010
```

### List

```bash
-condition A B C              # Three values
-model resnet vgg transformer # Three models
```

### File

```bash
# values.txt contains one value per line
--ids values.txt
```

## Using Swapfiles

For complex scenarios with many placeholders:

```yaml
# swapfile.yaml
experiment_id:
  range: 0-99
model:
  list:
    - resnet50
    - vgg16
    - inception
learning_rate:
  list: [0.001, 0.01, 0.1]
batch_size:
  range: 16-64
```

```bash
dir-wand --template exp_{experiment_id} --swapfile swapfile.yaml
```

## Running Commands

### Execute After Each Copy

```bash
dir-wand --template job_{id} --id 0-9 \
  --run "cd job_{id} && python run.py"
```

### Execute in Existing Directories

```bash
# No template, just run commands
dir-wand --run "cd exp_{num} && python analyze.py" --num 0-99
```

### Multiple Commands

```bash
dir-wand --template exp_{num} --num 0-5 \
  --run "cd exp_{num} && python train.py && python evaluate.py"
```

## Advanced Features

### Silent Mode

```bash
dir-wand --template exp_{num} --num 0-1000 --silent
```

### Custom Root Directory

```bash
dir-wand --template exp_{num} --root /data/experiments --num 0-99
```

### Creating Swapfiles

Generate a swapfile with all combinations:

```bash
dir-wand --swapfile output.yaml --num 0-9 -condition A B C
# Creates a swapfile with 30 combinations (10 × 3)
```

## Tips and Tricks

### Use Absolute Paths

```bash
dir-wand --template /full/path/to/template_{num} --num 0-5
```

### Check Template Structure First

```bash
# Dry run: create just one copy to verify
dir-wand --template exp_{num} --num 0-0
```

### Multiple Placeholders Must Match

```bash
# ✓ Correct: same number of values
dir-wand --template exp_{id}_{seed} --id 0-4 --seed 100-104

# ✗ Wrong: mismatched lengths
dir-wand --template exp_{id}_{seed} --id 0-4 --seed 100-105
```

### Preserve Permissions

WAND automatically preserves:

- Executable permissions
- Symbolic links
- File permissions

### Parallel Execution

Commands run concurrently on separate threads:

```bash
# All 100 jobs start immediately
dir-wand --template job_{id} --id 0-99 --run "cd job_{id} && ./run.sh"
```

## Next Steps

- [Full User Guide](templates.md)
- [Placeholder System Details](placeholders.md)
- [Swapfile Documentation](swapfiles.md)
- [Command Execution Guide](commands.md)
- [Real-World Examples](../examples/basic.md)

## Cheat Sheet

```bash
# Basic usage
dir-wand --template <template_path> --<placeholder> <values>

# With root directory
dir-wand --template <template> --root <output_dir> --<placeholder> <values>

# With command execution
dir-wand --template <template> --<placeholder> <values> --run "<command>"

# Using swapfile
dir-wand --template <template> --swapfile <yaml_file>

# Run command only (no template)
dir-wand --run "<command>" --<placeholder> <values>

# Silent mode
dir-wand --template <template> --<placeholder> <values> --silent

# Create swapfile
dir-wand --swapfile <output.yaml> --<placeholder1> <values1> --<placeholder2> <values2>
```
