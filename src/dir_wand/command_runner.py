"""A module containing the class defining the command runner.

The CommandRunner class is used to run commands on the system from a Template
instance. The commands are run in the context of the template root directory.

The command runner uses concurrent threads to run the commands in parallel.


"""

import os
import threading


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

    def run_command(self, **swaps):
        """
        Run the command.

        This method will run the command attached to the instance of
        CommandRunner. The command will be run in the current working
        directory.

        To stop blocking the main thread running a copy the running of the
        command line will be done on a concurrent thread.

        Args:
            swaps (dict):
                A dictionary of swaps to use when running the command.
        """
        # Exit if we have nothing to run
        if not self.command:
            return

        # Replace any swaps in the command
        command = self.command.format(**swaps)

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

    def wait_for_all(self):
        """Wait for all threads to complete."""
        # Loop over threads
        for thread in self.threads:
            thread.join()
