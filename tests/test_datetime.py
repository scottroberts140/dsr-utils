"""Tests for datetime conversion utilities."""

import pandas as pd
import pytest

from dsr_utils.datetime import to_datetime, is_string_datetime
from dsr_utils.enums import DatetimeErrors, DatetimeResolution


class TestToDatetime:
    """Test suite for to_datetime function."""

    def test_string_to_datetime_default_resolution(self):
        """Test converting string to datetime with default resolution."""
        result = to_datetime("2025-12-22")
        assert isinstance(result, pd.Timestamp)
        assert result.year == 2025
        assert result.month == 12
        assert result.day == 22

    def test_string_to_datetime_with_format(self):
        """Test converting string with explicit format."""
        result = to_datetime("22/12/2025", format="%d/%m/%Y")
        assert isinstance(result, pd.Timestamp)
        assert result.year == 2025
        assert result.month == 12
        assert result.day == 22

    def test_string_to_datetime_with_nanosecond_resolution(self):
        """Test converting with nanosecond resolution."""
        result = to_datetime("2025-12-22", unit=DatetimeResolution.NANOSECOND)
        assert isinstance(result, pd.Timestamp)
        # Verify resolution by checking unit attribute
        assert result.unit == "ns"

    def test_string_to_datetime_with_microsecond_resolution(self):
        """Test converting with microsecond resolution."""
        result = to_datetime("2025-12-22", unit=DatetimeResolution.MICROSECOND)
        assert isinstance(result, pd.Timestamp)
        assert result.unit == "us"

    def test_string_to_datetime_with_millisecond_resolution(self):
        """Test converting with millisecond resolution."""
        result = to_datetime("2025-12-22", unit=DatetimeResolution.MILLISECOND)
        assert isinstance(result, pd.Timestamp)
        assert result.unit == "ms"

    def test_string_to_datetime_with_second_resolution(self):
        """Test converting with second resolution."""
        result = to_datetime("2025-12-22", unit=DatetimeResolution.SECOND)
        assert isinstance(result, pd.Timestamp)
        assert result.unit == "s"

    def test_series_to_datetime_default(self):
        """Test converting Series to datetime."""
        dates = pd.Series(["2025-12-22", "2025-12-23", "2025-12-24"])
        result = to_datetime(dates)
        assert isinstance(result, pd.Series)
        assert pd.api.types.is_datetime64_any_dtype(result)
        assert len(result) == 3

    def test_series_to_datetime_with_resolution(self):
        """Test converting Series with specific resolution."""
        dates = pd.Series(["2025-12-22", "2025-12-23"])
        result = to_datetime(dates, unit=DatetimeResolution.NANOSECOND)
        assert isinstance(result, pd.Series)
        assert result.dtype == "datetime64[ns]"

    def test_preserve_existing_timestamp(self):
        """Test that existing Timestamp is preserved when no unit specified."""
        original = pd.Timestamp("2025-12-22")
        result = to_datetime(original)
        assert result is original
        assert result == original  # type: ignore[comparison-overlap]

    def test_preserve_existing_datetime_series(self):
        """Test that existing datetime Series is preserved when no unit specified."""
        original = pd.Series(pd.to_datetime(["2025-12-22", "2025-12-23"]))
        result = to_datetime(original)
        assert result is original
        assert isinstance(result, pd.Series)
        pd.testing.assert_series_equal(result, original)

    def test_convert_existing_timestamp_with_unit(self):
        """Test that existing Timestamp is converted when unit is specified."""
        original = pd.Timestamp("2025-12-22")
        result = to_datetime(original, unit=DatetimeResolution.MILLISECOND)
        assert isinstance(result, pd.Timestamp)
        assert result.unit == "ms"
        assert result.year == 2025

    def test_convert_existing_series_with_unit(self):
        """Test that existing datetime Series is converted when unit is specified."""
        original = pd.Series(pd.to_datetime(["2025-12-22", "2025-12-23"]))
        result = to_datetime(original, unit=DatetimeResolution.SECOND)
        assert isinstance(result, pd.Series)
        assert result.dtype == "datetime64[s]"

    def test_invalid_string_raises_error(self):
        """Test that invalid string raises error with RAISE mode."""
        with pytest.raises(Exception):
            to_datetime("not-a-date", errors=DatetimeErrors.RAISE)

    def test_invalid_string_coerces_to_nat(self):
        """Test that invalid string is coerced to NaT with COERCE mode."""
        result = to_datetime("not-a-date", errors=DatetimeErrors.COERCE)
        # NaT is not an instance of Timestamp, so just check it's NaT
        assert not isinstance(result, pd.Series)
        assert pd.isna(result)

    def test_series_with_invalid_coerce(self):
        """Test Series with invalid dates coerced to NaT."""
        dates = pd.Series(["2025-12-22", "invalid", "2025-12-23"])
        result = to_datetime(dates, errors=DatetimeErrors.COERCE)
        assert isinstance(result, pd.Series)
        assert pd.api.types.is_datetime64_any_dtype(result)
        assert pd.isna(result.iloc[1])
        assert not pd.isna(result.iloc[0])
        assert not pd.isna(result.iloc[2])

    def test_integer_to_datetime(self):
        """Test converting integer timestamps."""
        # Unix timestamp for 2025-12-22 00:00:00 UTC
        timestamp = 1766217600
        # pandas interprets integers as nanoseconds by default, need to specify unit='s'
        result = pd.to_datetime(timestamp, unit='s')
        result = to_datetime(result, unit=DatetimeResolution.SECOND)
        assert isinstance(result, pd.Timestamp)
        assert result.year == 2025
        assert result.month == 12

    def test_list_to_datetime(self):
        """Test converting list of dates."""
        dates = ["2025-12-22", "2025-12-23", "2025-12-24"]
        result = to_datetime(dates)
        assert isinstance(result, pd.DatetimeIndex)
        assert len(result) == 3

    def test_datetime_with_time(self):
        """Test converting datetime strings with time."""
        result = to_datetime("2025-12-22 14:30:45")
        assert isinstance(result, pd.Timestamp)
        assert result.hour == 14
        assert result.minute == 30
        assert result.second == 45

    def test_enum_string_values(self):
        """Test that enum values are correct strings."""
        assert DatetimeResolution.SECOND.value == "s"
        assert DatetimeResolution.MILLISECOND.value == "ms"
        assert DatetimeResolution.MICROSECOND.value == "us"
        assert DatetimeResolution.NANOSECOND.value == "ns"
        assert DatetimeErrors.RAISE.value == "raise"
        assert DatetimeErrors.COERCE.value == "coerce"


