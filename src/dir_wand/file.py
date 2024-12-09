"""A module contain the class defining the file.

A File contains all the information to make copies of a template file.

Example:
    # Create a file instance
    file = File("path/to/file")

    # Check if the file is a softlink
    file.is_softlink

    # Check if the file is executable
    file.is_executable

    # Get the placeholders
    file.get_placeholders()

    # Make a copy of the file with the placeholders swapped out
    file.make_copy_with_swaps("path/to/new/file", placeholder="value")

"""

import os
import re

from dir_wand.logger import Logger
from dir_wand.utils import swap_in_str

# Get the logger
logger = Logger()


class File:
    """
    A class for defining the file.

    A file contains all the information to make copies of a template file.

    A file can be a softlink, executable, hidden, empty, or a text based file
    containing placeholders.

    Attributes:
        path (str):
            The path to the file.
        name (str):
            The name of the file.
        is_softlink (bool):
            Whether the file is a softlink.
        is_executable (bool):
            Whether the file is executable.
        is_hidden (bool):
            Whether the file is hidden.
        is_empty (bool):
            Whether the file is empty.
        is_text (bool):
            Whether the file is text.
        has_placeholders (bool):
            Whether the file has placeholders.
    """

    def __init__(self, path):
        """
        Create the file instance.

        As well creating the File instance, we will also extract any
        placeholders and their line index for quicker swapping later.

        Args:
            path (str):
                The path to the file.
        """
        # Path to the file
        self.path = path

        # If this file contains any placeholders we'll store there line index
        # for quicker replacing later
        self._place_holder_lines = []
        self._placeholders = set()
        self.get_placeholders()

    def __str__(self):
        """
        Return the string representation of the file.

        Returns:
            str:
                The string representation of the file.
        """
        return self.path

    @property
    def name(self):
        """Return the name of the file."""
        return os.path.basename(self.path)

    @property
    def is_softlink(self):
        """Return whether the file is a softlink."""
        return os.path.islink(self.path)

    @property
    def is_executable(self):
        """Return whether the file is executable."""
        return os.access(self.path, os.X_OK)

    @property
    def is_hidden(self):
        """Return whether the file is hidden."""
        return self.path.startswith(".")

    @property
    def is_empty(self):
        """Return whether the file is empty."""
        return os.stat(self.path).st_size == 0

    @property
    def is_text(self):
        """Return whether the file is text."""
        try:
            with open(self.path, "r") as file:
                file.read()
            return True
        except UnicodeDecodeError:
            return False

    @property
    def has_placeholders(self):
        """Return whether the file has placeholders."""
        return len(self._placeholders) > 0

    def get_placeholders(self):
        """Extract what place holders a file contains."""
        # If the file isn't text we can't extract placeholders
        if not self.is_text:
            return

        # Open the file and read the lines
        with open(self.path, "r") as file:
            lines = file.readlines()

        # Define the regex pattern to extract the placeholders
        # (e.g. {placeholder})
        pattern = re.compile(r"\{([a-zA-Z0-9_]+)\}")

        # Iterate over the lines and extract the placeholders
        for index, line in enumerate(lines):
            # Find all the matches in the line
            matches = pattern.findall(line)

            # If we have matches...
            if matches is not None:
                # Store the line index for later
                self._place_holder_lines.append(index)

                # Add the placeholders to the set
                for match in matches:
                    self._placeholders.add(match)

    @logger.count("file")
    def _make_softlink_copy(self, path):
        """Make a copy of a softlink."""
        link = os.readlink(self.path)
        os.symlink(link, path)

    @logger.count("file")
    def _make_executable_copy(self, path):
        """Make a copy of an executable file."""
        # Copy the file
        with open(self.path, "rb") as file:
            with open(path, "wb") as new_file:
                new_file.write(file.read())

        # Copy the permissions
        os.chmod(path, os.stat(path).st_mode)

    @logger.count("file")
    def _make_simple_copy(self, path):
        """Make a simple copy of a file."""
        # Copy the file
        with open(self.path, "rb") as file:
            with open(path, "wb") as new_file:
                new_file.write(file.read())

    @logger.count("file")
    def _make_copy_with_placeholders(self, path, **swaps):
        """
        Make a copy of the file with the placeholders swapped out.

        This method will only work if the file has placeholders.

        Args:
            path (str):
                The path to save the new file.
            **swaps:
                The placeholders to swap out.
        """
        # Ensure we have all the placeholders before we start swapping
        missing = self._placeholders - set(swaps.keys())
        if len(missing) > 0:
            raise ValueError(f"Missing placeholders: {missing}")

        # Open the file and read the lines
        with open(self.path, "r") as file:
            lines = file.readlines()

        # Iterate over the lines and swap out the placeholders
        for index in self._place_holder_lines:
            # Get the line
            line = lines[index]

            line = swap_in_str(line, **swaps)

            # Update the line
            lines[index] = line

        # Write the new file
        with open(path, "w") as file:
            file.writelines(lines)

        # Copy the permissions
        os.chmod(path, os.stat(path).st_mode)

    def make_copy_with_swaps(self, path, **swaps):
        """
        Make a copy of the file with the placeholders swapped out.

        This will correctly handle softlinks, executable files, and files
        with placeholders. If the file has placeholders, you must provide
        the values to swap out, otherwise an error will be raised.

        Args:
            path (str):
                The path to save the new file.
            **swaps:
                The placeholders to swap out.
        """
        # Get the new file path handling any possible placeholders
        path += "/" if not path.endswith("/") else ""
        path = path + self.name
        path = swap_in_str(path, **swaps)

        # If we have placeholders we need to swap them out. We can do this
        # first since inherently a softlink or executable file won't have
        # placeholders
        if self.has_placeholders:
            self._make_copy_with_placeholders(path, **swaps)
            return

        # Handle the special cases of a softlink or executable file. In the
        # former we just need to make a new copy of the softlink, in the latter
        # we need to copy the file and permissions
        elif self.is_softlink:
            self._make_softlink_copy(path)
            return
        elif self.is_executable:
            self._make_executable_copy(path)
            return

        # Otherwise we just make a simple copy
        self._make_simple_copy(path)
