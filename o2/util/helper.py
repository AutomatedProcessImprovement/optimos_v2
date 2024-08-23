import random
import re
import string

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
