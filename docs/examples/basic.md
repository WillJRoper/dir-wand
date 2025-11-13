# Basic Examples

This page provides simple, practical examples to get you started with WAND.

## Example 1: Sequential Experiments

Create 10 experiment directories with sequential IDs.

### Setup

```bash
# Create template
mkdir "experiment_{num}"
echo "Experiment ID: {num}" > "experiment_{num}/config.txt"
echo "#!/bin/bash" > "experiment_{num}/run.sh"
echo "echo 'Running experiment {num}'" >> "experiment_{num}/run.sh"
chmod +x "experiment_{num}/run.sh"
```

### Execution

```bash
dir-wand --template "experiment_{num}" --num 0-9
```

### Result

```
experiment_0/
├── config.txt (contains: "Experiment ID: 0")
└── run.sh

experiment_1/
├── config.txt (contains: "Experiment ID: 1")
└── run.sh

...

experiment_9/
├── config.txt (contains: "Experiment ID: 9")
└── run.sh
```

## Example 2: Multiple Conditions

Create experiments with different conditions.

### Setup

```bash
# Create template
mkdir "test_{condition}"
cat > "test_{condition}/config.yaml" << 'EOF'
condition: {condition}
replicate: 1
output_file: "results_{condition}.csv"
EOF
```

### Execution

```bash
dir-wand --template "test_{condition}" \
  -condition control treatment1 treatment2 placebo
```

### Result

Four directories: `test_control/`, `test_treatment1/`, `test_treatment2/`, `test_placebo/`

## Example 3: Paired Values

Create directories with paired parameter values.

### Setup

```bash
# Create template
mkdir "sim_{scenario}_{seed}"
cat > "sim_{scenario}_{seed}/config.yaml" << 'EOF'
scenario: {scenario}
random_seed: {seed}
output: "output_{scenario}_{seed}.csv"
EOF
```

### Execution

```bash
dir-wand --template "sim_{scenario}_{seed}" \
  -scenario baseline enhanced optimized \
  -seed 100 200 300
```

### Result

Creates:

- `sim_baseline_100/`
- `sim_enhanced_200/`
- `sim_optimized_300/`

Each with corresponding values in `config.yaml`.

## Example 4: Using Value Files

Use a file to specify values.

### Setup

Create a file with experiment IDs:

```bash
cat > experiment_ids.txt << 'EOF'
exp_alpha
exp_beta
exp_gamma
exp_delta
EOF
```

Create template:

```bash
mkdir "job_{id}"
echo "Job: {id}" > "job_{id}/info.txt"
```

### Execution

```bash
dir-wand --template "job_{id}" --id experiment_ids.txt
```

### Result

Creates: `job_exp_alpha/`, `job_exp_beta/`, `job_exp_gamma/`, `job_exp_delta/`

## Example 5: Running Commands

Create directories and execute commands.

### Setup

```bash
mkdir "task_{num}"
cat > "task_{num}/process.sh" << 'EOF'
#!/bin/bash
echo "Processing task {num}"
sleep 1
echo "Task {num} complete" > result_{num}.txt
EOF

chmod +x "task_{num}/process.sh"
```

### Execution

```bash
dir-wand --template "task_{num}" --num 0-4 \
  --run "cd task_{num} && ./process.sh"
```

### Result

Creates 5 directories and runs `process.sh` in each, concurrently.

## Example 6: Data Processing Pipeline

Process multiple data files.

### Setup

```bash
# Create template
mkdir "batch_{id}"
cat > "batch_{id}/process.py" << 'EOF'
#!/usr/bin/env python3
import sys

batch_id = "{id}"
print(f"Processing batch {batch_id}")

# Simulate processing
with open(f"input_{batch_id}.csv", "r") as f_in:
    with open(f"output_{batch_id}.csv", "w") as f_out:
        for line in f_in:
            f_out.write(line.upper())

print(f"Batch {batch_id} complete")
EOF

chmod +x "batch_{id}/process.py"

# Create sample input files in template
for i in {0..4}; do
    echo "data,values,here" > "batch_{id}/input_{id}.csv"
done
```

### Execution

```bash
dir-wand --template "batch_{id}" --id 0-4 \
  --run "cd batch_{id} && python3 process.py"
```

## Example 7: Using Swapfiles

Manage complex configurations with swapfiles.

### Setup

Create a swapfile:

