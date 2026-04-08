"""Type conversion helpers for common data inputs."""

from typing import Any

import numpy as np


def any_to_list(a: Any) -> list[Any]:
    """
    Convert various data types to a list representation.

    Handles conversion from lists, NumPy arrays, scalars (int, float, str),
    tuples, and dictionaries.

    Parameters
    ----------
    a : Any
        The input value to convert into a list format.

    Returns
    -------
    list of Any
        A list representation of the input. Note that scalar values are
        returned as single-element lists containing their string
        representation, while tuples are returned as a nested list.

    Notes
    -----
    - NumPy arrays are converted using the `.tolist()` method.
    - Dictionary inputs result in a list of the dictionary's values.
    - If the data type is unrecognized, a warning is printed and an
      empty list is returned.

    Examples
    --------
    >>> any_to_list(np.array([1, 2, 3]))
    [1, 2, 3]
    >>> any_to_list(42)
    ['42']
    >>> any_to_list({'a': 1, 'b': 2})
    [1, 2]
    >>> any_to_list((10, 20))
    [[10, 20]]
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
            print(f"Unrecognized data type: {type(a)}")
            return []
