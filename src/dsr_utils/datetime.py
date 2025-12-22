"""Datetime conversion utilities with pandas integration."""

import math
from typing import Any

import pandas as pd
import numpy as np

from dsr_utils.enums import DatetimeErrors, DatetimeProperty, DatetimeResolution


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


def parse_datetime(
    value: pd.Timestamp,
    properties: DatetimeProperty = DatetimeProperty.YEAR
    | DatetimeProperty.MONTH
    | DatetimeProperty.DAY,
) -> dict[str, Any]:
    """
    Extract datetime properties from a single Timestamp.

    Args:
        value: Timestamp to parse.
        properties: DatetimeProperty flags specifying which properties to extract.
            Use bitwise OR (|) to combine multiple properties.

    Returns:
        Dictionary with lowercase property names as keys and extracted values.

    Examples:
        >>> ts = pd.Timestamp("2025-12-22 14:30:45")
        >>> parse_datetime(ts, DatetimeProperty.YEAR | DatetimeProperty.MONTH)
        {'year': 2025, 'month': 12}

        >>> parse_datetime(ts, DatetimeProperty.HOUR | DatetimeProperty.SIN_HOUR)
        {'hour': 14, 'sin_hour': 0.4067...}
    """
    result = {}

    if DatetimeProperty.YEAR in properties:
        result["year"] = value.year
    if DatetimeProperty.MONTH in properties:
        result["month"] = value.month
    if DatetimeProperty.DAY in properties:
        result["day"] = value.day
    if DatetimeProperty.DAYOFWEEK in properties:
        result["dayofweek"] = value.dayofweek
    if DatetimeProperty.DAYOFYEAR in properties:
        result["dayofyear"] = value.dayofyear
    if DatetimeProperty.QUARTER in properties:
        result["quarter"] = value.quarter
    if DatetimeProperty.WEEK in properties:
        result["week"] = value.isocalendar().week
    if DatetimeProperty.IS_MONTH_END in properties:
        result["is_month_end"] = value.is_month_end
    if DatetimeProperty.IS_MONTH_START in properties:
        result["is_month_start"] = value.is_month_start
    if DatetimeProperty.IS_QUARTER_END in properties:
        result["is_quarter_end"] = value.is_quarter_end
    if DatetimeProperty.IS_QUARTER_START in properties:
        result["is_quarter_start"] = value.is_quarter_start
    if DatetimeProperty.IS_YEAR_END in properties:
        result["is_year_end"] = value.is_year_end
    if DatetimeProperty.IS_YEAR_START in properties:
        result["is_year_start"] = value.is_year_start
    if DatetimeProperty.IS_WEEKEND in properties:
        result["is_weekend"] = value.dayofweek >= 5
    if DatetimeProperty.IS_LEAP_YEAR in properties:
        result["is_leap_year"] = (value.year % 4 == 0) and (
            value.year % 100 != 0 or value.year % 400 == 0
        )
    if DatetimeProperty.HOUR in properties:
        result["hour"] = value.hour
    if DatetimeProperty.MINUTE in properties:
        result["minute"] = value.minute
    if DatetimeProperty.SECOND in properties:
        result["second"] = value.second
    if DatetimeProperty.DAY_NAME in properties:
        result["day_name"] = value.day_name()
    if DatetimeProperty.MONTH_NAME in properties:
        result["month_name"] = value.month_name()
    if DatetimeProperty.SIN_HOUR in properties:
        result["sin_hour"] = math.sin(2 * math.pi * value.hour / 24)
    if DatetimeProperty.COS_HOUR in properties:
        result["cos_hour"] = math.cos(2 * math.pi * value.hour / 24)
    if DatetimeProperty.SIN_DAYOFWEEK in properties:
        result["sin_dayofweek"] = math.sin(2 * math.pi * value.dayofweek / 7)
    if DatetimeProperty.COS_DAYOFWEEK in properties:
        result["cos_dayofweek"] = math.cos(2 * math.pi * value.dayofweek / 7)
    if DatetimeProperty.SIN_MONTH in properties:
        result["sin_month"] = math.sin(2 * math.pi * value.month / 12)
    if DatetimeProperty.COS_MONTH in properties:
        result["cos_month"] = math.cos(2 * math.pi * value.month / 12)

    return result


