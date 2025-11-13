# Directory API Reference

The `Directory` class represents a directory node in the template tree structure.

## Module: `dir_wand.directory`

### Class: `Directory`

A Directory is a tree structure containing files and other directories. It handles unpacking directory contents and creating copies with placeholder replacements.

#### Constructor

```python
Directory(path)
```

**Parameters:**

- `path` (str): The filesystem path to the directory

**Example:**

```python
from dir_wand.directory import Directory

directory = Directory("/path/to/template")
directory.unpack_contents()  # Recursively load the directory tree
```

#### Attributes

- `path` (str): The filesystem path to this directory
- `children` (list[Directory]): List of child Directory objects
- `files` (list[File]): List of File objects in this directory

#### Properties

##### `name`

Returns the basename of the directory.

**Returns:** `str`

```python
dir = Directory("/path/to/my_dir")
print(dir.name)  # Output: "my_dir"
```

##### `is_empty`

Returns whether the directory contains any files or subdirectories.

**Returns:** `bool`

```python
dir = Directory("/empty/path")
dir.unpack_contents()
if dir.is_empty:
    print("Directory is empty")
```

##### `contains_placeholders`

Returns whether any files in this directory contain placeholders.

**Returns:** `bool`

**Note:** This only checks files in the current directory, not the directory name itself or child directories.

```python
dir = Directory("/path/with/placeholders")
dir.unpack_contents()
if dir.contains_placeholders:
    print("Directory contains files with placeholders")
```

##### `placeholders`

Returns a set of all unique placeholders found in files within this directory.

**Returns:** `set[str]`

```python
dir = Directory("/template")
dir.unpack_contents()
print(dir.placeholders)  # Output: {'num', 'name', 'seed'}
```

#### Methods

##### `unpack_contents()`

Recursively unpacks the directory contents, creating Directory and File objects for all children.

**Returns:** None

**Behavior:**

1. Lists all items in the directory
2. For each item:
   - If it's a directory: creates a child Directory object and recursively calls `unpack_contents()`
   - If it's a file: creates a File object and adds it to the files list
3. Builds the complete tree structure

**Example:**

```python
dir = Directory("/template")
dir.unpack_contents()

# Now dir.children and dir.files are populated
for child in dir.children:
    print(f"Subdirectory: {child.name}")

for file in dir.files:
    print(f"File: {file.name}")
```

##### `make_copy_with_swaps(path, **swaps)`

Creates a copy of this directory and all its contents with placeholders replaced.

**Parameters:**

- `path` (str): The parent path where this directory should be created
- `**swaps`: Keyword arguments mapping placeholder names to replacement values

**Returns:** None

**Behavior:**

1. Appends this directory's name to the path
2. Replaces any placeholders in the directory name using the swaps
3. Creates the new directory on the filesystem
4. Iterates through all files and calls `file.make_copy_with_swaps()`
5. Iterates through all child directories and recursively calls `make_copy_with_swaps()`

**Example:**

```python
# Template structure: experiment_{num}/config_{num}.txt
dir = Directory("experiment_{num}")
dir.unpack_contents()

# Creates: /output/experiment_42/config_42.txt
dir.make_copy_with_swaps("/output", num=42)
```

##### `__str__()`

Returns a tree-style string representation of the directory structure.

**Returns:** `str`

**Example:**

```python
dir = Directory("/template")
dir.unpack_contents()
print(dir)
```

**Output:**

```
  └── template/
      ├── config.yaml
      ├── scripts/
      │   ├── run.sh
      │   └── process.py
      └── data/
          └── input.csv
```

## Internal Implementation Details

### Tree Structure

The Directory class implements a tree data structure:

- Each Directory node stores references to its children (subdirectories) and files
- The tree is built recursively via `unpack_contents()`
- The root Directory has no parent reference (directories don't track their parent)

### String Representation

The `_str_helper()` private method builds the tree visualization:

- Uses box-drawing characters: `└──`, `├──`, `│`
- Tracks whether a node is the last child to determine connector style
- Recursively builds the string representation with proper indentation
- Files and directories are combined in display order

### Copy Algorithm

The `make_copy_with_swaps()` method uses a depth-first traversal:

1. Process the current directory (create it)
2. Process all files in the current directory
3. Recursively process all child directories

This ensures parent directories are created before their children.

### Counting and Logging

The `_make_dir_copy()` method is decorated with `@logger.count("directory")`:

- Each directory creation is counted by the Logger
- Counts are reported at the end of the WAND execution
- This provides visibility into how many directories were created

## Usage Patterns

### Building a Directory Tree

```python
from dir_wand.directory import Directory

# Create and populate the directory structure
root = Directory("/path/to/template")
root.unpack_contents()

# Inspect the structure
print(f"Root directory: {root.name}")
print(f"Number of subdirectories: {len(root.children)}")
print(f"Number of files: {len(root.files)}")
print(f"Contains placeholders: {root.contains_placeholders}")
```

### Creating Copies with Different Parameters

```python
root = Directory("experiment_{id}_{condition}")
root.unpack_contents()

# Create multiple copies with different swap values
for i in range(3):
    root.make_copy_with_swaps(
        "/output",
        id=i,
        condition=["control", "treatment1", "treatment2"][i]
    )
```

### Analyzing Template Structure

```python
def analyze_directory(dir, depth=0):
    """Recursively analyze a directory tree."""
    indent = "  " * depth
    print(f"{indent}{dir.name}/")
    print(f"{indent}  Files: {len(dir.files)}")
    print(f"{indent}  Subdirs: {len(dir.children)}")
    print(f"{indent}  Placeholders: {dir.placeholders}")

    for child in dir.children:
        analyze_directory(child, depth + 1)

root = Directory("/template")
root.unpack_contents()
analyze_directory(root)
```

## Error Handling

The Directory class can raise the following errors:

- `OSError` if the directory path doesn't exist or can't be read during `unpack_contents()`
- `ValueError` from child File objects if required placeholders are missing during `make_copy_with_swaps()`
- `OSError` if the destination path can't be created during `make_copy_with_swaps()`

## Performance Considerations

- `unpack_contents()` reads the entire directory tree into memory
- For very large directory structures, this could consume significant memory
- The recursive nature means deep directory trees could hit Python's recursion limit
- Directory creation is logged and counted, which has minimal overhead

## See Also

- [File API](file.md) - File handling within directories
- [Template API](template.md) - Template controller that uses Directory
- [Logger API](logger.md) - Logging and counting system
