# Working with Templates

Templates are the foundation of WAND. This guide covers everything you need to know about creating and managing templates.

## What is a Template?

A template is a directory structure that serves as a blueprint for creating multiple copies. Templates can contain:

- **Directories** (empty or nested)
- **Files** (text, binary, executables)
- **Symbolic links**
- **Placeholders** (in paths and file contents)

## Creating Templates

### Basic Template Structure

A simple template might look like:

```
experiment_{num}/
├── config.yaml
├── scripts/
│   ├── run.py
│   └── analyze.sh
└── data/
    └── .gitkeep
```

### Placeholders in Directory Names

```bash
mkdir "run_{experiment_id}_{condition}"
```

When copied with `experiment_id=1` and `condition=control`:

```
run_1_control/
```

### Placeholders in File Names

```bash
mkdir template_{num}
touch "template_{num}/result_{num}.csv"
```

Creates files like `result_0.csv`, `result_1.csv`, etc.

### Placeholders in File Contents

Text files can contain placeholders that will be replaced:

```yaml
# config.yaml
experiment:
  id: {num}
  name: "Experiment {num}"
  output_dir: "results_{num}"
  seed: {seed}
```

## File Types in Templates

### Text Files

Text files (detected by UTF-8 encoding) can contain placeholders:

```python
# script.py
import random

SEED = {seed}
EXPERIMENT_ID = {exp_id}
OUTPUT_FILE = "results_{exp_id}.csv"

random.seed(SEED)
# ... rest of script
```

### Binary Files

Binary files are copied as-is without placeholder replacement:

```bash
# Images, compiled binaries, etc. are copied exactly
cp logo.png template_{num}/
cp compiled_program template_{num}/
```

### Executable Files

Executable permissions are preserved:

```bash
# Create executable script
cat > template_{num}/run.sh << 'EOF'
#!/bin/bash
echo "Running experiment {num}"
python main.py --id {num}
EOF

chmod +x template_{num}/run.sh
```

After copying, `run.sh` remains executable.

### Symbolic Links

Symbolic links are preserved (not followed):

```bash
# Create symlink in template
ln -s /shared/data template_{num}/data_link
```

The copy will have the same symlink, pointing to the same target.

### Hidden Files

Hidden files (starting with `.`) are copied:

```bash
touch template_{num}/.env
echo "SECRET_KEY={key}" > template_{num}/.env
```

### Empty Directories

Empty directories are created in copies:

```bash
mkdir -p template_{num}/empty_dir
```

## Template Best Practices

### 1. Use Descriptive Placeholder Names

```bash
# Good
experiment_{scenario}_{replicate_id}

# Less clear
experiment_{s}_{r}
```

### 2. Keep Templates Self-Contained

Include all necessary files and scripts in the template:

```
experiment_{num}/
├── config_{num}.yaml    # Configuration
├── run.sh               # Execution script
├── requirements.txt     # Dependencies
└── README.md            # Documentation
```

### 3. Use Relative Paths

In template files, use relative paths:

```python
# Good
with open('results_{num}.csv', 'w') as f:

# Avoid
with open('/absolute/path/results_{num}.csv', 'w') as f:
```

### 4. Document Expected Placeholders

Add a README or comment in your template:

```yaml
# config.yaml
# Required placeholders:
#   {num} - Experiment number (0-99)
#   {seed} - Random seed (integer)
#   {condition} - Experimental condition (A, B, or C)

experiment_id: {num}
random_seed: {seed}
condition: {condition}
```

### 5. Test With a Single Copy First

```bash
# Test template creation with one copy
dir-wand --template exp_{num} --num 0-0

# Verify it looks correct
ls -la exp_0/

# Then create all copies
dir-wand --template exp_{num} --num 0-99
```

## Advanced Template Patterns

### Nested Placeholders

Use the same placeholder in multiple places:

```
project_{id}/
├── config_{id}.yaml
├── src/
│   └── main_{id}.py
└── output/
    └── results_{id}.csv
```

All occurrences of `{id}` will be replaced with the same value.

### Multiple Independent Placeholders

```
exp_{scenario}_{seed}/
├── config.yaml
└── run.sh
```

```yaml
# config.yaml
scenario: {scenario}
seed: {seed}
output: "results_{scenario}_{seed}.csv"
```

### Conditional Content with Placeholders

While WAND doesn't support conditionals directly, you can use placeholder values creatively:

```yaml
# config.yaml
use_feature_a: {feature_a_enabled}  # Pass "true" or "false"
use_feature_b: {feature_b_enabled}
```

Then:

```bash
dir-wand --template exp_{num} \
  --num 0-3 \
  -feature_a_enabled true false true false \
  -feature_b_enabled false false true true
```

### Template Hierarchies

Create sub-templates for different parts:

```
main_template_{id}/
├── config_{id}.yaml
├── module_a/
│   ├── settings_{id}.yaml
│   └── data/
└── module_b/
    ├── settings_{id}.yaml
    └── data/
```

## Template Validation

### Check for Missing Placeholders

WAND will error if a placeholder in the template isn't provided:

```bash
# Template has {num} and {seed}
# Only provide {num}
dir-wand --template exp_{num}_{seed} --num 0-5

# Error: Missing placeholders: {'seed'}
```

### Verify Placeholder Consistency

If using multiple placeholders, ensure all value lists have the same length:

```bash
# Correct
dir-wand --template exp_{id}_{seed} --id 0-9 --seed 100-109

# Error: mismatched lengths
dir-wand --template exp_{id}_{seed} --id 0-9 --seed 100-110
```

## Template Organization

### Single Template Directory

For simple projects:

```
templates/
└── experiment_{num}/
    ├── config.yaml
    └── run.sh
```

```bash
dir-wand --template templates/experiment_{num} --num 0-99
```

### Multiple Template Types

For complex projects:

```
templates/
├── simulation_{id}/
├── analysis_{id}/
└── visualization_{id}/
```

```bash
# Create simulations
dir-wand --template templates/simulation_{id} --id 0-99

# Create analyses
dir-wand --template templates/analysis_{id} --id 0-99

# Create visualizations
dir-wand --template templates/visualization_{id} --id 0-99
```

### Version-Controlled Templates

Keep templates in version control:

```bash
git init
git add template_{num}/
git commit -m "Add experiment template"
```

Benefits:

- Track template changes over time
- Share templates with collaborators
- Reproduce old experiments with historical templates

## Common Template Patterns

### Scientific Simulation

```
sim_{scenario}_{replicate}/
├── config.yaml          # Simulation parameters
├── run_simulation.sh    # Execution script
├── analysis.py          # Post-processing
├── input/               # Input data
└── output/              # Results (empty initially)
```

### Machine Learning Experiment

```
ml_exp_{model}_{dataset}/
├── config.yaml          # Hyperparameters
├── train.py             # Training script
├── evaluate.py          # Evaluation script
├── requirements.txt     # Dependencies
├── data/                # Dataset location
└── checkpoints/         # Model checkpoints (empty)
```

### Data Processing Job

```
job_{batch_id}/
├── process.sh           # Processing script
├── config.json          # Job configuration
├── input/               # Input files
│   └── data_{batch_id}.csv
└── output/              # Output directory (empty)
    └── .gitkeep
```

### Testing Environment

```
test_{env}_{version}/
├── docker-compose.yaml  # Environment setup
├── test_config.yaml     # Test configuration
├── tests/               # Test scripts
│   ├── unit/
│   └── integration/
└── results/             # Test results (empty)
```

## Troubleshooting Templates

### Template Not Found

```bash
# Use absolute path
dir-wand --template /full/path/to/template_{num} --num 0-5

# Or navigate to the directory
cd /path/to/templates
dir-wand --template template_{num} --num 0-5
```

### Placeholders Not Replaced

Check that:

1. Placeholder names match exactly (case-sensitive)
2. Placeholders use valid characters (alphanumeric + underscore)
3. Files with placeholders are text (UTF-8) encoded

### Permission Issues

```bash
# Ensure you have write permissions to the output directory
ls -la /output/path

# Or choose a different output directory
dir-wand --template exp_{num} --root ~/experiments --num 0-5
```

### Symbolic Links Not Working

Ensure the link target exists:

```bash
# Check link target
ls -la template_{num}/
lrwxr-xr-x  1 user  staff  20 Jan 10 10:00 data_link -> /shared/data

# Verify target exists
ls -la /shared/data
```

## Next Steps

- Learn about the [placeholder system](placeholders.md) in detail
- Explore [swapfiles](swapfiles.md) for complex templates
- See [command execution](commands.md) patterns
- Check out [examples](../examples/basic.md) for real-world templates