def parse_datetime_series(
    series: pd.Series,
    properties: DatetimeProperty = DatetimeProperty.YEAR
    | DatetimeProperty.MONTH
    | DatetimeProperty.DAY,
) -> dict[Any, dict[str, Any]]:
    """
    Extract datetime properties from a Series of timestamps.

    Uses vectorized pandas .dt accessor operations for efficient processing
    of large datasets (millions of rows).

    Args:
        series: Series of datetime values.
        properties: DatetimeProperty flags specifying which properties to extract.
            Use bitwise OR (|) to combine multiple properties.

    Returns:
        Dictionary where keys are series index values and values are dictionaries
        of extracted properties.

    Examples:
        >>> s = pd.Series(
        ...     [pd.Timestamp("2025-12-22"), pd.Timestamp("2025-12-23")],
        ...     index=['a', 'b']
        ... )
        >>> result = parse_datetime_series(s, DatetimeProperty.YEAR | DatetimeProperty.MONTH)
        >>> result['a']
        {'year': 2025, 'month': 12}
    """
    # Vectorized extraction using pandas .dt accessor
    extracted = {}

    if DatetimeProperty.YEAR in properties:
        extracted["year"] = series.dt.year
    if DatetimeProperty.MONTH in properties:
        extracted["month"] = series.dt.month
    if DatetimeProperty.DAY in properties:
        extracted["day"] = series.dt.day
    if DatetimeProperty.DAYOFWEEK in properties:
        extracted["dayofweek"] = series.dt.dayofweek
    if DatetimeProperty.DAYOFYEAR in properties:
        extracted["dayofyear"] = series.dt.dayofyear
    if DatetimeProperty.QUARTER in properties:
        extracted["quarter"] = series.dt.quarter
    if DatetimeProperty.WEEK in properties:
        extracted["week"] = series.dt.isocalendar().week
    if DatetimeProperty.IS_MONTH_END in properties:
        extracted["is_month_end"] = series.dt.is_month_end
    if DatetimeProperty.IS_MONTH_START in properties:
        extracted["is_month_start"] = series.dt.is_month_start
    if DatetimeProperty.IS_QUARTER_END in properties:
        extracted["is_quarter_end"] = series.dt.is_quarter_end
    if DatetimeProperty.IS_QUARTER_START in properties:
        extracted["is_quarter_start"] = series.dt.is_quarter_start
    if DatetimeProperty.IS_YEAR_END in properties:
        extracted["is_year_end"] = series.dt.is_year_end
    if DatetimeProperty.IS_YEAR_START in properties:
        extracted["is_year_start"] = series.dt.is_year_start
    if DatetimeProperty.IS_WEEKEND in properties:
        extracted["is_weekend"] = series.dt.dayofweek >= 5
    if DatetimeProperty.IS_LEAP_YEAR in properties:
        extracted["is_leap_year"] = (series.dt.year % 4 == 0) & (
            (series.dt.year % 100 != 0) | (series.dt.year % 400 == 0)
        )
    if DatetimeProperty.HOUR in properties:
        extracted["hour"] = series.dt.hour
    if DatetimeProperty.MINUTE in properties:
        extracted["minute"] = series.dt.minute
    if DatetimeProperty.SECOND in properties:
        extracted["second"] = series.dt.second
    if DatetimeProperty.DAY_NAME in properties:
        extracted["day_name"] = series.dt.day_name()
    if DatetimeProperty.MONTH_NAME in properties:
        extracted["month_name"] = series.dt.month_name()
    if DatetimeProperty.SIN_HOUR in properties:
        extracted["sin_hour"] = np.sin(2 * np.pi * series.dt.hour / 24)
    if DatetimeProperty.COS_HOUR in properties:
        extracted["cos_hour"] = np.cos(2 * np.pi * series.dt.hour / 24)
    if DatetimeProperty.SIN_DAYOFWEEK in properties:
        extracted["sin_dayofweek"] = np.sin(
            2 * np.pi * series.dt.dayofweek / 7)
    if DatetimeProperty.COS_DAYOFWEEK in properties:
        extracted["cos_dayofweek"] = np.cos(
            2 * np.pi * series.dt.dayofweek / 7)
    if DatetimeProperty.SIN_MONTH in properties:
        extracted["sin_month"] = np.sin(2 * np.pi * series.dt.month / 12)
    if DatetimeProperty.COS_MONTH in properties:
        extracted["cos_month"] = np.cos(2 * np.pi * series.dt.month / 12)

    # Convert the dictionary of Series into a DataFrame, then export to dict
    # This is vastly more efficient than iterating through index (O(n) vs O(n²))
    return pd.DataFrame(extracted).to_dict(orient='index')
