# Template API Reference

The `Template` class is the main controller for creating directory copies with placeholder swaps.

## Module: `dir_wand.template`

### Class: `Template`

The Template class manages the directory tree, makes copies with placeholders swapped out, and runs commands.

#### Constructor

```python
Template(root, run=None, **swaps)
```

**Parameters:**

- `root` (str): Path to the root template directory
- `run` (str, optional): Command to execute after each copy is created
- `**swaps` (dict): Keyword arguments where keys are placeholder names and values are lists of replacement values

**Example:**

```python
from dir_wand.template import Template

# Create a template with two placeholders
template = Template(
    "path/to/template",
    run="echo 'Created {name}'",
    name=["exp1", "exp2", "exp3"],
    seed=[42, 43, 44]
)
```

#### Attributes

- `root_path` (str): The full path to the template root
- `root` (str): The basename of the template root directory
- `directory` (Directory): The root Directory object containing the full tree structure
- `swaps` (dict): Dictionary of placeholder names to value lists
- `nswap_vars` (int): Number of different placeholder variables
- `nswaps` (int): Number of copies to create (length of value lists)
- `run_cmd` (CommandRunner): The command runner instance, or None if no command specified

#### Methods

##### `make_copies(new_root)`

Creates all copies of the template with placeholders swapped.

**Parameters:**

- `new_root` (str): Path to the directory where copies will be created

**Returns:** None

**Behavior:**

1. Generates all swap combinations from the provided placeholder values
2. Creates a formatted table showing the swap values for each copy
3. Iterates through each swap combination:
   - Calls `directory.make_copy_with_swaps()` to recursively copy all files and directories
   - Runs the command (if specified) on a concurrent thread
4. Waits for all commands to complete before returning

**Example:**

```python
template = Template(
    "template_{num}",
    num=[0, 1, 2],
    var=["a", "b", "c"]
)

# Creates template_0/, template_1/, template_2/ in /path/to/output
template.make_copies("/path/to/output")
```

**Output:**

```
Copying template_{num}...
 #      num                  var
--------------------------------------------------
 0      0                    a
 1      1                    b
 2      2                    c
--------------------------------------------------
```

##### `__str__()`

Returns a string representation of the template.

**Returns:** `str` - Formatted string describing the template

**Example:**

```python
template = Template("my_template")
print(template)
# Output: "Waving the directory WAND on my_template..."
```

## Internal Implementation Details

### Initialization Flow

1. Store the root path and extract the root directory name
2. Create a `Directory` object for the root
3. Call `directory.unpack_contents()` to recursively build the tree structure
4. Parse and store the swaps dictionary
5. Calculate the number of swap variables and copies
6. Create a `CommandRunner` instance if a run command was provided

### Copy Process

The `make_copies()` method orchestrates the entire copying process:

1. **Swap Preparation**: Transforms the swaps dictionary into a list of dictionaries, where each element contains one complete set of placeholder-value mappings
2. **Progress Display**: Prints a formatted table header with all placeholder names
3. **Iterative Copying**: For each swap combination:
   - Delegates to `Directory.make_copy_with_swaps()` which recursively handles all subdirectories and files
   - Submits the run command to `CommandRunner` for asynchronous execution
   - Prints the current swap values
4. **Synchronization**: Calls `run_cmd.wait_for_all()` to ensure all commands complete

## Usage Patterns

### Basic Template Creation

```python
from dir_wand.template import Template

template = Template(
    root="experiment_{id}",
    id=list(range(1, 11))  # Creates 10 experiments
)

template.make_copies("/data/experiments")
```

### Template with Multiple Placeholders

```python
template = Template(
    root="sim_{scenario}_{seed}",
    scenario=["baseline", "treatment", "control"],
    seed=[100, 200, 300]
)

template.make_copies("/simulations")
```

### Template with Command Execution

```python
template = Template(
    root="job_{id}",
    run="cd job_{id} && python run.py --id {id}",
    id=[1, 2, 3, 4, 5]
)

template.make_copies("/jobs")
```

## Error Handling

The Template class performs validation:

- All swap value lists must have the same length (validated in `main.py` before Template instantiation)
- If a placeholder in the template is missing from swaps, `Directory` or `File` methods will raise `ValueError`
- If the template root path doesn't exist, Directory creation will fail

## See Also

- [Directory API](directory.md) - Directory tree structure and copying
- [File API](file.md) - File handling and placeholder replacement
- [CommandRunner API](command_runner.md) - Command execution system
