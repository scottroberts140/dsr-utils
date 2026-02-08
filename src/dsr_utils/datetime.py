"""Datetime conversion utilities with pandas integration."""

import math
from typing import Any, cast

import pandas as pd
import numpy as np

from dsr_utils.enums import DatetimeErrors, DatetimeFormat, DatetimeProperty, DatetimeResolution


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
    if isinstance(value, pd.Timestamp):
        if unit is None:
            return value

    if isinstance(value, pd.DatetimeIndex):
        if unit is None:
            return value.to_series().reset_index(drop=True)

    if isinstance(value, pd.Series) and pd.api.types.is_datetime64_any_dtype(value):
        if unit is None:
            return value

    # Convert to datetime using pandas
    result = pd.to_datetime(value, format=format, errors=errors.value)

    # Apply specific resolution if requested
    if unit is not None:
        if isinstance(result, pd.Series):
            dtype_obj = np.dtype(f"datetime64[{unit.value}]")
            result = result.astype(dtype_obj)
        elif isinstance(result, pd.Timestamp):
            # Convert Timestamp to specified unit
            result = result.as_unit(unit.value)

    # Ensure return type matches annotation (DatetimeIndex → Series)
    if isinstance(result, pd.DatetimeIndex):
        result = result.to_series().reset_index(drop=True)

    return cast(pd.Timestamp | pd.Series, result)


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
        result["sin_month"] = math.sin(2 * math.pi * (value.month - 1) / 12)
    if DatetimeProperty.COS_MONTH in properties:
        result["cos_month"] = math.cos(2 * math.pi * (value.month - 1) / 12)

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
    # Cast series to datetime type for proper .dt accessor support
    # Avoid subscripted Series typing to maintain compatibility with pandas versions
    dt_series: pd.Series = cast(pd.Series, series)

    # Vectorized extraction using pandas .dt accessor
    from typing import Any
    dt_accessor: Any = dt_series.dt
    extracted = {}

    if DatetimeProperty.YEAR in properties:
        extracted["year"] = dt_accessor.year
    if DatetimeProperty.MONTH in properties:
        extracted["month"] = dt_accessor.month
    if DatetimeProperty.DAY in properties:
        extracted["day"] = dt_accessor.day
    if DatetimeProperty.DAYOFWEEK in properties:
        extracted["dayofweek"] = dt_accessor.dayofweek
    if DatetimeProperty.DAYOFYEAR in properties:
        extracted["dayofyear"] = dt_accessor.dayofyear
    if DatetimeProperty.QUARTER in properties:
        extracted["quarter"] = dt_accessor.quarter
    if DatetimeProperty.WEEK in properties:
        extracted["week"] = dt_accessor.isocalendar().week
    if DatetimeProperty.IS_MONTH_END in properties:
        extracted["is_month_end"] = dt_accessor.is_month_end
    if DatetimeProperty.IS_MONTH_START in properties:
        extracted["is_month_start"] = dt_accessor.is_month_start
    if DatetimeProperty.IS_QUARTER_END in properties:
        extracted["is_quarter_end"] = dt_accessor.is_quarter_end
    if DatetimeProperty.IS_QUARTER_START in properties:
        extracted["is_quarter_start"] = dt_accessor.is_quarter_start
    if DatetimeProperty.IS_YEAR_END in properties:
        extracted["is_year_end"] = dt_accessor.is_year_end
    if DatetimeProperty.IS_YEAR_START in properties:
        extracted["is_year_start"] = dt_accessor.is_year_start
    if DatetimeProperty.IS_WEEKEND in properties:
        extracted["is_weekend"] = dt_accessor.dayofweek >= 5
    if DatetimeProperty.IS_LEAP_YEAR in properties:
        extracted["is_leap_year"] = (dt_accessor.year % 4 == 0) & (
            (dt_accessor.year % 100 != 0) | (dt_accessor.year % 400 == 0)
        )
    if DatetimeProperty.HOUR in properties:
        extracted["hour"] = dt_accessor.hour
    if DatetimeProperty.MINUTE in properties:
        extracted["minute"] = dt_accessor.minute
    if DatetimeProperty.SECOND in properties:
        extracted["second"] = dt_accessor.second
    if DatetimeProperty.DAY_NAME in properties:
        extracted["day_name"] = dt_accessor.day_name()
    if DatetimeProperty.MONTH_NAME in properties:
        extracted["month_name"] = dt_accessor.month_name()
    if DatetimeProperty.SIN_HOUR in properties:
        extracted["sin_hour"] = np.sin(2 * np.pi * dt_accessor.hour / 24)
    if DatetimeProperty.COS_HOUR in properties:
        extracted["cos_hour"] = np.cos(2 * np.pi * dt_accessor.hour / 24)
    if DatetimeProperty.SIN_DAYOFWEEK in properties:
        extracted["sin_dayofweek"] = np.sin(
            2 * np.pi * dt_accessor.dayofweek / 7)
    if DatetimeProperty.COS_DAYOFWEEK in properties:
        extracted["cos_dayofweek"] = np.cos(
            2 * np.pi * dt_accessor.dayofweek / 7)
    if DatetimeProperty.SIN_MONTH in properties:
        extracted["sin_month"] = np.sin(
            2 * np.pi * (dt_accessor.month - 1) / 12)
    if DatetimeProperty.COS_MONTH in properties:
        extracted["cos_month"] = np.cos(
            2 * np.pi * (dt_accessor.month - 1) / 12)

    # Convert the dictionary of Series into a DataFrame, then export to dict
    # This is vastly more efficient than iterating through index (O(n) vs O(n²))
    return cast(dict[Any, dict[str, Any]], pd.DataFrame(extracted).to_dict(orient='index'))


