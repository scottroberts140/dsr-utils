"""Formatting helpers for numbers, dates, enums, and table-friendly output."""

from __future__ import annotations

import math
import textwrap
from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum, auto
from typing import Any, Optional, Sequence, TypeVar, Union

from dsr_utils.enums import GridOrder

T_Enum = TypeVar("T_Enum", bound=Enum)


class TextAlignment(Enum):
    """
    Enumeration for text alignment options in formatted output.

    Used for aligning text in tables, reports, and other formatted displays.
    """

    DEFAULT = auto()
    LEFT = auto()
    CENTER = auto()
    RIGHT = auto()

    def formatting_symbol(self) -> str:
        """
        Return the Python format specification alignment symbol.

        Returns
        -------
        str
            The symbol used in format strings ('<', '^', or '>').

        Examples
        --------
        >>> TextAlignment.RIGHT.formatting_symbol()
        '>'
        """
        match self:
            case TextAlignment.LEFT:
                return "<"
            case TextAlignment.CENTER:
                return "^"
            case TextAlignment.RIGHT:
                return ">"
            case _:
                return ""

    def matplot_alignment(self) -> str:
        """
        Return the matplotlib-compatible text alignment string.

        Returns
        -------
        str
            Alignment string ('left', 'center', or 'right').

        Examples
        --------
        >>> TextAlignment.CENTER.matplot_alignment()
        'center'
        """
        match self:
            case TextAlignment.LEFT:
                matplot_alignment = "left"
            case TextAlignment.CENTER:
                matplot_alignment = "center"
            case TextAlignment.RIGHT:
                matplot_alignment = "right"
            case _:
                matplot_alignment = "left"

        return matplot_alignment


class FormatType(Enum):
    """
    Supported formatting categories for `FormatConfig` subclasses.

    Defines the fundamental data types that the formatting system
    can process, ranging from numeric and financial to temporal
    and boolean data.
    """

    INTEGER = auto()
    FLOAT = auto()
    CURRENCY = auto()
    VALUE_DESC = auto()
    DATETIME = auto()
    STRING = auto()
    PERCENTAGE = auto()
    DATA = auto()
    ENUM = auto()
    BOOL = auto()


class CurrencySymbolPosition(Enum):
    """
    Placement of the currency symbol relative to the numeric value.
    """

    LEFT = auto()  # e.g., $100.00
    RIGHT = auto()  # e.g., 100.00€


class NumericScale(Enum):
    """
    Numeric scaling options for magnitude-based formatting.

    Allows values to be displayed as raw numbers or scaled to
    Thousands (K), Millions (M), or Billions (B).
    """

    NONE = auto()
    AUTO = auto()  # Choose automatically, based on magnitude
    K = auto()  # Thousands
    M = auto()  # Millions
    B = auto()  # Billions

    def get_size(self) -> float:
        """Return the scale factor for this numeric scale.

        Example:
            >>> NumericScale.M.get_size()
            1000000
        """
        match self:
            case self.NONE:
                return 1
            case self.AUTO:
                return 1
            case self.K:
                return 1_000
            case self.M:
                return 1_000_000
            case self.B:
                return 1_000_000_000
            case _:
                return 1

    def get_scaled_value(self, val: float) -> float:
        """
        Scale a value according to the selected numeric scale.

        Parameters
        ----------
        val : float
            The raw numeric value to be scaled.

        Returns
        -------
        float
            The value divided by the appropriate scale factor.

        Examples
        --------
        >>> NumericScale.K.get_scaled_value(12345)
        12.345
        """
        match self:
            case self.NONE:
                return val
            case self.AUTO:
                for scale in [self.B, self.M, self.K]:
                    size = scale.get_size()
                    if abs(val) >= size:
                        return val / size
                return val
            case _:
                size = self.get_size()

                if size == 1:
                    return val

                return val / self.get_size()

    def get_descriptor(self, val: Optional[float] = None) -> str:
        """Return the scale suffix for this numeric scale.

        For AUTO, `val` is required to determine the suffix.

        Example:
            >>> NumericScale.AUTO.get_descriptor(2_500_000)
            'M'
        """
        match self:
            case self.NONE:
                return ""
            case self.AUTO:
                if val is None:
                    raise ValueError("val must be specified to determine descriptor")

                size = NumericScale.B.get_size()
                if val >= size:
                    return "B"

                size = NumericScale.M.get_size()
                if val >= size:
                    return "M"

                size = NumericScale.K.get_size()
                if val >= size:
                    return "K"

                return ""
            case self.K:
                return "K"
            case self.M:
                return "M"
            case self.B:
                return "B"
            case _:
                return ""


class DataScale(Enum):
    """
    Data size scaling options from Bytes through Terabytes.

    Uses base-2 (1024) multipliers for calculating scale factors.
    """

    NONE = auto()
    AUTO = auto()  # Choose automatically, based on magnitude
    B = auto()  # Bytes
    KB = auto()  # Kilobytes
    MB = auto()  # Megabytes
    GB = auto()  # Gigabytes
    TB = auto()  # Terabytes

    def get_size(self) -> float:
        """
        Return the scale factor in bytes for this data scale.

        Returns
        -------
        float
            The multiplier (1024^n) for the selected scale.

        Examples
        --------
        >>> DataScale.GB.get_size()
        1073741824
        """
        match self:
            case self.NONE | self.B:
                return 1
            case self.AUTO:
                return 1
            case self.KB:
                return 1_024
            case self.MB:
                return 1_048_576
            case self.GB:
                return 1_073_741_824
            case self.TB:
                return 1_099_511_627_776
            case _:
                return 1

    def get_scaled_value(self, val: float) -> float:
        """Scale a value (bytes) according to the selected data scale.

        Example:
            >>> DataScale.KB.get_scaled_value(2048)
            2.0
        """
        match self:
            case self.NONE | self.B:
                return val
            case self.AUTO:
                for scale in [self.TB, self.GB, self.MB, self.KB]:
                    size = scale.get_size()
                    if abs(val) >= size:
                        return val / size
                return val
            case _:
                size = self.get_size()

                if size == 1:
                    return val

                return val / self.get_size()

    def get_descriptor(self, val: Optional[float] = None) -> str:
        """Return the data size suffix for this scale.

        For AUTO, `val` is required to determine the suffix.

        Example:
            >>> DataScale.AUTO.get_descriptor(5_000_000_000)
            'GB'
        """
        match self:
            case self.NONE:
                return ""
            case self.AUTO:
                if val is None:
                    raise ValueError("val must be specified to determine descriptor")

                size = DataScale.TB.get_size()
                if val >= size:
                    return "TB"

                size = DataScale.GB.get_size()
                if val >= size:
                    return "GB"

                size = DataScale.MB.get_size()
                if val >= size:
                    return "MB"

                size = DataScale.KB.get_size()
                if val >= size:
                    return "KB"

                size = DataScale.B.get_size()
                if val >= size:
                    return "B"

                return ""
            case self.B:
                return "B"
            case self.KB:
                return "KB"
            case self.MB:
                return "MB"
            case self.GB:
                return "GB"
            case self.TB:
                return "TB"
            case _:
                return ""


