"""A module containing the class defining the template.

A Template contains all the information to make copies of a template directory
structure. This is main interface from which the tree of directories and files
will be constructed and can later be copied with the placeholders swapped out.

Example:
    # Create a template instance
    template = Template("path/to/template", swap1=[1, 2, 3], swap2=[4, 5, 7])

    # Make copies of the template
    template.make_copies("path/to/new/template")

"""

import os

from dir_wand.directory import Directory


class Template:
    """
    A class for defining the template.

    A template is the controller class that will manage the directory tree
    making copies of the template with the placeholders swapped out, and
    running any commands that need to be executed.

    Attributes:
        root_path (str):
            The path to the root of the template.
        root (str):
            The name of the root directory.
        directory (Directory):
            The root directory of the template.
        swaps (dict):
            A dictionary of the swaps to make.
        nswap_vars (int):
            The number of swap variables.
        nswaps (int):
            The number of swaps to make.
    """

    def __init__(self, root, **swaps):
        """
        Create the template instance.

        Args:
            root (str):
                The path to the root of the template.
            **swaps (dict):
                The swaps to make in the template.
        """
        # Attach a pointer to the root of the template
        self.root_path = root
        self.root = os.path.basename(root)

        # We will store the directory structure as a tree, by creating
        # the root we'll recursively collect the whole directory structure
        # including files
        self.directory = Directory(self.root_path)
        self.directory.unpack_contents()

        # Print the directory structure
        print("Template structure:")
        print(self.directory)

        # Parse the swaps, we'll store these in a dictionary
        self.swaps = self.parse_swaps(**swaps)
        self.nswap_vars = len(self.swaps)
        self.nswaps = len(list(self.swaps.values())[0])

    def __str__(self):
        """
        Return the string representation of the template.

        Returns:
            str:
                The string representation of the template.
        """
        swaps = ", ".join(
            f"{key}={value}" for key, value in self.swaps.items()
        )
        return (
            f"Template(template_path={self.root_path},"
            f" root={self.root}, swaps={swaps})"
        )

    def parse_swaps(self, **swaps):
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

    def make_copies(self, new_root):
        """
        Make copies of the template.

        This method is the main interface to copying the template. It will call
        the copy method of the template root directory, which will recursively
        copy all the directories and files in the template.

        Args:
            new_root (str):
                The path to the new root directory.
        """
        # Unpack all the swaps into each set of directories we'll need to make
        swaps = [
            {swap: self.swaps[swap][i] for swap in self.swaps}
            for i in range(self.nswaps)
        ]

        # Loop over the swaps we'll have to make
        for swap in swaps:
            # Make a copy of the root directory, this will recursively copy all
            # the files and directories handling the swaps
            self.directory.make_copy_with_swaps(new_root, **swap)
