"""
dsr_utils: Generic utility functions for text, strings, and types.
"""

from dsr_utils.datetime import parse_datetime, parse_datetime_series, to_datetime
from dsr_utils.datetime import is_string_datetime
from dsr_utils.datetime import infer_string_datetime_format, resolve_date_ambiguity
from dsr_utils.enums import (
    DatetimeErrors,
    DatetimeFormat,
    DatetimeProperty,
    DatetimeResolution,
)
from dsr_utils.formatting import (
    TextAlignment,
    FormatType,
    CurrencySymbolPosition,
    FormatConfig,
    CurrencyFormat,
    PercentageFormat,
    IntegerFormat,
    FloatFormat,
    ValueDescFormat,
    DateTimeFormat,
    EnumFormat,
    BoolFormat,
    StringFormat,
    format_text,
    format_label_value_pairs,
    format_as_grid,
)
from dsr_utils.strings import is_float_string, apply_tracking
from dsr_utils.types import any_to_list
from dsr_utils.tables import (
    TableEdgeColor,
    TableEdgeLinewidth,
    TableColumnStyle,
    TableColumn,
    Table,
    render_table,
)
from dsr_utils.matplotlib import get_artist_bbox, get_axis_bbox

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
]

__version__ = "0.0.4"