class BoolRepresentation(Enum):
    """Display styles for boolean formatting (True/False, Yes/No, 1/0)."""

    TRUE_FALSE = auto()
    YES_NO = auto()
    ZERO_ONE = auto()


class FormatConfig(ABC):
    """
    Base class for formatting configuration and value rendering.

    Defines the shared properties and core logic for converting raw values
    into formatted strings. Subclasses must implement `_generate_fmt`
    to define their specific Python format specification string.

    Parameters
    ----------
    format_type : FormatType
        The category of formatting to apply (e.g., INTEGER, FLOAT, CURRENCY).
    width : int, optional
        Minimum field width for the output string.
    precision : int, optional
        Number of decimal places to include. If None, defaults to 2 for
        DataScale, 1 for NumericScale, and 2 otherwise.
    always_include_sign : bool, default False
        If True, includes '+' for positive numbers.
    accounting_style : bool, default False
        If True, uses specialized alignment or wrapping for negative values
        (e.g., parentheses in Currency).
    currency_symbol : str, default ""
        The symbol to use for currency formatting (e.g., "$").
    currency_symbol_position : CurrencySymbolPosition, default LEFT
        Placement of the currency symbol relative to the value.
    thousands_separator : str, default ","
        Character used for thousands separation.
    decimal_symbol : str, default "."
        Character used for the decimal point.
    description : str, default ""
        A descriptive label or unit suffix to append to the value.
    description_leading_space : bool, default True
        Whether to add a space before the description/unit.
    description_decorator : str, default ""
        Characters used to wrap the description (e.g., "()" or "[]").
    date_format : str, default ""
        The `strftime` string for date components.
    time_format : str, default ""
        The `strftime` string for time components.
    pad_value : str, default ""
        Character used for padding the output to reach the specified `width`.
    numeric_scale : NumericScale, default NumericScale.NONE
        Magnitude scaling (K, M, B) to apply before formatting.
    data_scale : DataScale, default DataScale.NONE
        Binary magnitude scaling (KB, MB, GB, TB) to apply.
    fallback : str, default "-"
        String returned when the input value is None.
    alignment : TextAlignment, default LEFT
        Horizontal alignment (LEFT, CENTER, RIGHT).
    include_space_before_scale : bool, default False
        Whether to insert a space between the numeric value and the scale
        descriptor (e.g., '1.25 MB' vs '1.25MB'). Set to False to match
        compact audit report standards (e.g., '4.14GB' or '5.4K').

    Notes
    -----
    - Modifying any property (e.g., `width`, `precision`) after
      instantiation will automatically re-generate the format string.
    - The `format_value` method is the public entry point for rendering.
    - If `precision` is explicitly set to 0 with a scale, the value will
      be rounded to the nearest whole unit (e.g., 1.2M becomes 1M).
    """

    @property
    def format_type(self) -> FormatType:
        return self._format_type

    @property
    def width(self) -> Optional[int]:
        return self._width

    @width.setter
    def width(self, val: Optional[int]) -> None:
        self._width = val
        self._generate_fmt()

    @property
    def precision(self) -> int:
        return self._precision

    @precision.setter
    def precision(self, val: int) -> None:
        self._precision = val
        self._generate_fmt()

    @property
    def always_include_sign(self) -> bool:
        return self._always_include_sign

    @always_include_sign.setter
    def always_include_sign(self, val: bool) -> None:
        self._always_include_sign = val
        self._generate_fmt()

    @property
    def accounting_style(self) -> bool:
        return self._accounting_style

    @accounting_style.setter
    def accounting_style(self, val: bool) -> None:
        self._accounting_style = val
        self._generate_fmt()

    @property
    def currency_symbol(self) -> str:
        return self._currency_symbol

    @currency_symbol.setter
    def currency_symbol(self, val: str) -> None:
        self._currency_symbol = val
        self._generate_fmt()

    @property
    def currency_symbol_position(self) -> CurrencySymbolPosition:
        return self._currency_symbol_position

    @currency_symbol_position.setter
    def currency_symbol_position(self, val: CurrencySymbolPosition) -> None:
        self._currency_symbol_position = val
        self._generate_fmt()

    @property
    def thousands_separator(self) -> str:
        return self._thousands_separator

    @thousands_separator.setter
    def thousands_separator(self, val: str) -> None:
        self._thousands_separator = val
        self._generate_fmt()

    @property
    def decimal_symbol(self) -> str:
        return self._decimal_symbol

    @decimal_symbol.setter
    def decimal_symbol(self, val: str) -> None:
        self._decimal_symbol = val
        self._generate_fmt()

    @property
    def description(self) -> str:
        return self._description

    @description.setter
    def description(self, val: str) -> None:
        self._description = val
        self._generate_fmt()

    @property
    def description_decorator(self) -> str:
        return self._description_decorator

    @description_decorator.setter
    def description_decorator(self, val: str) -> None:
        self._description_decorator = val
        self._generate_fmt()

    @property
    def description_leading_space(self) -> bool:
        return self._description_leading_space

    @description_leading_space.setter
    def description_leading_space(self, val: bool) -> None:
        self._description_leading_space = val
        self._generate_fmt()

    @property
    def date_format(self) -> str:
        return self._date_format

    @date_format.setter
    def date_format(self, val: str) -> None:
        if not self._is_valid_date_format(val):
            print(f"WARNING: Invalid date_format '{val}'. Falling back to default.")
            return

        self._date_format = val
        self._generate_fmt()

    @property
    def time_format(self) -> str:
        return self._time_format

    @time_format.setter
    def time_format(self, val: str) -> None:
        if not self._is_valid_date_format(val):
            print(f"WARNING: Invalid time_format '{val}'. Falling back to default.")
            return

        self._time_format = val
        self._generate_fmt()

    @property
    def pad_value(self) -> str:
        return self._pad_value

    @pad_value.setter
    def pad_value(self, val: str) -> None:
        self._pad_value = val
        self._generate_fmt()

    @property
    def numeric_scale(self) -> NumericScale:
        return self._numeric_scale

    @numeric_scale.setter
    def numeric_scale(self, val: NumericScale) -> None:
        self._numeric_scale = val
        self._generate_fmt()

    @property
    def data_scale(self) -> DataScale:
        return self._data_scale

    @data_scale.setter
    def data_scale(self, val: DataScale) -> None:
        self._data_scale = val
        self._generate_fmt()

    @property
    def fallback(self) -> str:
        return self._fallback

    @fallback.setter
    def fallback(self, val: str) -> None:
        self._fallback = val
        self._generate_fmt()

    @property
    def include_space_before_scale(self) -> bool:
        return self._include_space_before_scale

    @include_space_before_scale.setter
    def include_space_before_scale(self, val: bool) -> None:
        self._include_space_before_scale = val
        self._generate_fmt()

    @property
    def alignment(self) -> TextAlignment:
        return self._alignment

    @alignment.setter
    def alignment(self, val: TextAlignment) -> None:
        self._alignment = val
        self._generate_fmt()

    @property
    def fmt(self) -> str:
        return self._fmt

    def __init__(
        self,
        format_type: FormatType,
        width: Optional[int] = None,
        precision: Optional[int] = None,
        always_include_sign: bool = False,
        accounting_style: bool = False,
        currency_symbol: str = "",
        currency_symbol_position: CurrencySymbolPosition = CurrencySymbolPosition.LEFT,
        thousands_separator: str = ",",
        decimal_symbol: str = ".",
        description: str = "",
        description_leading_space: bool = True,
        # If two characters, the first is placed before the description, and the second is placed after the description
        # If one character, the first is placed before the description, and the second is determined as follows:
        #   '(' -> ')'
        #   '[' -> ']'
        #   '{' -> '}'
        #   Any other character will be used both before and after the description.
        # If more than two characters are specifie, any additional characters after the first two will be ignored.
        description_decorator: str = "",
        date_format: str = "",
        time_format: str = "",
        pad_value: str = "",
        numeric_scale: NumericScale = NumericScale.NONE,
        data_scale: DataScale = DataScale.NONE,
        fallback: str = "-",
        alignment: TextAlignment = TextAlignment.LEFT,
        include_space_before_scale: bool = False,
    ):
        self._format_type = format_type

        # Handle Precision Defaults
        if precision is None:
            if format_type is FormatType.DATA and data_scale is not DataScale.NONE:
                precision = 2
            elif numeric_scale is not NumericScale.NONE:
                precision = 1
            else:
                precision = 2  # General default

        # Ensure it's not negative
        self._precision = max(0, precision)

        self._width = width
        self._always_include_sign = always_include_sign
        self._accounting_style = accounting_style
        self._currency_symbol = currency_symbol
        self._currency_symbol_position = currency_symbol_position
        self._thousands_separator = thousands_separator
        self._decimal_symbol = decimal_symbol
        self._description = description
        self._description_leading_space = description_leading_space
        self._description_decorator = description_decorator
        self._date_format = date_format
        self._time_format = time_format
        self._pad_value = pad_value
        self._numeric_scale = numeric_scale
        self._data_scale = data_scale
        self._fallback = fallback
        self._alignment = alignment
        self._fmt = ""
        self._include_space_before_scale = include_space_before_scale
        self._generate_fmt()

    @abstractmethod
    def _generate_fmt(self) -> None:
        pass

    def _get_formatted_value(self, val: float) -> str:
        return f"{val:{self._fmt}}"

    def format_value(self, val: Any) -> str:
        """Standard python string formatting."""
        if val is None:
            return self.fallback
        try:
            return self._get_formatted_value(val=val)
        except (ValueError, TypeError):
            return str(val)

    def matplot_alignment(self) -> str:
        return self._alignment.matplot_alignment()

    def _is_valid_date_format(self, fmt: str) -> bool:
        if not fmt:
            return True  # Allow empty strings if they represent "default"
        try:
            # Use a dummy date to test the format string
            datetime.now().strftime(fmt)
            return True
        except (ValueError, TypeError):
            return False

    def to_dict(self) -> dict[str, Any]:
        return {
            "format_type": self.format_type,
            "width": self.width,
            "precision": self.precision,
            "always_include_sign": self.always_include_sign,
            "accounting_style": self.accounting_style,
            "currency_symbol": self.currency_symbol,
            "currency_symbol_position": self.currency_symbol_position,
            "thousands_separator": self.thousands_separator,
            "decimal_symbol": self.decimal_symbol,
            "description": self.description,
            "description_decorator": self.description_decorator,
            "description_leading_space": self.description_leading_space,
            "date_format": self.date_format,
            "time_format": self.time_format,
            "pad_value": self.pad_value,
            "numeric_scale": self.numeric_scale,
            "data_scale": self.data_scale,
            "fallback": self.fallback,
            "alignment": self.alignment,
            "fmt": self.fmt,
            "include_space_before_scale": self.include_space_before_scale,
        }


