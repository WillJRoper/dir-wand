"""The main runner for Directory WAND.

This module contains the main runner for Directory WAND. This is the entry
point for the template copying command line interface.

Example:
    $ python -m dir_wand path/to/template --root path/to/root
    --swap1 value1 --swap2 value2 -swap3 value3 value4 value5
"""

from dir_wand.parser import Parser
from dir_wand.template import Template


def main():
    """Wave the Directory WAND and make magic happen."""
    parser = Parser(
        description="Wave your Directory WAND and make magic happen."
    )

    # Get the arguments
    args = parser.parse_args()

    # Create the template
    template = Template(args.template, run=args.run, **args.replacements)

    # Give some feedback
    print(template)
    print("Template structure:")
    print(template.directory)

    # Make the copy
    template.make_copies(args.root)

    # Report we're done
    print("Done!")
