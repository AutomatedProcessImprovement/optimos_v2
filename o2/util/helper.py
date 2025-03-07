import functools
import random
import re
import string
from collections.abc import Generator
from typing import TYPE_CHECKING, Any, Callable, Concatenate, Generic, Optional, ParamSpec, TypeVar

import xxhash
from sympy import Symbol, lambdify

from o2.models.settings import ActionVariationSelection

if TYPE_CHECKING:
    from o2.store import Store

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


P = TypeVar("P")


def select_variant(
    store: "Store",
    options: list[P],
    inner: Optional[bool] = False,
    ordered: Optional[bool] = False,
) -> list[P]:
    """Pick a single or multiple elements from the list.

    This depends on the action_variation_selection setting.
    The inner parameter can be used to signal, that this is an inner loop,
    and so we should at max pick 1 element.

    If inner is True and the action_variation_selection is FIRST_MAX_VARIANTS_PER_ACTION_IN_ORDER or RANDOM_MAX_VARIANTS_PER_ACTION,
    we will pick at max 1 element. This is used to limit the number of elements
    we need to consider in the inner loop.

    The ordered parameter can be used to signal, that the options are already ordered,
    so random selection is not needed.
    """
    action_variation_selection = store.settings.action_variation_selection

    if ordered:
        action_variation_selection = action_variation_selection.ordered
    if inner:
        action_variation_selection = action_variation_selection.inner

    if action_variation_selection == ActionVariationSelection.SINGLE_RANDOM:
        return random.sample(options, 1)
    elif action_variation_selection == ActionVariationSelection.ALL_RANDOM:
        return random.sample(options, len(options))
    elif action_variation_selection == ActionVariationSelection.FIRST_IN_ORDER:
        return options[:1]
    elif action_variation_selection == ActionVariationSelection.FIRST_MAX_VARIANTS_PER_ACTION_IN_ORDER:
        assert isinstance(store.settings.max_variants_per_action, int)
        return options[: store.settings.max_variants_per_action]
    elif action_variation_selection == ActionVariationSelection.RANDOM_MAX_VARIANTS_PER_ACTION:
        assert isinstance(store.settings.max_variants_per_action, int)
        return random.sample(options, min(store.settings.max_variants_per_action, len(options)))
    elif action_variation_selection == ActionVariationSelection.ALL_IN_ORDER:
        return options
    else:
        raise ValueError(f"Invalid action variation selection: {action_variation_selection}")


def select_variants(
    store: "Store",
    options: list[P],
    inner: Optional[bool] = False,
    ordered: Optional[bool] = False,
) -> Generator[P, None, None]:
    """Create a generator (to be used in a for loop) that yields action variations.

    In accordance with the action_variation_selection setting.

    The inner parameter can be used to signal, that this is an inner loop,
    and (if action_variation_selection is FIRST_MAX_VARIANTS_PER_ACTION_IN_ORDER or RANDOM_MAX_VARIANTS_PER_ACTION)
    we should pick at max 1 element.

    The ordered parameter can be used to signal, that the options are already ordered,
    so random selection is not needed.
    """
    yield from select_variant(store, options, inner, ordered)
