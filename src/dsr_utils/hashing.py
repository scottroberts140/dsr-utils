import hashlib
from pathlib import Path
from typing import Any

import joblib
from cloudpathlib import AnyPath, CloudPath


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


def _normalize_file_path(filepath: str | Path | CloudPath) -> Path | CloudPath:
    """
    Normalize a local or cloud-backed file path into a readable path object.

    Parameters
    ----------
    filepath : str | Path | CloudPath
        Local filesystem path, cloud URI, or cloud path object.

    Returns
    -------
    Path | CloudPath
        Normalized path object suitable for existence checks and binary reads.
    """
    return AnyPath(filepath)


def calculate_file_hash(filepath: str | Path | CloudPath) -> str:
    """
    Generate a SHA-256 hash for a local or cloud-backed file.

    Reads the file in binary chunks to remain memory-efficient even when
    processing large datasets. Supports both local filesystem paths and
    cloud-backed paths handled by ``cloudpathlib``.

    Parameters
    ----------
    filepath : str | Path | CloudPath
        Local filesystem path, cloud URI, or cloud path object to hash.

    Returns
    -------
    str
        The SHA-256 hex digest of the file contents.

    Raises
    ------
    FileNotFoundError
        If the specified filepath does not exist.
    """
    path_obj = _normalize_file_path(filepath)
    if not path_obj.exists():
        raise FileNotFoundError(f"File not found: {path_obj}")

    sha256_hash = hashlib.sha256()
    with path_obj.open("rb") as f:
        for byte_block in iter(lambda: f.read(8192), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()
