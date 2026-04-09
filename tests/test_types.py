"""Tests for dsr_utils.types module."""

import numpy as np
import pandas as pd
import pytest

from dsr_utils.types import any_to_list


class TestAnyToList:
    """
    Test suite for the refactored `any_to_list` conversion utility.
    """

    def test_handle_none(self):
        """Verify None returns empty list."""
        assert any_to_list(None) == []

    def test_handle_scalar_int_preserves_type(self):
        """Verify integers remain integers (no implicit string conversion)."""
        assert any_to_list(123) == [123]

    def test_handle_list_is_copy(self):
        """Verify lists return a copy to prevent mutation of original."""
        original = [1, 2, 3]
        result = any_to_list(original)
        assert result == original
        assert result is not original

    def test_handle_tuple_flattening(self):
        """Verify tuples are converted to flat lists."""
        assert any_to_list((1, 2, 3)) == [1, 2, 3]

    def test_handle_set_conversion(self):
        """Verify sets are converted to lists."""
        result = any_to_list({1, 2, 3})
        assert sorted(result) == [1, 2, 3]

    def test_handle_pandas_objects(self):
        """Verify Pandas Series/Index are correctly converted."""
        assert any_to_list(pd.Series([10, 20])) == [10, 20]
        assert any_to_list(pd.Index(["a", "b"])) == ["a", "b"]

    def test_handle_numpy_arrays(self):
        """Verify NumPy arrays are converted to lists."""
        arr = np.array([1, 2, 3])
        assert any_to_list(arr) == [1, 2, 3]
