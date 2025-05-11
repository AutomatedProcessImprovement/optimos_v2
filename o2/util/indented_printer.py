import logging
from textwrap import TextWrapper

from o2.util.logger import STATS_LOG_LEVEL, log

PREFERRED_WIDTH = 120

l1_prefix = 4 * " " + "> "
text_wrapper_l1 = TextWrapper(
    initial_indent=l1_prefix,
    width=PREFERRED_WIDTH,
    subsequent_indent=" " * (len(l1_prefix) + 35),
)

l2_prefix = 6 * " " + ">> "
text_wrapper_l2 = TextWrapper(
    initial_indent=l2_prefix,
    width=PREFERRED_WIDTH,
    subsequent_indent=" " * (len(l2_prefix) + 35),
)

l3_prefix = 8 * " " + ">>> "
text_wrapper_l3 = TextWrapper(
    initial_indent=l3_prefix,
    width=PREFERRED_WIDTH,
    subsequent_indent=" " * (len(l3_prefix) + 35),
)

l4_prefix = 10 * " " + ">>>> "
text_wrapper_l4 = TextWrapper(
    initial_indent=l4_prefix,
    width=PREFERRED_WIDTH,
    subsequent_indent=" " * (len(l4_prefix) + 35),
)


def print_l0(string, log_level=STATS_LOG_LEVEL) -> None:
    """Print a string with no indentation."""
    log(log_level, string)


def print_l1(string, log_level=logging.INFO) -> None:
    """Print a string with l1 indentation."""
    log(log_level, text_wrapper_l1.fill(string))


def print_l2(string, log_level=logging.DEBUG) -> None:
    """Print a string with l2 indentation."""
    log(log_level, text_wrapper_l2.fill(string))


def print_l3(string, log_level=logging.DEBUG) -> None:
    """Print a string with l3 indentation."""
    log(log_level, text_wrapper_l3.fill(string))


def print_l4(string, log_level=logging.DEBUG) -> None:
    """Print a string with l4 indentation."""
    log(log_level, text_wrapper_l4.fill(string))