def is_string_datetime(series: pd.Series, sample_size: int = 500) -> bool:
    """Efficiently detect if a string series contains datetime data.

    - Only checks object-dtype (string-like) series
    - Drops NA values and samples up to `sample_size`
    - Parses sample via `pd.to_datetime(errors='coerce', cache=True, infer_datetime_format=True)`
    - Returns True if >95% of non-null sample values parse successfully

    This is intended for heuristic detection and favors speed over strictness.
    """
    # Only check 'object' (string-like) columns
    if not pd.api.types.is_object_dtype(series):
        return False

    # Drop NAs and sample
    sample = series.dropna().head(sample_size)
    if sample.empty:
        return False

    try:
        parsed = pd.to_datetime(sample, errors='coerce', cache=True)
        # If more than 95% of non-nulls parsed, it's likely datetime
        return float(parsed.notnull().mean()) > 0.95
    except Exception:
        return False


def infer_string_datetime_format(series: pd.Series, sample_size: int = 500, min_success: float = 0.95) -> str | None:
    """Infer the dominant strptime format for a string Series of datetimes.

    Tries a curated list of common datetime formats against a sample of non-null
    values. Returns the first format whose parse success rate exceeds `min_success`.

    Notes:
    - This is heuristic and not guaranteed for mixed-format columns.
    - Timezone and ISO-8601 variants are not fully covered.
    - Prefer using the inferred format with `pd.to_datetime(..., format=fmt)` for speed.

    Args:
        series: String-like pandas Series to inspect (object dtype).
        sample_size: Number of non-null values to test (head of cleaned sample).
        min_success: Minimum fraction of successful parses to accept a format.

    Returns:
        Detected format string (e.g., "%Y-%m-%d %H:%M:%S") or None if not inferred.
    """
    if not pd.api.types.is_object_dtype(series):
        return None

    sample = series.dropna().astype(str).str.strip().head(sample_size)
    if sample.empty:
        return None

    candidates = DatetimeFormat.list_all()

    for fmt in candidates:
        try:
            parsed = pd.to_datetime(sample, format=fmt, errors="coerce")
            if float(parsed.notnull().mean()) >= min_success:
                return fmt
        except Exception:
            # Try next format
            continue

    return None


def resolve_date_ambiguity(sample_series: pd.Series) -> str:
    """Resolve ambiguity between US_DATE (%m/%d/%Y) and EU_DATE (%d/%m/%Y) formats.

    When dates are in ambiguous format (e.g., '01/02/2025' could be Jan 2 or Feb 1),
    this function analyzes the numeric values to determine the most likely format.

    Strategy:
    - If any first number > 12: Must be day (EU format)
    - If any second number > 12: Must be month in first position (US format)
    - Otherwise: Cannot determine (ambiguous)

    Args:
        sample_series: Series with date strings in format like 'MM/DD/YYYY' or 'DD/MM/YYYY'.
            Supports both '/' and '-' as separators.

    Returns:
        str: One of "US", "EU", or "AMBIGUOUS"
             - "US": Format is %m/%d/%Y (month before day)
             - "EU": Format is %d/%m/%Y (day before month)
             - "AMBIGUOUS": Cannot determine from sample

    Examples:
        >>> # Clearly EU (day 25 > 12)
        >>> s = pd.Series(['25/01/2025', '13/02/2025'])
        >>> resolve_date_ambiguity(s)
        'EU'

        >>> # Clearly US (month 12 in second position)
        >>> s = pd.Series(['01/25/2025', '06/12/2025'])
        >>> resolve_date_ambiguity(s)
        'US'

        >>> # Ambiguous
        >>> s = pd.Series(['01/02/2025', '02/03/2025'])
        >>> resolve_date_ambiguity(s)
        'AMBIGUOUS'
    """
    # Extract the first two numeric parts using regex
    # e.g., '13/01/2025' -> ('13', '01'), '01-02-2025' -> ('01', '02')
    parts = sample_series.astype(str).str.extract(r'(\d+)[/-](\d+)').dropna()

    if parts.empty:
        return "AMBIGUOUS"

    first_part = parts[0].astype(int)
    second_part = parts[1].astype(int)

    # If the first number is > 12, it's almost certainly EU (DD/MM)
    if (first_part > 12).any():
        return "EU"

    # If the second number is > 12, it's almost certainly US (MM/DD)
    if (second_part > 12).any():
        return "US"

    return "AMBIGUOUS"
