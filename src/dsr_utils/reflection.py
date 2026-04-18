import inspect
from typing import Any, Callable, Tuple


def safe_call(
    func: Callable,
    params: dict[str, Any],
    valid_params: set[str] | None = None,
    **fixed_kwargs,
) -> Tuple[Any, dict[str, Any]]:
    """
    Call a function using only the compatible parameters from a provided dictionary.

    This utility inspects the target function's signature to identify which
    parameters are accepted. It filters the input dictionary
    to prevent `TypeError` exceptions caused by unexpected keyword arguments
    when switching between different underlying loaders or processors.

    If valid_params is provided, it bypasses reflection and uses the
    set as the ground truth for filtering.

    Parameters
    ----------
    func : Callable
        The target function or class constructor to be called (e.g., `pd.read_csv`).
    params : dict[str, Any]
        A dictionary of potential keyword arguments to filter and pass to the
        function.
    valid_params : set[str] | None
        An optional set of valid keyword arguments. If provided, reflection
        is bypassed.
    **fixed_kwargs : Any
        Key-value pairs that must be passed to the function regardless of
        filtering, such as file paths or mandatory buffer objects.

    Returns
    -------
    result : Any
        The value returned by the executed function `func`.
    rejected : dict[str, Any]
        A dictionary containing the subset of `params` that were not compatible
        with the function's signature, useful for debugging configuration
        discrepancies.

    Notes
    -----
    If the target function accepts `**kwargs` (variable keyword arguments),
    the filtering logic is bypassed and all parameters are considered valid.
    This function uses `inspect.signature` to perform reflection on the target
    callable.
    """
    if valid_params is not None:
        accepted = {}
        rejected = {}

        for k, v in params.items():
            # Skip any keys that are already defined as mandatory fixed_kwargs
            if k in fixed_kwargs:
                rejected[k] = v  # Move superseded value to rejected
                continue

            # Sort remaining parameters based on the valid_params set
            if k in valid_params:
                accepted[k] = v
            else:
                rejected[k] = v
    else:
        sig = inspect.signature(func)
        valid_keys = sig.parameters.keys()

        # Identify which parameters the function can actually receive
        has_kwargs = any(p.kind == p.VAR_KEYWORD for p in sig.parameters.values())

        if has_kwargs:
            # If the function accepts **kwargs, nothing is invalid
            accepted = params.copy()
            rejected = {}
        else:
            accepted = {k: v for k, v in params.items() if k in valid_keys}
            rejected = {k: v for k, v in params.items() if k not in valid_keys}

    # --- Conflict Resolution ---
    # Remove any keys from 'accepted' that are already in 'fixed_kwargs'
    # to avoid "got multiple values for keyword argument" errors.
    for key in fixed_kwargs:
        if key in accepted:
            # Move the superseded param to rejected for debugging visibility
            rejected[key] = accepted.pop(key)

    result = func(**fixed_kwargs, **accepted)
    return result, rejected
