"""A module containing the command-line interface for Directory WAND.

This module contains the Parser class for parsing command line arguments. The
Parser class is a wrapper around the argparse.ArgumentParser class that adds
some standardised arguments and enables arbitrarily many arbitrarily named
arguments.

Example:
    To use the Parser class, simply create an instance of the class and call
    the parse_args method. This will return a namespace containing the parsed
    command line arguments.

    >>> parser = Parser(description="A description of the program.")
    >>> args = parser.parse_args()
"""

import argparse
import os
import sys

import yaml


def parse_swapfile(swapfile):
    """
    Parse the swapfile.

    Args:
        swapfile (str):
            The path to the swapfile.

    Returns:
        dict:
            The swaps to make in the template.
    """
    # Create a dictionary to store the swaps
    swaps = {}

    # If we have no swapfile, return an empty dictionary
    if swapfile is None:
        return swaps

    # Process the swapfile if given
    with open(swapfile, "r") as file:
        swapfile_dict = yaml.safe_load(file)

    # Unpack the contents of the swapfile
    for key, swap_dict in swapfile_dict.items():
        # Do we have a list?
        if swap_dict.get("list") is not None:
            swaps[key] = swap_dict["list"]

        # Do we have a file?
        elif swap_dict.get("file") is not None:
            with open(swap_dict["file"], "r") as file:
                swaps[key] = file.read().splitlines()

        # Do we have the defintion of a range, i.e. 1-10?
        elif swap_dict.get("range") is not None:
            swap_range = swap_dict["range"]
            start, end = swap_range.split("-")
            swaps[key] = list(range(int(start), int(end) + 1))

    return swaps


def parse_swaps(**swaps):
    """
    Parse the swaps.

    Args:
        **swaps (dict):
            The swaps to make in the template.

    Raises:
        ValueError:
            If the number of swaps isn't equal between all placeholders.
    """
    for key, value in swaps.items():
        # Do we have a list?
        if isinstance(value, (list, tuple)):
            swaps[key] = value

        # Do we have a file?
        elif os.path.isfile(value):
            with open(value, "r") as file:
                swaps[key] = file.read().splitlines()

        # Do we have the defintion of a range, i.e. 1-10?
        elif "-" in value:
            # Split the range
            start, end = value.split("-")

            # Convert the range to a dictionary
            swaps[key] = list(range(int(start), int(end) + 1))
        else:
            raise ValueError(f"Invalid swap value: {value}")

    return swaps


class StoreDictKeyPair(argparse.Action):
    """A class for storing key-value pairs from the command line."""

    def __call__(self, parser, namespace, values, option_string=None):
        """
        Store the key-value pair in the namespace.

        Args:
            parser (argparse.ArgumentParser):
                The parser instance.
            namespace (argparse.Namespace):
                The namespace to store the key-value pair in.
            values (str):
                The key-value pair to store.
            option_string (str):
                The option string.
        """
        key = option_string.lstrip("--")
        if not hasattr(namespace, "swaps"):
            setattr(namespace, "swaps", {})
        getattr(namespace, "swaps")[key] = values


class StoreListKeyPair(argparse.Action):
    """A class for storing key-value pairs from the command line."""

    def __call__(self, parser, namespace, values, option_string=None):
        """
        Store the key-value pair in the namespace.

        Args:
            parser (argparse.ArgumentParser):
                The parser instance.
            namespace (argparse.Namespace):
                The namespace to store the key-value pair in.
            values (str):
                The key-value pair to store.
            option_string (str):
                The option string.
        """
        key = option_string.lstrip("-")
        if not hasattr(namespace, "list_args"):
            setattr(namespace, "list_args", {})
        namespace.list_args[key] = values


