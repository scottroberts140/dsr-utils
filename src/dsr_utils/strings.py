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


def _normalize_separators(name: str) -> str:
    """Normalize a string by handling various separators.

    Internal helper function that converts spaces, hyphens, and underscore sequences
    into single underscores, and handles camelCase/PascalCase by inserting underscores
    before uppercase letters preceded by lowercase letters or digits.

    Args:
        name (str): The string to normalize.

    Returns:
        str: The normalized string with consistent underscore separators.
    """
    import re

    # Replace hyphens and spaces with underscores
    name = name.replace('-', '_').replace(' ', '_')

    # Insert underscore before uppercase letters (for camelCase and PascalCase)
    # But avoid multiple underscores and handle consecutive capitals
    name = re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', name)

    # Remove any duplicate underscores
    name = re.sub(r'_+', '_', name)

    # Strip leading/trailing underscores
    name = name.strip('_')

    return name


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
    return _normalize_separators(name).lower()


def to_pascal_case(name: str) -> str:
    """Convert a string to PascalCase format.

    Handles various input formats including snake_case, camelCase, spaces, 
    hyphens, and mixed separators.

    Args:
        name (str): The string to convert.

    Returns:
        str: The string in PascalCase format (each word capitalized, no separators).

    Example:
        >>> to_pascal_case('first_name')
        'FirstName'
        >>> to_pascal_case('first-name')
        'FirstName'
        >>> to_pascal_case('firstName')
        'FirstName'
        >>> to_pascal_case('annual salary')
        'AnnualSalary'
    """
    # Normalize to have underscores as separators
    normalized = _normalize_separators(name)
    # Split on underscores and capitalize each part
    return ''.join(word.capitalize() for word in normalized.split('_'))


def to_camel_case(name: str) -> str:
    """Convert a string to camelCase format.

    Handles various input formats including snake_case, PascalCase, spaces, 
    hyphens, and mixed separators.

    Args:
        name (str): The string to convert.

    Returns:
        str: The string in camelCase format (first word lowercase, rest capitalized, no separators).

    Example:
        >>> to_camel_case('first_name')
        'firstName'
        >>> to_camel_case('first-name')
        'firstName'
        >>> to_camel_case('FirstName')
        'firstName'
        >>> to_camel_case('annual salary')
        'annualSalary'
    """
    # Normalize to have underscores as separators
    normalized = _normalize_separators(name)
    # Split on underscores
    parts = normalized.split('_')
    # First part lowercase, rest capitalized
    return parts[0].lower() + ''.join(word.capitalize() for word in parts[1:])


def to_kebab_case(name: str) -> str:
    """Convert a string to kebab-case format.

    Handles various input formats including snake_case, camelCase, PascalCase, 
    spaces, and mixed separators.

    Args:
        name (str): The string to convert.

    Returns:
        str: The string in kebab-case format (lowercase with hyphens).

    Example:
        >>> to_kebab_case('first_name')
        'first-name'
        >>> to_kebab_case('firstName')
        'first-name'
        >>> to_kebab_case('FIRST_NAME')
        'first-name'
        >>> to_kebab_case('annual salary')
        'annual-salary'
    """
    # Normalize to have underscores as separators
    normalized = _normalize_separators(name)
    # Convert to lowercase and replace underscores with hyphens
    return normalized.lower().replace('_', '-')


def to_constant_case(name: str) -> str:
    """Convert a string to CONSTANT_CASE format.

    Handles various input formats including snake_case, camelCase, PascalCase, 
    spaces, hyphens, and mixed separators.

    Args:
        name (str): The string to convert.

    Returns:
        str: The string in CONSTANT_CASE format (uppercase with underscores).

    Example:
        >>> to_constant_case('first_name')
        'FIRST_NAME'
        >>> to_constant_case('firstName')
        'FIRST_NAME'
        >>> to_constant_case('first-name')
        'FIRST_NAME'
        >>> to_constant_case('annual salary')
        'ANNUAL_SALARY'
    """
    # Normalize to have underscores as separators
    normalized = _normalize_separators(name)
    # Convert to uppercase
    return normalized.upper()
