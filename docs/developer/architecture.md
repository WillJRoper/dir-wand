# Architecture Overview

This document provides an overview of WAND's architecture and design principles.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        CLI Entry Point                       │
│                         (main.py)                            │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ├─> Parser (command-line arguments)
                       │
                       ├─> Logger (singleton, global state)
                       │
                       ▼
           ┌───────────┴───────────┐
           │                       │
    Template Mode          Run-Only Mode
           │                       │
           ▼                       ▼
      Template              CommandRunner
           │                       │
           ├─> Directory Tree      └─> Concurrent threads
           │   └─> File objects
           │
           ├─> Copy with swaps
           │
           └─> CommandRunner (optional)
```

## Core Components

### 1. Parser (`parser.py`)

**Responsibility:** Parse command-line arguments

**Key Features:**

- Extends `argparse.ArgumentParser`
- Supports dynamic placeholder arguments
- Parses swapfiles (YAML)
- Handles three value formats: ranges, lists, files

**Flow:**

```
Command line → parse_args() → Namespace with swaps dict
```

### 2. Template (`template.py`)

**Responsibility:** Orchestrate directory copying

**Key Components:**

- `Directory` instance (root of tree)
- Swaps dictionary
- Optional `CommandRunner`

**Flow:**

```
Template.__init__():
  1. Create Directory instance for root
  2. Call directory.unpack_contents() (builds tree)
  3. Store swaps
  4. Create CommandRunner if --run provided

Template.make_copies():
  1. Generate swap combinations
  2. For each combination:
     a. directory.make_copy_with_swaps()
     b. run_cmd.run_command() (concurrent thread)
  3. run_cmd.wait_for_all()
```

### 3. Directory (`directory.py`)

**Responsibility:** Represent directory tree structure

**Data Structure:**

```python
class Directory:
    path: str
    children: list[Directory]  # Subdirectories
    files: list[File]           # Files in this directory
```

**Tree Building:**

```
unpack_contents():
  for item in os.listdir(path):
    if isdir:
      child = Directory(item)
      child.unpack_contents()  # Recursive
      children.append(child)
    elif isfile:
      files.append(File(item))
```

**Copying:**

```
make_copy_with_swaps(path, **swaps):
  1. Replace placeholders in directory name
  2. Create directory on filesystem
  3. For each file: file.make_copy_with_swaps()
  4. For each child: child.make_copy_with_swaps() (recursive)
```

### 4. File (`file.py`)

**Responsibility:** Handle file copying with placeholder replacement

**File Type Detection:**

```
is_text → Can read as UTF-8
is_softlink → os.path.islink()
is_executable → os.access(path, os.X_OK)
```

**Copying Strategy:**

```
make_copy_with_swaps():
  if has_placeholders:
    _make_copy_with_placeholders()  # Read, replace, write
  elif is_softlink:
    _make_softlink_copy()            # os.symlink()
  elif is_executable:
    _make_executable_copy()          # Copy + preserve permissions
  else:
    _make_simple_copy()              # Binary copy
```

**Optimization:**

- Placeholder lines cached at initialization
- Only process lines known to have placeholders
- Binary files skipped entirely

### 5. CommandRunner (`command_runner.py`)

**Responsibility:** Execute commands concurrently

**Threading Model:**

```
run_command(**swaps):
  1. Replace placeholders in command
  2. Create thread:
     def run():
       os.system(command)
  3. thread.start()
  4. threads.append(thread)

wait_for_all():
  for thread in threads:
    thread.join()
```

**Key Characteristics:**

- One thread per command
- All threads start immediately (no pool limiting)
- Main thread waits for all to complete

### 6. Logger (`logger.py`)

**Responsibility:** Logging, counting, reporting

**Singleton Pattern:**

```python
_instance = None

def __new__(cls):
    if cls._instance is None:
        cls._instance = super().__new__(cls)
    return cls._instance
```

**Global Print Override:**

```python
builtins.print = custom_print

def custom_print(*args, **kwargs):
    Logger().log(*args, **kwargs)
```

**Counting Decorator:**

```python
@logger.count("operation_name")
def some_function():
    # Function call counted automatically
    pass
```

### 7. Swapfile (`swapfile.py`)

**Responsibility:** Generate all combinations of swaps

**Algorithm:**

```python
all_combinations(swaps):
    # Cartesian product using itertools.product
    for combo in itertools.product(*value_lists):
        yield dict(zip(keys, combo))
