# Command Execution

WAND can execute shell commands in directories after creation or in existing directories. This guide covers command execution patterns and best practices.

## Basic Command Execution

### Running Commands After Creation

Execute a command in each directory after it's created:

```bash
dir-wand --template exp_{num} --num 0-5 --run "cd exp_{num} && python run.py"
```

**What happens:**

1. WAND creates `exp_0/`, `exp_1/`, ..., `exp_5/`
2. For each directory, runs the command (on a separate thread)
3. Commands execute concurrently
4. WAND waits for all commands to complete before exiting

### Running Commands in Existing Directories

Execute commands without creating directories:

```bash
dir-wand --run "cd exp_{num} && python analyze.py" --num 0-5
```

**Use case:** You already have directories and want to run commands in them.

## Command Syntax

### Simple Commands

```bash
dir-wand --template job_{id} --id 0-9 --run "echo 'Job {id} started'"
```

### Multiple Commands

Use `&&` to chain commands:

```bash
dir-wand --template exp_{num} --num 0-5 \
  --run "cd exp_{num} && python train.py && python evaluate.py"
```

### Commands with Options

```bash
dir-wand --template sim_{id} --id 0-99 \
  --run "cd sim_{id} && python simulate.py --id {id} --output results_{id}.csv"
```

### Shell Scripts

```bash
dir-wand --template job_{id} --id 0-9 \
  --run "cd job_{id} && ./run.sh {id}"
```

## Working Directory

### Important: Commands Run in CWD

Commands execute in the **current working directory**, not in the created directories:

```bash
# Current directory: /home/user/projects

dir-wand --template exp_{num} --root /data/experiments --num 0-2 \
  --run "cd /data/experiments/exp_{num} && python run.py"
#      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#      Must navigate to the directory first!
```

### Relative Paths

```bash
# If output is in current directory:
dir-wand --template exp_{num} --num 0-2 \
  --run "cd exp_{num} && python run.py"

# If output is elsewhere:
dir-wand --template exp_{num} --root /data/experiments --num 0-2 \
  --run "cd /data/experiments/exp_{num} && python run.py"
```

## Placeholder Replacement in Commands

### Basic Replacement

Placeholders in commands are replaced just like in files:

```bash
dir-wand --template exp_{id} --id 0-5 \
  --run "echo 'Processing experiment {id}'"
```

Output:

```
Processing experiment 0
Processing experiment 1
...
```

### Multiple Placeholders

```bash
dir-wand --template exp_{scenario}_{seed} \
  --scenario baseline treatment \
  --seed 42-43 \
  --run "python run.py --scenario {scenario} --seed {seed}"
```

### Quoting

Use single quotes for the entire command, double quotes inside:

```bash
dir-wand --template exp_{num} --num 0-5 \
  --run 'cd exp_{num} && python run.py --name "Experiment {num}"'
```

## Concurrent Execution

### Commands Run in Parallel

Each command runs on its own thread:

```bash
dir-wand --template job_{id} --id 0-99 \
  --run "cd job_{id} && ./long_running_task.sh"
```

All 100 commands start immediately and run concurrently.

### Thread Management

WAND:

- Creates one thread per command
- Starts all threads immediately (no thread pool limit)
- Waits for all to complete before exiting

**Performance note:** For very large numbers of commands, consider batching or using a job scheduler.

### Synchronization

WAND automatically waits for all commands to complete:

```bash
dir-wand --template exp_{num} --num 0-100 --run "cd exp_{num} && python train.py"
# WAND will not exit until all 101 training jobs are done
```

## Common Patterns

### Pattern 1: Train Models

```bash
dir-wand --template model_{id} --id 0-99 \
  --run "cd model_{id} && python train.py --config config_{id}.yaml"
```

### Pattern 2: Process Data Batches

```bash
dir-wand --template batch_{id} --id 0-999 \
  --run "cd batch_{id} && python process.py --input data_{id}.csv --output result_{id}.csv"
```

### Pattern 3: Run Simulations

```bash
dir-wand --template sim_{scenario}_{seed} \
  -scenario baseline treatment control \
  -seed 42 43 44 \
  --run "cd sim_{scenario}_{seed} && ./run_simulation.sh {seed}"
```

### Pattern 4: Generate Reports

```bash
# No template - just run in existing directories
dir-wand --run "cd exp_{num} && python generate_report.py" --num 0-50
```

### Pattern 5: Cleanup

```bash
dir-wand --run "cd exp_{num} && rm -f *.tmp *.log" --num 0-100
```

### Pattern 6: Collect Results

```bash
dir-wand --run "cd exp_{num} && cp results.csv ../collected/results_{num}.csv" \
  --num 0-99
```

## Error Handling

### Command Failures

If a command fails (non-zero exit code), WAND prints an error but continues:

```
Error: Command 'cd exp_5 && python run.py' failed with status code 1.
```

Other commands continue running.

### OS Errors

```
OSError occurred while running command 'cd exp_5 && python run.py': [Errno 2] No such file or directory
```

### Best Practices for Error Handling

**1. Check for errors in your scripts:**

```bash
#!/bin/bash
set -e  # Exit on error

cd "exp_{num}" || exit 1
python run.py || exit 1
python analyze.py || exit 1
```

**2. Log errors:**

```bash
dir-wand --template exp_{num} --num 0-99 \
  --run "cd exp_{num} && python run.py 2>&1 | tee error_{num}.log"
```

**3. Use conditional execution:**

