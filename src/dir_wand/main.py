"""The main runner for Directory WAND.

This module contains the main runner for Directory WAND. This is the entry
point for the template copying command line interface.

Example:
    $ python -m dir_wand path/to/template --root path/to/root
    --swap1 value1 --swap2 value2 -swap3 value3 value4 value5
"""

from dir_wand.art import ASCII_ART
from dir_wand.logger import Logger
from dir_wand.parser import Parser
from dir_wand.swapfile import make_swapfile


def copies_main(args):
    """
    Make copies of a template directory.

    Args:
        args (Namespace):
            The parsed command line arguments.
    """
    # Delay import to ensure Logger is instantiated before we import
    # modules that use it's decorators
    from dir_wand.template import Template

    # Ensure we have the same number of elements for all swaps, we do this
    # here because not all use cases require the number to be equal at the time
    # of parsing
    length_dict = {key: len(value) for key, value in args.swaps.items()}
    lengths = {len(value) for value in args.swaps.values()}
    if len(lengths) > 1:
        raise ValueError(
            "All swaps must have the same number of elements. "
            f"Got: {length_dict}"
        )

    # Create the template
    template = Template(args.template, run=args.run, **args.swaps)

    # Give some feedback
    print(template)
    print()
    print("Template structure:")
    print(template.directory)

    # Make the copy
    template.make_copies(args.root)


def swapfile_main(args):
    """
    Create a swapfile for a template directory.

    Args:
        args (Namespace):
            The parsed command line arguments.
    """
    # Make the swapfile
    make_swapfile(args.swapfile, args.swaps)


def run_main(args):
    """
    Run a command in a directory.

    Args:
        args (Namespace):
            The parsed command line arguments.
    """
    # Delay import to ensure Logger is instantiated before we import
    # modules that use it's decorators
    from dir_wand.command_runner import CommandRunner

    # Ensure we have the same number of elements for all swaps, we do this
    # here because not all use cases require the number to be equal at the time
    # of parsing
    length_dict = {key: len(value) for key, value in args.swaps.items()}
    lengths = {len(value) for value in args.swaps.values()}
    if len(lengths) > 1:
        raise ValueError(
            "All swaps must have the same number of elements. "
            f"Got: {length_dict}"
        )

    # Create the command runner
    command_runner = CommandRunner(args.run)

    # Run the command for all the swap combinations
    command_runner.run_command_for_all_swaps(**args.swaps)


def main():
    """Wave the Directory WAND and make magic happen."""
    parser = Parser(
        description="Wave your Directory WAND and make magic happen."
    )

    # Get the arguments
    args = parser.parse_args()

    # Set up the logger
    Logger(silent=args.silent)

    # Greet
    print()
    print(ASCII_ART)
    print()

    # Are we copying a template?
    if args.template is not None:
        copies_main(args)

    # If we have no template but have been given a swapfile, we're creating
    # a swapfile
    elif args.swapfile is not None and args.run is None:
        swapfile_main(args)
        return  # no point in reporting

    # Otherwise, we're simply running a command
    else:
        run_main(args)

    # Report what we've done
    Logger().report()
