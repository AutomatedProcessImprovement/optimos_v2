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
    return False


def find_most_frequent_overlap(
    bitmasks: list[int], min_size: int = 1
) -> tuple[int, int, int] | None:
    """Find the most frequent overlap in a list of bitmasks.

    1. Convert bitmasks to bitarrays
    2. Add all bitarrays together
    3. Iterate over the resulting array and find the most frequent overlap of size >= min_size
    4. Return start and end of the overlap

    returns frequency of overlap, start, end; With [start, end) being the range of the overlap.
    If no overlap is found, returns the longest range of 1s >= min_size (if any).
    """
    bitarrays = [bitmask_to_array(bitmask) for bitmask in bitmasks]
    summed_bitarray = reduce(lambda a, b: [x + y for x, y in zip(a, b)], bitarrays)

    current_value = 0
    current_start = 0
    current_length = 0

    max_start = None
    max_end = None
    max_value = 0
    max_length = 0

    current_sufficient_start = 0
    current_sufficient_length = 0

    max_sufficient_start = None
    max_sufficient_end = None
    max_sufficient_length = 0

    for i, value in enumerate(summed_bitarray):
        if value > 0:
            if current_sufficient_length == 0:
                current_sufficient_start = i
            current_sufficient_length += 1
        else:
            if (
                current_sufficient_length >= min_size
                and current_sufficient_length > max_sufficient_length
            ):
                max_sufficient_start = current_sufficient_start
                max_sufficient_end = i
                max_sufficient_length = current_sufficient_length
            current_sufficient_start = i
            current_sufficient_length = 0

        if value == current_value:
            current_length += 1
        else:
            # Check if the current range meets the requirements
            if current_length >= min_size and (
                (current_value == max_value and current_length > max_length)
                or (current_value > max_value)
            ):
                max_start = current_start
                # End is exclusive
                max_end = current_start + current_length
                max_length = current_length
                max_value = current_value

            # Reset for new value
            current_value = value
            current_start = i
            current_length = 1

    # Final check after loop for sufficient length
    if (
        current_sufficient_length >= min_size
        and current_sufficient_length > max_sufficient_length
    ):
        max_sufficient_start = current_sufficient_start
        max_sufficient_end = len(summed_bitarray)
        max_sufficient_length = current_sufficient_length

    # Final check after loop for max length
    if current_length >= min_size and (
        (current_value == max_value and current_length > max_length)
        or (current_value > max_value)
    ):
        max_start = current_start
        # End is exclusive
        max_end = current_start + current_length

    if max_value > 0 and max_start is not None and max_end is not None:
        return max_value, max_start, max_end
    elif max_sufficient_start is not None and max_sufficient_end is not None:
        return 1, max_sufficient_start, max_sufficient_end
    else:
        return None
