"""Formatting helpers for numbers, dates, enums, and table-friendly output."""

from __future__ import annotations
from enum import Enum, auto
from typing import Any, Sequence, Union, Optional, TypeVar
import textwrap
import math
from dsr_utils.enums import GridOrder
from abc import ABC, abstractmethod
from datetime import datetime

T_Enum = TypeVar("T_Enum", bound=Enum)


class TextAlignment(Enum):
    """Enumeration for text alignment options in formatted output.

    Used for aligning text in tables, reports, and other formatted displays.

    Attributes:
        DEFAULT: No alignment specified, uses default alignment.
        LEFT: Align text to the left margin.
        CENTER: Center text within available space.
        RIGHT: Align text to the right margin.
    """

    DEFAULT = (0,)
    LEFT = (1,)
    CENTER = (2,)
    RIGHT = (3,)

    def formatting_symbol(self) -> str:
        """Return the format spec alignment symbol for this alignment.

        Example:
            >>> TextAlignment.RIGHT.formatting_symbol()
            '>'
        """
        match self:
            case TextAlignment.LEFT:
                alignment_symbol = "<"
            case TextAlignment.CENTER:
                alignment_symbol = "^"
            case TextAlignment.RIGHT:
                alignment_symbol = ">"
            case _:
                alignment_symbol = ""

        return alignment_symbol

    def matplot_alignment(self) -> str:
        """Return the matplotlib text alignment string.

        Example:
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
    """Supported formatting categories for `FormatConfig` subclasses."""

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
    """Placement of the currency symbol relative to the numeric value."""

    LEFT = auto()
    RIGHT = auto()


class NumericScale(Enum):
    """Numeric scaling options (none, automatic, or fixed K/M/B)."""

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
        """Scale a value according to the selected numeric scale.

        Example:
            >>> NumericScale.K.get_scaled_value(12345)
            12.345
        """
        match self:
            case self.NONE:
                return val
            case self.AUTO:
                size = NumericScale.B.get_size()
                if val >= size:
                    return val / size

                size = NumericScale.M.get_size()
                if val >= size:
                    return val / size

                size = NumericScale.K.get_size()
                if val >= size:
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
    """Data size scaling options (bytes through terabytes)."""

    NONE = auto()
    AUTO = auto()  # Choose automatically, based on magnitude
    B = auto()  # Bytes
    KB = auto()  # Kilobytes
    MB = auto()  # Megabytes
    GB = auto()  # Gigabytes
    TB = auto()  # Terabytes

    def get_size(self) -> float:
        """Return the scale factor in bytes for this data scale.

        Example:
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
                size = DataScale.KB.get_size()
                if val >= size:
                    return val / size

                size = DataScale.MB.get_size()
                if val >= size:
                    return val / size

                size = DataScale.GB.get_size()
                if val >= size:
                    return val / size

                size = DataScale.TB.get_size()
                if val >= size:
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
    """Base class for formatting configuration and value rendering.

    Subclasses implement `_generate_fmt()` and optionally override
    `_get_formatted_value()` for custom rendering behavior.

    Notes:
        - `format_value()` returns `fallback` when the input is `None`.
        - Most subclasses use Python's format spec mini-language.
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
        precision: int = 2,
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
    ):
        self._format_type = format_type

        if precision < 0:
            precision = 0

        if format_type is FormatType.DATA:
            if data_scale is not DataScale.NONE and precision == 0:
                precision = 2
                print(
                    f"INFO: Precision adjusted from 0 to 2 for data_scale: {data_scale}."
                )
        else:
            if numeric_scale is not NumericScale.NONE and precision == 0:
                precision = 1
                print(
                    f"INFO: Precision adjusted from 0 to 1 for numeric_scale: {numeric_scale}."
                )

        self._width = width
        self._precision = precision
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
        }


class CurrencyFormat(FormatConfig):
    """Formatter for currency values with symbols and separators.

    Args:
        precision: Number of decimal places.
        width: Minimum field width.
        currency_symbol: Symbol to prefix or suffix (e.g., "$", "€").
        currency_symbol_position: LEFT or RIGHT positioning.

    Example:
        >>> CurrencyFormat(precision=2, currency_symbol="$").format_value(12.5)
        '$12.50'
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
            always_include_sign=format.always_include_sign,
            currency_symbol=format.currency_symbol,
            currency_symbol_position=format.currency_symbol_position,
            thousands_separator=format.thousands_separator,
            decimal_symbol=format.decimal_symbol,
            numeric_scale=format.numeric_scale,
            alignment=format.alignment,
            fallback=format.fallback,
        )