class CurrencyFormat(FormatConfig):
    """
    Formatter for currency values with symbols and separators.

    Parameters
    ----------
    width : int, optional
        Minimum field width for the output string.
    precision : int, default 2
        Number of decimal places to include.
    accounting_style : bool, default False
        If True, use accounting-style formatting for negative values.
    always_include_sign : bool, default False
        Whether to always show the '+' or '-' sign.
    currency_symbol : str, default "$"
        The currency identifier to display.
    currency_symbol_position : CurrencySymbolPosition, default LEFT
        Whether to place the symbol before (LEFT) or after (RIGHT) the value.
    thousands_separator : str, default ","
        Character used for thousands separation.
    decimal_symbol : str, default "."
        Character used for the decimal point.
    pad_value : str, default ""
        Character used for padding the output to reach the specified `width`.
    numeric_scale : NumericScale, default NONE
        Scaling to apply (e.g., K, M, B) for large currency values.
    alignment : TextAlignment, default RIGHT
        Horizontal alignment for the formatted output.
    fallback : str, default "-"
        String returned when the input value is None.
    include_space_before_scale : bool, default False
        Toggle for visual spacing between the value and its unit suffix.
        - If True: Formats as '$1.25 M'.
        - If False: Formats as '$1.25M' (compact audit standard).

    Examples
    --------
    >>> fmt = CurrencyFormat(precision=2, currency_symbol="$")
    >>> fmt.format_value(12.5)
    '$12.50'
    >>> fmt_scaled = CurrencyFormat(numeric_scale=NumericScale.M)
    >>> fmt_scaled.format_value(1250000)
    '$1.25M'
    """

    def __init__(
        self,
        width: Optional[int] = None,
        precision: int = 2,
        accounting_style: bool = False,
        always_include_sign: bool = False,
        currency_symbol: str = "$",
        currency_symbol_position: CurrencySymbolPosition = CurrencySymbolPosition.LEFT,
        thousands_separator: str = ",",
        decimal_symbol: str = ".",
        pad_value: str = "",
        numeric_scale: NumericScale = NumericScale.NONE,
        alignment: TextAlignment = TextAlignment.RIGHT,
        fallback: str = "-",
        include_space_before_scale: bool = False,
    ):
        super().__init__(
            format_type=FormatType.CURRENCY,
            width=width,
            precision=precision,
            always_include_sign=always_include_sign,
            accounting_style=accounting_style,
            currency_symbol=currency_symbol,
            currency_symbol_position=currency_symbol_position,
            thousands_separator=thousands_separator,
            decimal_symbol=decimal_symbol,
            pad_value=pad_value,
            numeric_scale=numeric_scale,
            alignment=alignment,
            fallback=fallback,
            include_space_before_scale=include_space_before_scale,
        )

    def _generate_fmt(self):
        self._fmt = FloatFormat.get_format(self)

    def _get_formatted_value(self, val: float) -> str:
        formatted_val = f"{self.numeric_scale.get_scaled_value(val):{self._fmt}}"
        scale_descriptor = self.numeric_scale.get_descriptor(val=val)
        prefix = (
            self.currency_symbol
            if self.currency_symbol_position is CurrencySymbolPosition.LEFT
            else ""
        )
        suffix = (
            self.currency_symbol
            if self.currency_symbol_position is CurrencySymbolPosition.RIGHT
            else ""
        )
        return f"{prefix}{formatted_val}{scale_descriptor}{suffix}"

    @classmethod
    def from_format(cls, format: CurrencyFormat) -> CurrencyFormat:
        return CurrencyFormat(
            width=format.width,
            precision=format.precision,
            accounting_style=format.accounting_style,
            always_include_sign=format.always_include_sign,
            currency_symbol=format.currency_symbol,
            currency_symbol_position=format.currency_symbol_position,
            thousands_separator=format.thousands_separator,
            decimal_symbol=format.decimal_symbol,
            pad_value=format.pad_value,
            numeric_scale=format.numeric_scale,
            alignment=format.alignment,
            fallback=format.fallback,
        )


