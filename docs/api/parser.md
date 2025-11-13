# Parser API Reference

The `Parser` class handles command-line argument parsing for the WAND CLI.

## Module: `dir_wand.parser`

### Class: `Parser`

A custom argument parser that extends `argparse.ArgumentParser` to support arbitrarily many arbitrarily named placeholder arguments.

#### Constructor

```python
Parser(description)
```

**Parameters:**

- `description` (str): Description of the program for help text

**Example:**

```python
from dir_wand.parser import Parser

parser = Parser("Wave your Directory WAND and make magic happen.")
args = parser.parse_args()
```

#### Standard Arguments

The Parser adds the following standard arguments:

##### `--template`

Path to the template directory.

- **Type:** str
- **Default:** None
- **Example:** `--template path/to/template_{num}`

##### `--root`

Root directory where copies will be created.

- **Type:** str
- **Default:** `.` (current directory)
- **Example:** `--root /output/experiments`

##### `--run`

Command to execute in each copy after creation.

- **Type:** str
- **Default:** None
- **Example:** `--run "python run.py --id {num}"`

##### `--swapfile`

Path to a YAML swapfile defining placeholder values.

- **Type:** str
- **Default:** None
- **Example:** `--swapfile config.yaml`

##### `--silent`

Suppress all WAND output.

- **Type:** bool (flag)
- **Default:** False
- **Example:** `--silent`

#### Dynamic Placeholder Arguments

The Parser supports dynamic arguments for placeholders using two formats:

##### `--<name> <value>` (Double Dash)

Defines a placeholder with a single value (range or filepath).

- **Format:** `--key value`
- **Value types:**
  - Range: `0-10` (inclusive range from 0 to 10)
  - Filepath: `/path/to/values.txt` (file with one value per line)

**Examples:**

```bash
dir-wand --template exp_{num} --num 0-5
dir-wand --template exp_{id} --id values.txt
```

##### `-<name> <val1> <val2> ...` (Single Dash)

Defines a placeholder with an explicit list of values.

- **Format:** `-key val1 val2 val3`
- **Values:** Space-separated list

**Example:**

```bash
dir-wand --template exp_{cond} -cond control treatment1 treatment2
```

#### Methods

##### `parse_args(args=None, namespace=None)`

Parses command-line arguments including unknown placeholder arguments.

**Parameters:**

- `args` (list, optional): Arguments to parse. If None, uses `sys.argv[1:]`
- `namespace` (argparse.Namespace, optional): Namespace to store results

**Returns:** `argparse.Namespace` with the following attributes:

- `template` (str): Template path
- `root` (str): Output root directory
- `run` (str): Command to run
- `swapfile` (str): Swapfile path
- `silent` (bool): Silent mode flag
- `swaps` (dict): Dictionary of placeholder names to value lists

**Behavior:**

1. If no arguments provided, displays help and exits
2. Parses known arguments (template, root, run, swapfile, silent)
3. Processes the swapfile if provided
4. Processes unknown arguments as placeholder swaps
5. Parses all swap values (ranges, files, lists)
6. Returns the namespace with all parsed data

**Example:**

```python
parser = Parser("WAND CLI")
args = parser.parse_args()

print(args.template)  # Template path
print(args.swaps)     # {'num': [0, 1, 2], 'name': ['a', 'b', 'c']}
```

## Helper Functions

### `parse_swapfile(swapfile)`

Parses a YAML swapfile into a dictionary of swaps.

**Parameters:**

- `swapfile` (str): Path to the YAML swapfile

**Returns:** `dict` - Dictionary mapping placeholder names to value lists

**Swapfile Format:**

```yaml
placeholder_name:
  list: [val1, val2, val3]

another_placeholder:
  range: 0-10

file_based_placeholder:
  file: /path/to/values.txt
```

**Example:**

```python
from dir_wand.parser import parse_swapfile

swaps = parse_swapfile("config.yaml")
print(swaps)
# Output: {'num': [0, 1, 2], 'name': ['a', 'b', 'c']}
```

**Supported Swap Types:**

1. **List**: Explicit list of values
   ```yaml
   condition:
     list:
       - control
       - treatment
       - placebo
   ```

2. **Range**: Inclusive integer range
   ```yaml
   seed:
     range: 100-200
   ```

3. **File**: Path to file with one value per line
   ```yaml
   experiment_id:
     file: /data/ids.txt
   ```

### `parse_swaps(**swaps)`

Parses swap arguments into lists of values.

**Parameters:**