```

**Transposition:**

```
Input: [{a:1, b:x}, {a:1, b:y}, {a:2, b:x}, {a:2, b:y}]
       ↓
Output: {a: [1, 1, 2, 2], b: [x, y, x, y]}
```

## Data Flow

### Template Copying Flow

```
1. CLI: dir-wand --template exp_{num} --num 0-2

2. Parser:
   args.template = "exp_{num}"
   args.swaps = {"num": [0, 1, 2]}

3. Template.__init__:
   Directory("exp_{num}").unpack_contents()
   # Tree structure built in memory

4. Template.make_copies("/output"):
   For num=0:
     Directory.make_copy_with_swaps("/output", num=0)
       → Create /output/exp_0/
       → For each file:
           File.make_copy_with_swaps("/output/exp_0", num=0)
   For num=1:
     ...
   For num=2:
     ...

5. Logger.report():
   Print summary statistics
```

### Command Execution Flow

```
1. Template.make_copies():
   For each swap combination:
     CommandRunner.run_command(**swap)
       → Create thread
       → thread.start()
       → Add to threads list

2. (Main thread continues creating directories)

3. Template.make_copies() (end):
   CommandRunner.wait_for_all()
     → for thread in threads:
         thread.join()
```

## Design Patterns

### 1. Singleton (Logger)

Ensures single global logger instance for counting and output control.

### 2. Composite (Directory/File)

Directory tree is a composite structure where:

- Directory contains children (directories) and files
- Both have `make_copy_with_swaps()` method
- Recursive traversal for copying

### 3. Template Method (File Copying)

`File.make_copy_with_swaps()` delegates to different methods based on file type:

- `_make_copy_with_placeholders()`
- `_make_softlink_copy()`
- `_make_executable_copy()`
- `_make_simple_copy()`

### 4. Decorator (Counting)

`@logger.count()` decorator wraps functions to count invocations.

### 5. Generator (Combinations)

`all_combinations()` uses a generator to lazily produce combinations, saving memory.

## Threading Model

### Current Implementation

- One Python thread per command
- Threads created and started immediately
- No thread pool limiting
- GIL limits CPU parallelism

### Implications

**Good for:**

- I/O-bound commands (file operations, network)
- Moderate numbers of commands (<1000)

**Limitations:**

- CPU-bound commands don't benefit from threading (GIL)
- Very large numbers of threads can exhaust resources
- No built-in rate limiting

## Performance Characteristics

### Time Complexity

- **Template parsing:** O(n) where n = number of files/directories
- **Copying:** O(m × k) where m = number of copies, k = template size
- **Placeholder replacement:** O(l) where l = number of lines with placeholders

### Space Complexity

- **Directory tree:** O(k) where k = template size
- **Swaps storage:** O(m × p) where m = copies, p = placeholders
- **In-memory file reading:** O(largest file size)

### Optimizations

1. **Placeholder caching:** Line indices cached at initialization
2. **Binary file skipping:** No placeholder scanning for binary files
3. **Lazy generation:** Swapfile combinations generated lazily
4. **Concurrent execution:** Commands run in parallel

## Error Handling Strategy

### Philosophy

- Fail fast for configuration errors
- Continue on command failures
- Print errors but don't raise exceptions in threads

### Examples

**Configuration Errors (fail fast):**

```python
if len(lengths) > 1:
    raise ValueError("All swaps must have same number of elements")
```

**Command Errors (continue):**

```python
try:
    status = os.system(command)
    if status != 0:
        print(f"Error: Command failed with status {status}")
except Exception as e:
    print(f"Unexpected error: {e}")
# Don't re-raise; other commands continue
```

## Extension Points

### Adding New Value Types

Extend `parse_swaps()` in `parser.py`:

```python
elif is_new_format(value):
    swaps[key] = parse_new_format(value)
```

### Custom File Handlers

Extend `File.make_copy_with_swaps()`:

```python
elif self.is_new_type:
    self._make_new_type_copy(path, **swaps)
```

### Additional Operations

Add new decorators or extend Logger:

```python
@logger.time("operation")
def timed_operation():
    pass
```

## See Also

- [Contributing Guide](contributing.md)
- [Development Setup](setup.md)
- [API Reference](../api/template.md)
