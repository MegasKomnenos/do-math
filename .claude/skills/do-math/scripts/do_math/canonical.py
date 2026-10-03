"""The storage value domain and its exact encoding (layer 1).

``validate_storage_value`` is the domain: plain JSON with safe integers, no
floats and no surrogate code points. ``canonical_json`` is its one encoding and
``exact_content_hash`` the identity of an exact logical payload. A ``FrozenText``
is a sealed large string (``payloads.seal``) that carries its encoded bytes.
"""
import hashlib
import json
import re
from typing import Any


class FrozenText(str):
    def __deepcopy__(self, memo): return self


_SAFE_INTEGER = (1 << 53) - 1
_SURROGATE = re.compile(r"[\ud800-\udfff]")


def canonical_json(value: Any) -> bytes:
    """Encode a finite JSON value deterministically without changing Unicode."""
    if isinstance(value, FrozenText) and hasattr(value, 'payload_bytes'):
        return value.payload_bytes
    validate_storage_value(value)
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + "\n").encode("utf-8")


def exact_content_hash(value: Any) -> str:
    """Identity of an exact logical payload, not a file or semantic projection."""
    return hashlib.sha256(canonical_json(value)).hexdigest()


def same_json_value(left: Any, right: Any) -> bool:
    """Compare storage values without conflating booleans and integers.

    The parent is already validated. Immutable leaf identities are preserved
    by deepcopy, so unchanged strings and scalars need no serialization.
    Storage validation remains the caller's responsibility.
    """
    if left is right:
        return True
    if isinstance(left, dict) and isinstance(right, dict):
        return left.keys() == right.keys() and all(same_json_value(value, right[key])
                                                   for key, value in left.items())
    if isinstance(left, list) and isinstance(right, list):
        return len(left) == len(right) and all(same_json_value(a, b) for a, b in zip(left, right))
    if isinstance(left, str) and isinstance(right, str):
        return left == right
    if (isinstance(left, int) and not isinstance(left, bool)
            and isinstance(right, int) and not isinstance(right, bool)):
        return left == right
    return False


def validate_storage_value(value: Any) -> None:
    """Validate the exact storage value domain without constructing JSON bytes.

    Plain ``dict``, ``list`` and ``str`` values, nearly every node of a state,
    take a direct path with the same rules; string leaves are checked in
    place, and an ASCII string holds no surrogate. Other types (subclasses,
    sealed payloads) fall through to the general rules.
    """
    kind = type(value)
    if kind is dict:
        for key, item in value.items():
            if type(key) is not str:
                if not isinstance(key, str):
                    raise ValueError("JSON object keys must be strings")
                validate_storage_value(key)
            elif not key.isascii() and _SURROGATE.search(key):
                raise ValueError("JSON strings cannot contain surrogate code points")
            if type(item) is str:
                if not item.isascii() and _SURROGATE.search(item):
                    raise ValueError("JSON strings cannot contain surrogate code points")
            else:
                validate_storage_value(item)
        return
    if kind is list:
        for item in value:
            validate_storage_value(item)
        return
    if kind is str:
        if not value.isascii() and _SURROGATE.search(value):
            raise ValueError("JSON strings cannot contain surrogate code points")
        return
    if isinstance(value, FrozenText) and hasattr(value, 'payload_bytes'):
        return  # Sealing validated exact bytes and these values cannot be edited.
    if value is None or isinstance(value, (bool, str)):
        if isinstance(value, str) and _SURROGATE.search(value):
            raise ValueError("JSON strings cannot contain surrogate code points")
        return
    if isinstance(value, int) and not isinstance(value, bool):
        if abs(value) > _SAFE_INTEGER:
            raise ValueError("JSON integers must be safe integers")
        return
    if isinstance(value, float):
        raise ValueError("JSON floating-point numbers are not permitted")
    if isinstance(value, list):
        for item in value:
            validate_storage_value(item)
        return
    if isinstance(value, dict):
        for key, item in value.items():
            if not isinstance(key, str):
                raise ValueError("JSON object keys must be strings")
            validate_storage_value(key)
            validate_storage_value(item)
        return
    raise ValueError("value is not JSON-serializable")
