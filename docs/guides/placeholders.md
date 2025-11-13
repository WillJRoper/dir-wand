# Placeholder System

Placeholders are the core feature of WAND, allowing you to create parameterized templates. This guide covers everything about using placeholders effectively.

## Placeholder Syntax

### Basic Format

Placeholders use curly braces:

```
{placeholder_name}
```

### Naming Rules

**Valid placeholder names:**

- Must contain only alphanumeric characters and underscores
- Can start with a letter or underscore
- Case-sensitive

**Examples of valid placeholders:**

- `{num}`
- `{experiment_id}`
- `{seed_value}`
- `{param_123}`
- `{_private}`
- `{CONSTANT}`

**Examples of invalid placeholders:**

- `{my-param}` - contains hyphen
- `{my param}` - contains space
- `{my.param}` - contains dot
- `{123num}` - starts with number (technically valid in regex but not recommended)

## Where to Use Placeholders

### In Directory Names

```bash
mkdir "experiment_{scenario}_{replicate_id}"
```

Result: `experiment_baseline_1/`, `experiment_treatment_1/`, etc.

### In File Names

```bash
touch "experiment_{num}/config_{num}.yaml"
```

Result: `config_0.yaml`, `config_1.yaml`, etc.

### In File Contents

Any text file can contain placeholders:

```yaml
# config.yaml
experiment:
  id: {experiment_id}
  name: "Experiment {experiment_id}"
  seed: {random_seed}
  output: "results_{experiment_id}.csv"
```

```python
# script.py
EXPERIMENT_ID = {exp_id}
RANDOM_SEED = {seed}
OUTPUT_DIR = "output_{exp_id}"
```

```bash
#!/bin/bash
# run.sh
echo "Running experiment {num} with seed {seed}"
python main.py --id {num} --seed {seed}
```

### In Command Arguments

```bash
dir-wand --template exp_{num} --num 0-5 \
  --run "cd exp_{num} && python run.py --id {num}"
```

## Specifying Replacement Values

### Method 1: Range (Double Dash)

Use an inclusive range of integers:

```bash
--num 0-10     # Creates: 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10
--seed 100-105 # Creates: 100, 101, 102, 103, 104, 105
```

**Note:** Both ends are inclusive!

### Method 2: Explicit List (Single Dash)

Provide space-separated values:

```bash
-condition control treatment placebo
-model resnet vgg inception transformer
-learning_rate 0.001 0.01 0.1
```

Values can be:

- Numbers: `-num 1 2 3 5 8 13`
- Strings: `-name alice bob charlie`
- Mixed: `-param a 1 b 2 c 3`

### Method 3: File Reference (Double Dash)

Read values from a file (one value per line):

```bash
--ids experiment_ids.txt
```

```
# experiment_ids.txt
exp_001
exp_002
exp_003
```

## Multiple Placeholders

### Same Number of Values Required

All placeholders must have the same number of values:

```bash
# Correct: 3 values each
dir-wand --template exp_{id}_{seed} \
  --id 0-2 \
  --seed 100-102

# Error: mismatched lengths (3 vs 4)
dir-wand --template exp_{id}_{seed} \
  --id 0-2 \
  --seed 100-103
```

### Corresponding Values

Values at the same index are used together:

```bash
dir-wand --template exp_{id}_{condition} \
  --id 0-2 \
  -condition A B C
```

Creates:

- `exp_0_A/` (id=0, condition=A)
- `exp_1_B/` (id=1, condition=B)
- `exp_2_C/` (id=2, condition=C)

### All Combinations via Swapfile

For all combinations, use swapfile creation:

```bash
dir-wand --swapfile combos.yaml \
  --id 0-1 \
  -condition A B
```

Creates a swapfile with 4 combinations:

- id=0, condition=A
- id=0, condition=B
- id=1, condition=A
- id=1, condition=B

## Advanced Placeholder Usage

### Reusing the Same Placeholder

Use a placeholder multiple times:

```yaml
# config_{num}.yaml
experiment_id: {num}
input_file: "data_{num}.csv"
output_file: "results_{num}.csv"
log_file: "experiment_{num}.log"
```

All instances of `{num}` get the same value.

### Nested Structures

```
project_{id}/
├── config_{id}.yaml
├── src_{id}/
│   └── main_{id}.py
└── output_{id}/
    ├── results_{id}.csv
    └── logs_{id}.txt
```

### String Formatting

Since WAND uses Python's `str.format()`, you can use format specifications:

```python
# In a Python file
EXPERIMENT_ID = {num:03d}  # Zero-padded: 001, 002, etc.
PERCENTAGE = {value:.2f}%   # Two decimal places: 3.14%
```

```bash
dir-wand --template exp_{num:03d} --num 1-10
# Creates: exp_001/, exp_002/, ..., exp_010/
```

## Placeholder Validation

### Missing Placeholders

WAND validates that all required placeholders are provided:

```bash
# Template has {num} and {seed}
dir-wand --template exp_{num}_{seed} --num 0-5

# Error: Missing placeholders: {'seed'}
```

### Extra Placeholders

Extra provided placeholders are ignored (no error):

```bash
# Template only has {num}
dir-wand --template exp_{num} --num 0-5 --seed 42 --extra hello

# Works fine; seed and extra are ignored
```

### Type Conversion

All values are converted to strings during replacement:

```bash
--num 42        # "42"
--pi 3.14159    # "3.14159"
-flag true      # "true"
```

## Best Practices

### 1. Use Descriptive Names

```bash
# Good
{experiment_id}
{random_seed}
{learning_rate}

# Less clear
{e}
{r}
{l}
```

### 2. Be Consistent

Use the same placeholder name throughout your template:

```bash
# Good: consistent use of {num}
experiment_{num}/config_{num}.yaml

# Confusing: mixing {num} and {id}
experiment_{num}/config_{id}.yaml
```

### 3. Document Required Placeholders

Add comments or README files:

```yaml
# config.yaml
# Required placeholders:
#   {experiment_id}: Unique experiment identifier (integer)
#   {random_seed}: Random seed for reproducibility (integer)
#   {model_name}: Name of the model (string)

experiment_id: {experiment_id}
random_seed: {random_seed}
model: {model_name}
```

### 4. Use Semantic Naming

Names should reflect their purpose:

```bash
# Scientific experiments
{hypothesis_id}
{treatment_group}
{replicate_number}

# Machine learning
{model_architecture}
{learning_rate}
{batch_size}

# Data processing
{batch_id}
{processing_date}
{data_source}
```

### 5. Avoid Special Characters

Stick to alphanumeric and underscores:

```bash
# Good
{model_name}
{experiment_id}

# Bad
{model-name}   # Hyphen not allowed
{experiment.id} # Dot not allowed
```

## Placeholder Patterns

### Sequential IDs

```bash
dir-wand --template job_{id} --id 0-999
# Creates: job_0/, job_1/, ..., job_999/
```

### Date-Based

```bash
# Create values file with dates
seq -f "2024-01-%02g" 1 31 > dates.txt

dir-wand --template "backup_{date}" --date dates.txt
```

### Categorical Values

```bash
dir-wand --template "test_{browser}_{os}" \
  -browser chrome firefox safari edge \
  -os linux macos windows windows
```

### Hierarchical IDs

```bash
-id exp_001 exp_002 exp_003 exp_004 \
-subid a b c d
```

Creates: `exp_001_a/`, `exp_002_b/`, etc.

## Troubleshooting

### Placeholder Not Replaced

**Symptoms:** Placeholder appears literally in output

**Causes:**

1. Binary file (placeholders only work in text files)
2. Placeholder name mismatch
3. Invalid placeholder syntax

**Solutions:**

```bash
# Check file is text
file template_{num}/config.txt

# Verify placeholder names match exactly
# {Num} ≠ {num} (case-sensitive)

# Check syntax
{num}     # ✓ Correct
{ num }   # ✗ Spaces not allowed
{num }    # ✗ Trailing space
```

### Value Count Mismatch

**Error:**

```
ValueError: All swaps must have the same number of elements.
```

**Solution:**

```bash
# Check value counts
--num 0-5    # 6 values (0, 1, 2, 3, 4, 5)
--seed 0-4   # 5 values (0, 1, 2, 3, 4)
# Mismatch!

# Fix: make counts equal
--num 0-4
--seed 0-4
```

### Unexpected Replacement

**Symptoms:** Placeholder replaced with wrong value

**Cause:** Values at same index are used together

**Solution:**

```bash
# If you want all combinations, use swapfile creation:
dir-wand --swapfile all_combos.yaml --num 0-2 --letter a b c

# Then use the swapfile:
dir-wand --template exp_{num}_{letter} --swapfile all_combos.yaml
```

## See Also

- [Templates Guide](templates.md) - Creating templates
- [Swapfiles Guide](swapfiles.md) - Managing complex replacements
- [API Reference](../api/utils.md) - `swap_in_str()` function
- [Examples](../examples/basic.md) - Real-world usage
