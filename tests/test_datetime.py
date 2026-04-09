"""Tests for datetime conversion utilities."""

import pandas as pd
import pytest

from dsr_utils.datetime import (
    infer_string_datetime_format,
    is_string_datetime,
    to_datetime,
)
from dsr_utils.enums import DatetimeErrors, DatetimeResolution


class TestToDatetime:
    """
    Test suite for the `to_datetime` conversion utility.

    Validates that various input types (strings, lists, Series, integers) are
    correctly converted to Pandas datetime objects with the specified
    resolution and error handling.
    """

    def test_string_to_datetime_default_resolution(self):
        """
        Verify conversion of a standard ISO-8601 string using default resolution.

        Ensures the resulting Timestamp correctly identifies year, month, and day
        components.
        """
        result = to_datetime("2025-12-22")
        assert isinstance(result, pd.Timestamp)
        assert result.year == 2025
        assert result.month == 12
        assert result.day == 22

    def test_string_to_datetime_with_format(self):
        """
        Verify string conversion when an explicit format string is provided.

        Ensures that non-ISO formats (e.g., DD/MM/YYYY) are parsed correctly
        according to the `%d/%m/%Y` specification.
        """
        result = to_datetime("22/12/2025", format="%d/%m/%Y")
        assert isinstance(result, pd.Timestamp)
        assert result.year == 2025
        assert result.month == 12
        assert result.day == 22

    def test_string_to_datetime_with_nanosecond_resolution(self):
        """
        Test converting a string to a datetime with nanosecond resolution.

        Ensures that setting `unit=DatetimeResolution.NANOSECOND` results
        in a Timestamp with 'ns' resolution.
        """
        result = to_datetime("2025-12-22", unit=DatetimeResolution.NANOSECOND)
        assert isinstance(result, pd.Timestamp)
        # Verify resolution by checking unit attribute
        assert result.unit == "ns"

    def test_string_to_datetime_with_microsecond_resolution(self):
        """
        Verify string conversion with microsecond (us) precision.
        """
        result = to_datetime("2025-12-22", unit=DatetimeResolution.MICROSECOND)
        assert isinstance(result, pd.Timestamp)
        assert result.unit == "us"

    def test_string_to_datetime_with_millisecond_resolution(self):
        """
        Verify string conversion with millisecond (ms) precision.
        """
        result = to_datetime("2025-12-22", unit=DatetimeResolution.MILLISECOND)
        assert isinstance(result, pd.Timestamp)
        assert result.unit == "ms"

    def test_string_to_datetime_with_second_resolution(self):
        """
        Verify string conversion with second (s) precision.
        """
        result = to_datetime("2025-12-22", unit=DatetimeResolution.SECOND)
        assert isinstance(result, pd.Timestamp)
        assert result.unit == "s"

    def test_series_to_datetime_default(self):
        """
        Verify the conversion of a pandas Series containing date strings.

        Ensures the resulting Series is a true datetime64 type with
        preserved length.
        """
        dates = pd.Series(["2025-12-22", "2025-12-23", "2025-12-24"])
        result = to_datetime(dates)
        assert isinstance(result, pd.Series)
        assert pd.api.types.is_datetime64_any_dtype(result)
        assert len(result) == 3

    def test_series_to_datetime_with_resolution(self):
        """
        Verify Series conversion with forced nanosecond resolution.
        """
        dates = pd.Series(["2025-12-22", "2025-12-23"])
        result = to_datetime(dates, unit=DatetimeResolution.NANOSECOND)
        assert isinstance(result, pd.Series)
        assert result.dtype == "datetime64[ns]"

    def test_preserve_existing_timestamp(self):
        """
        Verify that an already-valid Timestamp object is returned unchanged.

        Ensures the utility avoids redundant processing if no unit
        conversion is requested.
        """
        original = pd.Timestamp("2025-12-22")
        result = to_datetime(original)
        assert result is original
        assert result == original  # type: ignore[comparison-overlap]

    def test_preserve_existing_datetime_series(self):
        """
        Verify that a Series already containing datetime objects is preserved.
        """
        original = pd.Series(pd.to_datetime(["2025-12-22", "2025-12-23"]))
        result = to_datetime(original)
        assert result is original
        assert isinstance(result, pd.Series)
        pd.testing.assert_series_equal(result, original)

    def test_convert_existing_timestamp_with_unit(self):
        """
        Verify that an existing Timestamp is converted when a new unit is requested.
        """
        original = pd.Timestamp("2025-12-22")
        result = to_datetime(original, unit=DatetimeResolution.MILLISECOND)
        assert isinstance(result, pd.Timestamp)
        assert result.unit == "ms"
        assert result.year == 2025

    def test_convert_existing_series_with_unit(self):
        """
        Verify that an existing datetime Series is correctly rescaled to a new unit.
        """
        original = pd.Series(pd.to_datetime(["2025-12-22", "2025-12-23"]))
        result = to_datetime(original, unit=DatetimeResolution.SECOND)
        assert isinstance(result, pd.Series)
        assert result.dtype == "datetime64[s]"

    def test_invalid_string_raises_error(self):
        """
        Ensure that unparseable strings raise an exception when using `RAISE` mode.
        """
        with pytest.raises(Exception):
            to_datetime("not-a-date", errors=DatetimeErrors.RAISE)

    def test_invalid_string_coerces_to_nat(self):
        """
        Ensure that unparseable strings return `NaT` when using `COERCE` mode.
        """
        result = to_datetime("not-a-date", errors=DatetimeErrors.COERCE)
        # NaT is not an instance of Timestamp, so just check it's NaT
        assert not isinstance(result, pd.Series)
        assert pd.isna(result)

    def test_series_with_invalid_coerce(self):
        """
        Verify that mixed valid/invalid strings in a Series result in partial NaT coercion.
        """
        dates = pd.Series(["2025-12-22", "invalid", "2025-12-23"])
        result = to_datetime(dates, errors=DatetimeErrors.COERCE)
        assert isinstance(result, pd.Series)
        assert pd.api.types.is_datetime64_any_dtype(result)
        assert pd.isna(result.iloc[1])
        assert not pd.isna(result.iloc[0])
        assert not pd.isna(result.iloc[2])

    def test_integer_to_datetime(self):
        """
        Verify conversion of Unix integer timestamps to Pandas Timestamps.
        """
        # Unix timestamp for 2025-12-22 00:00:00 UTC
        timestamp = 1766217600
        # pandas interprets integers as nanoseconds by default, need to specify unit='s'
        result = pd.to_datetime(timestamp, unit="s")
        result = to_datetime(result, unit=DatetimeResolution.SECOND)
        assert isinstance(result, pd.Timestamp)
        assert result.year == 2025
        assert result.month == 12

    def test_list_to_datetime(self):
        """
        Verify that a standard Python list of date strings is converted to a Series.
        """
        dates = ["2025-12-22", "2025-12-23", "2025-12-24"]
        result = to_datetime(dates)
        assert isinstance(result, pd.Series)
        assert pd.api.types.is_datetime64_any_dtype(result)
        assert len(result) == 3

    def test_datetime_with_time(self):
        """
        Verify that strings containing full time components are parsed accurately.
        """
        result = to_datetime("2025-12-22 14:30:45")
        assert isinstance(result, pd.Timestamp)
        assert result.hour == 14
        assert result.minute == 30
        assert result.second == 45

    def test_enum_string_values(self):
        """
        Validate that the DatetimeResolution and DatetimeErrors enums map to
        expected string values.
        """
        assert DatetimeResolution.SECOND.value == "s"
        assert DatetimeResolution.MILLISECOND.value == "ms"
        assert DatetimeResolution.MICROSECOND.value == "us"
        assert DatetimeResolution.NANOSECOND.value == "ns"
        assert DatetimeErrors.RAISE.value == "raise"
        assert DatetimeErrors.COERCE.value == "coerce"


