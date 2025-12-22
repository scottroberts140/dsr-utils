"""Datetime conversion utilities with pandas integration."""

from typing import Any

import pandas as pd

from dsr_utils.enums import DatetimeErrors, DatetimeResolution


def to_datetime(
    value: Any,
    unit: DatetimeResolution | None = None,
    format: str | None = None,
    errors: DatetimeErrors = DatetimeErrors.RAISE,
) -> pd.Timestamp | pd.Series:
    """
    Convert value to datetime, preserving existing datetime types unless unit specified.

    This function wraps pandas.to_datetime() with additional logic to preserve
    existing datetime types when no specific resolution is requested.

    Args:
        value: Input to convert. Can be scalar, Series, array, string, etc.
        unit: Target resolution (SECOND, MILLISECOND, MICROSECOND, NANOSECOND).
            If None, uses pandas default (typically MICROSECOND in pandas >= 2.0)
            or preserves existing datetime resolution.
        format: strptime format string for parsing (e.g., '%Y-%m-%d %H:%M:%S').
            If None, pandas will infer the format.
        errors: Error handling strategy:
            - RAISE: raise exception on invalid parse
            - COERCE: set invalid values as NaT (Not a Time)

    Returns:
        pd.Timestamp for scalar input, pd.Series for array-like input.
        For Series, returns with datetime64 dtype at specified resolution.

    Examples:
        >>> # Convert string to datetime (uses pandas default resolution)
        >>> to_datetime('2025-12-22')
        Timestamp('2025-12-22 00:00:00')

        >>> # Convert with specific resolution
        >>> to_datetime('2025-12-22', unit=DatetimeResolution.NANOSECOND)
        Timestamp('2025-12-22 00:00:00')

        >>> # Convert Series with format
        >>> df['date'] = to_datetime(df['date_str'], format='%Y-%m-%d')

        >>> # Coerce errors to NaT
        >>> to_datetime('invalid', errors=DatetimeErrors.COERCE)
        NaT

        >>> # Preserve existing datetime type
        >>> existing_dt = pd.Timestamp('2025-12-22')
        >>> to_datetime(existing_dt)  # Returns unchanged
        Timestamp('2025-12-22 00:00:00')
    """
    # If already datetime and no unit specified, return as-is
    if isinstance(value, (pd.Timestamp, pd.DatetimeIndex)):
        if unit is None:
            return value

    if isinstance(value, pd.Series) and pd.api.types.is_datetime64_any_dtype(value):
        if unit is None:
            return value

    # Convert to datetime using pandas
    result = pd.to_datetime(value, format=format, errors=errors.value)

    # Apply specific resolution if requested
    if unit is not None:
        dtype = f"datetime64[{unit.value}]"
        if isinstance(result, pd.Series):
            result = result.astype(dtype)
        elif isinstance(result, pd.Timestamp):
            # Convert Timestamp to specified unit
            result = pd.Timestamp(result.value, unit="ns").as_unit(unit.value)

    return result