class PercentageFormat(FormatConfig):
    """
    Formatter for percentage values.

    Multiplies the input value by 100 and appends a percent sign.

    Parameters
    ----------
    precision : int, optional
        Number of decimal places to include after scaling to percentage.
        If None, defaults to 2.
    always_include_sign : bool, default False
        Whether to include a '+' for positive percentage values.
    width : int, optional
        Minimum field width for the output string.
    decimal_symbol : str, default "."
        Character used for the decimal point.
    alignment : TextAlignment, default RIGHT
        Horizontal alignment for the formatted output.
    fallback : str, default "-"
        String returned when the input value is None.

    Examples
    --------
    >>> fmt = PercentageFormat(precision=1)
    >>> fmt.format_value(0.1234)
    '12.3%'
    >>> fmt_delta = PercentageFormat(precision=1, always_include_sign=True)
    >>> fmt_delta.format_value(0.052)
    '+5.2%'
    """

    def __init__(
        self,
        precision: Optional[int] = None,
        always_include_sign: bool = False,
        width: Optional[int] = None,
        decimal_symbol: str = ".",
        alignment: TextAlignment = TextAlignment.RIGHT,
        fallback: str = "-",
    ):
        super().__init__(
            format_type=FormatType.PERCENTAGE,
            width=width,
            precision=precision,
            always_include_sign=always_include_sign,
            decimal_symbol=decimal_symbol,
            alignment=alignment,
            fallback=fallback,
        )

    def _generate_fmt(self):
        self._fmt = FloatFormat.get_format(self)

    @classmethod
    def from_format(cls, format: PercentageFormat) -> PercentageFormat:
        return PercentageFormat(
            precision=format.precision,
            always_include_sign=format.always_include_sign,
            width=format.width,
            decimal_symbol=format.decimal_symbol,
            alignment=format.alignment,
            fallback=format.fallback,
        )


class IntegerFormat(FormatConfig):
    """
    Formatter for integer values, optionally scaled or padded.

    Parameters
    ----------
    precision : int, optional
        Number of decimal places to show when numeric_scale is not NONE.
        If None, defaults to 0 for raw integers and 1 for scaled integers.
    width : int, optional
        Minimum field width for padding.
    always_include_sign : bool, default False
        Whether to always show the '+' or '-' sign.
    accounting_style : bool, default False
        If True, uses specialized alignment or wrapping for negative values
        (e.g., parentheses).
    thousands_separator : str, default ","
        Character used to separate thousands.
    numeric_scale : NumericScale, default NumericScale.NONE
        The scale to apply (e.g., K, M, B).
    alignment : TextAlignment, default TextAlignment.RIGHT
        Horizontal alignment for the formatted output.
    fallback : str, default "-"
        String returned when the input value is None.
    include_space_before_scale : bool, default False
        Toggle for visual spacing between the value and its unit suffix.
        - If True: Formats as '1.25M'.
        - If False: Formats as '1.25 M'.

    Examples
    --------
    >>> fmt_raw = IntegerFormat(width=4, pad_value="0")
    >>> fmt_raw.format_value(7)
    '0007'
    >>> fmt_scaled = IntegerFormat(precision=2, numeric_scale=NumericScale.M)
    >>> fmt_scaled.format_value(1250000)
    '1.25M'
    """

    def __init__(
        self,
        precision: Optional[
            int
        ] = None,  # Use when numeric_scale is not NumericScale.NONE
        width: Optional[int] = None,
        always_include_sign: bool = False,
        accounting_style: bool = False,
        thousands_separator: str = ",",
        pad_value: str = "",
        numeric_scale: NumericScale = NumericScale.NONE,
        alignment: TextAlignment = TextAlignment.RIGHT,
        fallback: str = "-",
        include_space_before_scale: bool = False,
    ):
        super().__init__(
            format_type=FormatType.INTEGER,
            width=width,
            precision=precision,
            always_include_sign=always_include_sign,
            accounting_style=accounting_style,
            thousands_separator=thousands_separator,
            pad_value=pad_value,
            numeric_scale=numeric_scale,
            alignment=alignment,
            fallback=fallback,
            include_space_before_scale=include_space_before_scale,
        )

    def _generate_fmt(self):
        self._fmt = FloatFormat.get_format(self)

    def _get_formatted_value(self, val: Any) -> str:
        # Ensure that val is an actual int for compatibility with the 'd' specifier
        int_val = int(val)
        scaled_value = self.numeric_scale.get_scaled_value(int_val)
        scale_descriptor = self.numeric_scale.get_descriptor(val=int_val)
        return f"{scaled_value:{self._fmt}}{scale_descriptor}"

    @classmethod
    def from_format(cls, format: IntegerFormat) -> IntegerFormat:
        return IntegerFormat(
            precision=format.precision,
            width=format.width,
            always_include_sign=format.always_include_sign,
            accounting_style=format.accounting_style,
            thousands_separator=format.thousands_separator,
            pad_value=format.pad_value,
            numeric_scale=format.numeric_scale,
            alignment=format.alignment,
            fallback=format.fallback,
        )


