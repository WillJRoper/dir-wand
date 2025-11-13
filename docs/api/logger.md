# Logger API Reference

The `Logger` class provides logging, counting, and reporting for WAND operations.

## Module: `dir_wand.logger`

### Class: `Logger`

A singleton logger that tracks operations, counts swaps, and provides execution summaries. The Logger also overrides Python's built-in `print` function to enable silent mode.

#### Constructor

```python
Logger(silent=False)
```

**Parameters:**

- `silent` (bool): If True, suppresses all output

**Note:** Logger is a singleton. Subsequent instantiations return the same instance.

**Example:**

```python
from dir_wand.logger import Logger

# First instantiation creates the instance
logger = Logger(silent=False)

# Subsequent calls return the same instance
logger2 = Logger()  # Returns the same object
assert logger is logger2
```

#### Attributes

- `silent` (bool): Whether to suppress output
- `counts` (dict[str, int]): Count of operations by type
- `swap_counts` (dict[str, int]): Count of swaps by placeholder name
- `start_time` (float): Timestamp when logger was created
- `end_time` (float): Timestamp when timer was stopped

#### Properties

##### `elapsed_time`

Returns the elapsed time between start and stop.

**Returns:** `float` - Seconds elapsed

**Example:**

```python
logger = Logger()
# ... do work ...
logger._stop_timer()
print(f"Elapsed: {logger.elapsed_time:.2f} seconds")
```

#### Methods

##### `log(*args, **kwargs)`

Logs a message to the console if not in silent mode.

**Parameters:**

- `*args`: Arguments to pass to print
- `**kwargs`: Keyword arguments to pass to print

**Returns:** None

**Behavior:**

- If `silent=False`: Calls the original print function
- If `silent=True`: Does nothing

**Example:**

```python
logger = Logger(silent=False)
logger.log("This message will be printed")

logger2 = Logger(silent=True)
logger2.log("This message will be suppressed")
```

##### `count(*keys)`

Decorator that counts function calls.

**Parameters:**

- `*keys` (str): Keys to store the counts under

**Returns:** Decorated function

**Behavior:**

- Each time the decorated function is called, increments the counter for each key
- Multiple keys can be specified to track the same operation under different categories

**Example:**

```python
logger = Logger()

@logger.count("file", "copy")
def copy_file(src, dst):
    # ... copy logic ...
    pass

# Each call increments counts["file"] and counts["copy"]
copy_file("a.txt", "b.txt")
copy_file("c.txt", "d.txt")

print(logger.counts)  # {'file': 2, 'copy': 2}
```

##### `report()`

Prints a comprehensive summary of all operations and swaps.

**Returns:** None

**Behavior:**

1. Stops the timer
2. Prints swap summary table showing each placeholder and count
3. Calculates totals for copies, directories, files, commands, and swaps
4. Prints final summary line with all statistics and elapsed time

**Example:**

```python
logger = Logger()

# ... perform operations ...

logger.report()
```

**Output:**

```
-----------Swap Report-----------
|Swap                  | Count     |
|-----------------------------------
|num                   | 50        |
|condition             | 50        |
|seed                  | 50        |
|Total                 | 150       |
|-----------------------------------

WAND waved in 2.34 seconds, making 150 copies (50 directories, 100 files), running 50 commands, and replacing 150 placeholders.
```

## Internal Implementation Details

### Singleton Pattern

The Logger uses the `__new__` method to implement the singleton pattern:

```python
_instance = None

def __new__(cls, *args, **kwargs):
    if cls._instance is None:
        cls._instance = super(Logger, cls).__new__(cls)
        cls._instance._setup_instance(*args, **kwargs)
    return cls._instance
```

This ensures:

- Only one Logger instance exists across the entire application
- Settings (like `silent`) are global
- Counts and timers are consistent

### Print Function Override

The logger overrides Python's built-in `print`:

```python
# Store original
_print = print

def custom_print(*args, **kwargs):
    Logger().log(*args, **kwargs)

# Override built-in
builtins.print = custom_print
```

This allows:

- Silent mode to work for all print statements in the codebase
- No need to pass the logger to every function
- Seamless integration without code changes

### Counting Mechanism

The `count()` decorator uses `functools.wraps` to preserve function metadata:

