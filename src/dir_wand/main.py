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

    # Create the template
    template = Template(args.template, run=args.run, **args.swaps)

    # Give some feedback
    print(template)
    print()
    print("Template structure:")
    print(template.directory)

    # Make the copy
    template.make_copies(args.root)


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
    else:
        # Otherwise, we're simply running a command
        run_main(args)

    # Report what we've done
    Logger().report()
