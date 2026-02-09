"""Tests for dsr_utils.formatting module."""

from datetime import datetime

import pytest

from dsr_utils.formatting import (
    TextAlignment,
    NumericScale,
    DataScale,
    DateTimeFormat,
    format_text,
    format_label_value_pairs,
    format_as_grid,
)


class TestFormattingUtilities:
    """Test cases for core formatting helpers."""

    def test_text_alignment_symbols(self):
        """Ensure alignment symbols and matplotlib strings are correct."""
        assert TextAlignment.LEFT.formatting_symbol() == "<"
        assert TextAlignment.CENTER.formatting_symbol() == "^"
        assert TextAlignment.RIGHT.formatting_symbol() == ">"
        assert TextAlignment.LEFT.matplot_alignment() == "left"
        assert TextAlignment.CENTER.matplot_alignment() == "center"
        assert TextAlignment.RIGHT.matplot_alignment() == "right"

    def test_numeric_scale_auto_descriptor(self):
        """Verify AUTO numeric scale chooses appropriate suffix."""
        assert NumericScale.AUTO.get_descriptor(2_500_000) == "M"
        assert NumericScale.AUTO.get_descriptor(2_500) == "K"

    def test_numeric_scale_auto_scaled_value(self):
        """Verify AUTO numeric scale returns scaled values."""
        assert NumericScale.AUTO.get_scaled_value(2_500_000) == pytest.approx(2.5)

    def test_data_scale_descriptor_auto(self):
        """Verify AUTO data scale chooses largest applicable suffix."""
        assert DataScale.AUTO.get_descriptor(5_000_000_000) == "GB"

    def test_data_scale_scaled_value_gb(self):
        """Verify data scale conversion to GB."""
        two_gb = 2 * DataScale.GB.get_size()
        assert DataScale.GB.get_scaled_value(two_gb) == pytest.approx(2.0)

    def test_datetime_format_separator(self):
        """Ensure DateTimeFormat uses custom separator and persists it."""
        dt = datetime(2025, 1, 2, 3, 4)
        fmt = DateTimeFormat(date_format="%Y-%m-%d", time_format="%H:%M", separator="T")
        assert fmt.format_value(dt) == "2025-01-02T03:04"

        fmt_dict = fmt.to_dict()
        assert fmt_dict["separator"] == "T"
        assert fmt_dict["use_duration_format"] is False

        cloned = DateTimeFormat.from_format(fmt)
        assert cloned.separator == "T"

    def test_datetime_duration_format(self):
        """Ensure duration formatting outputs human-readable values."""
        fmt = DateTimeFormat(use_duration_format=True)
        assert fmt.format_value(3661) == "1h 1m 1s"

    def test_format_text_wrap(self):
        """Wrap text with prefix/suffix and alignment."""
        output = format_text(
            text="Long message that wraps",
            buffer_width=20,
            prefix="|",
            suffix="|",
        )
        lines = output.splitlines()
        assert lines[0].startswith("|") and lines[0].endswith("|")
        assert len(lines) == 2

    def test_format_label_value_pairs_alignment(self):
        """Align values by label width and padding."""
        pairs = [("Rows", 10), ("Columns", 2)]
        formatted = format_label_value_pairs(pairs)
        lines = formatted.splitlines()
        assert len(lines) == 2
        value_start_0 = lines[0].find("10")
        value_start_1 = lines[1].find("2")
        assert value_start_0 == value_start_1

    def test_format_as_grid_column_major(self):
        """Verify default column-major layout for grids."""
        output = format_as_grid(["A", "B", "C", "D"], cols=2, padding=4)
        lines = output.splitlines()
        assert lines[0].startswith("A")
        assert "C" in lines[0]
        assert lines[1].startswith("B")
        assert "D" in lines[1]
