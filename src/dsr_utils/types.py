import numpy as np
from typing import Any


def any_to_list(a: Any) -> list[Any]:
    """Convert various data types to a list representation.

    Handles conversion from list, numpy array, scalar types (int/float/str),
    tuple, and dict to a list format. Prints warning for unrecognized types.

    Args:
        a (Any): Value to convert to list.

    Returns:
        list[Any]: List representation of the input value.

    Example:
        >>> any_to_list([1, 2, 3])
        [1, 2, 3]
        >>> any_to_list(np.array([1, 2, 3]))
        [1, 2, 3]
        >>> any_to_list(42)
        ['42']
        >>> any_to_list({'a': 1, 'b': 2})
        [1, 2]
    """
    match a:
        case list():
            return a
        case np.ndarray():
            return a.tolist()
        case int() | float() | str():
            return [str(a)]
        case tuple():
            return [list(a)]
        case dict():
            return list(a.values())
        case _:
            print(f'Unrecognized data type: {type(a)}')
            return []
