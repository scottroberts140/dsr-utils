"""Type conversion helpers for common data inputs."""

from typing import Any

import numpy as np


def any_to_list(a: Any) -> list[Any]:
    """
    Convert various input types into a standardized flat list.

    Parameters
    ----------
    a : Any
        The input to be converted. Supported types include scalars (int, float, str),
        sequences (list, tuple, ndarray), and collections (set, dict, pd.Series).

    Returns
    -------
    list[Any]
        A standardized list representation of the input. Returns an empty list
        if the input is None.
    """
    if a is None:
        return []

    # Handle standard list directly (returning a shallow copy is safer)
    if isinstance(a, list):
        return a.copy()

    # Handle Pandas Series and Index (convert to list)
    if hasattr(a, "tolist") and callable(getattr(a, "tolist")):
        return a.tolist()

    # Handle NumPy arrays
    if isinstance(a, np.ndarray):
        return a.tolist()

    # Handle other iterables (tuple, set, dict values)
    # but exclude strings which are technically iterable
    if isinstance(a, (tuple, set)):
        return list(a)

    if isinstance(a, dict):
        return list(a.values())

    # Handle scalars (str, int, float, etc.)
    if isinstance(a, (str, int, float, np.number)):
        return [a]

    # Fallback for other objects
    try:
        return list(a)
    except TypeError:
        return [a]
