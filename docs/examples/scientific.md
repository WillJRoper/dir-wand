# Scientific Computing Examples

Examples of using WAND for scientific simulations, experiments, and analyses.

## Monte Carlo Simulations

Run Monte Carlo simulations with different random seeds.

### Template Setup

```bash
# Create template
mkdir "monte_carlo_{seed}"

# Configuration file
cat > "monte_carlo_{seed}/config.yaml" << 'EOF'
simulation:
  name: "Monte Carlo Simulation {seed}"
  random_seed: {seed}
  iterations: 100000
  output_file: "results_{seed}.csv"

parameters:
  sample_size: 1000
  confidence_level: 0.95
EOF

# Simulation script
cat > "monte_carlo_{seed}/run_simulation.py" << 'EOF'
#!/usr/bin/env python3
import random
import yaml
import csv

# Load configuration
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

# Set random seed for reproducibility
random.seed(config["simulation"]["random_seed"])

# Run simulation
results = []
for i in range(config["simulation"]["iterations"]):
    # Simulate random process
    value = random.gauss(0, 1)
    results.append(value)

# Save results
with open(config["simulation"]["output_file"], "w") as f:
    writer = csv.writer(f)
    writer.writerow(["iteration", "value"])
    for i, value in enumerate(results):
        writer.writerow([i, value])

print(f"Simulation complete: {len(results)} iterations")
EOF

chmod +x "monte_carlo_{seed}/run_simulation.py"
```

### Execution

```bash
# Run 10 simulations with different seeds
dir-wand --template "monte_carlo_{seed}" --seed 42-51 \
  --run "cd monte_carlo_{seed} && python3 run_simulation.py"
```

## Parameter Sensitivity Analysis

Test how a model responds to different parameter values.

### Template Setup

```bash
mkdir "sensitivity_{param_value}"

cat > "sensitivity_{param_value}/config.yaml" << 'EOF'
analysis:
  parameter_name: "diffusion_coefficient"
  parameter_value: {param_value}
  baseline_value: 1.0

model:
  time_steps: 1000
  spatial_resolution: 0.01
  output: "sensitivity_{param_value}.nc"
EOF

cat > "sensitivity_{param_value}/run_model.sh" << 'EOF'
#!/bin/bash
echo "Running sensitivity analysis with parameter value: {param_value}"
python3 /shared/models/diffusion_model.py --config config.yaml
EOF

chmod +x "sensitivity_{param_value}/run_model.sh"
```

### Execution

```bash
# Test parameter values from 0.5 to 2.0
dir-wand --template "sensitivity_{param_value}" \
  -param_value 0.5 0.75 1.0 1.25 1.5 1.75 2.0 \
  --run "cd sensitivity_{param_value} && ./run_model.sh"
```

## Multi-Model Ensemble

Run multiple models with identical initial conditions.

### Template Setup

```bash
mkdir "ensemble_{model}_{member}"

cat > "ensemble_{model}_{member}/config.yaml" << 'EOF'
ensemble:
  model: {model}
  member_id: {member}

initial_conditions:
  temperature: 298.15
  pressure: 101325
  concentration: 1.0

random_seed: {member}  # Different seed for each member

output:
  directory: "output_{model}_{member}"
  format: "netcdf"
EOF
```

### Execution with Swapfile

```bash
# Create all combinations
dir-wand --swapfile ensemble.yaml \
  -model ModelA ModelB ModelC ModelD \
  -member 1 2 3 4 5

# Run ensemble
dir-wand --template "ensemble_{model}_{member}" \
  --swapfile ensemble.yaml \
  --run "cd ensemble_{model}_{member} && /usr/local/bin/run_model config.yaml"
```

## Experimental Design: Full Factorial

Run all combinations of experimental factors.

### Template Setup

