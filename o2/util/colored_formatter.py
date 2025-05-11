import logging

from colorama import Fore, Style, init

# Initialize colorama for Windows compatibility
init()


# Custom formatter with colors
class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors."""

    COLORS = {
        5: Style.DIM + Fore.BLUE,
        logging.DEBUG: Style.DIM + Fore.CYAN,
        logging.INFO: Style.DIM + Fore.WHITE,
        logging.WARNING: Style.BRIGHT + Fore.YELLOW,
        logging.ERROR: Style.BRIGHT + Fore.RED,
        logging.CRITICAL: Style.BRIGHT + Fore.MAGENTA,
        25: Style.BRIGHT + Fore.GREEN,
    }

    def format(self, record):
        """Format the log record with appropriate colors.

        Applies color formatting based on the log level and creates a consistent
        output format.
        """
        color = self.COLORS.get(record.levelno, Style.RESET_ALL)
        reset = Style.RESET_ALL
        if record.levelno == logging.INFO:
            return f"{color}{self.formatTime(record)} [{record.levelname}]:{reset} {record.msg}"
        if record.levelno == logging.DEBUG:
            return f"{color}{super().format(record)}{reset}"
        record.msg = f"{color}{record.msg}{reset}"
        return super().format(record)