class PercentageFormat(FormatConfig):
    """Formatter for percentage values.

    Args:
        precision: Number of decimal places.
        always_include_sign: If True, include '+' for positive values.

    Example:
        >>> PercentageFormat(precision=1).format_value(0.1234)
        '12.3%'
    """

    def __init__(
        self,
        precision: int,
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
            width=format.width,
            always_include_sign=format.always_include_sign,
            decimal_symbol=format.decimal_symbol,
            alignment=format.alignment,
            fallback=format.fallback,
        )


class IntegerFormat(FormatConfig):
    """Formatter for integer values, optionally scaled or padded.

    Args:
        width: Minimum field width.
        thousands_separator: Separator for thousands.
        pad_value: Pad character (e.g., "0" for zero padding).
        numeric_scale: Optional scaling (e.g., K, M).

    Example:
        >>> IntegerFormat(width=4, pad_value="0").format_value(7)
        '0007'
    """

    def __init__(
        self,
        precision: int = 0,  # Use when numeric_scale is not NumericScale.NONE
        width: Optional[int] = None,
        always_include_sign: bool = False,
        accounting_style: bool = False,
        thousands_separator: str = ",",
        pad_value: str = "",
        numeric_scale: NumericScale = NumericScale.NONE,
        alignment: TextAlignment = TextAlignment.RIGHT,
        fallback: str = "-",
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
            thousands_separator=format.thousands_separator,
            numeric_scale=format.numeric_scale,
            alignment=format.alignment,
            fallback=format.fallback,
        )


class FloatFormat(FormatConfig):
    """Formatter for floating-point values with precision control.

    Args:
        precision: Number of decimal places.
        thousands_separator: Separator for thousands.
        decimal_symbol: Decimal separator.

    Example:
        >>> FloatFormat(precision=2).format_value(1234.567)
        '1,234.57'
    """

    def __init__(
        self,
        precision: int,
        width: Optional[int] = None,
        always_include_sign: bool = False,
        accounting_style: bool = False,
        thousands_separator: str = ",",
        decimal_symbol: str = ".",
        pad_value: str = "",
        numeric_scale: NumericScale = NumericScale.NONE,
        alignment: TextAlignment = TextAlignment.RIGHT,
        fallback: str = "-",
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
        )

    def _generate_fmt(self) -> None:
        self._fmt = FloatFormat.get_format(config=self)

    @classmethod
    def get_format(cls, config: FormatConfig) -> str:
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
        return f"{scaled_value:{self._fmt}}{scale_descriptor}"

    @classmethod
    def from_format(cls, format: FloatFormat) -> FloatFormat:
        return FloatFormat(
            precision=format.precision,
            width=format.width,
            always_include_sign=format.always_include_sign,
            thousands_separator=format.thousands_separator,
            decimal_symbol=format.decimal_symbol,
            numeric_scale=format.numeric_scale,
            alignment=format.alignment,
            fallback=format.fallback,
        )


class ValueDescFormat(FormatConfig):
    """Formatter that appends a description label to numeric values.

    Args:
        description: Text suffix label (e.g., "ms", "GB").
        description_decorator: Optional decorator around the description.

    Example:
        >>> ValueDescFormat(precision=1, description="ms").format_value(12.34)
        '12.3 ms'
    """

    def __init__(
        self,
        precision: int,
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
        )

    def _generate_fmt(self):
        self._fmt = FloatFormat.get_format(self)

    def _get_formatted_value(self, val: float) -> str:
        formatted_val = f"{self.numeric_scale.get_scaled_value(val):{self._fmt}}"
        scale_descriptor = self.numeric_scale.get_descriptor(val=val)
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
            thousands_separator=format.thousands_separator,
            decimal_symbol=format.decimal_symbol,
            description=format.description,
            description_leading_space=format.description_leading_space,
            description_decorator=format.description_decorator,
            alignment=format.alignment,
            numeric_scale=format.numeric_scale,
            data_scale=format.data_scale,
            fallback=format.fallback,
        )


