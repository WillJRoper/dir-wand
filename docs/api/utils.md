# Utils API Reference

The `utils` module provides utility functions used throughout WAND.

## Module: `dir_wand.utils`

### Functions

#### `swap_in_str(string, **swaps)`

Replaces placeholders in a string with their corresponding values.

**Parameters:**

- `string` (str): The string containing placeholders in `{name}` format
- `**swaps`: Keyword arguments mapping placeholder names to replacement values

**Returns:** `str` - The string with all placeholders replaced

**Raises:**

- `ValueError`: If required placeholders are missing from swaps

**Example:**

```python
from dir_wand.utils import swap_in_str

result = swap_in_str(
    "experiment_{num}_{condition}",
    num=42,
    condition="control"
)
print(result)  # "experiment_42_control"
```

## Functionality

### Placeholder Detection

The function uses a regular expression to find all placeholders:

```python
swap_in_string = set(re.findall(r"\{(\w+)\}", string))
```

**Pattern breakdown:**

- `\{` - Matches opening brace
- `(\w+)` - Captures one or more word characters (alphanumeric + underscore)
- `\}` - Matches closing brace

**Valid placeholders:**

- `{num}`
- `{experiment_id}`
- `{seed123}`
- `{UPPERCASE}`
- `{mixed_Case_123}`

**Invalid placeholders:**

- `{my-var}` - Contains hyphen
- `{my var}` - Contains space
- `{my.var}` - Contains dot

### Swap Counting

The function automatically counts each swap for logging:

```python
for swap in swap_in_string:
    Logger().swap_counts.setdefault(swap, 0)
    Logger().swap_counts[swap] += 1
```

This ensures:

- Every placeholder replacement is tracked
- Statistics are available in the final report
- Count is per placeholder name, not per occurrence

### Validation

Before performing replacement, validates that all required placeholders are provided:

```python
missing_swaps = swap_in_string - set(swaps.keys())
if len(missing_swaps) > 0:
    raise ValueError(f"Missing swaps: {missing_swaps}")
```

### String Formatting

Uses Python's built-in `str.format()` for the actual replacement:

```python
return string.format(**swaps)
```

This provides:

- Consistent behavior with Python string formatting
- Support for all standard format specifications
- Efficient implementation

## Internal Implementation

### Complete Function

```python
def swap_in_str(string, **swaps):
    # Find all placeholders in the string
    swap_in_string = set(re.findall(r"\{(\w+)\}", string))

    # Count swaps for logging
    for swap in swap_in_string:
        Logger().swap_counts.setdefault(swap, 0)
        Logger().swap_counts[swap] += 1

    # Validate all required swaps are provided
    missing_swaps = swap_in_string - set(swaps.keys())
    if len(missing_swaps) > 0:
        raise ValueError(f"Missing swaps: {missing_swaps}")

    # Perform the replacement
    return string.format(**swaps)
```

### Flow Diagram

```
Input: "exp_{num}_{seed}", num=1, seed=42
  ↓
Find placeholders: {'num', 'seed'}
  ↓
Count swaps: Logger().swap_counts['num'] += 1
            Logger().swap_counts['seed'] += 1
  ↓
Validate: {'num', 'seed'} ⊆ {'num', 'seed'} ✓
  ↓
Format: "exp_{num}_{seed}".format(num=1, seed=42)
  ↓
Output: "exp_1_42"
```

## Usage Patterns

### Basic Replacement

```python
from dir_wand.utils import swap_in_str

# Simple replacement
result = swap_in_str("run_{id}", id=5)
print(result)  # "run_5"

# Multiple placeholders
result = swap_in_str(
    "exp_{num}_seed_{seed}",
    num=1,
    seed=42
)
print(result)  # "exp_1_seed_42"
```

### With Type Conversion

```python
# Numbers are automatically converted to strings
result = swap_in_str("value_{x}", x=3.14159)
print(result)  # "value_3.14159"

# Lists/tuples converted to their string representation
result = swap_in_str("data_{ids}", ids=[1, 2, 3])
print(result)  # "data_[1, 2, 3]"
```

### Error Handling

