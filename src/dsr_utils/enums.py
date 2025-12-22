"""Enumerations for dsr_utils."""

from enum import Enum, Flag, auto


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


class DatetimeProperty(Flag):
    """Datetime properties for extraction from timestamps."""

    # Date properties
    YEAR = auto()
    MONTH = auto()
    DAY = auto()
    DAYOFWEEK = auto()
    DAYOFYEAR = auto()
    QUARTER = auto()
    WEEK = auto()
    IS_MONTH_END = auto()
    IS_MONTH_START = auto()
    IS_QUARTER_END = auto()
    IS_QUARTER_START = auto()
    IS_YEAR_END = auto()
    IS_YEAR_START = auto()
    IS_WEEKEND = auto()
    IS_LEAP_YEAR = auto()

    # Time properties
    HOUR = auto()
    MINUTE = auto()
    SECOND = auto()

    # Name properties
    DAY_NAME = auto()
    MONTH_NAME = auto()

    # Cyclical properties (sine/cosine transformations)
    SIN_HOUR = auto()
    COS_HOUR = auto()
    SIN_DAYOFWEEK = auto()
    COS_DAYOFWEEK = auto()
    SIN_MONTH = auto()
    COS_MONTH = auto()
