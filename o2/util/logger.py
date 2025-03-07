import logging
from functools import wraps
from logging.handlers import RotatingFileHandler

from o2.models.settings import Settings
from o2.util.colored_formatter import ColoredFormatter
from o2.util.helper import withSignatureFrom

STATS_LOG_LEVEL = 25
IO_LOG_LEVEL = 5

logging.addLevelName(STATS_LOG_LEVEL, "STATS")
logging.addLevelName(IO_LOG_LEVEL, "IO")
logger = logging.getLogger("optimos_v2")
# Convenience functions
debug = logger.debug
info = logger.info
warn = logger.warning
error = logger.error
critical = logger.critical
log = logger.log


@withSignatureFrom(logger.debug)
def stats(*args, **kwargs):  # noqa: ANN002, ANN003, ANN201
    """Log a message at the STATS log level."""
    return logger.log(STATS_LOG_LEVEL, *args, **kwargs)


@withSignatureFrom(logger.debug)
def log_io(*args, **kwargs) -> None:  # noqa: ANN002, ANN003, ANN201
    """Log a message at the IO log level."""
    return logger.log(IO_LOG_LEVEL, *args, **kwargs)


def setup_logging() -> None:
    """Set up logging for the application."""
    global logger

    if logger.hasHandlers():
        logger.handlers.clear()

    log_level = Settings.LOG_LEVEL
    log_file = Settings.LOG_FILE

    # Create formatters
    simple_formatter = ColoredFormatter("%(asctime)s [%(levelname)s]: %(message)s")
    detailed_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s: %(message)s")

    # Create handlers
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(simple_formatter)
    console_handler.setLevel(log_level)

    # Create logger
    logger.setLevel(log_level)
    # Check if the console handler is already added
    logger.addHandler(console_handler)

    # Add rotating file logging only if LOG_FILE is set
    if log_file:
        debug(f"Logging to file: {log_file}")
        file_handler = RotatingFileHandler(
            filename=log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB per file
            backupCount=5,  # Keep the last 5 log files
            encoding="utf-8",
        )
        file_handler.setFormatter(detailed_formatter)
        file_handler.setLevel(log_level)
        # Check if the file handler is already added
        logger.addHandler(file_handler)