class TestIsStringDatetime:
    """
    Test suite for the `is_string_datetime` heuristic utility.

    Validates the ability to distinguish between datetime-like string columns
    and arbitrary text columns based on statistical thresholds.
    """

    def test_detects_datetime_strings(self):
        """
        Verify that a Series of valid ISO date strings is identified as datetime.
        """
        series = pd.Series(
            [
                "2025-12-22",
                "2024-01-01",
                "2023-07-04",
                "1999-12-31",
                "2020-02-29",
            ]
        )
        assert is_string_datetime(series) is True

    def test_non_object_dtype_returns_false(self):
        """
        Ensure that pre-converted datetime Series return False to avoid redundant detection.
        """
        series = pd.Series(
            pd.to_datetime(
                [
                    "2025-12-22",
                    "2024-01-01",
                ]
            )
        )
        assert is_string_datetime(series) is False

    def test_random_strings_return_false(self):
        """
        Ensure that standard text columns (e.g., fruit names) are not
        misidentified as dates.
        """
        series = pd.Series(
            [
                "apple",
                "banana",
                "carrot",
                "delta",
                "echo",
            ]
        )
        assert is_string_datetime(series) is False

    def test_mixed_strings_threshold(self):
        """
        Verify the 95% threshold logic for mixed valid and invalid strings.
        """
        # 19 valid, 1 invalid -> 95% valid; threshold is > 0.95, so False
        valid_dates = [f"2025-01-{day:02d}" for day in range(1, 20)]
        series = pd.Series(valid_dates + ["not-a-date"])  # 20 total
        assert is_string_datetime(series) is False

    def test_ignores_nas_and_empty(self):
        """
        Verify that null values are excluded from the validity ratio calculation.
        """
        # With NAs removed, remaining are valid dates
        series = pd.Series([None, "2025-01-01", None, "2025-01-02", None])
        assert is_string_datetime(series) is True

    def test_respects_sample_size(self):
        """
        Verify that sampling logic works correctly for large datasets.
        """
        # Ensure sampling doesn't break detection
        series = pd.Series([f"2025-03-{day:02d}" for day in range(1, 1000)])
        assert is_string_datetime(series, sample_size=10) is True

    def test_infer_string_datetime_format_date_only(self):
        """
        Verify format inference for date-only strings (%Y-%m-%d).
        """
        series = pd.Series(["2025-12-22", "2024-07-01", "1999-01-31"])
        fmt = infer_string_datetime_format(series)
        assert fmt == "%Y-%m-%d"

    def test_infer_string_datetime_format_datetime(self):
        """
        Verify format inference for strings with time components (%Y-%m-%d %H:%M:%S).
        """
        series = pd.Series(
            ["2025-12-22 14:30:45", "2024-07-01 00:00:00", "1999-01-31 23:59:59"]
        )
        fmt = infer_string_datetime_format(series)
        assert fmt == "%Y-%m-%d %H:%M:%S"

    def test_infer_string_datetime_format_none_for_mixed(self):
        """
        Ensure that mixed or unparseable formats return `None` rather than
        an inaccurate guess.
        """
        series = pd.Series(["2025-12-22", "07/01/2024", "not-a-date"])  # mixed formats
        fmt = infer_string_datetime_format(series, min_success=0.99)
        assert fmt is None