```bash
mkdir "factorial_{factor_a}_{factor_b}_{replicate}"

cat > "factorial_{factor_a}_{factor_b}_{replicate}/experiment.yaml" << 'EOF'
experiment:
  design: "full_factorial"

factors:
  factor_a: {factor_a}
  factor_b: {factor_b}

replicate:
  number: {replicate}
  seed: {replicate}

measurements:
  - response_time
  - accuracy
  - throughput

output_file: "results_{factor_a}_{factor_b}_{replicate}.csv"
EOF

cat > "factorial_{factor_a}_{factor_b}_{replicate}/run_experiment.py" << 'EOF'
#!/usr/bin/env python3
import yaml
import random
import csv

with open("experiment.yaml") as f:
    config = yaml.safe_load(f)

# Set seed
random.seed(config["replicate"]["seed"])

# Simulate experiment
factor_a = float(config["factors"]["factor_a"])
factor_b = float(config["factors"]["factor_b"])

# Simulated measurements (replace with actual experiment)
response_time = factor_a * 10 + factor_b * 5 + random.gauss(0, 1)
accuracy = 0.9 - (factor_a - 1) * 0.1 + random.gauss(0, 0.05)
throughput = factor_b * 100 + random.gauss(0, 10)

# Save results
with open(config["output_file"], "w") as f:
    writer = csv.DictWriter(f, fieldnames=["metric", "value"])
    writer.writeheader()
    writer.writerow({"metric": "response_time", "value": response_time})
    writer.writerow({"metric": "accuracy", "value": accuracy})
    writer.writerow({"metric": "throughput", "value": throughput})

print(f"Experiment complete: A={factor_a}, B={factor_b}, Rep={config['replicate']['number']}")
EOF

chmod +x "factorial_{factor_a}_{factor_b}_{replicate}/run_experiment.py"
```

### Execution

```bash
# Generate all combinations
dir-wand --swapfile factorial_design.yaml \
  -factor_a 0.5 1.0 1.5 \
  -factor_b 10 20 30 \
  -replicate 1 2 3

# This creates 27 combinations (3 × 3 × 3)

# Run all experiments
dir-wand --template "factorial_{factor_a}_{factor_b}_{replicate}" \
  --swapfile factorial_design.yaml \
  --run "cd factorial_{factor_a}_{factor_b}_{replicate} && python3 run_experiment.py"
```

## Time Series Analysis with Bootstrapping

Perform bootstrap analysis with multiple resamples.

### Template Setup

```bash
mkdir "bootstrap_{dataset}_{resample_id}"

cat > "bootstrap_{dataset}_{resample_id}/analysis_config.yaml" << 'EOF'
analysis:
  method: "bootstrap"
  dataset: {dataset}
  resample_id: {resample_id}
  seed: {resample_id}

bootstrap:
  n_resamples: 1
  confidence_level: 0.95
  statistic: "mean"

input_file: "/shared/data/{dataset}.csv"
output_file: "bootstrap_{dataset}_{resample_id}.json"
EOF

cat > "bootstrap_{dataset}_{resample_id}/run_bootstrap.py" << 'EOF'
#!/usr/bin/env python3
import yaml
import pandas as pd
import numpy as np
import json

with open("analysis_config.yaml") as f:
    config = yaml.safe_load(f)

# Load data
data = pd.read_csv(config["input_file"])

# Set seed
np.random.seed(config["analysis"]["seed"])

# Perform bootstrap resample
n = len(data)
indices = np.random.choice(n, size=n, replace=True)
bootstrap_sample = data.iloc[indices]

# Calculate statistic
statistic_value = bootstrap_sample.mean().to_dict()

# Save result
result = {
    "dataset": config["analysis"]["dataset"],
    "resample_id": config["analysis"]["resample_id"],
    "statistic": statistic_value
}

with open(config["output_file"], "w") as f:
    json.dump(result, f, indent=2)

print(f"Bootstrap complete: dataset={config['analysis']['dataset']}, resample={config['analysis']['resample_id']}")
EOF

chmod +x "bootstrap_{dataset}_{resample_id}/run_bootstrap.py"
```