- `**swaps`: Keyword arguments where values are strings or lists

**Returns:** `dict` - Dictionary mapping names to value lists

**Value Processing:**

1. **List/Tuple**: Used as-is
2. **File Path**: Read lines from file
3. **Range String**: Parse as `start-end` and generate range
4. **Other**: Raises ValueError

**Example:**

```python
from dir_wand.parser import parse_swaps

swaps = parse_swaps(
    num="0-5",
    name=["a", "b", "c"],
    id="ids.txt"
)
```

## Custom Action Classes

### `StoreDictKeyPair`

Custom argparse Action for storing `--key value` pairs.

**Usage:** Internal to Parser class for handling `--` prefix arguments

**Behavior:**

- Strips `--` from option string to get the key
- Creates `swaps` dictionary in namespace if it doesn't exist
- Stores the value under the key

### `StoreListKeyPair`

Custom argparse Action for storing `-key val1 val2 val3` arguments.

**Usage:** Internal to Parser class for handling `-` prefix arguments

**Behavior:**

- Strips `-` from option string to get the key
- Creates `list_args` dictionary in namespace if it doesn't exist
- Stores the list of values under the key

## Internal Implementation Details

### Argument Processing Flow

1. **Standard parsing**: `parse_known_args()` processes recognized arguments
2. **Swapfile parsing**: If swapfile exists, load swap definitions from YAML
3. **Unknown argument processing**:
   - Loop through unknown arguments
   - Identify `--key value` and `-key val1 val2 ...` patterns
   - Add to swaps dictionary
4. **Swap value parsing**: Convert strings to appropriate types (ranges, files, lists)

### Special Modes

The parser detects three operational modes:

1. **Template copying**: `--template` is provided
2. **Command running**: `--run` is provided (without template)
3. **Swapfile creation**: `--swapfile` is provided (without template or run)

In swapfile creation mode, silent mode is automatically enabled.

### Unknown Argument Handling

The parser processes unknown arguments manually:

```python
while unknown_args:
    if unknown_args[0].startswith("--"):
        key = unknown_args.pop(0).lstrip("--")
        value = unknown_args.pop(0)  # Next arg is the value
        args.swaps[key] = value
    elif unknown_args[0].startswith("-"):
        key = unknown_args.pop(0).lstrip("-")
        values = []
        # Collect all values until next flag
        while unknown_args and not unknown_args[0].startswith("-"):
            values.append(unknown_args.pop(0))
        args.swaps[key] = values
```

This allows for completely dynamic argument definitions.

## Usage Patterns

### Basic CLI Usage

```bash
# Using ranges
dir-wand --template exp_{num} --num 0-5

# Using explicit lists
dir-wand --template job_{id} -id 1 2 3 4 5

# Using swapfile
dir-wand --template sim_{scenario} --swapfile config.yaml

# Mixed mode
dir-wand --template test_{a}_{b} --a 0-2 -b x y z

# With command execution
dir-wand --template job_{id} --id 0-9 --run "python run.py {id}"

# Running commands only (no template copying)
dir-wand --run "cd dir_{num}; ls" --num 0-5
```

### Programmatic Usage

```python
from dir_wand.parser import Parser

# Create parser
parser = Parser("WAND automation")

# Parse arguments
args = parser.parse_args([
    "--template", "exp_{num}",
    "--root", "/output",
    "--num", "0-10",
    "-name", "a", "b", "c"
])

# Access parsed values
print(args.template)  # "exp_{num}"
print(args.root)      # "/output"
print(args.swaps)     # {'num': [0,1,2,...,10], 'name': ['a','b','c']}
```

### Creating a Swapfile Programmatically

```python
import sys
from dir_wand.parser import Parser

# Simulate command-line arguments
sys.argv = [
    "dir-wand",
    "--swapfile", "output.yaml",
    "--num", "0-5",
    "-condition", "A", "B", "C"
]

parser = Parser("Generate swapfile")
args = parser.parse_args()

# This will create output.yaml with all combinations
```

## Error Handling

The parser can encounter the following errors:

- **No arguments**: Displays help and exits
- **Invalid range format**: ValueError if range isn't "start-end" with valid integers
- **Missing file**: FileNotFoundError if a file path doesn't exist
- **Invalid YAML**: yaml.YAMLError if swapfile is malformed
- **Invalid swap value**: ValueError if value can't be parsed as range, file, or list

## See Also

- [Swapfile API](swapfile.md) - Swapfile generation and structure
- [Main Module](../guides/getting-started.md) - CLI usage examples
