"""Tests for datetime parsing utilities."""

import math

import numpy as np
import pandas as pd
import pytest

from dsr_utils.datetime import parse_datetime, parse_datetime_series
from dsr_utils.enums import DatetimeProperty


class TestParseDatetime:
    """Test suite for parse_datetime function."""

    def test_parse_timestamp_basic_date(self):
        """Test parsing basic date properties from Timestamp."""
        ts = pd.Timestamp("2025-12-22")
        result = parse_datetime(
            ts, DatetimeProperty.YEAR | DatetimeProperty.MONTH | DatetimeProperty.DAY)
        assert result == {"year": 2025, "month": 12, "day": 22}

    def test_parse_timestamp_time_properties(self):
        """Test parsing time properties."""
        ts = pd.Timestamp("2025-12-22 14:30:45")
        result = parse_datetime(
            ts, DatetimeProperty.HOUR | DatetimeProperty.MINUTE | DatetimeProperty.SECOND)
        assert result == {"hour": 14, "minute": 30, "second": 45}

    def test_parse_timestamp_dayofweek(self):
        """Test parsing day of week (Monday=0, Sunday=6)."""
        # 2025-12-22 is a Monday
        ts = pd.Timestamp("2025-12-22")
        result = parse_datetime(ts, DatetimeProperty.DAYOFWEEK)
        assert result["dayofweek"] == 0  # Monday

    def test_parse_timestamp_weekend_detection(self):
        """Test IS_WEEKEND property."""
        monday = pd.Timestamp("2025-12-22")  # Monday
        saturday = pd.Timestamp("2025-12-27")  # Saturday
        sunday = pd.Timestamp("2025-12-28")  # Sunday

        assert parse_datetime(monday, DatetimeProperty.IS_WEEKEND)[
            "is_weekend"] is False
        assert parse_datetime(saturday, DatetimeProperty.IS_WEEKEND)[
            "is_weekend"] is True
        assert parse_datetime(sunday, DatetimeProperty.IS_WEEKEND)[
            "is_weekend"] is True

    def test_parse_timestamp_leap_year(self):
        """Test IS_LEAP_YEAR property."""
        leap = pd.Timestamp("2024-02-29")  # Leap year
        non_leap = pd.Timestamp("2025-12-22")  # Non-leap year

        assert parse_datetime(leap, DatetimeProperty.IS_LEAP_YEAR)[
            "is_leap_year"] is True
        assert parse_datetime(non_leap, DatetimeProperty.IS_LEAP_YEAR)[
            "is_leap_year"] is False

    def test_parse_timestamp_quarter(self):
        """Test QUARTER property."""
        q1 = pd.Timestamp("2025-03-15")
        q2 = pd.Timestamp("2025-06-15")
        q3 = pd.Timestamp("2025-09-15")
        q4 = pd.Timestamp("2025-12-15")

        assert parse_datetime(q1, DatetimeProperty.QUARTER)["quarter"] == 1
        assert parse_datetime(q2, DatetimeProperty.QUARTER)["quarter"] == 2
        assert parse_datetime(q3, DatetimeProperty.QUARTER)["quarter"] == 3
        assert parse_datetime(q4, DatetimeProperty.QUARTER)["quarter"] == 4

    def test_parse_timestamp_month_boundaries(self):
        """Test IS_MONTH_START and IS_MONTH_END."""
        start = pd.Timestamp("2025-12-01")
        end = pd.Timestamp("2025-12-31")
        middle = pd.Timestamp("2025-12-15")

        assert parse_datetime(start, DatetimeProperty.IS_MONTH_START)[
            "is_month_start"] is True
        assert parse_datetime(end, DatetimeProperty.IS_MONTH_END)[
            "is_month_end"] is True
        assert parse_datetime(middle, DatetimeProperty.IS_MONTH_START)[
            "is_month_start"] is False
        assert parse_datetime(middle, DatetimeProperty.IS_MONTH_END)[
            "is_month_end"] is False

    def test_parse_timestamp_names(self):
        """Test DAY_NAME and MONTH_NAME."""
        ts = pd.Timestamp("2025-12-22")  # Monday, December
        result = parse_datetime(
            ts, DatetimeProperty.DAY_NAME | DatetimeProperty.MONTH_NAME)
        assert result["day_name"] == "Monday"
        assert result["month_name"] == "December"

    def test_parse_timestamp_cyclical_sine_cosine(self):
        """Test cyclical sine/cosine transformations."""
        ts = pd.Timestamp("2025-12-22 12:00:00")  # Noon
        result = parse_datetime(
            ts,
            DatetimeProperty.SIN_HOUR
            | DatetimeProperty.COS_HOUR
            | DatetimeProperty.SIN_MONTH
            | DatetimeProperty.COS_MONTH,
        )

        # At hour 12: sin(2π * 12/24) = sin(π) = 0, cos(π) = -1
        assert abs(result["sin_hour"] - 0.0) < 1e-10
        assert abs(result["cos_hour"] - (-1.0)) < 1e-10

        # At month 12: sin(2π * 12/12) = sin(2π) = 0, cos(2π) = 1
        assert abs(result["sin_month"] - 0.0) < 1e-10
        assert abs(result["cos_month"] - 1.0) < 1e-10

    def test_parse_timestamp_multiple_properties(self):
        """Test parsing multiple properties at once."""
        ts = pd.Timestamp("2025-12-22 14:30:45")
        result = parse_datetime(
            ts,
            DatetimeProperty.YEAR
            | DatetimeProperty.MONTH
            | DatetimeProperty.DAY
            | DatetimeProperty.HOUR
            | DatetimeProperty.MINUTE,
        )
        assert len(result) == 5
        assert result["year"] == 2025
        assert result["month"] == 12
        assert result["day"] == 22
        assert result["hour"] == 14
        assert result["minute"] == 30


