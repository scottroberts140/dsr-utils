"""Tests for dsr_utils.strings module."""

from dsr_utils.enums import StringCase
from dsr_utils.strings import (
    convert_keys_to_case,
    convert_list_to_case,
    func_for_string_conv,
    is_float_string,
    to_camel_case,
    to_constant_case,
    to_kebab_case,
    to_pascal_case,
    to_snake_case,
)


class TestStringFunctions:
    """
    Test suite for the `dsr_utils.strings` module.

    Validates float detection, multiple case transformation formats (Snake,
    Pascal, Camel, Kebab, Constant), and recursive dictionary key
    conversions.
    """

    def test_is_float_string(self):
        """
        Verify the detection of numeric float representations within strings.

        Ensures valid float strings return True while alphabetic strings
        and None types return False.
        """
        assert is_float_string("3.14") is True
        assert is_float_string("abc") is False
        assert is_float_string(None) is False

    def test_case_conversions(self):
        """
        Validate all primary case conversion helpers.

        Ensures accurate bidirectional transformation between FirstName and
        various formats like first_name, firstName, and FIRST_NAME.
        """
        assert to_snake_case("FirstName") == "first_name"
        assert to_pascal_case("first_name") == "FirstName"
        assert to_camel_case("FirstName") == "firstName"
        assert to_kebab_case("FirstName") == "first-name"
        assert to_constant_case("firstName") == "FIRST_NAME"

    def test_func_for_string_conv(self):
        """
        Verify that the conversion function resolver correctly maps Enums to logic.

        Ensures that passing a `StringCase` enum returns the expected
        transformation callable.
        """
        conv = func_for_string_conv(StringCase.SNAKE)
        assert conv("FirstName") == "first_name"

    def test_convert_keys_to_case(self):
        """
        Verify recursive dictionary key conversion.

        Ensures that nested dictionaries have their keys transformed
        according to the requested case while keeping the original
        dictionary immutable.
        """
        data = {"FirstName": "Ada", "MetaData": {"LastName": "Lovelace"}}
        converted = convert_keys_to_case(data, StringCase.SNAKE)
        assert converted == {
            "first_name": "Ada",
            "meta_data": {"last_name": "Lovelace"},
        }
        # original should remain unchanged
        assert "FirstName" in data

    def test_convert_list_to_case(self):
        """
        Verify the bulk conversion of string lists into a specific case format.
        """
        result = convert_list_to_case(["FirstName", "LastName"], StringCase.SNAKE)
        assert result == ["first_name", "last_name"]