```bash
dir-wand --template exp_{num} --num 0-99 \
  --run "cd exp_{num} && python run.py && echo 'Success' || echo 'Failed'"
```

## Advanced Techniques

### Environment Variables

```bash
export DATA_DIR=/shared/data

dir-wand --template exp_{num} --num 0-5 \
  --run "cd exp_{num} && python run.py --data \$DATA_DIR/input_{num}.csv"
```

Note the escaped `$` to prevent early expansion.

### Conditional Commands

```bash
dir-wand --template exp_{num} --num 0-99 \
  --run "cd exp_{num} && [ -f results.csv ] || python run.py"
#      Run only if results.csv doesn't exist
```

### Background Jobs

```bash
# Commands already run in background threads
# But if you want to detach from WAND:
dir-wand --template exp_{num} --num 0-5 \
  --run "cd exp_{num} && nohup python long_job.py > output.log 2>&1 &"
```

### Resource Management

```bash
# Limit parallel execution with external tools
dir-wand --template job_{id} --id 0-999 \
  --run "cd job_{id} && sem --jobs 10 python run.py"
#      GNU parallel's semaphore limits to 10 concurrent jobs
```

### Retry Logic

```bash
dir-wand --template exp_{num} --num 0-99 \
  --run "cd exp_{num} && for i in 1 2 3; do python run.py && break || sleep 10; done"
#      Retry up to 3 times with 10-second delay
```

## Integration with Swapfiles

Commands work with swapfiles:

```yaml
# config.yaml
experiment_id:
  range: 0-99

model:
  list:
    - resnet
    - vgg
```

```bash
dir-wand --template exp_{experiment_id}_{model} \
  --swapfile config.yaml \
  --run "cd exp_{experiment_id}_{model} && python train.py --model {model}"
```

## Output Capture

### Standard Output

Command output goes directly to stdout:

```bash
dir-wand --template exp_{num} --num 0-2 \
  --run "echo 'Running experiment {num}'"
```

Output:

```
Running experiment 0
Running experiment 1
Running experiment 2
```

### Redirect to Files

```bash
dir-wand --template exp_{num} --num 0-99 \
  --run "cd exp_{num} && python run.py > output_{num}.log 2>&1"
```

### Tee for Both

```bash
dir-wand --template exp_{num} --num 0-99 \
  --run "cd exp_{num} && python run.py 2>&1 | tee output_{num}.log"
```

## Performance Considerations

### Thread Overhead

- Each command creates a Python thread
- Thousands of concurrent commands may strain resources
- Consider batching for very large jobs

### I/O Bound vs CPU Bound

**Good for I/O bound tasks:**

```bash
# Network requests, file operations
dir-wand --template job_{id} --id 0-1000 \
  --run "cd job_{id} && wget https://example.com/data_{id}.csv"
```

**Less efficient for CPU bound:**

```bash
# CPU-intensive computations may not benefit from threading
dir-wand --template calc_{id} --id 0-1000 \
  --run "cd calc_{id} && python heavy_compute.py"
# Consider using a job scheduler instead
```

### Resource Limits

```bash
# Check system limits
ulimit -u  # Max user processes
ulimit -n  # Max open files

# Adjust if needed
ulimit -u 4096
```

## Troubleshooting

### Commands Not Running

**Check:**

1. Is the command valid in your shell?

   ```bash
   # Test command manually first
   cd exp_0 && python run.py
   ```

2. Are paths correct?

   ```bash
   # Use absolute paths if unsure
   dir-wand --template exp_{num} --num 0-5 \
     --run "cd /full/path/to/exp_{num} && python run.py"
   ```

3. Are placeholders replaced?

   ```bash
   # Verify with echo
   dir-wand --template exp_{num} --num 0-0 \
     --run "echo 'Directory: exp_{num}'"
   ```

### Permission Denied

```bash
# Make scripts executable
chmod +x template_{num}/run.sh

# Then create copies
dir-wand --template template_{num} --num 0-5 \
  --run "cd template_{num} && ./run.sh"
```

### Path Issues

```bash
# Add directory to PATH if needed
export PATH=$PATH:/path/to/scripts

dir-wand --template exp_{num} --num 0-5 \
  --run "cd exp_{num} && my_script.sh"
```

## Best Practices

### 1. Test Commands First

```bash
# Test with one copy
dir-wand --template exp_{num} --num 0-0 --run "cd exp_{num} && python run.py"

# If successful, run all
dir-wand --template exp_{num} --num 0-99 --run "cd exp_{num} && python run.py"
```

### 2. Use Absolute Paths

```bash
dir-wand --template exp_{num} --root /data/experiments --num 0-99 \
  --run "cd /data/experiments/exp_{num} && /usr/bin/python3 run.py"
```

### 3. Log Everything

```bash
dir-wand --template exp_{num} --num 0-99 \
  --run "cd exp_{num} && python run.py > stdout.log 2> stderr.log"
```

### 4. Handle Errors Gracefully

```bash
dir-wand --template exp_{num} --num 0-99 \
  --run "cd exp_{num} && python run.py || echo 'FAILED' > status.txt"
```

### 5. Document Commands

```bash
# Add comments to swapfile
# config.yaml
experiment_id:
  range: 0-99

# Run command:
# dir-wand --template exp_{experiment_id} --swapfile config.yaml \
#   --run "cd exp_{experiment_id} && python run.py"
```

## See Also

- [CommandRunner API](../api/command_runner.md) - Technical details
- [Templates Guide](templates.md) - Creating templates
- [Examples](../examples/basic.md) - Command execution examples
