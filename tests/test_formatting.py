"""Tests for dsr_utils.formatting module."""

from datetime import datetime

import pytest

from dsr_utils.formatting import (
    DataScale,
    DateTimeFormat,
    NumericScale,
    TextAlignment,
    format_as_grid,
    format_label_value_pairs,
    format_text,
)


class TestFormattingUtilities:
    """
    Test suite for the `dsr_utils.formatting` module.

    Validates text alignment symbols, numeric and data scaling logic,
    datetime formatting, and grid-based text layout utilities.
    """

    def test_text_alignment_symbols(self):
        """
        Verify that alignment enums return correct formatting and Matplotlib strings.

        Ensures `TextAlignment` symbols match standard Python format specs (<, ^, >)
        and Matplotlib alignment properties.
        """
        assert TextAlignment.LEFT.formatting_symbol() == "<"
        assert TextAlignment.CENTER.formatting_symbol() == "^"
        assert TextAlignment.RIGHT.formatting_symbol() == ">"
        assert TextAlignment.LEFT.matplot_alignment() == "left"
        assert TextAlignment.CENTER.matplot_alignment() == "center"
        assert TextAlignment.RIGHT.matplot_alignment() == "right"

    def test_numeric_scale_auto_descriptor(self):
        """
        Verify that the AUTO numeric scale selects the correct magnitude descriptor.

        Ensures values in the millions (M) and thousands (K) are assigned
        the appropriate shorthand suffixes.
        """
        assert NumericScale.AUTO.get_descriptor(2_500_000) == "M"
        assert NumericScale.AUTO.get_descriptor(2_500) == "K"

    def test_numeric_scale_auto_scaled_value(self):
        """
        Verify that the AUTO numeric scale accurately scales large integers.
        """
        assert NumericScale.AUTO.get_scaled_value(2_500_000) == pytest.approx(2.5)

    def test_data_scale_descriptor_auto(self):
        """
        Verify that the AUTO data scale identifies the largest applicable unit.

        Ensures byte-count values are correctly identified as GB, MB, etc.,
        based on their magnitude.
        """
        assert DataScale.AUTO.get_descriptor(5_000_000_000) == "GB"

    def test_data_scale_scaled_value_gb(self):
        """
        Verify the conversion of byte counts into Gigabyte (GB) units.
        """
        two_gb = 2 * DataScale.GB.get_size()
        assert DataScale.GB.get_scaled_value(two_gb) == pytest.approx(2.0)

    def test_datetime_format_separator(self):
        """
        Ensure custom separators in `DateTimeFormat` are applied and persisted.

        Validates that separators (e.g., 'T') are used during string formatting
        and correctly serialized/deserialized via dictionaries and cloning.
        """
        dt = datetime(2025, 1, 2, 3, 4)
        fmt = DateTimeFormat(date_format="%Y-%m-%d", time_format="%H:%M", separator="T")
        assert fmt.format_value(dt) == "2025-01-02T03:04"

        fmt_dict = fmt.to_dict()
        assert fmt_dict["separator"] == "T"
        assert fmt_dict["use_duration_format"] is False

        cloned = DateTimeFormat.from_format(fmt)
        assert cloned.separator == "T"

    def test_datetime_duration_format(self):
        """
        Verify that time offsets are formatted into human-readable durations.

        Ensures raw second counts are converted into 'Hh Mm Ss' format.
        """
        fmt = DateTimeFormat(use_duration_format=True)
        assert fmt.format_value(3661) == "1h 1m 1s"

    def test_format_text_wrap(self):
        """
        Verify text wrapping with custom prefixes, suffixes, and buffer widths.

        Ensures that long strings are split across lines while maintaining
        structural padding and alignment.
        """
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
        """
        Verify that label-value pairs are vertically aligned based on label width.

        Ensures that values remain column-aligned even when labels have
        varying character lengths.
        """
        pairs = [("Rows", 10), ("Columns", 2)]
        formatted = format_label_value_pairs(pairs)
        lines = formatted.splitlines()
        assert len(lines) == 2
        value_start_0 = lines[0].find("10")
        value_start_1 = lines[1].find("2")
        assert value_start_0 == value_start_1

    def test_format_as_grid_column_major(self):
        """
        Verify the column-major layout logic for grid-based text formatting.

        Ensures list items are distributed vertically through columns
        before moving to the next horizontal position.
        """
        output = format_as_grid(["A", "B", "C", "D"], cols=2, padding=4)
        lines = output.splitlines()
        assert lines[0].startswith("A")
        assert "C" in lines[0]
        assert lines[1].startswith("B")
        assert "D" in lines[1]
