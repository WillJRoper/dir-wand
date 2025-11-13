# CommandRunner API Reference

The `CommandRunner` class manages command execution with placeholder replacement and concurrent threading.

## Module: `dir_wand.command_runner`

### Class: `CommandRunner`

The CommandRunner executes shell commands with placeholder replacements, using concurrent threads for parallel execution.

#### Constructor

```python
CommandRunner(command)
```

**Parameters:**

- `command` (str): The shell command to execute, optionally with placeholders

**Example:**

```python
from dir_wand.command_runner import CommandRunner

runner = CommandRunner("echo 'Processing {num}'")
```

#### Attributes

- `command` (str): The command template with placeholders
- `threads` (list[threading.Thread]): List of active command execution threads
- `_placeholders` (set[str]): Set of placeholder names found in the command

#### Methods

##### `get_placeholders()`

Extracts placeholder names from the command string.

**Returns:** None (updates `_placeholders` attribute)

**Behavior:**

- Uses regex pattern `r"\{([a-zA-Z0-9_]+)\}"` to find placeholders
- Stores unique placeholder names in `_placeholders` set
- Called automatically during initialization

**Example:**

```python
runner = CommandRunner("python run.py --id {id} --seed {seed}")
print(runner._placeholders)  # {'id', 'seed'}
```

##### `run_command(**swaps)`

Executes the command with placeholders replaced, on a concurrent thread.

**Parameters:**

- `**swaps`: Keyword arguments mapping placeholder names to values

**Returns:** None

**Raises:**

- `ValueError`: If required placeholders are missing from swaps

**Decorated with:** `@logger.count("command")`

**Behavior:**

1. Validates that all required placeholders are provided
2. Replaces placeholders in the command using `swap_in_str()`
3. Creates a new thread to execute the command
4. Starts the thread (non-blocking)
5. Adds the thread to the threads list for later synchronization

**Thread Execution:**

- Runs `os.system(command)` in the thread
- Captures the exit status
- Prints error messages if the command fails
- Catches and reports OSError and unexpected exceptions

**Example:**

```python
runner = CommandRunner("echo 'Run {num}'")
runner.run_command(num=42)  # Returns immediately, runs in background
runner.wait_for_all()  # Wait for completion
```

##### `run_command_for_all_swaps(**swaps)`

Executes the command for all combinations of swap values.

**Parameters:**

- `**swaps`: Keyword arguments where values are lists of replacement values

**Returns:** None

**Behavior:**

1. Counts the number of swap combinations (length of first value list)
2. Unpacks swaps into individual combination dictionaries
3. For each combination:
   - Calls `run_command()` with that combination
   - Prints a newline for output separation
4. Calls `wait_for_all()` to synchronize all threads

**Example:**

```python
runner = CommandRunner("echo {num} {letter}")

# Run for all combinations: (0, 'a'), (1, 'b'), (2, 'c')
runner.run_command_for_all_swaps(
    num=[0, 1, 2],
    letter=['a', 'b', 'c']
)
```

##### `wait_for_all()`

Waits for all command threads to complete.

**Returns:** None

**Behavior:**

- Iterates through all threads in `self.threads`
- Calls `thread.join()` on each to wait for completion
- Blocks until all threads have finished

**Example:**

```python
runner = CommandRunner("sleep {duration}")

for i in range(5):
    runner.run_command(duration=i)

# All commands running in parallel
print("All commands started")

runner.wait_for_all()
print("All commands completed")
```

## Internal Implementation Details

### Threading Model

The CommandRunner uses Python's `threading` module:

- Each command execution runs in its own thread
- Threads are started immediately (non-blocking)
- The main thread continues while commands execute
- `wait_for_all()` provides synchronization

**Advantages:**

- Multiple commands run concurrently
- Main thread isn't blocked during execution
- Good for I/O-bound commands (network, disk)

**Limitations:**

- Python GIL limits CPU-bound parallelism
- No built-in thread pool limiting (all threads start immediately)
- Error handling is per-thread, not centralized

