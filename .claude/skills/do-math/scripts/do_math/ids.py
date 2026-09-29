"""Identifier shapes: registry IDs (a prefix and a ULID composed from time and entropy) and Git OIDs.

The composition is pure; the clock port supplies milliseconds and entropy.
"""
import re
from typing import Final

ULID_ALPHABET: Final = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"
ULID_LENGTH: Final = 26
ULID_PATTERN: Final = f"[0-7][{ULID_ALPHABET}]{{{ULID_LENGTH - 1}}}"
PREFIX: Final = re.compile(r"[A-Z][A-Z0-9]{0,7}\Z")
ENTROPY_BYTES: Final = 10
_HEX = re.compile(r"[0-9a-f]+\Z")


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


def is_new_id(prefix: str, value) -> bool:
    """True for ``<prefix>-<ULID>``, the form ``ulid`` composes."""
    return isinstance(value, str) and re.fullmatch(re.escape(prefix) + "-" + ULID_PATTERN, value) is not None


def oid_shape(oid: str) -> str:
    """Validate only OID syntax, not object existence or this instance's format."""
    if not isinstance(oid, str) or len(oid) not in {40, 64} or not _HEX.fullmatch(oid):
        raise ValueError("OID must be a lowercase 40/64-character hexadecimal string")
    return "sha1" if len(oid) == 40 else "sha256"
