"""A module containing the utility functions."""

import re

from dir_wand.logger import Logger


def swap_in_str(string, **swaps):
    """
    Swap in the values to the string.

    This function will swap in the values to the string using the swaps
    dictionary.

    Args:
        string (str):
            The string to swap the values into.
        **swaps (dict):
            The swaps to make in the string.

    Returns:
        str:
            The string with the values swapped in.
    """
    # Find all swap in string
    swap_in_string = set(re.findall(r"\{(\w+)\}", string))

    # Count the swaps we've made
    for swap in swap_in_string:
        Logger().swap_counts.setdefault(swap, 0)
        Logger().swap_counts[swap] += 1

    # Ensure we have enough swaps
    missing_swaps = swap_in_string - set(swaps.keys())
    if len(missing_swaps) > 0:
        raise ValueError(f"Missing swaps: {missing_swaps}")

    return string.format(**swaps)