```python
try:
    result = swap_in_str("exp_{num}_{seed}", num=1)
except ValueError as e:
    print(e)  # "Missing swaps: {'seed'}"
```

### No Placeholders

```python
# If no placeholders, returns the string unchanged
result = swap_in_str("no_placeholders_here", num=1, seed=42)
print(result)  # "no_placeholders_here"
```

### Extra Swaps

```python
# Extra swaps are ignored (no error)
result = swap_in_str(
    "exp_{num}",
    num=1,
    seed=42,  # Not used, but no error
    extra="ignored"  # Also ignored
)
print(result)  # "exp_1"
```

## Integration with WAND

The `swap_in_str()` function is used throughout WAND:

### In File Copying

```python
# dir_wand/file.py
def make_copy_with_swaps(self, path, **swaps):
    path += "/" if not path.endswith("/") else ""
    path = path + self.name
    path = swap_in_str(path, **swaps)  # Replace placeholders in path
    # ...
```

### In Directory Copying

```python
# dir_wand/directory.py
def make_copy_with_swaps(self, path, **swaps):
    path += "/" if not path.endswith("/") else ""
    path = path + self.name
    path = swap_in_str(path, **swaps)  # Replace placeholders in path
    # ...
```

### In File Content

```python
# dir_wand/file.py
def _make_copy_with_placeholders(self, path, **swaps):
    # ...
    for index in self._place_holder_lines:
        line = lines[index]
        line = swap_in_str(line, **swaps)  # Replace in file content
        lines[index] = line
    # ...
```

### In Command Execution

```python
# dir_wand/command_runner.py
def run_command(self, **swaps):
    # ...
    command = swap_in_str(self.command, **swaps)  # Replace in command
    # ...
```

## Advanced Format Specifications

Since `swap_in_str()` uses `str.format()`, you can use format specifications:

### Number Formatting

```python
# Fixed precision
result = swap_in_str("value_{x:.2f}", x=3.14159)
print(result)  # "value_3.14"

# Width and padding
result = swap_in_str("id_{num:05d}", num=42)
print(result)  # "id_00042"
```

### String Alignment

```python
# Right alignment
result = swap_in_str("name_{s:>10}", s="test")
print(result)  # "name_      test"

# Left alignment
result = swap_in_str("name_{s:<10}", s="test")
print(result)  # "name_test      "
```

### Type Conversion

```python
# Hexadecimal
result = swap_in_str("addr_{n:x}", n=255)
print(result)  # "addr_ff"

# Binary
result = swap_in_str("bits_{n:b}", n=10)
print(result)  # "bits_1010"
```

**Note:** These format specifications work because `str.format()` is used internally.

## Performance Considerations

- **Regex compilation**: Uses `re.findall()` which compiles the pattern each time
  - Could be optimized with a pre-compiled pattern
  - Current implementation is simple and sufficient for typical usage
- **Set operations**: Finding missing swaps is O(n) where n is the number of placeholders
- **Format operation**: Python's `str.format()` is highly optimized
- **Logger access**: `Logger()` singleton lookup is fast

For typical WAND usage (hundreds of swaps), performance is not a concern.

## Testing Considerations

### Unit Tests

```python
import pytest
from dir_wand.utils import swap_in_str

def test_basic_swap():
    result = swap_in_str("test_{num}", num=42)
    assert result == "test_42"

def test_multiple_swaps():
    result = swap_in_str("exp_{a}_{b}", a=1, b=2)
    assert result == "exp_1_2"

def test_missing_swap():
    with pytest.raises(ValueError, match="Missing swaps"):
        swap_in_str("test_{num}", other=42)

def test_no_placeholders():
    result = swap_in_str("no_placeholders", num=42)
    assert result == "no_placeholders"

def test_extra_swaps():
    result = swap_in_str("test_{num}", num=1, extra=2)
    assert result == "test_1"
```

## See Also

- [Logger API](logger.md) - Swap counting integration
- [File API](file.md) - Usage in file copying
- [Directory API](directory.md) - Usage in directory copying
- [CommandRunner API](command_runner.md) - Usage in command execution
