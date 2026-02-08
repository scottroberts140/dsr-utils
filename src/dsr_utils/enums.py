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


class DatetimeFormat(Enum):
    """Common strptime formats for inference.

    Enum members are organized by specificity/priority for format inference.
    More specific formats (longer, with time components) should be checked first.
    Use list_all_ordered() to get formats in priority order for inference.
    """

    # Datetime with highest specificity (check first)
    ISO_T_PRECISION = "%Y-%m-%dT%H:%M:%S.%f"  # Priority: 1 (most specific)
    ISO_T_DATETIME = "%Y-%m-%dT%H:%M:%S"  # Priority: 2
    ISO_DATETIME = "%Y-%m-%d %H:%M:%S"  # Priority: 3
    US_DATETIME = "%m/%d/%Y %H:%M:%S"  # Priority: 4
    EU_DATETIME = "%d/%m/%Y %H:%M:%S"  # Priority: 5
    ISO_DATETIME_SHORT = "%Y-%m-%d %H:%M"  # Priority: 6

    # Date formats (check after datetime, as they're less specific)
    ISO_DATE = "%Y-%m-%d"  # Priority: 7
    # Priority: 8 (alpha sorts are distinctive)
    ALPHA_DATE = "%d-%b-%Y"
    US_DATE = "%m/%d/%Y"  # Priority: 9
    EU_DATE = "%d/%m/%Y"  # Priority: 10
    PATH_DATE = "%Y/%m/%d"  # Priority: 11
    # Priority: 12 (least specific, ambiguous)
    COMPACT_DATE = "%Y%m%d"

    @classmethod
    def list_all(cls):
        """Return all format values in their defined order (which is priority order).

        Returns:
            List of format strings in priority order (most to least specific).
        """
        return [f.value for f in cls]

    @classmethod
    def list_all_ordered(cls):
        """Alias for list_all() for clarity when using priority-aware ordering.

        Returns:
            List of format strings in priority order (most to least specific).
        """
        return cls.list_all()


class StringCase(Enum):
    ORIGINAL = "ORIGINAL"  # Leave original string as-is
    SNAKE = "SNAKE"
    PASCAL = "PASCAL"
    CAMEL = "CAMEL"
    KEBAB = "KEBAB"
    CONSTANT = "CONSTANT"


class GridOrder(Enum):
    ROW_MAJOR = "ROW_MAJOR"
    COLUMN_MAJOR = "COLUMN_MAJOR"