### Command Execution

Commands are executed using `os.system()`:

```python
def run():
    try:
        status = os.system(command)
        if status != 0:
            print(f"Error: Command '{command}' failed with status code {status}.")
    except OSError as e:
        print(f"OSError occurred while running command '{command}': {e}")
    except Exception as e:
        print(f"Unexpected error occurred while running command '{command}': {e}")
```

**Characteristics:**

- Runs in a shell environment
- Blocks the thread until completion
- Returns the exit status
- Output goes directly to stdout/stderr (not captured)

### Placeholder Replacement

Placeholder replacement delegates to `swap_in_str()`:

```python
command = swap_in_str(self.command, **swaps)
```

This ensures:

- Consistent placeholder syntax with File and Directory
- Swap counting for the Logger
- Validation that all required placeholders are provided

## Usage Patterns

### Basic Command Execution

```python
from dir_wand.command_runner import CommandRunner

# Simple command
runner = CommandRunner("echo 'Hello, {name}!'")
runner.run_command(name="World")
runner.wait_for_all()
```

### Parallel Command Execution

```python
# Run multiple commands in parallel
runner = CommandRunner("python process.py --id {id}")

for i in range(10):
    runner.run_command(id=i)

# All 10 commands running concurrently
runner.wait_for_all()
```

### Command with Multiple Placeholders

```python
runner = CommandRunner(
    "cd exp_{id} && python run.py --seed {seed} --config config_{id}.yaml"
)

for i in range(5):
    runner.run_command(id=i, seed=42 + i)

runner.wait_for_all()
```

### Batch Command Execution

```python
runner = CommandRunner("./process.sh {input} {output}")

runner.run_command_for_all_swaps(
    input=["data1.txt", "data2.txt", "data3.txt"],
    output=["out1.txt", "out2.txt", "out3.txt"]
)
# Automatically waits for all commands
```

### Error Handling

```python
runner = CommandRunner("risky_command.sh {param}")

# Commands with errors will print error messages
runner.run_command(param="bad_value")
runner.wait_for_all()

# Check logs for error messages
# Errors don't raise exceptions; they're printed
```

## Integration with Template

The CommandRunner is integrated into the Template workflow:

```python
class Template:
    def __init__(self, root, run=None, **swaps):
        self.run_cmd = CommandRunner(run) if run is not None else None

    def make_copies(self, new_root):
        for swap in swaps:
            # Create directory copy
            self.directory.make_copy_with_swaps(new_root, **swap)

            # Run command in parallel
            if self.run_cmd is not None:
                self.run_cmd.run_command(**swap)

        # Wait for all commands
        if self.run_cmd is not None:
            self.run_cmd.wait_for_all()
```

This allows:

- Commands to run while subsequent directories are being copied
- All commands to finish before the program exits
- Efficient use of CPU and I/O resources

## Performance Considerations

### Concurrency

- Commands run in parallel threads
- Good for I/O-bound tasks (file operations, network calls)
- Limited benefit for CPU-bound tasks due to Python's GIL
- No thread pool limiting; all threads start immediately

### Resource Usage

- Each thread consumes memory and system resources
- Large numbers of concurrent commands could exhaust system resources
- Consider the command type when deciding how many to run

### Synchronization

- `wait_for_all()` blocks until ALL threads complete
- No mechanism for partial synchronization
- No timeout for thread joining

## Error Handling

The CommandRunner handles errors gracefully:

- **Missing placeholders**: Raises ValueError before starting thread
- **Command failure**: Prints error message with exit code
- **OSError**: Catches and prints system errors
- **Unexpected exceptions**: Catches and prints all other exceptions

**Important:** Errors are printed but don't stop execution or raise exceptions to the caller.

## See Also

- [Template API](template.md) - Template integration with CommandRunner
- [Utils API](utils.md) - `swap_in_str()` for placeholder replacement
- [Logger API](logger.md) - Command execution counting
