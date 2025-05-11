"""DISTRIBUTION_TYPE enum for defining probability distributions."""

from enum import Enum


class DISTRIBUTION_TYPE(str, Enum):
    """Different types of probability distributions."""

    # No distribution
    FIXED = "fix"

    # Uniform aka random between, min and max
    # (Using numpy.random.uniform)
    UNIFORM = "uniform"

    # The rest of the distributions are from scipy.stats
    NORMAL = "norm"
    EXPONENTIAL = "expon"
    EXPONENTIAL_NORMAL = "exponnorm"
    GAMMA = "gamma"
    TRIANGULAR = "triang"
    LOG_NORMAL = "lognorm"