class FloatFormat(FormatConfig):
    """
    Formatter for floating-point values with precision control.

    Parameters
    ----------
    precision : int, optional
        Number of decimal places to include. If None, defaults to 2.
    width : int, optional
        Minimum field width for the output string.
    always_include_sign : bool, default False
        If True, includes '+' for positive numbers.
    accounting_style : bool, default False
        If True, uses specialized alignment or wrapping for negative values
        (e.g., parentheses).
    thousands_separator : str, default ","
        Character used to separate thousands.
    decimal_symbol : str, default "."
        Character used for the decimal point.
    pad_value : str, default ""
        Character used for padding the output to reach the specified `width`.
    numeric_scale : NumericScale, default NumericScale.NONE
        The magnitude-based scale to apply to the value.
    alignment : TextAlignment, default RIGHT
        Horizontal alignment (LEFT, CENTER, RIGHT).
    fallback : str, default "-"
        String returned when the input value is None.
    include_space_before_scale : bool, default False
        Toggle for visual spacing between the value and its unit suffix.
        - If True: Formats as '1.25M'.
        - If False: Formats as '1.25 M'.

    Examples
    --------
    >>> fmt = FloatFormat(precision=2)
    >>> fmt.format_value(1234.567)
    '1,234.57'
    >>> fmt_scaled = FloatFormat(precision=2, numeric_scale=NumericScale.K)
    >>> fmt_scaled.format_value(1234.567)
    '1.23K'
    """

    def __init__(
        self,
        precision: Optional[int] = None,
        width: Optional[int] = None,
        always_include_sign: bool = False,
        accounting_style: bool = False,
        thousands_separator: str = ",",
        decimal_symbol: str = ".",
        pad_value: str = "",
        numeric_scale: NumericScale = NumericScale.NONE,
        alignment: TextAlignment = TextAlignment.RIGHT,
        fallback: str = "-",
        include_space_before_scale: bool = False,
    ):
        super().__init__(
            format_type=FormatType.FLOAT,
            width=width,
            precision=precision,
            always_include_sign=always_include_sign,
            accounting_style=accounting_style,
            thousands_separator=thousands_separator,
            decimal_symbol=decimal_symbol,
            pad_value=pad_value,
            numeric_scale=numeric_scale,
            alignment=alignment,
            fallback=fallback,
            include_space_before_scale=include_space_before_scale,
        )

    def _generate_fmt(self) -> None:
        self._fmt = FloatFormat.get_format(config=self)

    @classmethod
    def get_format(cls, config: FormatConfig) -> str:
        """
        Generate a Python format specification string based on configuration.

        Parameters
        ----------
        config : FormatConfig
            The configuration object containing precision, alignment, and scale.

        Returns
        -------
        str
            A format specifier string (e.g., ">10.2f" or ",d").
        """
        if config.accounting_style:
            align = "="
        else:
            align = f"{config.alignment.formatting_symbol()}"

        sign = "+" if config.always_include_sign else ""

        fmt = f"{config.pad_value}{align}{sign}"

        if config.width is not None:
            fmt = f"{fmt}{config.width}"

        is_percentage = config.format_type is FormatType.PERCENTAGE
        if not is_percentage and len(config.thousands_separator) > 0:
            fmt = f"{fmt}{config.thousands_separator}"

        is_integer = config.format_type is FormatType.INTEGER
        if (not is_integer or config.numeric_scale is not NumericScale.NONE) and len(
            config.decimal_symbol
        ) > 0:
            fmt = f"{fmt}{config.decimal_symbol}{config.precision}"

        if is_percentage:
            fmt += "%"
        elif is_integer and config.numeric_scale is NumericScale.NONE:
            fmt += "d"
        else:
            fmt += "f"

        return fmt

    def _get_formatted_value(self, val: Any) -> str:
        scaled_value = self.numeric_scale.get_scaled_value(val)
        scale_descriptor = self.numeric_scale.get_descriptor(val=val)
        sep = " " if self.include_space_before_scale and scale_descriptor else ""
        return f"{scaled_value:{self._fmt}}{sep}{scale_descriptor}"

    @classmethod
    def from_format(cls, format: FloatFormat) -> FloatFormat:
        return FloatFormat(
            precision=format.precision,
            width=format.width,
            always_include_sign=format.always_include_sign,
            accounting_style=format.accounting_style,
            thousands_separator=format.thousands_separator,
            decimal_symbol=format.decimal_symbol,
            numeric_scale=format.numeric_scale,
            alignment=format.alignment,
            fallback=format.fallback,
        )


class ValueDescFormat(FormatConfig):
    """
    Formatter that appends a description label to numeric values.

    Combines magnitude scaling (Numeric or Data) with a customizable
    text suffix and optional decorators like brackets or parentheses.

    Parameters
    ----------
    precision : int, optional
        Number of decimal places. If None, defaults to 1 for numeric
        scales and 2 for data scales.
    width : int, optional
        Minimum field width for the output string.
    always_include_sign : bool, default False
        If True, includes '+' for positive numbers.
    accounting_style : bool, default False
        If True, uses specialized alignment or wrapping for negative values
        (e.g., parentheses in Currency).
    thousands_separator : str, default ","
        Character used for thousands separation.
    decimal_symbol : str, default "."
        Character used for the decimal point.
    pad_value : str, default ""
        Character used for padding the output to reach the specified `width`.
    description : str, default ""
        The unit or label to append (e.g., "ms", "GB", "rows/sec").
    description_leading_space : bool, default True
        Whether to include a space before the decorated description.
    description_decorator : str, default ""
        Characters used to wrap the description. If one character is provided,
        brackets '(', '[', and '{' are automatically matched.
    alignment : TextAlignment, default RIGHT
        Horizontal alignment (LEFT, CENTER, RIGHT).
    numeric_scale : NumericScale, default NONE
        Standard magnitude scaling (K, M, B).
    data_scale : DataScale, default NONE
        Byte-based magnitude scaling (KB, MB, GB).
    fallback : str, default "-"
        String returned when the input value is None.
    include_space_before_scale : bool, default False
        Toggle for visual spacing between the value and its unit suffix.
        - If True: Formats as '1.25M', or '1.25MB'.
        - If False: Formats as '1.25 M', or '1.25 MB'.

    Examples
    --------
    >>> fmt = ValueDescFormat(precision=1, description="ms")
    >>> fmt.format_value(12.34)
    '12.3 ms'
    >>> fmt_wrap = ValueDescFormat(description="Score", description_decorator="[")
    >>> fmt_wrap.format_value(95)
    '95.0 [Score]'
    """

    def __init__(
        self,
        precision: Optional[int] = None,
        width: Optional[int] = None,
        always_include_sign: bool = False,
        accounting_style: bool = False,
        thousands_separator: str = ",",
        decimal_symbol: str = ".",
        pad_value: str = "",
        description: str = "",
        description_leading_space: bool = True,
        # If two characters, the first is placed before the description, and the second is placed after the description
        # If one character, the first is placed before the description, and the second is determined as follows:
        #   '(' -> ')'
        #   '[' -> ']'
        #   '{' -> '}'
        #   Any other character will be used both before and after the description.
        # If more than two characters are specifie, any additional characters after the first two will be ignored.
        description_decorator: str = "",
        alignment: TextAlignment = TextAlignment.RIGHT,
        numeric_scale: NumericScale = NumericScale.NONE,
        data_scale: DataScale = DataScale.NONE,
        fallback: str = "-",
        include_space_before_scale: bool = False,
    ):
        super().__init__(
            format_type=FormatType.VALUE_DESC,
            width=width,
            precision=precision,
            always_include_sign=always_include_sign,
            accounting_style=accounting_style,
            thousands_separator=thousands_separator,
            decimal_symbol=decimal_symbol,
            pad_value=pad_value,
            description=description,
            description_leading_space=description_leading_space,
            description_decorator=description_decorator,
            alignment=alignment,
            numeric_scale=numeric_scale,
            data_scale=data_scale,
            fallback=fallback,
            include_space_before_scale=include_space_before_scale,
        )

    def _generate_fmt(self):
        self._fmt = FloatFormat.get_format(self)

    def _get_formatted_value(self, val: float) -> str:
        # 1. Determine which scale to use
        if self.data_scale is not DataScale.NONE:
            scaled_value = self.data_scale.get_scaled_value(val)
            scale_descriptor = self.data_scale.get_descriptor(val=val)
        else:
            scaled_value = self.numeric_scale.get_scaled_value(val)
            scale_descriptor = self.numeric_scale.get_descriptor(val=val)

        # 2. Apply the format specification (precision, width, etc.)
        formatted_val = f"{scaled_value:{self._fmt}}"

        # 3. Handle the empty description edge case
        if not self.description:
            return f"{formatted_val}{scale_descriptor}"

        # 4. Handle Decorators
        left_decorator = ""
        right_decorator = ""
        space = " " if self.description_leading_space else ""
        decorator = self.description_decorator

        if len(decorator) > 0:
            left_decorator = decorator[0]
            if len(decorator) > 1:
                right_decorator = decorator[1]
            else:
                match left_decorator:
                    case "(":
                        right_decorator = ")"
                    case "[":
                        right_decorator = "]"
                    case "{":
                        right_decorator = "}"
                    case _:
                        right_decorator = left_decorator

        return f"{formatted_val}{scale_descriptor}{space}{left_decorator}{self.description}{right_decorator}"

    @classmethod
    def from_format(cls, format: ValueDescFormat) -> ValueDescFormat:
        return ValueDescFormat(
            precision=format.precision,
            width=format.width,
            always_include_sign=format.always_include_sign,
            accounting_style=format.accounting_style,
            thousands_separator=format.thousands_separator,
            decimal_symbol=format.decimal_symbol,
            pad_value=format.pad_value,
            description=format.description,
            description_leading_space=format.description_leading_space,
            description_decorator=format.description_decorator,
            alignment=format.alignment,
            numeric_scale=format.numeric_scale,
            data_scale=format.data_scale,
            fallback=format.fallback,
        )


