from enum import Enum


class RATING(float, Enum):
    """Rating values used to prioritize or evaluate optimization actions.

    This enum provides a scale of importance or effectiveness ratings
    from NOT_APPLICABLE (0) to EXTREME (99).
    """

    NOT_APPLICABLE = 0
    VERY_LOW = 1
    LOW = 2
    MEDIUM = 3
    HIGH = 4
    EXTREME = 99
