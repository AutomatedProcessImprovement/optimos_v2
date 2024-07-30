from functools import reduce


def bitmask_to_string(bitmask: int, padLeft=24) -> str:
    """Convert a bitmask to a string of 1s and 0s.

    Pads the left side with 0s to the specified length.
    """
    return bin(bitmask)[2:].zfill(padLeft)


def string_to_bitmask(bitmask: str) -> int:
    """Convert a string of 1s and 0s to a bitmask."""
    return int(bitmask, 2)


def bitmask_to_array(bitmask: int, padLeft=24) -> list[int]:
    """Convert a bitmask to an array of integers."""
    return [int(i) for i in bitmask_to_string(bitmask, padLeft)]


def array_to_bitmask(bitmask: list[int]) -> int:
    """Convert an array of integers to a bitmask."""
    return string_to_bitmask("".join(map(str, bitmask)))


def get_ranges_from_bitmask(bitmask: int) -> list[tuple[int, int]]:
    """Get the ranges of 1s in a bitmask."""
    bitmask_str = bitmask_to_string(bitmask)
    ranges: list[tuple[int, int]] = []
    start = None
    for i in range(len(bitmask_str)):
        if bitmask_str[i] == "1" and start is None:
            start = i
        elif bitmask_str[i] == "0" and start is not None:
            ranges.append((start, i))
            start = None
    if start is not None:
        ranges.append((start, len(bitmask_str)))
    return ranges


def has_overlap(bitmaskA: int, bitmaskB: int) -> bool:
    """Check if two bitmasks have an overlap."""
    return bitmaskA & bitmaskB != 0


def any_has_overlap(bitmasks: list[int]) -> bool:
    """Check if any of the bitmasks have an overlap with any other."""
    acc = 0
    for bitmask in bitmasks:
        if acc & bitmask != 0:
            return True
        acc |= bitmask