class TestParseDatetimeSeries:
    """Test suite for parse_datetime_series function."""

    def test_parse_series_basic_date(self):
        """Test parsing basic date properties from Series."""
        series = pd.Series(
            [pd.Timestamp("2025-12-22"), pd.Timestamp("2025-12-23")],
            index=["a", "b"],
        )
        result = parse_datetime_series(
            series, DatetimeProperty.YEAR | DatetimeProperty.MONTH | DatetimeProperty.DAY
        )

        assert result["a"] == {"year": 2025, "month": 12, "day": 22}
        assert result["b"] == {"year": 2025, "month": 12, "day": 23}

    def test_parse_series_preserves_index(self):
        """Test that Series index is preserved in output."""
        series = pd.Series(
            [pd.Timestamp("2025-12-22"), pd.Timestamp("2025-12-23"),
             pd.Timestamp("2025-12-24")],
            index=["row1", "row2", "row3"],
        )
        result = parse_datetime_series(series, DatetimeProperty.DAY)

        assert set(result.keys()) == {"row1", "row2", "row3"}
        assert result["row1"]["day"] == 22
        assert result["row2"]["day"] == 23
        assert result["row3"]["day"] == 24

    def test_parse_series_numeric_index(self):
        """Test Series with numeric index."""
        series = pd.Series(
            [pd.Timestamp("2025-12-22"), pd.Timestamp("2025-12-23")],
            index=[0, 1],
        )
        result = parse_datetime_series(series, DatetimeProperty.DAY)

        assert 0 in result
        assert 1 in result
        assert result[0]["day"] == 22
        assert result[1]["day"] == 23

    def test_parse_series_weekend_vectorized(self):
        """Test IS_WEEKEND property works vectorized."""
        # Mon, Sat, Sun, Tue, Wed
        series = pd.Series(
            [
                pd.Timestamp("2025-12-22"),  # Monday
                pd.Timestamp("2025-12-27"),  # Saturday
                pd.Timestamp("2025-12-28"),  # Sunday
                pd.Timestamp("2025-12-23"),  # Tuesday
                pd.Timestamp("2025-12-24"),  # Wednesday
            ],
            index=["mon", "sat", "sun", "tue", "wed"],
        )
        result = parse_datetime_series(series, DatetimeProperty.IS_WEEKEND)

        assert result["mon"]["is_weekend"] == False
        assert result["sat"]["is_weekend"] == True
        assert result["sun"]["is_weekend"] == True
        assert result["tue"]["is_weekend"] == False
        assert result["wed"]["is_weekend"] == False

    def test_parse_series_cyclical_vectorized(self):
        """Test cyclical transformations work vectorized."""
        series = pd.Series(
            [
                pd.Timestamp("2025-12-22 00:00"),  # Midnight
                pd.Timestamp("2025-12-22 12:00"),  # Noon
                pd.Timestamp("2025-12-22 18:00"),  # 6 PM
            ],
            index=["midnight", "noon", "evening"],
        )
        result = parse_datetime_series(
            series, DatetimeProperty.SIN_HOUR | DatetimeProperty.COS_HOUR)

        # Midnight (0h): sin(0) = 0, cos(0) = 1
        assert abs(result["midnight"]["sin_hour"] - 0.0) < 1e-10
        assert abs(result["midnight"]["cos_hour"] - 1.0) < 1e-10

        # Noon (12h): sin(π) = 0, cos(π) = -1
        assert abs(result["noon"]["sin_hour"] - 0.0) < 1e-10
        assert abs(result["noon"]["cos_hour"] - (-1.0)) < 1e-10

    def test_parse_series_large_dataset(self):
        """Test performance with larger dataset (1000 rows)."""
        dates = pd.date_range("2025-01-01", periods=1000, freq="h")
        series = pd.Series(dates)

        result = parse_datetime_series(
            series, DatetimeProperty.YEAR | DatetimeProperty.MONTH | DatetimeProperty.DAY | DatetimeProperty.HOUR
        )

        assert len(result) == 1000
        # Verify first and last entries
        assert result[0]["year"] == 2025
        assert result[0]["month"] == 1
        assert result[0]["day"] == 1
        # 1000 hours from 2025-01-01 00:00 = 2025-02-11 16:00 (41 days + 16 hours)
        assert result[999]["day"] == 11
        assert result[999]["month"] == 2
        assert result[999]["hour"] == 15  # 999 hours (0-indexed) = 41*24 + 15

    def test_parse_series_multiple_properties(self):
        """Test parsing multiple properties from Series."""
        series = pd.Series(
            [pd.Timestamp("2025-12-22 14:30:45"),
             pd.Timestamp("2025-12-23 09:15:30")],
            index=["ts1", "ts2"],
        )
        result = parse_datetime_series(
            series,
            DatetimeProperty.YEAR
            | DatetimeProperty.MONTH
            | DatetimeProperty.HOUR
            | DatetimeProperty.MINUTE
            | DatetimeProperty.IS_WEEKEND,
        )

        assert len(result["ts1"]) == 5
        assert result["ts1"]["year"] == 2025
        assert result["ts1"]["hour"] == 14
        assert result["ts1"]["is_weekend"] == False

    def test_parse_series_with_nat_values(self):
        """Test Series with NaT values."""
        series = pd.Series(
            [pd.Timestamp("2025-12-22"), pd.NaT, pd.Timestamp("2025-12-23")],
            index=["a", "b", "c"],
        )
        result = parse_datetime_series(series, DatetimeProperty.YEAR)

        assert result["a"]["year"] == 2025
        assert pd.isna(result["b"]["year"])  # NaT should propagate
        assert result["c"]["year"] == 2025

    def test_parse_series_all_properties(self):
        """Test parsing all available properties."""
        series = pd.Series(
            [pd.Timestamp("2025-06-15 14:30:45")],
            index=["ts"],
        )

        # Use all properties
        all_props = (
            DatetimeProperty.YEAR
            | DatetimeProperty.MONTH
            | DatetimeProperty.DAY
            | DatetimeProperty.DAYOFWEEK
            | DatetimeProperty.DAYOFYEAR
            | DatetimeProperty.QUARTER
            | DatetimeProperty.WEEK
            | DatetimeProperty.IS_MONTH_END
            | DatetimeProperty.IS_MONTH_START
            | DatetimeProperty.IS_QUARTER_END
            | DatetimeProperty.IS_QUARTER_START
            | DatetimeProperty.IS_YEAR_END
            | DatetimeProperty.IS_YEAR_START
            | DatetimeProperty.IS_WEEKEND
            | DatetimeProperty.IS_LEAP_YEAR
            | DatetimeProperty.HOUR
            | DatetimeProperty.MINUTE
            | DatetimeProperty.SECOND
            | DatetimeProperty.DAY_NAME
            | DatetimeProperty.MONTH_NAME
            | DatetimeProperty.SIN_HOUR
            | DatetimeProperty.COS_HOUR
            | DatetimeProperty.SIN_DAYOFWEEK
            | DatetimeProperty.COS_DAYOFWEEK
            | DatetimeProperty.SIN_MONTH
            | DatetimeProperty.COS_MONTH
        )

        result = parse_datetime_series(series, all_props)
        props = result["ts"]

        # Verify we got all properties (24 enum values + 2 derived: is_weekend, is_leap_year = 26 total)
        assert len(props) == 26

        # Spot check some values
        assert props["year"] == 2025
        assert props["month"] == 6
        assert props["quarter"] == 2
        assert props["is_weekend"] == True  # 2025-06-15 is Sunday
        assert props["day_name"] == "Sunday"
        assert props["month_name"] == "June"
