def is_float_string(value) -> bool:
    """Check if a value can be converted to a float.

    Attempts to convert the value to float and returns True if successful,
    False if conversion fails or value is None.

    Args:
        value: Any value to test for float conversion.

    Returns:
        bool: True if value can be converted to float, False otherwise.

    Example:
        >>> is_float_string("3.14")
        True
        >>> is_float_string("abc")
        False
        >>> is_float_string(None)
        False
    """
    if value is None:
        return False
    try:
        float(value)
        return True
    except ValueError:
        return False
