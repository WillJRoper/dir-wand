"""A module defining the directory class.

A Directory contains all the information to make copies of a template
directory. A directory is a tree structure containing files and other
directories.

Example:
    # Create a directory instance
    directory = Directory("path/to/directory")

    # Check if the directory is empty
    directory.is_empty

    # Check if the directory contains placeholders
    directory.contains_placeholders

    # Get the placeholders
    directory.placeholders

    # Make a copy of the directory with the placeholders swapped out
    directory.make_copy_with_swaps(
        "path/to/new/directory",
        placeholder="value"
    )
"""

import os

from dir_wand.file import File
from dir_wand.logger import Logger
from dir_wand.utils import swap_in_str

# Get the logger
logger = Logger()


class Directory:
    """
    A class for defining the directory.

    A directory is a tree structure containing files and other directories.
    Once instantiated, the directory will unpack its contents and build the
    tree structure.

    A single call to `make_copy_with_swaps` will make a copy of the directory
    and any files it contains including any children directories with the
    placeholders swapped out.

    Attributes:
        path (str):
            The path to the directory.
        children (list):
            A list of child directories.
        files (list):
            A list of files in the directory.
    """

    def __init__(self, path):
        """
        Create the directory instance.

        Args:
            path (str):
                The path to the directory.
        """
        self.path = path
        self.children = []
        self.files = []

    def __str__(self):
        """
        Return the string representation of the directory.

        Returns:
            str:
                The string representation of the directory.
        """
        return self._str_helper()

    def _str_helper(self, prefix="  ", is_last=True):
        """
        Build the string representation with lines and indentation.

        Args:
            prefix (str):
                The prefix to add to the string.
            is_last (bool):
                Whether the directory is the last in the list.
        """
        connector = "└── " if is_last else "├── "
        result = f"{prefix}{connector}{os.path.basename(self.path)}/\n"
        prefix += "    " if is_last else "│   "

        entries = self.files + self.children
        for index, entry in enumerate(entries):
            is_last_entry = index == len(entries) - 1
            if isinstance(entry, File):
                file_connector = "└── " if is_last_entry else "├── "
                result += f"{prefix}{file_connector}{entry.name}\n"
            else:
                result += entry._str_helper(prefix, is_last_entry)

        return result

    @property
    def name(self):
        """Return the name of the directory."""
        return os.path.basename(self.path)

    @property
    def is_empty(self):
        """Return whether the directory is empty."""
        return not (self.children or self.files)

    @property
    def contains_placeholders(self):
        """Return whether the directory contains placeholders."""
        return any(file.contains_placeholders for file in self.files)

    @property
    def placeholders(self):
        """Return the placeholders in the directory."""
        placeholders = set()

        for file in self.files:
            placeholders.update(file.placeholders)

        return placeholders

    def unpack_contents(self):
        """Unpack the contents of the directory."""
        # Get the contents
        contents = os.listdir(self.path)

        # Iterate over the contents
        for item in contents:
            # Get the full path
            item_path = os.path.join(self.path, item)

            # Check if the item is a directory
            if os.path.isdir(item_path):
                # Create a new directory instance
                directory = Directory(item_path)

                # Add the directory to the children
                self.children.append(directory)

                # Unpack the contents of the directory
                directory.unpack_contents()

            # Check if the item is a file
            elif os.path.isfile(item_path):
                # Create a new file instance
                f = File(item_path)

                # Add the file to the files
                self.files.append(f)

    @logger.count("directory")
    def _make_dir_copy(self, path):
        """
        Make a copy of the directory.

        Args:
            path (str):
                The path to the new directory.
        """
        os.makedirs(path, exist_ok=True)

    def make_copy_with_swaps(self, path, **swaps):
        """
        Make a copy of the directory with the placeholders swapped out.

        Args:
            path (str):
                The path to the new directory.
            **swaps:
                The placeholders to swap out.
        """
        # Get the new file path handling any possible placeholders
        path += "/" if not path.endswith("/") else ""
        path = path + self.name
        path = swap_in_str(path, **swaps)

        # Make the new directory
        self._make_dir_copy(path)

        # Iterate over the files
        for file in self.files:
            # Make a copy of the file with the swaps
            file.make_copy_with_swaps(path, **swaps)

        # Iterate over the children
        for child in self.children:
            # Make a copy of the child with the swaps
            child.make_copy_with_swaps(path, **swaps)