```yaml
# config.yaml
experiment_id:
  range: 0-9

model_type:
  list:
    - linear
    - neural
    - ensemble

learning_rate:
  list:
    - 0.001
    - 0.01
    - 0.1
    - 0.001
    - 0.01
    - 0.1
    - 0.001
    - 0.01
    - 0.1
    - 0.001

batch_size:
  list:
    - 32
    - 32
    - 32
    - 64
    - 64
    - 64
    - 128
    - 128
    - 128
    - 256
```

Create template:

```bash
mkdir "ml_exp_{experiment_id}"
cat > "ml_exp_{experiment_id}/config.yaml" << 'EOF'
experiment_id: {experiment_id}
model_type: {model_type}
learning_rate: {learning_rate}
batch_size: {batch_size}
EOF
```

### Execution

```bash
dir-wand --template "ml_exp_{experiment_id}" --swapfile config.yaml
```

## Example 8: Running in Existing Directories

Execute commands in already created directories.

### Setup

Assume you already have `exp_0/` through `exp_9/`.

### Execution

```bash
# No --template, just run commands
dir-wand --run "cd exp_{num} && python analyze.py" --num 0-9
```

This runs `analyze.py` in each existing directory.

## Example 9: Custom Output Directory

Create copies in a specific location.

### Setup

```bash
mkdir "job_{id}"
echo "Job {id}" > "job_{id}/info.txt"
```

### Execution

```bash
dir-wand --template "job_{id}" --root /tmp/jobs --id 0-9
```

### Result

Creates directories in `/tmp/jobs/`:

- `/tmp/jobs/job_0/`
- `/tmp/jobs/job_1/`
- ...
- `/tmp/jobs/job_9/`

## Example 10: Silent Mode

Suppress all output for use in scripts.

### Execution

```bash
#!/bin/bash

# Run WAND silently
dir-wand --template "exp_{num}" --num 0-99 --silent

# Check exit code
if [ $? -eq 0 ]; then
    echo "Successfully created 100 experiments"
else
    echo "Error creating experiments"
    exit 1
fi
```

## Example 11: Creating Swapfiles

Generate all combinations of parameters.

### Execution

```bash
# Create all combinations of num (0-2) and letter (A, B, C)
dir-wand --swapfile all_combos.yaml --num 0-2 -letter A B C
```

### Result

`all_combos.yaml` contains 9 combinations (3 × 3):

```yaml
letter:
  list: [A, A, A, B, B, B, C, C, C]
num:
  list: [0, 1, 2, 0, 1, 2, 0, 1, 2]
```

### Usage

```bash
dir-wand --template "exp_{num}_{letter}" --swapfile all_combos.yaml
```

## Example 12: Complex Directory Structure

Create nested directory structures.

### Setup

```bash
# Create complex template
mkdir -p "project_{id}/src"
mkdir -p "project_{id}/tests"
mkdir -p "project_{id}/data/input"
mkdir -p "project_{id}/data/output"
mkdir -p "project_{id}/logs"

# Add files
echo "Project {id}" > "project_{id}/README.md"
echo "# Project {id} source" > "project_{id}/src/main.py"
echo "# Tests for project {id}" > "project_{id}/tests/test_main.py"
touch "project_{id}/data/input/.gitkeep"
touch "project_{id}/data/output/.gitkeep"
```

### Execution

```bash
dir-wand --template "project_{id}" --id 0-4
```

### Result

Each directory has the complete structure:

```
project_0/
├── README.md
├── src/
│   └── main.py
├── tests/
│   └── test_main.py
├── data/
│   ├── input/
│   │   └── .gitkeep
│   └── output/
│       └── .gitkeep
└── logs/
```

## Tips and Tricks

### Dry Run

Test with a single copy first:

```bash
# Create just one to verify
dir-wand --template "exp_{num}" --num 0-0

# If it looks good, create all
dir-wand --template "exp_{num}" --num 0-99
```

### Cleanup

Remove all created directories:

```bash
# Be careful with this!
dir-wand --run "rm -rf exp_{num}" --num 0-99
```

### Verify Structure

Check what WAND will create:

```bash
# WAND shows the template structure before copying
dir-wand --template "exp_{num}" --num 0-1
```

Look at the "Template structure" section in the output.

## Next Steps

- [Scientific Computing Examples](scientific.md)
- [Data Processing Examples](data-processing.md)
- [Testing Examples](testing.md)
- [User Guide](../guides/getting-started.md)
