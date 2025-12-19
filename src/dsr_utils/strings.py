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


def to_snake_case(name: str) -> str:
    """Convert a string to snake_case format.
    
    Handles various input formats including PascalCase, camelCase, spaces, 
    hyphens, and mixed separators.
    
    Args:
        name (str): The string to convert (typically a column name).
        
    Returns:
        str: The string in snake_case format (lowercase with underscores).
        
    Example:
        >>> to_snake_case('FirstName')
        'first_name'
        >>> to_snake_case('first-name')
        'first_name'
        >>> to_snake_case('FIRST_NAME')
        'first_name'
        >>> to_snake_case('Annual Salary')
        'annual_salary'
    """
    import re
    
    # Replace hyphens and spaces with underscores
    name = name.replace('-', '_').replace(' ', '_')
    
    # Insert underscore before uppercase letters (for camelCase and PascalCase)
    # But avoid multiple underscores and handle consecutive capitals
    name = re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', name)
    
    # Convert to lowercase
    name = name.lower()
    
    # Remove any duplicate underscores
    name = re.sub(r'_+', '_', name)
    
    # Strip leading/trailing underscores
    name = name.strip('_')
    
    return name
