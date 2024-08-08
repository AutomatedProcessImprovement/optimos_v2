import random
import string


def random_string(length: int = 8) -> str:
    """Generate a random alphanumeric string of length `length`."""
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=length))
