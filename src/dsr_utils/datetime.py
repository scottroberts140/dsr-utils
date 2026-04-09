"""Datetime conversion utilities with pandas integration."""

import math
from typing import Any, cast

import numpy as np
import pandas as pd

from dsr_utils.enums import (
    DatetimeErrors,
    DatetimeFormat,
    DatetimeProperty,
    DatetimeResolution,
)


def to_datetime(
    value: Any,
    unit: DatetimeResolution | None = None,
    format: str | None = None,
    errors: DatetimeErrors = DatetimeErrors.RAISE,
) -> pd.Timestamp | pd.Series:
    """
    Convert input to datetime, preserving existing types unless a unit is specified.

    Wraps pandas.to_datetime with additional logic to prevent unnecessary
    re-casting of existing temporal types when no specific resolution is requested.

    Parameters
    ----------
    value : Any
        The input to convert. Can be a scalar, Series, array, or string.
    unit : DatetimeResolution, optional
        Target resolution (e.g., SECOND, MILLISECOND). If None, preserves
        existing resolution or uses the pandas default.
    format : str, optional
        The `strptime` format string for parsing. If None, pandas will
        attempt to infer the format.
    errors : DatetimeErrors, default RAISE
        Error handling strategy:
        - RAISE: raise an exception on invalid parsing.
        - COERCE: set invalid values as NaT (Not a Time).

    Returns
    -------
    pd.Timestamp or pd.Series
        A pandas Timestamp for scalar input or a Series for array-like input.
        Series are returned with a datetime64 dtype at the specified resolution.

    Examples
    --------
    >>> # Standard conversion
    >>> to_datetime('2026-02-08')
    Timestamp('2026-02-08 00:00:00')
    >>> # Explicit resolution
    >>> to_datetime('2026-02-08', unit=DatetimeResolution.SECOND)
    Timestamp('2026-02-08 00:00:00')
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

    Utilizes DatetimeProperty flags to determine which temporal components
    to extract, including support for cyclical transformations (sine/cosine).

    Parameters
    ----------
    value : pd.Timestamp
        The timestamp from which to extract properties.
    properties : DatetimeProperty, default YEAR | MONTH | DAY
        Flags specifying the components to extract. Combine multiple
        properties using bitwise OR (|).

    Returns
    -------
    dict of str to Any
        A dictionary where keys are lowercase property names (e.g., 'hour',
        'sin_hour') and values are the extracted temporal data.

    Examples
    --------
    >>> ts = pd.Timestamp("2026-02-08 16:36:29")
    >>> parse_datetime(ts, DatetimeProperty.HOUR | DatetimeProperty.SIN_HOUR)
    {'hour': 16, 'sin_hour': -0.8660...}
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
        result["is_leap_year"] = value.is_leap_year
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

    Uses vectorized pandas `.dt` accessor operations and NumPy for efficient
    processing of large datasets (millions of rows).

    Parameters
    ----------
    series : pd.Series
        Series of datetime values to parse.
    properties : DatetimeProperty, default YEAR | MONTH | DAY
        Flags specifying which properties to extract. Combine multiple
        properties using bitwise OR (|).

    Returns
    -------
    dict of Any to dict
        A dictionary where keys are the original Series index values and
        values are dictionaries of extracted properties (e.g., {'year': 2025}).

    Notes
    -----
    - This function is significantly more efficient than iterating over rows
      for large datasets.
    - Features such as 'sin_hour' and 'cos_hour' are calculated using
      vectorized NumPy functions.

    Examples
    --------
    >>> s = pd.Series(
    ...     [pd.Timestamp("2026-02-08"), pd.Timestamp("2026-02-09")],
    ...     index=['row1', 'row2']
    ... )
    >>> result = parse_datetime_series(s, DatetimeProperty.YEAR | DatetimeProperty.MONTH)
    >>> result['row1']
    {'year': 2026, 'month': 2}
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
        extracted["is_leap_year"] = dt_accessor.is_leap_year
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
        extracted["sin_dayofweek"] = np.sin(2 * np.pi * dt_accessor.dayofweek / 7)
    if DatetimeProperty.COS_DAYOFWEEK in properties:
        extracted["cos_dayofweek"] = np.cos(2 * np.pi * dt_accessor.dayofweek / 7)
    if DatetimeProperty.SIN_MONTH in properties:
        extracted["sin_month"] = np.sin(2 * np.pi * (dt_accessor.month - 1) / 12)
    if DatetimeProperty.COS_MONTH in properties:
        extracted["cos_month"] = np.cos(2 * np.pi * (dt_accessor.month - 1) / 12)

    # Convert the dictionary of Series into a DataFrame, then export to dict
    # This is vastly more efficient than iterating through index (O(n) vs O(n²))
    return cast(
        dict[Any, dict[str, Any]], pd.DataFrame(extracted).to_dict(orient="index")
    )


def is_string_datetime(series: pd.Series, sample_size: int = 500) -> bool:
    """
    Efficiently detect if a string series contains datetime data.

    A heuristic check that favors performance over strictness, primarily
    intended for high-volume data profiling.

    Parameters
    ----------
    series : pd.Series
        The pandas Series to check. Only object-dtype (string-like)
        series are evaluated.
    sample_size : int, default 500
        The maximum number of non-null values to sample for validation.

    Returns
    -------
    bool
        True if more than 95% of the sampled non-null values parse
        successfully as datetimes, False otherwise.

    Notes
    -----
    - This function skips non-object dtypes immediately to save processing time.
    - It utilizes `pd.to_datetime` with `errors='coerce'` to statistically
      evaluate the content of the sample.

    Examples
    --------
    >>> s = pd.Series(["2026-02-08", "2026-02-09", "not-a-date"])
    >>> is_string_datetime(s)
    True
    """
    # Only check 'object' (string-like) columns
    if not pd.api.types.is_object_dtype(series):
        return False

    # Drop NAs and sample
    sample = series.dropna().head(sample_size)
    if sample.empty:
        return False

    try:
        # 'mixed' tells pandas to try different formats without warning for each
        parsed = pd.to_datetime(sample, errors="coerce", cache=True, format="mixed")
        # If more than 95% of non-nulls parsed, it's likely datetime
        return float(parsed.notnull().mean()) > 0.95
    except Exception:
        return False


def infer_string_datetime_format(
    series: pd.Series, sample_size: int = 500, min_success: float = 0.95
) -> str | None:
    """
    Infer the dominant strptime format for a string Series of datetimes.

    Iterates through a prioritized list of common formats to find a match
    that satisfies the success threshold on a sample of the data.

    Parameters
    ----------
    series : pd.Series
        The string-like (object dtype) pandas Series to inspect.
    sample_size : int, default 500
        Maximum number of non-null values to test for format validation.
    min_success : float, default 0.95
        The minimum required success rate (0.0 to 1.0) to accept a format.

    Returns
    -------
    str or None
        The detected strptime format string (e.g., "%Y-%m-%d %H:%M:%S")
        or None if no dominant format is identified.

    Notes
    -----
    - This is a heuristic approach and may not be reliable for columns
      containing multiple date formats.
    - Leveraging the returned format with `pd.to_datetime(format=...)`
      significantly improves conversion speed for large datasets.
    - Candidate formats are retrieved in priority order from the
      `DatetimeFormat` enum.

    Examples
    --------
    >>> s = pd.Series(["2026-02-08 16:30", "2026-02-08 16:45"])
    >>> infer_string_datetime_format(s)
    '%Y-%m-%d %H:%M'
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
    """
    Resolve ambiguity between US_DATE (%m/%d/%Y) and EU_DATE (%d/%m/%Y) formats.

    Analyzes a sample of date strings to determine if the first or second
    numeric component consistently exceeds 12, indicating its role as the day.

    Parameters
    ----------
    sample_series : pd.Series
        A pandas Series containing date strings (e.g., 'MM/DD/YYYY').
        Supports both '/' and '-' as separators.

    Returns
    -------
    str
        A string indicating the resolved format:
        - "US": Month-Day-Year format (%m/%d/%Y).
        - "EU": Day-Month-Year format (%d/%m/%Y).
        - "AMBIGUOUS": The sample does not contain values high enough to
          distinguish between month and day.

    Notes
    -----
    - The function uses regex to extract the first two numeric parts.
    - It validates that the first component is <= 31 to prevent misidentifying
      years as days in YYYY-MM-DD formats.

    Examples
    --------
    >>> s = pd.Series(['25/01/2026', '08/04/2026'])
    >>> resolve_date_ambiguity(s)
    'EU'
    >>> s_ambig = pd.Series(['01/02/2026', '02/03/2026'])
    >>> resolve_date_ambiguity(s_ambig)
    'AMBIGUOUS'
    """
    # Extract the first two numeric parts using regex
    # e.g., '13/01/2025' -> ('13', '01'), '01-02-2025' -> ('01', '02')
    parts = sample_series.astype(str).str.extract(r"(\d+)[/-](\d+)").dropna()

    if parts.empty:
        return "AMBIGUOUS"

    first_part = parts[0].astype(int)
    second_part = parts[1].astype(int)

    # If the first number is > 12, it's almost certainly EU (DD/MM).
    # We check <= 31 to avoid misidentifying years (e.g. 2025 in YYYY-MM-DD) as days.
    if ((first_part > 12) & (first_part <= 31)).any():
        return "EU"

    # If the second number is > 12, it's almost certainly US (MM/DD)
    if (second_part > 12).any():
        return "US"

    return "AMBIGUOUS"
