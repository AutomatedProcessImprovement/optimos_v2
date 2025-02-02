from textwrap import TextWrapper

PREFERRED_WIDTH = 120

l1_prefix = 4 * " " + "> "
text_wrapper_l1 = TextWrapper(
    initial_indent=l1_prefix,
    width=PREFERRED_WIDTH,
    subsequent_indent=" " * len(l1_prefix),
)

l2_prefix = 6 * " " + ">> "
text_wrapper_l2 = TextWrapper(
    initial_indent=l2_prefix,
    width=PREFERRED_WIDTH,
    subsequent_indent=" " * len(l2_prefix),
)

l3_prefix = 8 * " " + ">>> "
text_wrapper_l3 = TextWrapper(
    initial_indent=l3_prefix,
    width=PREFERRED_WIDTH,
    subsequent_indent=" " * len(l3_prefix),
)


def print_l0(string) -> None:
    """Print a string with no indentation."""
    print(string)


def print_l1(string) -> None:
    """Print a string with l1 indentation."""
    print(text_wrapper_l1.fill(string))


def print_l2(string) -> None:
    """Print a string with l2 indentation."""
    print(text_wrapper_l2.fill(string))


def print_l3(string) -> None:
    """Print a string with l3 indentation."""
    print(text_wrapper_l3.fill(string))