class Parser(argparse.ArgumentParser):
    """
    A class for parsing command line arguments.

    NOTE: This class is a wrapper around the argparse.ArgumentParser class
    adding some standardised arguments and enabling arbitrarily many
    arbitrarily named arguments.

    Attributes:
        parser (argparse.ArgumentParser):
            The parser instance.
    """

    def __init__(self, description):
        """
        Create the parser instance.

        Args:
            description (str):
                A description of the program.
        """
        # Create the parser
        super(Parser, self).__init__(description=description)

        # Add the template argument
        self.add_argument(
            "--template",
            type=str,
            help="The template to use for the model.",
            default=None,
        )

        # Add an optional path to the root for the outputs
        self.add_argument(
            "--root",
            type=str,
            help="The root directory for the outputs.",
            default=".",
        )

        # Add an optional argument for a command to run once a copy is complete
        self.add_argument(
            "--run",
            type=str,
            help="A command to run in each copy once the copy is complete. "
            "The command will be run in the current working directory.",
            default=None,
        )

        # Add an optional argument for the swapfile
        self.add_argument(
            "--swapfile",
            type=str,
            help="A yaml file defining the swaps for each placeholder.",
            default=None,
        )

        # Add silent mode which will suppress all WAND prints
        self.add_argument(
            "--silent",
            action="store_true",
            help="Suppress all WAND prints.",
            default=False,
        )

        # Add arbitrary arguments
        self.add_argument(
            "--",
            dest="swaps",
            action=StoreDictKeyPair,
            nargs=1,
            metavar="VALUE",
            help="A key-value pair for a placeholder replacement. Should "
            "be in the form --key value, where key is the name ({name}) to "
            "replace in directory paths and files, and value is an "
            "inclusive range (1-5), or a filepath to a file contain a list."
            "of values.",
        )
        self.add_argument(
            "-",
            dest="swaps",
            action=StoreListKeyPair,
            nargs="+",
            metavar="VALUE",
            help="A key-value pair for a placeholder replacement. Should "
            "be in the form -key value1 value2 value3, where key is the name "
            "({name}) to replace in directory paths and files, and value is "
            "a list.",
        )

    def __str__(self):
        """Summarise the command line arguments."""
        self.print_help()
        return ""

    def parse_args(self, args=None, namespace=None):
        """
        Parse the command line arguments.

        This will handle any "unknown" arguments that are passed to the
        command line by storing them in a dictionary called "swaps"
        attached to the returned namespace.

        Args:
            args (list):
                The command line arguments to parse.
            namespace (argparse.Namespace):
                The namespace to store the parsed arguments in.

        Returns:
            argparse.Namespace:
                The parsed command line arguments.
        """
        if args is None:
            args = sys.argv[1:]

        # If no arguments are provided, display help
        if not args:
            self.print_help()
            self.exit()
        # Parse arguments
        args, unknown_args = self.parse_known_args()

        # Parse the swapfile. If we have a swapfile but no template or run then
        # we're creating a swapfile instead so we can ignore this step
        if args.template is not None or args.run is not None:
            args.swaps = parse_swapfile(args.swapfile)
        else:
            args.swaps = {}

            # When creating a swapfile we want to be silent
            args.silent = True

        # Process unknown_args manually
        while unknown_args:
            if unknown_args[0].startswith("--"):
                key = unknown_args.pop(0).lstrip("--")
                if (
                    unknown_args
                    and not unknown_args[0].startswith("-")
                    and not unknown_args[0].startswith("--")
                ):
                    value = unknown_args.pop(0)
                    args.swaps[key] = value
                else:
                    args.swaps[key] = None
            elif unknown_args[0].startswith("-"):
                key = unknown_args.pop(0).lstrip("-")
                values = []
                while (
                    unknown_args
                    and not unknown_args[0].startswith("-")
                    and not unknown_args[0].startswith("--")
                ):
                    values.append(unknown_args.pop(0))
                args.swaps[key] = values
            else:
                unknown_args.pop(0)

        # Parse the swaps so we have what we need
        args.swaps = parse_swaps(**args.swaps)

        return args
