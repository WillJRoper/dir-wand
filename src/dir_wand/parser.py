"""A module containing the command-line interface for Directory WAND.

This module contains the Parser class for parsing command line arguments. The
Parser class is a wrapper around the argparse.ArgumentParser class that adds
some standardised arguments and enables arbitrarily many arbitrarily named
arguments.
"""

import argparse


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
        print(key, value)
        # Do we have a list?
        if isinstance(value, (list, tuple)):
            swaps[key] = value

        # Do we have the defintion of a range, i.e. 1-10?
        elif "-" in value:
            # Split the range
            start, end = value.split("-")

            # Convert the range to a dictionary
            swaps[key] = list(range(int(start), int(end) + 1))
        else:
            raise ValueError(f"Invalid swap value: {value}")

    # Ensure we have the same number of elements for all swaps
    lengths = {len(value) for value in swaps.values()}
    if len(lengths) > 1:
        raise ValueError("All swaps must have the same number of elements")

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
        if not hasattr(namespace, "replacements"):
            setattr(namespace, "replacements", {})
        getattr(namespace, "replacements")[key] = values


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

        # Add arbitrary arguments
        self.add_argument(
            "--",
            dest="replacements",
            action=StoreDictKeyPair,
            nargs=1,
            metavar="VALUE",
            help="A key-value pair for a placeholder replacement. Should "
            "be in the form --key value, where key is the name ({name}) to "
            "replace in directory paths and files, and value is an "
            "inclusive range (1-5).",
        )
        self.add_argument(
            "-",
            dest="replacements",
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

    def parse_args(self):
        """
        Parse the command line arguments.

        This will handle any "unknown" arguments that are passed to the
        command line by storing them in a dictionary called "replacements"
        attached to the returned namespace.

        Returns:
            argparse.Namespace:
                The parsed command line arguments.
        """
        # Parse arguments
        args, unknown_args = self.parse_known_args()

        args.replacements = {}

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
                    args.replacements[key] = value
                else:
                    args.replacements[key] = None
            elif unknown_args[0].startswith("-"):
                key = unknown_args.pop(0).lstrip("-")
                values = []
                while (
                    unknown_args
                    and not unknown_args[0].startswith("-")
                    and not unknown_args[0].startswith("--")
                ):
                    values.append(unknown_args.pop(0))
                args.replacements[key] = values
            else:
                unknown_args.pop(0)

        # Parse the swaps so we have what we need
        args.replacements = parse_swaps(**args.replacements)

        return args
