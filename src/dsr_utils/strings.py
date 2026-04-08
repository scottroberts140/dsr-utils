"""String utilities for case conversion and parsing helpers."""

from typing import Any, Callable

from dsr_utils.enums import StringCase


def is_float_string(value: Any) -> bool:
    """
    Check if a value can be converted to a float.

    Attempts to cast the input to a float and returns the success status.

    Parameters
    ----------
    value : Any
        The value to test for float conversion.

    Returns
    -------
    bool
        True if the value can be converted to a float, False otherwise.

    Examples
    --------
    >>> is_float_string("3.14")
    True
    >>> is_float_string("abc")
    False
    """
    if value is None:
        return False
    try:
        float(value)
        return True
    except ValueError:
        return False


def _normalize_separators(name: str) -> str:
    """
    Normalize a string by handling various separators.

    Internal helper that standardizes spaces, hyphens, and casing transitions
    into single underscores.

    Parameters
    ----------
    name : str
        The string to normalize.

    Returns
    -------
    str
        The normalized string with consistent underscore separators.
    """
    import re

    # Replace hyphens and spaces with underscores
    name = name.replace("-", "_").replace(" ", "_")

    # Insert underscore before uppercase letters (for camelCase and PascalCase)
    # But avoid multiple underscores and handle consecutive capitals
    name = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", name)

    # Remove any duplicate underscores
    name = re.sub(r"_+", "_", name)

    # Strip leading/trailing underscores
    name = name.strip("_")

    return name


def to_snake_case(name: str) -> str:
    """
    Convert a string to snake_case format.

    Parameters
    ----------
    name : str
        The string to convert (typically a column name).

    Returns
    -------
    str
        The string in lowercase with underscore separators.

    Examples
    --------
    >>> to_snake_case('FirstName')
    'first_name'
    >>> to_snake_case('Annual Salary')
    'annual_salary'
    """
    return _normalize_separators(name).lower()


def to_pascal_case(name: str) -> str:
    """
    Convert a string to PascalCase format.

    Parameters
    ----------
    name : str
        The string to convert.

    Returns
    -------
    str
        The string with each word capitalized and no separators.

    Examples
    --------
    >>> to_pascal_case('first_name')
    'FirstName'
    """
    normalized = _normalize_separators(name)
    return "".join(word.capitalize() for word in normalized.split("_"))


def to_camel_case(name: str) -> str:
    """
    Convert a string to camelCase format.

    Parameters
    ----------
    name : str
        The string to convert.

    Returns
    -------
    str
        The string with the first word lowercase and subsequent words capitalized.

    Examples
    --------
    >>> to_camel_case('annual salary')
    'annualSalary'
    """
    normalized = _normalize_separators(name)
    parts = normalized.split("_")
    return parts[0].lower() + "".join(word.capitalize() for word in parts[1:])


def to_kebab_case(name: str) -> str:
    """
    Convert a string to kebab-case format.

    Parameters
    ----------
    name : str
        The string to convert.

    Returns
    -------
    str
        The string in lowercase with hyphen separators.
    """
    normalized = _normalize_separators(name)
    return normalized.lower().replace("_", "-")


def to_constant_case(name: str) -> str:
    """
    Convert a string to CONSTANT_CASE format.

    Parameters
    ----------
    name : str
        The string to convert.

    Returns
    -------
    str
        The string in uppercase with underscore separators.
    """
    normalized = _normalize_separators(name)
    return normalized.upper()


def to_original_string(text: str) -> str:
    """
    Return the input string unchanged.

    Parameters
    ----------
    text : str
        The input string.

    Returns
    -------
    str
        The original input string.
    """
    return text


def func_for_string_conv(string_case: StringCase) -> Callable[[str], str]:
    """
    Resolve a case conversion function for the requested StringCase.

    Parameters
    ----------
    string_case : StringCase
        Target string case enumeration.

    Returns
    -------
    Callable[[str], str]
        A conversion function mapped to the requested case.
    """
    match string_case:
        case StringCase.SNAKE:
            convert_func = to_snake_case
        case StringCase.PASCAL:
            convert_func = to_pascal_case
        case StringCase.CAMEL:
            convert_func = to_camel_case
        case StringCase.KEBAB:
            convert_func = to_kebab_case
        case StringCase.CONSTANT:
            convert_func = to_constant_case
        case _:
            convert_func = to_original_string

    return convert_func


def convert_keys_to_case(input_dict: dict, string_case: StringCase) -> dict:
    """
    Convert all keys in a dictionary (recursively) to the requested case.

    Parameters
    ----------
    input_dict : dict
        The dictionary whose keys should be transformed.
    string_case : StringCase
        Target string case.

    Returns
    -------
    dict
        A new dictionary with transformed keys.
    """
    convert_func = func_for_string_conv(string_case)

    def convert_keys_to_case_using_func(source: dict) -> dict:
        converted: dict = {}
        for k, v in source.items():
            new_key = convert_func(k)
            if isinstance(v, dict):
                converted[new_key] = convert_keys_to_case_using_func(v)
            else:
                converted[new_key] = v
        return converted

    return convert_keys_to_case_using_func(input_dict)


def convert_list_to_case(input_list: list[str], string_case: StringCase) -> list[str]:
    """
    Convert a list of strings to the requested case.

    Parameters
    ----------
    input_list : list of str
        List of strings to convert.
    string_case : StringCase
        Target string case.

    Returns
    -------
    list of str
        List of converted strings.
    """
    convert_func = func_for_string_conv(string_case)
    return [convert_func(s) for s in input_list]


def convert_str_to_case(input_str: str, string_case: StringCase) -> str:
    """
    Convert a single string to the requested case.

    Parameters
    ----------
    input_str : str
        String to convert.
    string_case : StringCase
        Target string case.

    Returns
    -------
    str
        Converted string.
    """
    convert_func = func_for_string_conv(string_case)
    return convert_func(input_str)


def apply_tracking(text: str) -> str:
    """
    Apply character tracking (spacing) to a string.

    Parameters
    ----------
    text : str
        The input string.

    Returns
    -------
    str
        The string with spaces inserted between characters.

    Examples
    --------
    >>> apply_tracking("ABC")
    'A B C'
    """
    return " ".join(list(text))
