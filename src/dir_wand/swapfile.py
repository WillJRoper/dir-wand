"""A module for creating swapfiles.

A swapfile is a yaml file that contains all possible combinations of swaps that
can be made in a template. This modules provides the functionality to create
these files instead of generate them manually.

To use this functionatility, pass a swapfile and swaps to dir-wand but no
template.

Example:
    dir-wand --swapfile path/to/swapfile.yaml --swap1 1 2 3 --swap2 4 5 6
"""

import itertools

import yaml


def all_combinations(swaps):
    """
    Get all combinations of the swaps.

    Args:
        swaps (dict):
            The swaps to get the combinations for.

    Yields:
        dict:
            The next combination of swaps.
    """
    # Extract keys and value lists
    keys = list(swaps.keys())
    value_lists = [swaps[key] for key in keys]

    # Use product to get all combinations
    for combination in itertools.product(*value_lists):
        # Zip the combination values back with their keys
        yield dict(zip(keys, combination))


def get_swap_combos(swaps):
    """
    Get the swap combinations.

    Args:
        swaps (dict):
            The swaps to get the combinations for.

    Returns:
        list:
            A list of all the swap combinations.
    """
    # Combine each combination into a single dictionary with an entry for each
    # placeholder
    transposed = {}
    for combo in all_combinations(swaps):
        for key in combo:
            if key not in transposed:
                transposed[key] = {"list": []}  # "list" for yaml structure
            transposed[key]["list"].append(combo[key])

    return transposed


def make_swapfile(yaml_path, swaps):
    """
    Make a swapfile from the swaps.

    This will create a yaml file with all possible combinations of the swaps.

    Args:
        yaml_path (str):
            The path to the yaml file to write.
        swaps (dict):
            The swaps to get the combinations for.

    Returns:
        dict:
            The swapfile dictionary.
    """
    # Write the swapfile
    with open(yaml_path, "w") as file:
        yaml.safe_dump(get_swap_combos(swaps), file)
