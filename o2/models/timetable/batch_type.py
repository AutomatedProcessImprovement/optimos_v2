"""BATCH_TYPE enum for defining how batches are processed."""

from enum import Enum


class BATCH_TYPE(str, Enum):  # noqa: D101, N801
    SEQUENTIAL = "Sequential"  # one after another
    CONCURRENT = "Concurrent"  # tasks are in progress simultaneously
    # (executor changes the context between different tasks)
    PARALLEL = "Parallel"  # tasks are being executed simultaneously
