# Swapfile API Reference

The `swapfile` module provides functions for generating YAML swapfiles with all combinations of placeholder values.

## Module: `dir_wand.swapfile`

### Functions

#### `make_swapfile(yaml_path, swaps)`

Creates a YAML swapfile containing all combinations of the provided swaps.

**Parameters:**

- `yaml_path` (str): Path where the YAML file should be written
- `swaps` (dict): Dictionary mapping placeholder names to value lists

**Returns:** None

**Behavior:**

1. Generates all combinations of swap values using `get_swap_combos()`
2. Writes the combinations to a YAML file
3. Each placeholder becomes a key with a `list` containing all values for that placeholder across all combinations

**Example:**

```python
from dir_wand.swapfile import make_swapfile

swaps = {
    'num': [0, 1],
    'letter': ['a', 'b']
}

make_swapfile('output.yaml', swaps)
```

**Generated `output.yaml`:**

```yaml
letter:
  list:
  - a
  - a
  - b
  - b
num:
  list:
  - 0
  - 1
  - 0
  - 1
```

This represents the combinations: `(0, a)`, `(1, a)`, `(0, b)`, `(1, b)`.

#### `get_swap_combos(swaps)`

Generates all combinations of swaps and transposes them into swapfile format.

**Parameters:**

- `swaps` (dict): Dictionary mapping placeholder names to value lists

**Returns:** `dict` - Dictionary in swapfile format with `list` keys

**Example:**

```python
from dir_wand.swapfile import get_swap_combos

swaps = {
    'x': [1, 2],
    'y': [10, 20]
}

combos = get_swap_combos(swaps)
print(combos)
```

**Output:**

```python
{
    'x': {'list': [1, 2, 1, 2]},
    'y': {'list': [10, 10, 20, 20]}
}
```

**Combinations represented:**

1. `x=1, y=10`
2. `x=2, y=10`
3. `x=1, y=20`
4. `x=2, y=20`

#### `all_combinations(swaps)`

Generator that yields all combinations of swap values.

**Parameters:**

- `swaps` (dict): Dictionary mapping placeholder names to value lists

**Yields:** `dict` - One combination at a time

**Example:**

```python
from dir_wand.swapfile import all_combinations

swaps = {
    'a': [1, 2],
    'b': ['x', 'y']
}

for combo in all_combinations(swaps):
    print(combo)
```

**Output:**

```python
{'a': 1, 'b': 'x'}
{'a': 1, 'b': 'y'}
{'a': 2, 'b': 'x'}
{'a': 2, 'b': 'y'}
```

## Internal Implementation Details

### Cartesian Product

The `all_combinations()` function uses `itertools.product` to generate the Cartesian product:

```python
def all_combinations(swaps):
    keys = list(swaps.keys())
    value_lists = [swaps[key] for key in keys]

    for combination in itertools.product(*value_lists):
        yield dict(zip(keys, combination))
```

**How it works:**

1. Extract keys and their corresponding value lists
2. Use `itertools.product(*value_lists)` to generate all combinations
3. Zip each combination back with the keys to create a dictionary
4. Yield one combination at a time (memory efficient)

### Transposition

The `get_swap_combos()` function transposes combinations:

**Input format (combinations):**

```python
[
    {'x': 1, 'y': 10},
    {'x': 1, 'y': 20},
    {'x': 2, 'y': 10},
    {'x': 2, 'y': 20}
]
```

**Output format (transposed):**

```python
{
    'x': {'list': [1, 1, 2, 2]},
    'y': {'list': [10, 20, 10, 20]}
}
```

This format matches the swapfile structure expected by the Parser.

### YAML Format

The generated YAML uses the `yaml.safe_dump` function:

```python
with open(yaml_path, "w") as file:
    yaml.safe_dump(get_swap_combos(swaps), file)
```

This creates a readable YAML file that can be edited manually or used directly with `--swapfile`.

## Usage Patterns

### Command-Line Usage

The most common way to use swapfile generation is via the CLI:

```bash
dir-wand --swapfile output.yaml --num 0-2 --condition A B C
```

This generates a swapfile with all 9 combinations (3 × 3).

### Programmatic Usage

```python
from dir_wand.swapfile import make_swapfile

# Define all possible values for each parameter
swaps = {
    'algorithm': ['SGD', 'Adam', 'RMSprop'],
    'learning_rate': [0.001, 0.01, 0.1],
    'batch_size': [16, 32, 64]
}

# Generate swapfile with all 27 combinations
make_swapfile('hyperparams.yaml', swaps)
```

### Generating Combinations for Inspection