### Execution

```bash
# Run 1000 bootstrap resamples for each of 3 datasets
for dataset in dataset1 dataset2 dataset3; do
    dir-wand --template "bootstrap_${dataset}_{resample_id}" \
      --resample_id 0-999 \
      --run "cd bootstrap_${dataset}_{resample_id} && python3 run_bootstrap.py"
done
```

## Climate Model Scenarios

Run climate models with different scenarios and initial conditions.

### Template Setup

```bash
mkdir "climate_{scenario}_{start_year}_{ensemble_member}"

cat > "climate_{scenario}_{start_year}_{ensemble_member}/model_config.yaml" << 'EOF'
model:
  name: "RegionalClimateModel"
  version: "2.5"

scenario:
  name: {scenario}
  description: "Climate scenario {scenario}"

time:
  start_year: {start_year}
  end_year: 2100
  timestep: "1day"

ensemble:
  member: {ensemble_member}
  perturbation_seed: {ensemble_member}

output:
  directory: "output_{scenario}_{start_year}_{ensemble_member}"
  variables:
    - temperature
    - precipitation
    - wind_speed
  format: "netcdf4"
EOF

cat > "climate_{scenario}_{start_year}_{ensemble_member}/run_model.sh" << 'EOF'
#!/bin/bash
set -e

echo "Starting climate model run"
echo "Scenario: {scenario}"
echo "Start year: {start_year}"
echo "Ensemble member: {ensemble_member}"

# Load modules (adjust for your system)
module load netcdf/4.7.4
module load hdf5/1.12.0

# Run model
/opt/climate/bin/run_model \
    --config model_config.yaml \
    --threads 8 \
    --output output_{scenario}_{start_year}_{ensemble_member}

echo "Model run complete"
EOF

chmod +x "climate_{scenario}_{start_year}_{ensemble_member}/run_model.sh"
```

### Execution

```bash
# Create swapfile with all combinations
dir-wand --swapfile climate_scenarios.yaml \
  -scenario RCP26 RCP45 RCP60 RCP85 \
  -start_year 2020 2030 2040 \
  -ensemble_member 1 2 3 4 5 6 7 8 9 10

# This creates 4 × 3 × 10 = 120 model runs

# Run on HPC cluster (example with SLURM)
dir-wand --template "climate_{scenario}_{start_year}_{ensemble_member}" \
  --swapfile climate_scenarios.yaml \
  --run "cd climate_{scenario}_{start_year}_{ensemble_member} && sbatch run_model.sh"
```

## Best Practices for Scientific Computing

### 1. Use Version Control

```bash
# Track template
git add template_{id}/
git commit -m "Add simulation template v1.0"

# Track swapfile
git add experiment_design.yaml
git commit -m "Define experimental parameters"
```

### 2. Document Parameters

```yaml
# Always document in configs
# config.yaml
# Parameter definitions:
#   diffusion_coeff: Diffusion coefficient (m²/s), range: 0.001-0.01
#   temperature: Temperature (K), range: 273-373
#   pressure: Pressure (Pa), range: 1e5-1e6

parameters:
  diffusion_coeff: {diff}
  temperature: {temp}
  pressure: {press}
```

### 3. Use Consistent Random Seeds

```bash
# Reproducible results
dir-wand --template "sim_{id}" --id 0-99 \
  # seed = id + fixed_offset for reproducibility
```

### 4. Log Everything

```bash
dir-wand --template "exp_{id}" --id 0-999 \
  --run "cd exp_{id} && python run.py > stdout.log 2> stderr.log"
```

### 5. Check Results

```bash
# After running, verify all completed
for i in {0..99}; do
    if [ ! -f "exp_$i/results.csv" ]; then
        echo "Missing results for experiment $i"
    fi
done
```

## See Also

- [Data Processing Examples](data-processing.md)
- [Testing Examples](testing.md)
- [Basic Examples](basic.md)
