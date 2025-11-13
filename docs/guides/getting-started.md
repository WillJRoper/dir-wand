# Getting Started with WAND

This guide will help you install WAND and create your first template-based directory structure.

## Installation

WAND is available on PyPI and can be installed using pip:

```bash
pip install dir-wand
```

### Requirements

- Python 3.8 or higher
- PyYAML (installed automatically as a dependency)

### Verifying Installation

After installation, verify that WAND is installed correctly:

```bash
dir-wand --help
```

You should see the help message with all available options.

## Your First WAND Project

Let's create a simple example to understand how WAND works.

### Step 1: Create a Template Directory

First, create a template directory structure:

```bash
mkdir template_{num}
echo "Experiment number: {num}" > template_{num}/config.txt
echo "#!/bin/bash" > template_{num}/run.sh
echo "echo 'Running experiment {num}'" >> template_{num}/run.sh
chmod +x template_{num}/run.sh
```

Your template structure now looks like this:

```
template_{num}/
├── config.txt (contains: "Experiment number: {num}")
└── run.sh (executable script)
```

### Step 2: Generate Copies

Use WAND to generate multiple copies with different values:

```bash
dir-wand --template template_{num} --num 0-4
```

This creates:

```
template_0/
├── config.txt (contains: "Experiment number: 0")
└── run.sh

template_1/
├── config.txt (contains: "Experiment number: 1")
└── run.sh

template_2/
├── config.txt (contains: "Experiment number: 2")
└── run.sh

template_3/
├── config.txt (contains: "Experiment number: 3")
└── run.sh

template_4/
├── config.txt (contains: "Experiment number: 4")
└── run.sh
```

### Step 3: Run Commands in Each Directory

You can also execute commands in each created directory:

```bash
dir-wand --template template_{num} --root /tmp/experiments --num 0-4 --run "cd template_{num} && ./run.sh"
```

This will:

1. Create the directories in `/tmp/experiments/`
2. Execute the run script in each directory concurrently
3. Display the output from each script

## Understanding the Output

When WAND runs, it displays:

1. **ASCII Art Banner**: The WAND logo
2. **Template Information**: What template is being processed
3. **Directory Structure**: Visual representation of the template tree
4. **Progress Table**: Shows each copy being created with its swap values
5. **Summary Report**: Statistics about operations performed

Example output:

```
  └── WAND/
       ├── WAND/
       │   ├── WAND/
       │   │   ├── WAND/
       │   │   │   └── ...

Waving the directory WAND on template_{num}...

Template structure:
  └── template_{num}/
      ├── config.txt
      └── run.sh

Copying template_{num}...
 #      num
--------------------------------------------------
 0      0
 1      1
 2      2
 3      3
 4      4
--------------------------------------------------

-----------Swap Report-----------
|Swap                  | Count     |
|-----------------------------------
|num                   | 10        |
|Total                 | 10        |
|-----------------------------------

WAND waved in 0.15 seconds, making 15 copies (5 directories, 10 files) and replacing 10 placeholders.
```

## Key Concepts

### Placeholders

Placeholders are markers in file paths and file contents that get replaced with actual values. They use the format `{name}`.

**Valid placeholder names:**

- `{num}`
- `{experiment_id}`
- `{seed_value}`
- `{param123}`

**Invalid placeholder names:**

- `{my-param}` (hyphens not allowed)
- `{my param}` (spaces not allowed)
- `{my.param}` (dots not allowed)

### Value Formats

WAND supports three ways to specify replacement values:

**1. Range (inclusive):**

```bash
--num 0-10  # Creates values: 0, 1, 2, ..., 10
```

**2. Explicit list:**

```bash
-condition control treatment placebo  # Three values
```

**3. File reference:**

```bash
--ids ids.txt  # Reads values from file (one per line)
```

### Root Directory

By default, copies are created in the current directory. Use `--root` to specify a different location:

```bash
dir-wand --template template_{num} --root /output/experiments --num 0-5
```

## Common Patterns

### Multiple Placeholders

```bash
dir-wand --template exp_{id}_{condition} --id 0-2 -condition A B C
```

This creates 3 directories:

- `exp_0_A/`
- `exp_1_B/`
- `exp_2_C/`

**Important:** All value lists must have the same length!

### Running Without Template

If you already have directories and just want to run commands:

```bash
dir-wand --run "cd exp_{num} && python analyze.py" --num 0-5
```

### Silent Mode

Suppress all output (useful for scripts):

```bash
dir-wand --template template_{num} --num 0-100 --silent
```

## Next Steps

Now that you understand the basics:

- Learn about [working with templates](templates.md)
- Explore the [placeholder system](placeholders.md) in detail
- Discover [swapfiles](swapfiles.md) for complex scenarios
- See [command execution](commands.md) patterns
- Check out [examples](../examples/basic.md) for real-world use cases

## Troubleshooting

### Permission Errors

If you get permission errors when creating directories:

```bash
# Make sure you have write permissions
ls -la /path/to/output

# Or use a different root directory
dir-wand --template template --root ~/my_experiments --num 0-5
```

### Template Not Found

```bash
# Use absolute paths if relative paths don't work
dir-wand --template /full/path/to/template_{num} --num 0-5

# Or navigate to the directory first
cd /path/to/templates
dir-wand --template template_{num} --num 0-5
```

### Mismatched Value Lengths

```
ValueError: All swaps must have the same number of elements.
```

**Solution:** Ensure all placeholder value lists have the same length:

```bash
# Wrong: 3 values for num, 2 for seed
dir-wand --template exp_{num}_{seed} --num 0-2 --seed 42-43

# Correct: 3 values for each
dir-wand --template exp_{num}_{seed} --num 0-2 --seed 42-44
```

## Getting Help

- Use `dir-wand --help` to see all options
- Check the [API reference](../api/template.md) for detailed information
- Report issues on [GitHub](https://github.com/WillJRoper/dir-wand/issues)
