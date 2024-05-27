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

from dir_wand.command_runner import CommandRunner
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

    def __init__(self, root, run=None, **swaps):
        """
        Create the template instance.

        Args:
            root (str):
                The path to the root of the template.
            run (str):
                The command to run after the template is copied.
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

        # Parse the swaps, we'll store these in a dictionary
        self.swaps = swaps
        self.nswap_vars = len(self.swaps)
        self.nswaps = len(list(self.swaps.values())[0])

        # Store the run command (if not given this will be None)
        self.run_cmd = CommandRunner(run) if run is not None else None

    def __str__(self):
        """
        Return the string representation of the template.

        Returns:
            str:
                The string representation of the template.
        """
        return f"Waving the directory WAND on {self.root_path}..."

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

        print(f"Copying {self.root}...")

        # Set up the header of the table we'll print
        header = f" {'#':<5} "
        for swap in self.swaps:
            header += f" {swap:<20} "
        print(header)
        print("-" * len(header))

        # Loop over the swaps we'll have to make
        for i, swap in enumerate(swaps):
            # Make a copy of the root directory, this will recursively copy all
            # the files and directories handling the swaps
            self.directory.make_copy_with_swaps(new_root, **swap)

            # Print the swap
            line = f" {i:<5} "
            for key in swap:
                line += f" {swap[key]:<20} "
            print(line)

            # If we have a command to run, run it (this will be done on a
            # concurrent thread so we don't block the main thread)
            if self.run_cmd is not None:
                self.run_cmd.run_command(**swap)

        print("-" * len(header))

        # Wait for the command threads before exiting if we need to
        if self.run_cmd is not None:
            self.run_cmd.wait_for_all()