class DateTimeFormat(FormatConfig):
    """Formatter for datetime strings or duration values.

    Args:
        date_format: `strftime`-style date format.
        time_format: `strftime`-style time format.
        separator: Separator between date and time.
        use_duration_format: If True, format numeric seconds as duration.

    Example:
        >>> DateTimeFormat(date_format="%Y-%m-%d", time_format="%H:%M").format_value(datetime(2025,1,2,3,4))
        '2025-01-02 03:04'
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
            return f"{minutes}m {seconds}s"
        else:
            return f"{val:{self._fmt}}"

    @classmethod
    def from_format(cls, format: DateTimeFormat) -> DateTimeFormat:
        return DateTimeFormat(
            date_format=format.date_format,
            time_format=format.time_format,
            separator=format.separator,
            use_duration_format=format._use_duration_format,
            alignment=format.alignment,
            fallback=format.fallback,
        )

    def to_dict(self) -> dict[str, Any]:
        d = super().to_dict()
        d["use_duration_format"] = self.use_duration_format
        d["separator"] = self.separator
        return d


class DataFormat(FormatConfig):
    """Formatter for data sizes with optional scaling (KB/MB/GB).

    Args:
        data_scale: Target scale (KB/MB/GB/TB).
        precision: Number of decimal places.

    Example:
        >>> DataFormat(data_scale=DataScale.GB, precision=2).format_value(1073741824)
        '1.00 GB'
    """

    def __init__(
        self,
        width: Optional[int] = None,
        precision: int = 2,
        thousands_separator: str = ",",
        decimal_symbol: str = ".",
        data_scale: DataScale = DataScale.NONE,
        alignment: TextAlignment = TextAlignment.RIGHT,
        fallback: str = "-",
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
        )

    def _generate_fmt(self) -> None:
        self._fmt = DataFormat.get_format(config=self)

    @classmethod
    def get_format(cls, config: FormatConfig) -> str:
        fmt = f"{config.alignment.formatting_symbol()}"

        if config.width is not None:
            fmt = f"{fmt}{config.width}"

        is_percentage = config.format_type is FormatType.PERCENTAGE
        if not is_percentage and len(config.thousands_separator) > 0:
            fmt = f"{fmt}{config.thousands_separator}"

        is_integer = config.format_type is FormatType.INTEGER
        if not is_integer and len(config.decimal_symbol) > 0:
            fmt = f"{fmt}{config.decimal_symbol}{config.precision}"

        if is_percentage:
            fmt += "%"
        elif is_integer:
            fmt += "d"
        else:
            fmt += "f"

        return fmt

    def _get_formatted_value(self, val: Any) -> str:
        scaled_value = self.data_scale.get_scaled_value(val)
        scale_descriptor = self.data_scale.get_descriptor(val)
        return f"{scaled_value:{self._fmt}}{scale_descriptor}"

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
    """Formatter for string values with width and alignment.

    Args:
        width: Minimum field width.
        alignment: Text alignment.

    Example:
        >>> StringFormat(width=6, alignment=TextAlignment.RIGHT).format_value("hi")
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
        self._fmt = ""

    def _get_formatted_value(self, val: float) -> str:
        return str(val)

    @classmethod
    def from_format(cls, format: StringFormat) -> StringFormat:
        return StringFormat(
            width=format.width,
            alignment=format.alignment,
            fallback=format.fallback,
        )