```python
def count(self, *keys):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            for key in keys:
                if key not in self.counts:
                    self.counts[key] = 0
                self.counts[key] += 1
            return result
        return wrapper
    return decorator
```

Features:

- Preserves function name, docstring, and signature
- Increments counters after the function executes
- Supports multiple keys per function
- Initializes counters on first use

### Swap Counting

Swaps are counted in the `swap_in_str()` utility function:

```python
def swap_in_str(string, **swaps):
    swap_in_string = set(re.findall(r"\{(\w+)\}", string))

    for swap in swap_in_string:
        Logger().swap_counts.setdefault(swap, 0)
        Logger().swap_counts[swap] += 1

    return string.format(**swaps)
```

This ensures:

- Every placeholder replacement is counted
- Counts are per placeholder name, not per replacement
- Statistics reflect actual usage

### Timer Management

The logger automatically starts timing on initialization:

```python
def _setup_instance(self, silent=False):
    # ... other setup ...
    self._start_timer()

def _start_timer(self):
    self.start_time = time.time()

def _stop_timer(self):
    self.end_time = time.time()
```

The timer is stopped when `report()` is called.

## Usage Patterns

### Basic Logging

```python
from dir_wand.logger import Logger

logger = Logger()
logger.log("Processing started")
logger.log(f"Found {len(items)} items")
```

### Silent Mode

```python
# Create logger in silent mode
logger = Logger(silent=True)

# These won't print anything
print("This is suppressed")
logger.log("This too")
```

### Counting Operations

```python
logger = Logger()

@logger.count("database_query")
def fetch_data(query):
    # ... fetch logic ...
    pass

@logger.count("file", "read")
def read_file(path):
    # ... read logic ...
    pass

# Perform operations
for i in range(100):
    fetch_data(f"SELECT * FROM table{i}")
    read_file(f"data{i}.txt")

# Check counts
print(logger.counts)
# {'database_query': 100, 'file': 100, 'read': 100}
```

### Multi-Key Counting

```python
@logger.count("operation", "copy", "file_operation")
def copy_file(src, dst):
    # ... copy logic ...
    pass

# This increments three different counters
copy_file("a.txt", "b.txt")
```

### Generating Reports

```python
logger = Logger()

# ... perform WAND operations ...

# Generate summary report
logger.report()
```

## Integration with WAND

The Logger is integrated throughout WAND:

### In File Copying

```python
class File:
    @logger.count("file")
    def _make_simple_copy(self, path):
        # ... copy logic ...
```

### In Directory Creation

```python
class Directory:
    @logger.count("directory")
    def _make_dir_copy(self, path):
        os.makedirs(path, exist_ok=True)
```

### In Command Execution

```python
class CommandRunner:
    @logger.count("command")
    def run_command(self, **swaps):
        # ... command logic ...
```

### In Main Flow

```python
def main():
    # Set up logger with silent mode from args
    Logger(silent=args.silent)

    # ... perform operations ...

    # Report statistics
    Logger().report()
```

## Performance Considerations

- **Singleton lookup**: Minimal overhead for `Logger()` calls
- **Print override**: Small overhead for every print statement (dictionary lookup)
- **Counting**: Minimal overhead (dictionary increment)
- **Memory**: Counts and timers use negligible memory
- **Silent mode**: When silent, print statements do nothing (very fast)

## Thread Safety

**Warning:** The Logger is **not thread-safe**.

- Multiple threads incrementing counts can cause race conditions
- In WAND, this is generally not an issue because:
  - File and directory copying happens on the main thread
  - Command execution threads don't update counts

For true thread safety, would need:

```python
import threading

class Logger:
    def __init__(self):
        self._lock = threading.Lock()

    def count(self, *keys):
        def decorator(func):
            def wrapper(*args, **kwargs):
                result = func(*args, **kwargs)
                with self._lock:
                    for key in keys:
                        self.counts[key] = self.counts.get(key, 0) + 1
                return result
            return wrapper
        return decorator
```

## See Also

- [Utils API](utils.md) - `swap_in_str()` for swap counting
- [File API](file.md) - File operation counting
- [Directory API](directory.md) - Directory operation counting
- [CommandRunner API](command_runner.md) - Command execution counting
