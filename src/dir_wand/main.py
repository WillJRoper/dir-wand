"""The main runner for Directory WAND
"""
from dir_wand.parser import Parser


def main():
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
