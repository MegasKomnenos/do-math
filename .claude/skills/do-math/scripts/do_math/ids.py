"""Registry identifiers: a prefix and a ULID composed from time and entropy.

The composition is pure; the clock port supplies milliseconds and entropy.
"""
import re
from typing import Final

ULID_ALPHABET: Final = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"
ULID_LENGTH: Final = 26
ULID_PATTERN: Final = f"[0-7][{ULID_ALPHABET}]{{{ULID_LENGTH - 1}}}"
PREFIX: Final = re.compile(r"[A-Z][A-Z0-9]{0,7}\Z")
ENTROPY_BYTES: Final = 10


def ulid(prefix, millis, entropy):
    """``PREFIX-ULID`` from Unix milliseconds and ten entropy bytes."""
    if not isinstance(prefix, str) or not PREFIX.fullmatch(prefix):
        raise ValueError("prefix must be a canonical uppercase registry prefix")
    if not isinstance(entropy, bytes) or len(entropy) != ENTROPY_BYTES:
        raise ValueError("a ULID needs exactly ten entropy bytes")
    value = (millis << 80) | int.from_bytes(entropy, "big")
    encoded = ""
    for _ in range(ULID_LENGTH):
        encoded = ULID_ALPHABET[value & 31] + encoded
        value >>= 5
    return f"{prefix}-{encoded}"
