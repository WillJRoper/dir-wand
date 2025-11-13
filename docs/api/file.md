# File API Reference

The `File` class handles file copying with placeholder replacement and preservation of file properties.

## Module: `dir_wand.file`

### Class: `File`

The File class represents a file in the template directory tree and handles creating copies with placeholder replacements while preserving file properties like permissions, executable status, and softlinks.

#### Constructor

```python
File(path)
```

**Parameters:**

- `path` (str): The filesystem path to the file

**Behavior:**

During initialization, the File object:
1. Stores the path
2. Scans the file for placeholders (if it's a text file)
3. Records which lines contain placeholders for efficient replacement later

**Example:**

```python
from dir_wand.file import File

file = File("/path/to/config_{num}.yaml")
print(file.has_placeholders)  # True
print(file.placeholders)  # {'num'}
```

#### Attributes

- `path` (str): The filesystem path to the file
- `_place_holder_lines` (list[int]): Line indices containing placeholders (private)
- `_placeholders` (set[str]): Set of placeholder names found in the file (private)

#### Properties

##### `name`

Returns the basename of the file.

**Returns:** `str`

```python
file = File("/path/to/script.py")
print(file.name)  # Output: "script.py"
```

##### `is_softlink`

Returns whether the file is a symbolic link.

**Returns:** `bool`

```python
file = File("/path/to/link")
if file.is_softlink:
    print("This is a symbolic link")
```

##### `is_executable`

Returns whether the file has executable permissions.

**Returns:** `bool`

```python
file = File("/path/to/script.sh")
if file.is_executable:
    print("This file can be executed")
```

##### `is_hidden`

Returns whether the file is hidden (starts with '.').

**Returns:** `bool`

**Note:** This checks if the filename starts with a dot, not the full path.

```python
file = File("/path/to/.hidden")
print(file.is_hidden)  # True
```

##### `is_empty`

Returns whether the file has zero size.

**Returns:** `bool`

```python
file = File("/path/to/empty.txt")
if file.is_empty:
    print("File is empty")
```

##### `is_text`

Returns whether the file can be read as text.

**Returns:** `bool`

**Implementation:** Attempts to read the file as UTF-8 text. Returns False if a UnicodeDecodeError occurs.

```python
file = File("/path/to/image.png")
if not file.is_text:
    print("This is a binary file")
```

##### `has_placeholders`

Returns whether the file contains any placeholders.

**Returns:** `bool`

```python
file = File("/path/to/config.yaml")
if file.has_placeholders:
    print(f"Placeholders found: {file.placeholders}")
```

##### `placeholders`

Returns the set of placeholder names (read-only access to `_placeholders`).

**Returns:** `set[str]`

```python
file = File("template_{num}_{name}.txt")
print(file.placeholders)  # Output: set() (no placeholders in file content)
```

**Note:** This returns placeholders found in the file **contents**, not the filename.

#### Methods

##### `get_placeholders()`

Extracts placeholders from the file contents.

**Returns:** None (updates internal state)

**Behavior:**

1. Checks if the file is text (returns early if not)
2. Reads all lines from the file
3. Uses regex pattern `r"\{([a-zA-Z0-9_]+)\}"` to find placeholders
4. Stores line indices with placeholders in `_place_holder_lines`
5. Stores unique placeholder names in `_placeholders`

**Example:**

```python
# File contains: "Value: {num}\nName: {name}\n"
file = File("config.txt")
# get_placeholders() is called automatically in __init__
print(file.placeholders)  # {'num', 'name'}
```

##### `make_copy_with_swaps(path, **swaps)`

Creates a copy of the file with placeholders replaced.

**Parameters:**

- `path` (str): The parent directory path where the file should be created
- `**swaps`: Keyword arguments mapping placeholder names to replacement values

**Returns:** None

**Behavior:**

1. Appends the filename to the path
2. Replaces any placeholders in the filename
3. Chooses the appropriate copy method:
   - If file has placeholders: `_make_copy_with_placeholders()`
   - If file is a softlink: `_make_softlink_copy()`
   - If file is executable: `_make_executable_copy()`
   - Otherwise: `_make_simple_copy()`

**Example:**

```python
file = File("config_{num}.yaml")
file.make_copy_with_swaps("/output", num=42)
# Creates: /output/config_42.yaml
```

##### `_make_softlink_copy(path)`

Creates a copy of a symbolic link.

**Parameters:**

- `path` (str): Destination path for the new link

**Returns:** None

**Decorated with:** `@logger.count("file")`

**Behavior:**

1. Reads the target of the original symlink
2. Creates a new symlink at the destination pointing to the same target

##### `_make_executable_copy(path)`

Creates a copy of an executable file, preserving permissions.

**Parameters:**

- `path` (str): Destination path for the copy

**Returns:** None

**Decorated with:** `@logger.count("file")`

**Behavior:**

1. Copies the file in binary mode
2. Copies the permissions from the original file

##### `_make_simple_copy(path)`

Creates a simple binary copy of a file.

**Parameters:**

- `path` (str): Destination path for the copy

**Returns:** None

**Decorated with:** `@logger.count("file")`

**Behavior:**

1. Opens both files in binary mode
2. Copies all content from source to destination

##### `_make_copy_with_placeholders(path, **swaps)`

Creates a copy with placeholders replaced in the file contents.

**Parameters:**

- `path` (str): Destination path for the copy
- `**swaps`: Placeholder name to value mappings

**Returns:** None

**Raises:** `ValueError` if required placeholders are missing from swaps

**Decorated with:** `@logger.count("file")`

**Behavior:**

1. Validates that all required placeholders are provided
2. Reads all lines from the source file
3. For each line with placeholders (using cached line indices):
   - Replaces placeholders using `swap_in_str()`
   - Updates the line in the list
4. Writes all lines to the new file
5. Copies permissions from the original file

## Internal Implementation Details

### Placeholder Detection

The placeholder detection uses a compiled regex pattern:

```python
pattern = re.compile(r"\{([a-zA-Z0-9_]+)\}")
```

This matches:
- Opening brace `{`
- One or more alphanumeric characters or underscores
- Closing brace `}`

Valid placeholders: `{num}`, `{experiment_id}`, `{seed123}`
Invalid: `{my-var}` (hyphens), `{my var}` (spaces)

### Optimization Strategy

The File class optimizes placeholder replacement:

1. **Line Indexing**: During initialization, records which lines contain placeholders
2. **Selective Replacement**: Only processes lines known to have placeholders
3. **Single Pass**: Reads the file once during initialization, once during copying

For large files with few placeholders, this provides significant performance benefits.

### Copy Method Selection

The `make_copy_with_swaps()` method uses a priority order:

1. **Placeholders first**: If the file has placeholders, content must be modified
2. **Softlinks**: Preserve the symlink nature, don't copy the target
3. **Executables**: Preserve executable permissions
4. **Default**: Simple binary copy

This ensures special file types are handled correctly.

### Binary vs Text Handling

Files are categorized as text or binary:

- **Text files**: Can be read as UTF-8, may contain placeholders
- **Binary files**: Will raise UnicodeDecodeError when read as text, copied as-is

This automatic detection means binary files (images, compiled code, etc.) are safely copied without modification.

## Usage Patterns

### Basic File Copying

```python
from dir_wand.file import File

file = File("script_{version}.py")
file.make_copy_with_swaps("/output", version="v2.0")
# Creates: /output/script_v2.0.py
```

### Handling Different File Types

```python
# Softlink
link = File("/template/data_link")
if link.is_softlink:
    link.make_copy_with_swaps("/output")  # Preserves the link

# Executable
script = File("/template/run.sh")
if script.is_executable:
    script.make_copy_with_swaps("/output")  # Preserves +x permission

# Binary file
image = File("/template/logo.png")
if not image.is_text:
    image.make_copy_with_swaps("/output")  # Binary copy
```

### Analyzing File Properties

```python
file = File("config.yaml")

print(f"Name: {file.name}")
print(f"Is text: {file.is_text}")
print(f"Is empty: {file.is_empty}")
print(f"Is executable: {file.is_executable}")
print(f"Has placeholders: {file.has_placeholders}")
if file.has_placeholders:
    print(f"Placeholders: {file.placeholders}")
```

## Error Handling

The File class can raise:

- `ValueError`: If required placeholders are missing during `make_copy_with_placeholders()`
- `FileNotFoundError`: If the source file doesn't exist
- `PermissionError`: If the file can't be read or destination can't be written
- `UnicodeDecodeError`: Caught internally in `is_text` property (returns False)

## Performance Considerations

- Placeholder scanning happens once at initialization
- Line indices are cached for fast replacement
- Binary files are copied without scanning for placeholders
- Large text files with many placeholders will be read twice (init + copy)

## See Also

- [Directory API](directory.md) - Directory structure containing files
- [Utils API](utils.md) - `swap_in_str()` function for placeholder replacement
- [Logger API](logger.md) - File copy counting