class EnumFormat(FormatConfig):
    """Formatter for Enum values (by name or value).

    Args:
        use_value: If True, format using enum `.value`, else `.name`.

    Example:
        >>> EnumFormat(use_value=False).format_value(TextAlignment.LEFT)
        'LEFT'
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
        self._fmt = ""

    def _get_formatted_value(self, val: Any) -> str:
        if isinstance(val, Enum):
            return str(val.value) if self.use_value else str(val.name)
        return str(val)

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
    """Formatter for boolean values with custom labels.

    Args:
        true_label: Label for True.
        false_label: Label for False.

    Example:
        >>> BoolFormat(true_label="Yes", false_label="No").format_value(True)
        'Yes'
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
        self._fmt = ""

    def _get_formatted_value(self, val: float) -> str:
        bool_val = bool(val)
        match self.representation:
            case BoolRepresentation.TRUE_FALSE:
                return "True" if bool_val else "False"
            case BoolRepresentation.YES_NO:
                return "Yes" if bool_val else "No"
            case _:
                return "1" if bool_val else "0"

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
    """Format text with wrapping, alignment, and decorative borders for display.

    This utility function formats text within a specified width, adds prefix/suffix
    characters (typically border characters), handles text alignment, and optionally
    wraps long text across multiple lines. Commonly used for creating formatted
    console output with consistent visual styling.

    Args:
        text: The text content to format.
        buffer_width: Total width including prefix and suffix characters.
        prefix: String to prepend to each line (e.g., border character).
        suffix: String to append to each line (e.g., border character).
        fill_buffer: If True, repeats text to fill the entire buffer width.
            Useful for creating separator lines. Defaults to False.
        alignment: Text alignment within the buffer (Left, Center, or Right).
            Defaults to TextAlignment.Left.
        include_start_lf: If True, prepends a newline before the formatted text.
            Defaults to False.
        include_end_lf: If True, appends a newline after the formatted text.
            Defaults to False.
        insert_leading_space: If True, adds a space after the prefix on each line.
            Reduces usable buffer width by 1. Defaults to False.

    Returns:
        Formatted string with applied alignment, wrapping, and border characters.
        Multi-line text is separated by newline characters.

    Examples:
        >>> # Simple bordered text
        >>> format_text(
        ...     text="Model Results",
        ...     buffer_width=50,
        ...     prefix="|",
        ...     suffix="|",
        ...     alignment=TextAlignment.Center,
        ... )
        '|              Model Results               |'
        >>> # Wrapped output with left alignment
        >>> format_text(
        ...     text="Long message that wraps",
        ...     buffer_width=20,
        ...     prefix="|",
        ...     suffix="|",
        ... )
        '|Long message that|\n|wraps              |'

        >>> # Create a separator line
        >>> format_text(
        ...     text="=",
        ...     buffer_width=50,
        ...     prefix="|",
        ...     suffix="|",
        ...     fill_buffer=True
        ... )
        '|================================================|'

        >>> # Long text with wrapping
        >>> format_text(
        ...     text="This is a very long text that will wrap",
        ...     buffer_width=30,
        ...     prefix="| ",
        ...     suffix=" |",
        ...     insert_leading_space=True
        ... )
        '|  This is a very long    |\\n|  text that will wrap   |'

    Note:
        The actual usable width for text is buffer_width minus the lengths of
        prefix and suffix (and minus 1 if insert_leading_space is True).
        Text wrapping uses Python's textwrap module for clean line breaks.
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
                suffix = " " * len(prefix)

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
    """Aligns key-value pairs by the suffix (usually a colon), while allowing raw strings
    for headers or blank lines.

    This utility function formats a list of label-value pairs with consistent
    alignment. All suffix characters (typically colons) are positioned at the same
    column, creating a neat, aligned output suitable for displaying configuration
    information, metadata, or structured reports.

    Args:
        pairs: Sequence of (label, value) tuples to format; raw strings are rendered
            verbatim so you can insert headers or blank lines.
        padding: Number of spaces between the suffix and the value. Defaults to 2.
        suffix: String to append to each label (typically a colon ':'). Defaults to ":".

    Returns:
        A formatted string with aligned label-value pairs, one per line.

    Examples:
        >>> pairs = ["Model Results", ("Model Type", "Decision Tree"), ("Score", 0.95), ""]
        >>> print(format_label_value_pairs(pairs))
        Model Results
        Model Type:  Decision Tree
        Score:       0.95
        >>> print(format_label_value_pairs([("Rows", 100), ("Cols", 8)], padding=1))
        Rows: 100
        Cols: 8

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
    """Arrange a list of strings into a fixed-width text grid.

    Args:
        input: List of strings to place into the grid.
        cols: Number of columns.
        padding: Column width padding.
        indent: Left indentation spaces.
        grid_order: Column-major or row-major fill.

    Returns:
        A newline-delimited grid of padded strings.

    Examples:
        >>> print(format_as_grid(["A", "B", "C", "D"], cols=2, padding=4))
        A   C
        B   D
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
