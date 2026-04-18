import pytest

from dsr_utils.reflection import safe_call

# --- Sample functions for testing ---


def simple_func(a, b=2):
    """Standard function with one default argument."""
    return a + b


def func_with_kwargs(a, **kwargs):
    """Function that explicitly accepts variable keyword arguments."""
    return a, kwargs


class SampleClass:
    """Class to test constructor signature inspection."""

    def __init__(self, name, age=None):
        self.name = name
        self.age = age


# --- Test Cases ---


class TestSafeCall:

    def test_exact_match(self):
        """Verify behavior when all parameters match the signature."""
        params = {"b": 10}
        result, rejected = safe_call(simple_func, params, a=5)

        assert result == 15
        assert rejected == {}

    def test_partial_match_with_rejection(self):
        """Verify that extra parameters are filtered and returned as rejected."""
        params = {"b": 10, "extra_param": "ignore_me"}
        result, rejected = safe_call(simple_func, params, a=5)

        assert result == 15
        assert "extra_param" in rejected
        assert rejected["extra_param"] == "ignore_me"

    def test_fixed_kwargs_override_params(self):
        """Ensure fixed_kwargs take priority and are not filtered."""
        params = {"a": 1, "b": 10}
        # Fixed 'a' should be used even if 'a' is in params
        result, rejected = safe_call(simple_func, params, a=100)

        assert result == 110
        # 'a' from params is essentially 'rejected' or superseded
        assert "a" in rejected

    def test_function_with_var_keywords(self):
        """Verify that nothing is rejected if the function accepts **kwargs."""
        params = {"b": 2, "c": 3, "any_key": "any_value"}
        result, rejected = safe_call(func_with_kwargs, params, a=1)

        val_a, val_kwargs = result
        assert val_a == 1
        assert val_kwargs == params
        assert rejected == {}

    def test_class_constructor(self):
        """Verify that safe_call works with class __init__ signatures."""
        params = {"age": 30, "location": "Lexington"}
        result, rejected = safe_call(SampleClass, params, name="Scott")

        assert isinstance(result, SampleClass)
        assert result.name == "Scott"
        assert result.age == 30
        assert "location" in rejected

    def test_empty_params(self):
        """Ensure it handles empty input dictionaries gracefully."""
        result, rejected = safe_call(simple_func, {}, a=1)
        assert result == 3
        assert rejected == {}

    def test_none_values_in_params(self):
        """Verify that None values are passed if they are valid parameters."""
        params = {"b": None}
        # This will fail at the function level if the function doesn't handle None,
        # but safe_call should still pass it through if it's in the signature.
        with pytest.raises(TypeError):
            safe_call(simple_func, params, a=1)


class TestSafeCallUpdates:
    # A strict function for testing standard reflection
    def sample_func(self, a, b, c=10):
        return a + b + c

    def test_valid_params_override(self):
        """Verify that valid_params bypasses reflection and filters strictly."""
        params = {"a": 1, "b": 5, "extra": 2}
        result, rejected = safe_call(self.sample_func, params, valid_params={"a"}, b=5)

        assert result == 16
        assert "extra" in rejected

    def test_valid_params_with_fixed_kwargs(self):
        """Verify that fixed_kwargs are always passed, regardless of valid_params."""
        params = {"a": 1, "b": 5}

        # Even if 'b' isn't in valid_params, it is accepted because it is a fixed_kwarg.
        result, rejected = safe_call(self.sample_func, params, valid_params={"a"}, b=20)

        # result is 31 (a=1 from params, b=20 from fixed_kwargs, c=10 default)
        assert result == 31
        assert rejected["b"] == 5

    def test_conflict_resolution_fixed_kwargs(self):
        """Verify fixed_kwargs supersede params and move them to rejected."""
        params = {"a": 1, "b": 2}
        # 'b' is provided in params but overridden in fixed_kwargs
        result, rejected = safe_call(self.sample_func, params, b=10)

        assert result == 21  # a=1, b=10, c=10
        assert rejected["b"] == 2  # The original value from 'params'

    def test_standard_reflection_unaffected(self):
        """Ensure standard reflection still works when valid_params is None."""
        params = {"a": 1, "b": 2, "invalid": 99}
        result, rejected = safe_call(self.sample_func, params)

        assert result == 13
        assert "invalid" in rejected