class DateTimeFormat(FormatConfig):
    """
    Formatter for datetime objects or numeric duration values.

    This class operates in two modes:
    1. Timestamp mode: Formats `datetime.datetime` objects using strftime.
    2. Duration mode: Formats numeric seconds into a human-readable
       string (e.g., '1h 5m 10s').

    Parameters
    ----------
    date_format : str, optional
        `strftime`-style date format string.
    time_format : str, optional
        `strftime`-style time format string.
    separator : str, default " "
        The string to place between the date and time components.
    use_duration_format : bool, default False
        If True, treats the input as numeric seconds (int or float).
    alignment : TextAlignment, default RIGHT
        Horizontal alignment for the formatted output.
    fallback : str, default "-"
        String returned when the input value is None.

    Notes
    -----
    - When `use_duration_format` is False, the input to `format_value`
      should be a `datetime.datetime` object.
    - When `use_duration_format` is True, the input should be a
      numeric value representing total seconds.
    """

    @property
    def use_duration_format(self) -> bool:
        return self._use_duration_format

    @use_duration_format.setter
    def use_duration_format(self, val: bool) -> None:
        self._use_duration_format = val

    @property
    def separator(self) -> str:
        return self._separator

    @separator.setter
    def separator(self, val: str) -> None:
        self._separator = val

    def __init__(
        self,
        date_format: Optional[str] = None,
        time_format: Optional[str] = None,
        separator: str = " ",
        use_duration_format: bool = False,
        alignment: TextAlignment = TextAlignment.RIGHT,
        fallback: str = "-",
    ):
        self._separator = separator
        self._use_duration_format = use_duration_format
        super().__init__(
            format_type=FormatType.DATETIME,
            date_format=date_format if date_format is not None else "",
            time_format=time_format if time_format is not None else "",
            alignment=alignment,
            fallback=fallback,
        )

    def _generate_fmt(self):
        fmt = ""

        if len(self.date_format) > 0:
            fmt += f"{self.date_format}"
            separator = self.separator
        else:
            separator = ""

        if len(self.time_format) > 0:
            fmt += f"{separator}{self.time_format}"

        self._fmt = fmt

    def _get_formatted_value(self, val: float) -> str:
        if self.use_duration_format:
            hours, rem = divmod(int(val), 3600)
            minutes, seconds = divmod(rem, 60)
            if hours > 0:
                return f"{hours}h {minutes}m {seconds}s"
            if minutes > 0:
                return f"{minutes}m {seconds}s"
            return f"{seconds}s"
        else:
            return f"{val:{self._fmt}}"

    @classmethod
    def from_format(cls, format: DateTimeFormat) -> DateTimeFormat:
        return DateTimeFormat(
            date_format=format.date_format,
            time_format=format.time_format,
            separator=format.separator,
            use_duration_format=format.use_duration_format,
            alignment=format.alignment,
            fallback=format.fallback,
        )

    def to_dict(self) -> dict[str, Any]:
        d = super().to_dict()
        d["use_duration_format"] = self.use_duration_format
        d["separator"] = self.separator
        return d


class DataFormat(FormatConfig):
    """
    Formatter for data sizes (bytes) with magnitude scaling.

    Converts raw byte counts into human-readable strings using base-2 (1024)
    scaling for KB, MB, GB, and TB.

    Parameters
    ----------
    width : int, optional
        Minimum field width for the output string.
    precision : int, optional
        Number of decimal places. If None, defaults to 2 when a scale is used.
    thousands_separator : str, default ","
        Character used for thousands separation.
    decimal_symbol : str, default "."
        Character used for the decimal point.
    data_scale : DataScale, default NONE
        The magnitude to scale by (e.g., MB, GB, or AUTO).
    alignment : TextAlignment, default RIGHT
        Horizontal alignment for the formatted output.
    fallback : str, default "-"
        String returned when the input value is None.
    include_space_before_scale : bool, default False
        Toggle for visual spacing between the value and its unit suffix.
        - If True: Formats as '1.25 MB' or '5.4 K'.
        - If False: Formats as '1.25MB' or '5.4K'.

    Examples
    --------
    >>> fmt = DataFormat(data_scale=DataScale.GB, precision=2)
    >>> fmt.format_value(1073741824)
    '1.00 GB'
    >>> fmt_auto = DataFormat(data_scale=DataScale.AUTO)
    >>> fmt_auto.format_value(5242880)
    '5.00 MB'
    """

    def __init__(
        self,
        width: Optional[int] = None,
        precision: Optional[int] = None,
        thousands_separator: str = ",",
        decimal_symbol: str = ".",
        data_scale: DataScale = DataScale.NONE,
        alignment: TextAlignment = TextAlignment.RIGHT,
        fallback: str = "-",
        include_space_before_scale: bool = False,
    ):
        super().__init__(
            format_type=FormatType.FLOAT,
            width=width,
            precision=precision,
            thousands_separator=thousands_separator,
            decimal_symbol=decimal_symbol,
            data_scale=data_scale,
            alignment=alignment,
            fallback=fallback,
            include_space_before_scale=include_space_before_scale,
        )

    def _generate_fmt(self) -> None:
        self._fmt = FloatFormat.get_format(config=self)

    def _get_formatted_value(self, val: Any) -> str:
        scaled_value = self.data_scale.get_scaled_value(val)
        scale_descriptor = self.data_scale.get_descriptor(val)
        sep = " " if self.include_space_before_scale and scale_descriptor else ""
        return f"{scaled_value:{self._fmt}}{sep}{scale_descriptor}"

    @classmethod
    def from_format(cls, format: DataFormat) -> DataFormat:
        return DataFormat(
            width=format.width,
            precision=format.precision,
            thousands_separator=format.thousands_separator,
            decimal_symbol=format.decimal_symbol,
            data_scale=format.data_scale,
            alignment=format.alignment,
            fallback=format.fallback,
        )


