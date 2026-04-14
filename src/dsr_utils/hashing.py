import hashlib
from pathlib import Path
from typing import Any

import joblib


def calculate_object_hash(obj: Any) -> str:
    """
    Generates a deterministic hash for complex Python objects.

    This function utilizes `joblib.hash` to inspect the underlying memory buffers
    of objects like pandas DataFrames or NumPy arrays, ensuring that changes
    to data values, dtypes, or structures result in a unique hash.

    Parameters
    ----------
    obj : Any
        The Python object to be hashed.

    Returns
    -------
    str
        A deterministic hex string representing the state of the object.

    Raises
    ------
    ValueError
        If joblib fails to generate a hash for the provided object type.
    """
    h = joblib.hash(obj)

    if h is None:
        raise ValueError(
            f"Joblib failed to generate a hash for object of type {type(obj)}"
        )

    return h


def calculate_file_hash(filepath: Path) -> str:
    """
    Generates a SHA-256 hash for a physical file on disk.

    Reads the file in binary chunks to remain memory-efficient,
    even when processing large raw datasets.

    Parameters
    ----------
    filepath : Path
        The filesystem path to the file to be hashed.

    Returns
    -------
    str
        The SHA-256 hex digest of the file contents.

    Raises
    ------
    FileNotFoundError
        If the specified filepath does not exist.
    """
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(8192), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()
