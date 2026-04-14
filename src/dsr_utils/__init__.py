"""
dsr_utils: Generic utility functions for text, strings, and types.
"""

from importlib.metadata import PackageNotFoundError, version

from dsr_utils.datetime import (
    infer_string_datetime_format,
    is_string_datetime,
    parse_datetime,
    parse_datetime_series,
    resolve_date_ambiguity,
    to_datetime,
)
from dsr_utils.enums import (
    DatetimeErrors,
    DatetimeFormat,
    DatetimeProperty,
    DatetimeResolution,
)
from dsr_utils.formatting import (
    BoolFormat,
    CurrencyFormat,
    CurrencySymbolPosition,
    DateTimeFormat,
    EnumFormat,
    FloatFormat,
    FormatConfig,
    FormatType,
    IntegerFormat,
    PercentageFormat,
    StringFormat,
    TextAlignment,
    ValueDescFormat,
    format_as_grid,
    format_label_value_pairs,
    format_text,
)
from dsr_utils.hashing import calculate_file_hash, calculate_object_hash
from dsr_utils.matplotlib import get_artist_bbox, get_axis_bbox
from dsr_utils.strings import apply_tracking, is_float_string
from dsr_utils.tables import (
    Table,
    TableColumn,
    TableColumnStyle,
    TableEdgeColor,
    TableEdgeLinewidth,
    render_table,
)
from dsr_utils.types import any_to_list

__all__ = [
    "DatetimeErrors",
    "DatetimeFormat",
    "DatetimeProperty",
    "DatetimeResolution",
    "FormatType",
    "TextAlignment",
    "CurrencySymbolPosition",
    "FormatConfig",
    "CurrencyFormat",
    "PercentageFormat",
    "IntegerFormat",
    "FloatFormat",
    "ValueDescFormat",
    "DateTimeFormat",
    "EnumFormat",
    "BoolFormat",
    "StringFormat",
    "format_as_grid",
    "any_to_list",
    "apply_tracking",
    "format_label_value_pairs",
    "format_text",
    "is_float_string",
    "parse_datetime",
    "parse_datetime_series",
    "is_string_datetime",
    "infer_string_datetime_format",
    "resolve_date_ambiguity",
    "to_datetime",
    "TableEdgeColor",
    "TableEdgeLinewidth",
    "TableColumnStyle",
    "TableColumn",
    "Table",
    "render_table",
    "get_artist_bbox",
    "get_axis_bbox",
    "calculate_object_hash",
    "calculate_file_hash",
]

try:
    __version__ = version("dsr-utils")
except PackageNotFoundError:
    __version__ = "unknown"