class StringFormat(FormatConfig):
    """
    Formatter for string values with width and alignment.

    Parameters
    ----------
    width : int, optional
        Minimum field width for the output string.
    fallback : str, default "-"
        String returned when the input value is None.
    alignment : TextAlignment, default LEFT
        Horizontal alignment for the formatted output.

    Examples
    --------
    >>> fmt = StringFormat(width=6, alignment=TextAlignment.RIGHT)
    >>> fmt.format_value("hi")
    '    hi'
    """

    def __init__(
        self,
        width: Optional[int] = None,
        fallback: str = "-",
        alignment: TextAlignment = TextAlignment.LEFT,
    ):
        super().__init__(
            format_type=FormatType.STRING,
            width=width,
            fallback=fallback,
            alignment=alignment,
        )

    def _generate_fmt(self):
        align = self.alignment.formatting_symbol()
        width = self.width if self.width is not None else ""
        self._fmt = f"{align}{width}"

    def _get_formatted_value(self, val: Any) -> str:
        # Use the generated format string to handle width and alignment
        return f"{str(val):{self._fmt}}"

    @classmethod
    def from_format(cls, format: StringFormat) -> StringFormat:
        return StringFormat(
            width=format.width,
            fallback=format.fallback,
            alignment=format.alignment,
        )


class EnumFormat(FormatConfig):
    """
    Formatter for Enum values (by name or value).

    Extracts the display string from an Enum member based on whether
    the name or the value is desired for output.

    Parameters
    ----------
    use_value : bool, default True
        If True, formats using the Enum's `.value`.
        If False, uses the Enum's `.name`.
    alignment : TextAlignment, default LEFT
        Horizontal alignment for the formatted output.
    fallback : str, default "-"
        String returned when the input value is None.

    Examples
    --------
    >>> from enum import Enum
    >>> class Color(Enum): RED = 1
    >>> fmt_name = EnumFormat(use_value=False)
    >>> fmt_name.format_value(Color.RED)
    'RED'
    >>> fmt_val = EnumFormat(use_value=True)
    >>> fmt_val.format_value(Color.RED)
    '1'
    """

    @property
    def use_value(self) -> bool:
        return self._use_value

    @use_value.setter
    def use_value(self, val: bool) -> None:
        self._use_value = val

    def __init__(
        self,
        use_value: bool = True,
        alignment: TextAlignment = TextAlignment.LEFT,
        fallback: str = "-",
    ):
        super().__init__(
            format_type=FormatType.ENUM,
            alignment=alignment,
            fallback=fallback,
        )
        self._use_value = use_value

    def _generate_fmt(self) -> None:
        # Use formatting symbols from TextAlignment (e.g., '<', '>', '^')
        align = self.alignment.formatting_symbol()
        width = self.width if self.width is not None else ""
        self._fmt = f"{align}{width}"

    def _get_formatted_value(self, val: Any) -> str:
        if isinstance(val, Enum):
            display_str = str(val.value) if self.use_value else str(val.name)
        else:
            display_str = str(val)

        return f"{display_str:{self._fmt}}"

    @classmethod
    def from_format(cls, format: EnumFormat) -> EnumFormat:
        return EnumFormat(
            use_value=format.use_value,
            alignment=format.alignment,
            fallback=format.fallback,
        )

    def to_dict(self) -> dict[str, Any]:
        d = super().to_dict()
        d["use_value"] = self.use_value
        return d


class BoolFormat(FormatConfig):
    """
    Formatter for boolean values with customizable representations.

    Translates boolean inputs into user-friendly text or numeric
    indicators based on the selected representation style.

    Parameters
    ----------
    alignment : TextAlignment, default LEFT
        Horizontal alignment for the formatted output.
    fallback : str, default "-"
        String returned when the input value is None.
    representation : BoolRepresentation, default TRUE_FALSE
        The display style to use (e.g., True/False, Yes/No, or 1/0).

    Examples
    --------
    >>> fmt = BoolFormat(representation=BoolRepresentation.YES_NO)
    >>> fmt.format_value(True)
    'Yes'
    >>> fmt_num = BoolFormat(representation=BoolRepresentation.ZERO_ONE)
    >>> fmt_num.format_value(False)
    '0'
    """

    @property
    def representation(self) -> BoolRepresentation:
        return self._representation

    @representation.setter
    def representation(self, val: BoolRepresentation) -> None:
        self._representation = val

    def __init__(
        self,
        alignment: TextAlignment = TextAlignment.LEFT,
        fallback: str = "-",
        representation: BoolRepresentation = BoolRepresentation.TRUE_FALSE,
    ):
        super().__init__(
            format_type=FormatType.BOOL, alignment=alignment, fallback=fallback
        )
        self._representation = representation

    def _generate_fmt(self):
        align = self.alignment.formatting_symbol()
        width = self.width if self.width is not None else ""
        self._fmt = f"{align}{width}"

    def _get_formatted_value(self, val: Any) -> str:
        bool_val = bool(val)
        display_str = ""

        match self.representation:
            case BoolRepresentation.TRUE_FALSE:
                display_str = "True" if bool_val else "False"
            case BoolRepresentation.YES_NO:
                display_str = "Yes" if bool_val else "No"
            case BoolRepresentation.ZERO_ONE:
                display_str = "1" if bool_val else "0"
            case _:
                display_str = str(bool_val)

        return f"{display_str:{self._fmt}}"

    @classmethod
    def from_format(cls, format: BoolFormat) -> BoolFormat:
        return BoolFormat(
            alignment=format.alignment,
            fallback=format.fallback,
            representation=format.representation,
        )

    def to_dict(self) -> dict[str, Any]:
        d = super().to_dict()
        d["representation"] = self.representation
        return d