```python
from dir_wand.swapfile import all_combinations

swaps = {
    'model': ['resnet', 'vgg'],
    'dataset': ['cifar10', 'imagenet'],
    'seed': [42, 43, 44]
}

# Print all 12 combinations
for i, combo in enumerate(all_combinations(swaps), 1):
    print(f"Experiment {i}: {combo}")
```

**Output:**

```
Experiment 1: {'model': 'resnet', 'dataset': 'cifar10', 'seed': 42}
Experiment 2: {'model': 'resnet', 'dataset': 'cifar10', 'seed': 43}
Experiment 3: {'model': 'resnet', 'dataset': 'cifar10', 'seed': 44}
...
```

### Creating Swapfiles for Large Experiments

```python
from dir_wand.swapfile import make_swapfile

# Generate all combinations of hyperparameters
swaps = {
    'model': ['cnn', 'rnn', 'transformer'],
    'lr': [1e-5, 1e-4, 1e-3, 1e-2],
    'dropout': [0.1, 0.2, 0.3, 0.4, 0.5],
    'layers': [2, 4, 6, 8],
    'units': [64, 128, 256, 512]
}

# This creates 3 * 4 * 5 * 4 * 4 = 960 combinations!
make_swapfile('grid_search.yaml', swaps)

print("Created swapfile with 960 experiment configurations")
```

## Swapfile Format Specification

### Input to `make_swapfile`

```python
{
    'placeholder1': [value1, value2, ...],
    'placeholder2': [value1, value2, ...],
    ...
}
```

### Output YAML Structure

```yaml
placeholder1:
  list:
    - value1_for_combo1
    - value1_for_combo2
    - value1_for_combo3
    - ...

placeholder2:
  list:
    - value2_for_combo1
    - value2_for_combo2
    - value2_for_combo3
    - ...
```

### Alternative Manual Swapfile Formats

You can also manually create swapfiles with these formats:

**Range Format:**

```yaml
seed:
  range: 100-200
```

**File Reference:**

```yaml
experiment_ids:
  file: /path/to/ids.txt
```

**Explicit List:**

```yaml
conditions:
  list:
    - control
    - treatment1
    - treatment2
```

These are parsed by the `parse_swapfile()` function in the parser module.

## Mathematical Properties

### Number of Combinations

For swaps with values of lengths `n₁, n₂, ..., nₖ`, the total number of combinations is:

```
total = n₁ × n₂ × ... × nₖ
```

**Example:**

```python
swaps = {
    'a': [1, 2, 3],           # 3 values
    'b': [10, 20],            # 2 values
    'c': ['x', 'y', 'z', 'w'] # 4 values
}
# Total combinations = 3 × 2 × 4 = 24
```

### Memory Efficiency

The `all_combinations()` function uses a generator:

- **Memory usage**: O(k) where k is the number of placeholders
- **Without generator**: O(n₁ × n₂ × ... × nₖ × k) to store all combinations

This is important for large combination spaces.

## Performance Considerations

- **Combination generation**: O(n₁ × n₂ × ... × nₖ) time
- **Memory**: Generator keeps memory usage low during iteration
- **YAML writing**: Linear in the number of total values
- **Large files**: Swapfiles with millions of combinations can be very large

For 1000 combinations with 5 placeholders:

- **Combinations to generate**: 1000 iterations
- **Values to write**: 5000 values (1000 × 5)
- **YAML file size**: Typically a few hundred KB

## Use Cases

### 1. Grid Search for Hyperparameters

```python
make_swapfile('grid_search.yaml', {
    'learning_rate': [1e-5, 1e-4, 1e-3],
    'batch_size': [16, 32, 64],
    'epochs': [10, 20, 50]
})
# Creates 27 experiment configurations
```

### 2. Sensitivity Analysis

```python
make_swapfile('sensitivity.yaml', {
    'parameter1': [0.8, 0.9, 1.0, 1.1, 1.2],
    'parameter2': [0.8, 0.9, 1.0, 1.1, 1.2]
})
# Creates 25 parameter combinations
```

### 3. Multi-Seed Experiments

```python
make_swapfile('multi_seed.yaml', {
    'model': ['model_a', 'model_b'],
    'dataset': ['dataset1', 'dataset2'],
    'seed': list(range(42, 52))  # 10 seeds
})
# Creates 40 experiments for statistical significance
```

## See Also

- [Parser API](parser.md) - `parse_swapfile()` for reading swapfiles
- [Swapfiles Guide](../guides/swapfiles.md) - User guide for swapfiles
- [Examples](../examples/basic.md) - Swapfile usage examples