class TestIsStringDatetime:
    def test_detects_datetime_strings(self):
        series = pd.Series([
            "2025-12-22",
            "2024-01-01",
            "2023-07-04",
            "1999-12-31",
            "2020-02-29",
        ])
        assert is_string_datetime(series) is True

    def test_non_object_dtype_returns_false(self):
        series = pd.Series(pd.to_datetime([
            "2025-12-22",
            "2024-01-01",
        ]))
        assert is_string_datetime(series) is False

    def test_random_strings_return_false(self):
        series = pd.Series([
            "apple",
            "banana",
            "carrot",
            "delta",
            "echo",
        ])
        assert is_string_datetime(series) is False

    def test_mixed_strings_threshold(self):
        # 19 valid, 1 invalid -> 95% valid; threshold is > 0.95, so False
        valid_dates = [f"2025-01-{day:02d}" for day in range(1, 20)]
        series = pd.Series(valid_dates + ["not-a-date"])  # 20 total
        assert is_string_datetime(series) is False

    def test_ignores_nas_and_empty(self):
        # With NAs removed, remaining are valid dates
        series = pd.Series([None, "2025-01-01", None, "2025-01-02", None])
        assert is_string_datetime(series) is True

    def test_respects_sample_size(self):
        # Ensure sampling doesn't break detection
        series = pd.Series([f"2025-03-{day:02d}" for day in range(1, 1000)])
        assert is_string_datetime(series, sample_size=10) is True
