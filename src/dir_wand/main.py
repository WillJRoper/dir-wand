"""The main runner for Directory WAND"""

from dir_wand.parser import Parser
from dir_wand.template import Template


def main():
    """Wave the Directory WAND and make magic happen."""
    parser = Parser(
        description="Wave your Directory WAND and make magic happen."
    )

    # Get the arguments
    args = parser.parse_args()

    # Report what we found
    print("Template:", args.template)
    print("Root:", args.root)
    for key, value in args.replacements.items():
        print(f"Replacement: {key} = {value}")

    # Create the template
    template = Template(args.template, **args.replacements)
    print(template)

    # Make the copy
    template.make_copies(args.root)

    # Report we're done
    print("Done!")
