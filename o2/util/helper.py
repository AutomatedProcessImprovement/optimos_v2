import random
import re
import string
from typing import Any, Callable, Concatenate, Generic, Optional, ParamSpec, TypeVar

import xxhash
from sympy import Symbol, lambdify

CLONE_REGEX = re.compile(r"^(.*)_clone_[a-z0-9]{8}(?:timetable)?$")


def random_string(length: int = 8) -> str:
    """Generate a random alphanumeric string of length `length`."""
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=length))


def name_is_clone_of(potential_clone_name: str, resource_id: str) -> bool:
    """Check if the name is a clone of a resource id."""
    match = CLONE_REGEX.match(potential_clone_name)
    return match is not None and (
        match.group(1) == resource_id
        or match.group(1) + "timetable" == resource_id
        or match.group(1) == resource_id + "timetable"
    )


T = TypeVar("T")


def safe_list_index(l: list[T], item: T) -> Optional[int]:
    """Return the index of the item in the list, or None if it is not present."""
    try:
        return l.index(item)
    except ValueError:
        return None


def hash_int(s: object) -> int:
    """Create int hash based on the string representation of the object."""
    return xxhash.xxh32(str(s)).intdigest()


def hash_string(s: object) -> str:
    """Create string hash based on the string representation of the object."""
    return xxhash.xxh32(str(s)).hexdigest()


def lambdify_dict(d: dict[str, str]) -> dict[str, Callable[[float], float]]:
    """Convert all lambdas in the dictionary to functions."""
    return {k: lambdify(Symbol("size"), v) for k, v in d.items()}


P = ParamSpec("P")
R = TypeVar("R")


def withSignatureFrom(
    f: Callable[Concatenate[Any, P], R], /
) -> Callable[[Callable[Concatenate[Any, P], R]], Callable[Concatenate[Any, P], R]]:
    return lambda _: _
