"""Enumerations for dsr_utils."""

from enum import Enum


class DatetimeResolution(str, Enum):
    """Datetime resolution for pandas datetime64 types."""

    SECOND = "s"
    MILLISECOND = "ms"
    MICROSECOND = "us"
    NANOSECOND = "ns"


class DatetimeErrors(str, Enum):
    """Error handling strategies for datetime conversion."""

    RAISE = "raise"
    COERCE = "coerce"
