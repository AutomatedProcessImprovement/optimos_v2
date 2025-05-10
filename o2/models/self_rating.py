from enum import Enum


class RATING(float, Enum):
    NOT_APPLICABLE = 0
    VERY_LOW = 1
    LOW = 2
    MEDIUM = 3
    HIGH = 4
    EXTREME = 99
