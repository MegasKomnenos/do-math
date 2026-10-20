"""Run with PYTHONPATH=src: python -m contract_checks.s1."""

import importlib
import inspect
from typing import get_type_hints
from unittest.mock import create_autospec

from linecount.contracts import IMPLEMENTATION_MODULE, IMPLEMENTATION_SYMBOL, LineCounter

CASES = (
    ("", {}),
    ("A\r\nA\n a \r\n\n", {"A": 2, " a ": 1}),
    (" \n \n", {" ": 2}),
    ("A\ra\r", {"A": 1, "a": 1}),
    ("x\u2028y", {"x\u2028y": 1}),
    ("가\n가\n나\n", {"가": 2, "나": 1}),
    ("\ufeffA\nA", {"\ufeffA": 1, "A": 1}),
)


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def assert_counts(value):
    require(isinstance(value, dict), "S1 returns the dictionary itself")
    require(all(isinstance(key, str) and key != "" for key in value), "S1 keys are nonempty strings")
    require(all(type(count) is int and count > 0 for count in value.values()), "S1 counts are positive integers, not bools")


def assert_provider(counter):
    shape = inspect.signature(counter)
    expected_types = get_type_hints(LineCounter.__call__)
    actual_types = get_type_hints(counter)
    for name, expected in expected_types.items():
        require(actual_types.get(name) == expected, f"S1 annotation mismatch: {name}")
    for text, expected in CASES:
        for args, kwargs in (((text,), {}), ((), {"text": text})):
            shape.bind(*args, **kwargs)
            value = counter(*args, **kwargs)
            assert_counts(value)
            require(value == expected, f"S1: {text!r}: expected {expected!r}, got {value!r}")


def make_consumer_stub(result):
    """Keep a consumer's isolated test double on the exact public call signature."""
    assert_counts(result)
    return create_autospec(LineCounter, instance=True, return_value=result.copy())


def assert_consumed_text(stub, expected):
    stub.assert_called_once()
    bound = inspect.signature(stub).bind(*stub.call_args.args, **stub.call_args.kwargs)
    require(bound.arguments["text"] == expected, "consumer changed the input before calling S1")


def main():
    provider = getattr(importlib.import_module(IMPLEMENTATION_MODULE), IMPLEMENTATION_SYMBOL)
    assert_provider(provider)
    print("PASS S1: implementation import, signature, return shape, and shared cases")


if __name__ == "__main__":
    main()
