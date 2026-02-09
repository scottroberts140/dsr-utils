"""Tests for dsr_utils.strings module."""

from dsr_utils.enums import StringCase
from dsr_utils.strings import (
    is_float_string,
    to_snake_case,
    to_pascal_case,
    to_camel_case,
    to_kebab_case,
    to_constant_case,
    func_for_string_conv,
    convert_keys_to_case,
    convert_list_to_case,
)


class TestStringFunctions:
    """Test cases for string utility functions."""

    def test_is_float_string(self):
        """Validate float string detection."""
        assert is_float_string("3.14") is True
        assert is_float_string("abc") is False
        assert is_float_string(None) is False

    def test_case_conversions(self):
        """Validate case conversion helpers."""
        assert to_snake_case("FirstName") == "first_name"
        assert to_pascal_case("first_name") == "FirstName"
        assert to_camel_case("FirstName") == "firstName"
        assert to_kebab_case("FirstName") == "first-name"
        assert to_constant_case("firstName") == "FIRST_NAME"

    def test_func_for_string_conv(self):
        """Resolve conversion function by enum."""
        conv = func_for_string_conv(StringCase.SNAKE)
        assert conv("FirstName") == "first_name"

    def test_convert_keys_to_case(self):
        """Convert dictionary keys recursively."""
        data = {"FirstName": "Ada", "MetaData": {"LastName": "Lovelace"}}
        converted = convert_keys_to_case(data, StringCase.SNAKE)
        assert converted == {
            "first_name": "Ada",
            "meta_data": {"last_name": "Lovelace"},
        }
        # original should remain unchanged
        assert "FirstName" in data

    def test_convert_list_to_case(self):
        """Convert list of strings to requested case."""
        result = convert_list_to_case(["FirstName", "LastName"], StringCase.SNAKE)
        assert result == ["first_name", "last_name"]
