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
        self.silent = silent

    def log(self, *args, **kwargs):
        """Log a message to the console.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
        if not self.silent:
            _print(*args, **kwargs)


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
