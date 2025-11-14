#!/usr/bin/env python3
"""Scientific computing workflow using WAND programmatic API."""

import json
from pathlib import Path

from dir_wand import (
    create_directories,
    create_template_structure,
    generate_swapfile,
    load_swapfile,
    run_commands,
)


def setup_simulation_template():
    """Create a simulation template programmatically."""
    print("Setting up simulation template...")

    # Create template structure
    create_template_structure(
        "simulation_{scenario}_{seed}",
        directories=["input", "output", "logs"],
        files={
            "config.yaml": """
simulation:
  scenario: {scenario}
  random_seed: {seed}
  timesteps: 1000

output:
  directory: output
  format: csv
  filename: results_{scenario}_{seed}.csv
""",
            "run.sh": """#!/bin/bash
set -e
echo "Running simulation: {scenario} with seed {seed}"
python /usr/local/bin/simulate.py --config config.yaml
echo "Simulation complete"
""",
            "README.md": """# Simulation {scenario}_{seed}

Random seed: {seed}
Scenario: {scenario}

## Running
```bash
./run.sh
```
"""
        }
    )

    print("Template created: simulation_{scenario}_{seed}")


def create_parameter_grid():
    """Generate a swapfile with all parameter combinations."""
    print("\nGenerating parameter grid...")

    num_combinations = generate_swapfile(
        "/tmp/simulation_grid.yaml",
        scenario=["baseline", "intervention_a", "intervention_b"],
        seed=range(42, 52)  # 10 random seeds
    )

    print(f"Generated {num_combinations} parameter combinations")
    return num_combinations


def run_simulation_batch():
    """Run a batch of simulations using the parameter grid."""
    print("\nRunning simulation batch...")

    # Load the swapfile
    params = load_swapfile("/tmp/simulation_grid.yaml")

    # Create all simulation directories
    stats = create_directories(
        template="simulation_{scenario}_{seed}",
        output_dir="/tmp/simulations",
        run_command="cd simulation_{scenario}_{seed} && ./run.sh",
        **params
    )

    print(f"\nCreated {stats['directories']} simulation directories")
    print(f"Executed {stats['commands']} simulations")

    return stats


def analyze_results():
    """Analyze simulation results."""
    print("\nAnalyzing results...")

    # Load parameters
    params = load_swapfile("/tmp/simulation_grid.yaml")

    # Run analysis in each directory
    stats = run_commands(
        command=(
            "cd /tmp/simulations/simulation_{scenario}_{seed} && "
            "echo '{\"scenario\": \"{scenario}\", \"seed\": {seed}}' > analysis.json"
        ),
        **params
    )

    print(f"Analyzed {stats['commands']} simulations")


def collect_and_summarize():
    """Collect results from all simulations."""
    print("\nCollecting and summarizing results...")

    # Create collection directory
    Path("/tmp/simulation_results").mkdir(exist_ok=True)

    # Load parameters
    params = load_swapfile("/tmp/simulation_grid.yaml")

    # Collect results
    run_commands(
        command=(
            "cp /tmp/simulations/simulation_{scenario}_{seed}/output/results_{scenario}_{seed}.csv "
            "/tmp/simulation_results/ 2>/dev/null || echo 'No results for {scenario}_{seed}'"
        ),
        silent=True,
        **params
    )

    print("Results collected in /tmp/simulation_results/")


def main():
    """Run complete scientific workflow."""
    print("=" * 60)
    print("Scientific Computing Workflow with WAND")
    print("=" * 60)

    # Step 1: Set up template
    setup_simulation_template()

    # Step 2: Generate parameter combinations
    num_params = create_parameter_grid()

    # Step 3: Run simulations
    stats = run_simulation_batch()

    # Step 4: Analyze results
    analyze_results()

    # Step 5: Collect and summarize
    collect_and_summarize()

    print("\n" + "=" * 60)
    print("Workflow Summary:")
    print(f"  - Parameter combinations: {num_params}")
    print(f"  - Directories created: {stats['directories']}")
    print(f"  - Simulations run: {stats['commands']}")
    print(f"  - Placeholder replacements: {stats['swaps']}")
    print("=" * 60)


if __name__ == "__main__":
    main()