def format_text(
    text: str,
    buffer_width: int,
    prefix: str,
    suffix: str,
    include_prefix_on_wrapped_lines: bool = True,
    include_suffix_on_wrapped_lines: bool = True,
    fill_buffer: bool = False,
    alignment: TextAlignment = TextAlignment.LEFT,
    include_start_lf: bool = False,
    include_end_lf: bool = False,
    insert_leading_space: bool = False,
) -> str:
    """
    Format text with wrapping, alignment, and decorative borders.

    Parameters
    ----------
    text : str
        The content to format.
    buffer_width : int
        Total width of the line including prefix and suffix.
    prefix : str
        String prepended to each line (e.g., "|").
    suffix : str
        String appended to each line (e.g., "|").
    include_prefix_on_wrapped_lines : bool, default True
        If False, uses empty spacing instead of the prefix on lines 2+.
    include_suffix_on_wrapped_lines : bool, default True
        If False, uses empty spacing instead of the suffix on lines 2+.
    fill_buffer : bool, default False
        If True, repeats `text` to fill the usable width (e.g., for separators).
    alignment : TextAlignment, default LEFT
        Horizontal alignment (LEFT, CENTER, RIGHT) within the buffer.
    include_start_lf : bool, default False
        If True, prepends a newline before the result.
    include_end_lf : bool, default False
        If True, appends a newline after the result.
    insert_leading_space : bool, default False
        If True, adds a space after the prefix, reducing usable width by 1.

    Returns
    -------
    str
        The formatted string, potentially multi-line.

    Examples
    --------
    >>> format_text("Results", 20, "|", "|", alignment=TextAlignment.CENTER)
    '|      Results      |'
    >>> format_text("=", 20, "|", "|", fill_buffer=True)
    '|==================|'
    """
    buffer_width -= len(prefix) + len(suffix)
    text_alignment = alignment.formatting_symbol()

    leading_space = ""

    if insert_leading_space:
        leading_space = " "
        buffer_width -= 1

    if fill_buffer and len(text) > 0:
        repetitions = (buffer_width // len(text)) + 1
        repeated_text = text * repetitions
        text = repeated_text[:buffer_width]

    wrapped_lines = textwrap.wrap(text, buffer_width)

    # This code allows a blank line to be printed if text = ' ' and fill_buffer = True
    if len(wrapped_lines) == 0:
        wrapped_lines = [text]

    formatted_text = ""
    is_first_line = True
    new_line_text = ""

    for wl in wrapped_lines:
        aligned_text = f"{leading_space}{wl:{text_alignment}{buffer_width}}"
        formatted_text += f"{new_line_text}{prefix}{aligned_text}{suffix}"

        if is_first_line:
            is_first_line = False
            new_line_text = "\n"

            if not include_prefix_on_wrapped_lines:
                prefix = " " * len(prefix)

            if not include_suffix_on_wrapped_lines:
                suffix = " " * len(suffix)

    if include_start_lf:
        start_lf = "\n"
    else:
        start_lf = ""

    if include_end_lf:
        end_lf = "\n"
    else:
        end_lf = ""

    return f"{start_lf}{formatted_text}{end_lf}"


def format_label_value_pairs(
    pairs: Sequence[Union[tuple[str, Any], str]], padding: int = 2, suffix: str = ":"
) -> str:
    """
    Align label-value pairs by a common suffix with support for raw headers.

    Calculates a consistent 'gutter' width based on the longest label provided,
    ensuring all values are vertically aligned while preserving raw strings
    for section headers or spacing.

    Parameters
    ----------
    pairs : Sequence[Union[tuple[str, Any], str]]
        A sequence of items to format. Tuples are treated as (label, value)
        pairs; strings are rendered verbatim.
    padding : int, default 2
        Number of spaces to insert between the suffix and the value.
    suffix : str, default ":"
        The character(s) appended to labels to facilitate alignment.

    Returns
    -------
    str
        A multi-line string with aligned pairs and integrated headers.

    Examples
    --------
    >>> pairs = [("Model", "RFR"), ("Score", 0.76)]
    >>> print(format_label_value_pairs(pairs, padding=1))
    Model: RFR
    Score: 0.76
    """
    if not pairs:
        return ""

    # Calculate max label length only for items that are actually tuples (pairs)
    label_items = [p for p in pairs if isinstance(p, tuple)]

    # If no tuples are present, just join and return the strings
    if not label_items:
        return "\n".join(str(p) for p in pairs)

    # Determine the 'gutter' width based on the longest label
    max_label_len = max(len(str(label)) for label, _ in label_items) + len(suffix)
    gutter_width = max_label_len + padding

    formatted_lines = []
    for item in pairs:
        if isinstance(item, tuple):
            # Standard alignment logic
            label, value = item
            # Align the label and suffix, then append the value
            label_part = f"{label}{suffix}".ljust(gutter_width)
            formatted_lines.append(f"{label_part}{value}")
        else:
            # Append raw strings (like confusion matrices or blank lines) directly
            formatted_lines.append(str(item))

    return "\n".join(formatted_lines)


def format_as_grid(
    input: list[str],
    cols: int = 3,
    padding: int = 25,
    indent: int = 0,
    grid_order: GridOrder = GridOrder.COLUMN_MAJOR,
) -> str:
    """
    Arrange a list of strings into a fixed-width text grid.

    Parameters
    ----------
    input : list[str]
        List of strings to place into the grid.
    cols : int, default 3
        Number of columns in the grid.
    padding : int, default 25
        The fixed width of each column.
    indent : int, default 0
        Number of spaces to indent the entire grid from the left margin.
    grid_order : GridOrder, default COLUMN_MAJOR
        The order in which to fill the grid (COLUMN_MAJOR or ROW_MAJOR).

    Returns
    -------
    str
        A multi-line string representing the formatted grid.

    Examples
    --------
    >>> items = ["A", "B", "C", "D"]
    >>> print(format_as_grid(items, cols=2, padding=5))
    A    C
    B    D
    """
    if not input:
        return ""

    total_items = len(input)
    rows = math.ceil(total_items / cols)
    row_major_index = [0]

    lines = []

    def get_row_major_index(r: int, c: int) -> int:
        index = row_major_index[0]
        row_major_index[0] += 1
        return index

    def get_col_major_index(r: int, c: int) -> int:
        return r + (c * rows)

    get_index = (
        get_col_major_index
        if grid_order == GridOrder.COLUMN_MAJOR
        else get_row_major_index
    )

    for r in range(rows):
        row_items = []
        for c in range(cols):
            # Calculate the index of the item that belongs in this row/column
            index = get_index(r, c)
            if index < total_items:
                row_items.append(f"{input[index]:<{padding}}")

        lines.append(" " * indent + "".join(row_items).rstrip())

    return "\n".join(lines)
