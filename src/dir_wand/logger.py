"""A module defining the logger used to replace print statements in the code.

The logger is a simple class that can be used to replace print statements in
the code. It is used to provide a more flexible and powerful logging system
that can be easily controlled by the user.

Example:
    The logger can be used to print messages to the console. For example:

        logger = Logger()
        logger.log("This is a message.")
"""

import builtins
import time
from functools import wraps


class Logger:
    """A class used to log messages to the console.

    The logger is a simple class that can be used to replace print statements
    in the code. It is used to provide a more flexible and powerful logging
    system that can be easily controlled by the user.

    The logger is a singleton so only needs to be instantiated once and can
    then be used throughout the code.

    Attributes:
        silent (bool): A boolean flag indicating whether the logger should
            suppress all output.
    """

    _instance = None

    def __new__(cls, *args, **kwargs):
        """Create a new instance of the logger.

        This method is used to ensure that only one instance of the logger is
        created.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            Logger: The logger instance.
        """
        if cls._instance is None:
            cls._instance = super(Logger, cls).__new__(cls)
            cls._instance._setup_instance(*args, **kwargs)

        return cls._instance

    def _setup_instance(self, silent=False):
        """Set up the logger instance.

        This method is used to set up the logger instance with the specified
        silent flag.

        Args:
            silent (bool): A boolean flag indicating whether the logger should
                suppress all output.
        """
        # Attach the silent flag to the instance
        self.silent = silent

        # We will log counts of WAND's operations, make containers for them
        self.counts = {}
        self.swap_counts = {}

        # We'll also keep track of the time taken for each operation
        self.start_time = None
        self.end_time = None

        # Start the timer
        self._start_timer()

    @property
    def elapsed_time(self):
        """Return the elapsed time."""
        return self.end_time - self.start_time

    def _start_timer(self):
        """Initialise the timer."""
        self.start_time = time.time()

    def _stop_timer(self):
        """Stop the timer."""
        self.end_time = time.time()

    def log(self, *args, **kwargs):
        """Log a message to the console.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
        if not self.silent:
            _print(*args, **kwargs)

    def count(self, *keys):
        """
        Time and count an operation defined by a function.

        This function will time and count the operation represented by any
        function decorated by it. The counts and times will be stored under the
        specified keys.

        Args:
            *keys (str): The keys to store the counts and times under.

        Returns:
            function: The decorated function.
        """

        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                result = func(*args, **kwargs)
                for key in keys:
                    if key not in self.counts:
                        self.counts[key] = 0
                    self.counts[key] += 1
                return result

            return wrapper

        return decorator

    def _swap_summary(self):
        """Print a summary of the swaps made."""
        # Prepare header and format strings
        header = f"|{'Swap':<20} | {'Count':<10}|"
        line = "|" + "-" * (len(header) - 2) + "|"
        print("\n" + "Swap Report".center(len(line), "-"))
        print(header)
        print(line)

        # Print each swap's summary
        for key, value in self.swap_counts.items():
            print(f"|{key:<20} | {value:<10}|")
        print(f"|{'Total':<20} | {sum(self.swap_counts.values()):<10}|")
        print(line)

    def report(self):
        """Print a summary of the operations and swaps."""
        self._stop_timer()

        self._swap_summary()

        # Count the total number of copies made
        total_copies = sum(
            [val for key, val in self.counts.items() if key != "command"]
        )
        total_swaps = sum(self.swap_counts.values())
        total_cmds = self.counts.get("command", 0)

        final_line = [
            f"\nWAND waved in {self.elapsed_time:.2f} seconds, ",
            f"making {total_copies} copies ",
            f"({self.counts.get('directory', 0)} directories, ",
            f"{self.counts.get('file', 0)} files)",
            f", running {total_cmds} commands," if total_cmds > 0 else "",
            f" and replacing {total_swaps} placeholders.",
        ]

        _print("".join(final_line))


# Store the original print function
_print = print


def custom_print(*args, **kwargs):
    """
    Overload the print function.

    This function will replace print and redirect all print calls to the
    Logger.log function for handling verbosity and logging.

    Args:
        *args: Variable length argument list.
        **kwargs: Arbitrary keyword arguments.
    """
    Logger().log(*args, **kwargs)


# Override the built-in print function
builtins.print = custom_print
