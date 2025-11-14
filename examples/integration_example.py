#!/usr/bin/env python3
"""Example of integrating WAND into a larger Python application."""

import argparse
import json
from pathlib import Path
from typing import Dict, List

from dir_wand import create_directories, run_commands


class ExperimentManager:
    """Manage machine learning experiments using WAND."""

    def __init__(self, base_dir: str = "/tmp/ml_experiments"):
        """Initialize the experiment manager.

        Args:
            base_dir: Base directory for all experiments.
        """
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def create_experiment(
        self,
        experiment_id: int,
        models: List[str],
        datasets: List[str],
        learning_rates: List[float],
    ) -> Dict[str, int]:
        """Create experiment directories for a grid search.

        Args:
            experiment_id: Unique experiment identifier.
            models: List of model architectures to test.
            datasets: List of datasets to use.
            learning_rates: List of learning rates to try.

        Returns:
            Dictionary with creation statistics.
        """
        # Ensure all lists have the same length
        # (Cartesian product would require swapfile generation)
        if not (len(models) == len(datasets) == len(learning_rates)):
            raise ValueError("All parameter lists must have the same length")

        # Create experiment template
        template_dir = self.base_dir / f"exp_{experiment_id}_{{model}}_{{lr}}"

        # Create directories with WAND
        stats = create_directories(
            template=str(template_dir),
            output_dir=str(self.base_dir),
            model=models,
            dataset=datasets,
            lr=learning_rates,
            silent=True
        )

        # Create config files programmatically
        for i, (model, dataset, lr) in enumerate(
            zip(models, datasets, learning_rates)
        ):
            config_dir = (
                self.base_dir
                / f"exp_{experiment_id}_{model}_{lr}"
            )
            config_file = config_dir / "config.json"

            config = {
                "experiment_id": experiment_id,
                "model": model,
                "dataset": dataset,
                "learning_rate": lr,
                "batch_size": 32,
                "epochs": 100,
            }

            config_file.write_text(json.dumps(config, indent=2))

        return stats

    def run_training(
        self,
        experiment_id: int,
        models: List[str],
        learning_rates: List[float],
    ) -> Dict[str, int]:
        """Run training for all experiment configurations.

        Args:
            experiment_id: Experiment identifier.
            models: List of models used in the experiment.
            learning_rates: List of learning rates used.

        Returns:
            Dictionary with execution statistics.
        """
        command = (
            f"cd {self.base_dir}/exp_{experiment_id}_{{model}}_{{lr}} && "
            "python -m train --config config.json > training.log 2>&1"
        )

        stats = run_commands(
            command=command,
            model=models,
            lr=learning_rates,
            silent=True
        )

        return stats

    def collect_results(
        self,
        experiment_id: int,
        models: List[str],
        learning_rates: List[float],
    ) -> List[Dict]:
        """Collect results from all experiment runs.

        Args:
            experiment_id: Experiment identifier.
            models: List of models used.
            learning_rates: List of learning rates used.

        Returns:
            List of result dictionaries.
        """
        results = []

        for model, lr in zip(models, learning_rates):
            exp_dir = self.base_dir / f"exp_{experiment_id}_{model}_{lr}"
            result_file = exp_dir / "results.json"

            if result_file.exists():
                result = json.loads(result_file.read_text())
                results.append(result)
            else:
                results.append({
                    "model": model,
                    "lr": lr,
                    "status": "not_found"
                })

        return results

    def cleanup(self, experiment_id: int) -> None:
        """Clean up experiment directories.

        Args:
            experiment_id: Experiment to clean up.
        """
        # Find all directories for this experiment
        import shutil

        for exp_dir in self.base_dir.glob(f"exp_{experiment_id}_*"):
            shutil.rmtree(exp_dir)

        print(f"Cleaned up experiment {experiment_id}")


def main():
    """Run example workflow."""
    parser = argparse.ArgumentParser(
        description="ML Experiment Manager using WAND"
    )
    parser.add_argument(
        "--experiment-id",
        type=int,
        default=1,
        help="Experiment ID"
    )
    args = parser.parse_args()

    print("=" * 60)
    print(f"Machine Learning Experiment Manager (ID: {args.experiment_id})")
    print("=" * 60)

    # Initialize manager
    manager = ExperimentManager()

    # Define experiment parameters
    models = ["resnet50", "vgg16", "inception"]
    datasets = ["cifar10", "cifar10", "cifar10"]  # Same dataset for simplicity
    learning_rates = [0.001, 0.01, 0.1]

    # Create experiments
    print("\nCreating experiment directories...")
    stats = manager.create_experiment(
        experiment_id=args.experiment_id,
        models=models,
        datasets=datasets,
        learning_rates=learning_rates
    )
    print(f"Created {stats['directories']} experiment configurations")

    # Simulate running training (commented out - would need actual training code)
    # print("\nRunning training...")
    # train_stats = manager.run_training(
    #     experiment_id=args.experiment_id,
    #     models=models,
    #     learning_rates=learning_rates
    # )
    # print(f"Executed {train_stats['commands']} training runs")

    # # Collect results
    # print("\nCollecting results...")
    # results = manager.collect_results(
    #     experiment_id=args.experiment_id,
    #     models=models,
    #     learning_rates=learning_rates
    # )
    # print(f"Collected {len(results)} results")
    #
    # # Display summary
    # print("\nExperiment Summary:")
    # for result in results:
    #     print(f"  {result}")

    print("\nExperiment directories created successfully!")
    print(f"Location: {manager.base_dir}")

    # Cleanup (commented out - uncomment to clean up)
    # print("\nCleaning up...")
    # manager.cleanup(args.experiment_id)

    print("=" * 60)


if __name__ == "__main__":
    main()
