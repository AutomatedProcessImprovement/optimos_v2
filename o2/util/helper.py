import functools
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
    return xxhash.xxh3_64_intdigest(str(s))


def hash_string(s: object) -> str:
    """Create string hash based on the string representation of the object."""
    return xxhash.xxh3_64_hexdigest(str(s)).zfill(16)


def hex_id(id: int) -> str:
    """Convert an item id to a hex id."""
    # If the item id is negative, then it "overflowed" to a signed int,
    # so we need to convert it to an unsigned int.
    # (rTree used C types in the backend, so int don't "just" scale)
    if id < 0:
        id &= 0xFFFFFFFFFFFFFFFF
    return f"{id:x}".zfill(16)


@functools.lru_cache(maxsize=100)
def cached_lambdify(expr: str) -> Callable[[float], float]:
    """Lambdify an expression and cache the result."""
    return functools.lru_cache(maxsize=100)(lambdify(Symbol("size"), expr))


def lambdify_dict(d: dict[str, str]) -> dict[str, Callable[[float], float]]:
    """Convert all lambdas in the dictionary to functions."""
    return {k: cached_lambdify(v) for k, v in d.items()}


P = ParamSpec("P")
R = TypeVar("R")


def withSignatureFrom(
    f: Callable[Concatenate[Any, P], R], /
) -> Callable[[Callable[Concatenate[Any, P], R]], Callable[Concatenate[Any, P], R]]:
    return lambda _: _
