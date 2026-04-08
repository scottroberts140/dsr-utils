"""Enumerations for dsr_utils."""

from enum import Enum, Flag, auto


class DatetimeResolution(str, Enum):
    """
    Datetime resolution for pandas datetime64 types.

    Used to specify the temporal precision when converting or
    truncating timestamps.
    """

    SECOND = "s"
    MILLISECOND = "ms"
    MICROSECOND = "us"
    NANOSECOND = "ns"


class DatetimeErrors(str, Enum):
    """
    Error handling strategies for datetime conversion.

    Determines how the system responds to unparseable date strings.
    """

    RAISE = "raise"
    COERCE = "coerce"


class DatetimeProperty(Flag):
    """
    Datetime properties for extraction from timestamps.

    These flags define which temporal components to extract during
    feature engineering. Supports bitwise operations for multi-selection.
    """

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
    # Essential for model features like 'dropoff_hour_sin'
    SIN_HOUR = auto()
    COS_HOUR = auto()
    SIN_DAYOFWEEK = auto()
    COS_DAYOFWEEK = auto()
    SIN_MONTH = auto()
    COS_MONTH = auto()


class DatetimeFormat(Enum):
    """
    Common strptime formats for inference.

    Formats are organized by specificity/priority. Use `list_all_ordered()`
    to retrieve them in descending priority for inference logic.
    """

    # Datetime with highest specificity
    ISO_T_PRECISION = "%Y-%m-%dT%H:%M:%S.%f"
    ISO_T_DATETIME = "%Y-%m-%dT%H:%M:%S"
    ISO_DATETIME = "%Y-%m-%d %H:%M:%S"
    US_DATETIME = "%m/%d/%Y %H:%M:%S"
    EU_DATETIME = "%d/%m/%Y %H:%M:%S"
    ISO_DATETIME_SHORT = "%Y-%m-%d %H:%M"

    # Date formats
    ISO_DATE = "%Y-%m-%d"
    ALPHA_DATE = "%d-%b-%Y"
    US_DATE = "%m/%d/%Y"
    EU_DATE = "%d/%m/%Y"
    PATH_DATE = "%Y/%m/%d"
    COMPACT_DATE = "%Y%m%d"

    @classmethod
    def list_all(cls):
        """
        Return all format values in priority order.

        Returns
        -------
        list of str
            Format strings from most to least specific.
        """
        return [f.value for f in cls]

    @classmethod
    def list_all_ordered(cls):
        """
        Alias for list_all() for clarity during inference.

        Returns
        -------
        list of str
            Ordered format strings.
        """
        return cls.list_all()


class StringCase(Enum):
    """Target casing styles for string transformation."""

    ORIGINAL = "ORIGINAL"
    SNAKE = "SNAKE"
    PASCAL = "PASCAL"
    CAMEL = "CAMEL"
    KEBAB = "KEBAB"
    CONSTANT = "CONSTANT"


class GridOrder(Enum):
    """
    Fill order for text grid arrangements.

    Determines if `format_as_grid` fills items row-by-row or column-by-column.
    """

    ROW_MAJOR = "ROW_MAJOR"
    COLUMN_MAJOR = "COLUMN_MAJOR"
