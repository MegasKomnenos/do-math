"""Pure value rules shared by the engine, the workers and the transport (layer 1).

JSON encoding, parsing and digests; SHA-256 shape; nonempty text and Windows
path-segment checks; ISO time parsing. Workers inside a Windows Job load this
module without the package, so it imports only the standard library.
"""
from datetime import datetime, timezone
from functools import lru_cache
import hashlib
import json
import re


def json_copy(value):
    """A copy of a JSON value in which no container is shared with ``value`` or within itself.

    ``copy.deepcopy`` keeps a node that occurs twice in ``value`` as one shared
    node of the copy. Schema builders return this copy, so a caller may change
    any node in place without changing another field or a module global.
    """
    return json.loads(json.dumps(value))


def compact_json_bytes(value):
    """Compact sorted UTF-8 JSON, for values outside the state tree.

    Provider responses and transport files may hold fractional numbers, which
    ``canonical.canonical_json`` rejects. NaN and infinities are refused.
    """
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"),
                      allow_nan=False).encode("utf-8")


def json_digest(value):
    """SHA-256 of ``compact_json_bytes(value)``."""
    return hashlib.sha256(compact_json_bytes(value)).hexdigest()


def bytes_evidence(raw):
    """Bytes recorded in JSON evidence: their SHA-256, a lossy UTF-8 reading and the exact base64."""
    import base64
    return {"sha256": hashlib.sha256(raw).hexdigest(), "text": raw.decode("utf-8", "replace"),
            "base64": base64.b64encode(raw).decode("ascii")}


def unique_pairs(pairs):
    """``object_pairs_hook`` that refuses a repeated key."""
    result={}
    for key,value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key: "+key)
        result[key]=value
    return result


def reject_constant(value):
    """``parse_constant`` hook that refuses NaN and the infinities."""
    raise ValueError("non-finite JSON constant: "+value)


def strict_json_loads(raw):
    """Parse JSON refusing duplicate keys, named non-finite constants and
    exponents that overflow to infinity (such as ``1e999``)."""
    value=json.loads(raw,object_pairs_hook=unique_pairs,parse_constant=reject_constant)
    compact_json_bytes(value)
    return value


# The shape of a SHA-256 digest. Stored, wire and toolchain record schemas embed this node.
SHA256_SCHEMA={"type":"string","pattern":"^[0-9a-f]{64}$"}
_SHA256=re.compile(SHA256_SCHEMA["pattern"])


def is_sha256(value):
    """Lowercase 64-digit hexadecimal: the shape of a SHA-256 digest."""
    return isinstance(value,str) and _SHA256.fullmatch(value) is not None


def validate_profile_ref(reference):
    """A sealed execution profile reference: exactly a nonblank id, a revision >= 1 and a SHA-256.

    The CLI workers check it inside their Windows Job, where they load this module
    without the package; the engine's stored profile lookup checks it too.
    """
    if (not isinstance(reference, dict) or set(reference) != {"id", "revision", "sha256"}
            or not isinstance(reference["id"], str) or not reference["id"].strip()
            or type(reference["revision"]) is not int or reference["revision"] < 1
            or not is_sha256(reference["sha256"])):
        raise ValueError("profile reference requires exact id, revision and sha256")


def require_text(value, label):
    """``value`` when it is a string with a non-whitespace character; otherwise ``ValueError``."""
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} must be nonempty text")
    return value


_WINDOWS_RESERVED = frozenset({
    "CON", "PRN", "AUX", "NUL",
    *(f"COM{number}" for number in range(1, 10)),
    *(f"LPT{number}" for number in range(1, 10)),
})


# Pure in its string argument; saves re-checking the same segments on every save.
@lru_cache(maxsize=65536)
def check_path_segment(part: str) -> None:
    """Reject one path segment that Windows cannot store under that name.

    Empty, ``.``/``..``, trailing dot or space (Win32 strips them), separators,
    ``<>:"|?*`` and control characters, and reserved device names (``CON``,
    ``com1.txt``) are refused. State paths, record IDs and the control transport's
    file names share this rule; the transport loads this module without the package.
    """
    if (not isinstance(part, str) or not part or part in {".", ".."} or part[-1] in {".", " "}
            or "/" in part or "\\" in part):
        raise ValueError("path contains an invalid segment")
    if any(character in '<>:"|?*' or ord(character) < 32 for character in part):
        raise ValueError("path contains a Windows-invalid segment")
    if part.rstrip(". ").split(".", 1)[0].upper() in _WINDOWS_RESERVED:
        raise ValueError("path contains a reserved Windows device name")


def distinct_texts(value, label, *, nonempty=False):
    """``value`` as a new list when it is a list of distinct nonempty texts (and, with ``nonempty``, not empty)."""
    if (not isinstance(value, list) or any(not isinstance(item, str) or not item.strip() for item in value)
            or len(set(value)) != len(value) or (nonempty and not value)):
        raise ValueError(f"{label} requires {'a nonempty list of ' if nonempty else ''}distinct nonempty strings")
    return list(value)


def parse_utc(value):
    """Parse an ISO time that states its offset, as an aware UTC datetime.

    A trailing ``Z`` means UTC. A missing offset, a non-string or a malformed
    time raises ``ValueError``.
    """
    if not isinstance(value,str) or not value:
        raise ValueError("time must be a nonempty ISO timestamp string")
    parsed=datetime.fromisoformat(value.replace("Z","+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("timestamp requires a timezone: "+value)
    return parsed.astimezone(timezone.utc)
