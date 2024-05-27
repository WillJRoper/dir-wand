"""A module containing the class defining the command runner.

The CommandRunner class is used to run commands on the system from a Template
instance. The commands are run in the context of the template root directory.

The command runner uses concurrent threads to run the commands in parallel.

Example:
    # Create a command runner instance
    command_runner = CommandRunner("echo {placeholder}")

    # Run the command
    command_runner.run_command(placeholder="Hello, World!")

    # Wait for the command to complete
    command_runner.wait_for_all()
"""

import os
import re
import threading

from dir_wand.logger import Logger
from dir_wand.utils import swap_in_str

# Get the logger
logger = Logger()


class CommandRunner:
    """
    A class for running commands.

    The CommandRunner class is used to run commands on the system from a
    Template instance. The commands are run in the context of the template root
    directory.

    The command runner uses concurrent threads to run the commands in parallel.

    Attributes:
        command (str):
            The command to run.
        threads (list):
            A list of threads that are running commands.
    """

    def __init__(self, command):
        """
        Create the command runner instance.

        Args:
            command (str):
                The command to run.
        """
        # Store the command
        self.command = command

        # Initialise a container for the threads so we can wait for them to
        # complete at a later stage
        self.threads = []

        # Unpack placeholders
        self._placeholders = set()
        self.get_placeholders()

    def get_placeholders(self):
        """Extract what place holders the command contains."""
        # Define the regex pattern to extract the placeholders
        # (e.g. {placeholder})
        pattern = re.compile(r"\{([a-zA-Z0-9_]+)\}")

        # Find all the matches in the command
        matches = pattern.findall(self.command)

        # If we have matches...
        if matches is not None:
            # Add the placeholders to the set
            for match in matches:
                self._placeholders.add(match)

    @logger.count("command")
    def run_command(self, **swaps):
        """
        Run the command.

        This method will run the command attached to the instance of
        CommandRunner. The command will be run in the current working
        directory.

        To stop blocking the main thread running a copy the running of the
        command line will be doneon a concurrent thread.

        Args:
            swaps (dict):
                A dictionary of swaps to use when running the command.
        """
        # Exit if we have nothing to run
        if not self.command:
            return

        # Ensure we have all the placeholders before we start swapping
        missing = self._placeholders - set(swaps.keys())
        if len(missing) > 0:
            raise ValueError(f"Missing placeholders: {missing}")

        # Replace any swaps in the command
        command = swap_in_str(self.command, **swaps)

        # Function to run the command
        def run():
            try:
                status = os.system(command)
                if status != 0:
                    print(
                        f"Error: Command '{command}' failed "
                        f"with status code {status}."
                    )
            except OSError as e:
                print(
                    "OSError occurred while running command "
                    f"'{command}': {e}"
                )
            except Exception as e:
                print(
                    "Unexpected error occurred while "
                    f"running command '{command}': {e}"
                )

        # Create and start a thread to run the command
        thread = threading.Thread(target=run)
        thread.start()

        # Add the thread to the list
        self.threads.append(thread)

    def run_command_for_all_swaps(self, **swaps):
        """
        Run a command for all swaps.

        Args:
            swaps (dict):
                A dictionary of swaps to use when running the command.
        """
        # Count the swaps
        nswaps = len(list(swaps.values())[0])

        # Unpack all the swaps into each set we'll need to run
        swaps = [
            {swap: swaps[swap][i] for swap in swaps} for i in range(nswaps)
        ]

        # Ensure we have all the swaps we need for the command

        # Loop over the swaps we'll have to make
        for swap in swaps:
            self.run_command(**swap)
            print()

        # Wait for the command threads before exiting
        self.wait_for_all()

    def wait_for_all(self):
        """Wait for all threads to complete."""
        # Loop over threads
        for thread in self.threads:
            thread.join()
