"""The provider vocabulary a native final response is judged by (layer 1).

Which worker-request key names each provider's executable, and which final
bytes a parsed stream selected. The collector (the adapters) and the
native-final check (``native_final``) share these; each provider's stream parse
is ``parse_response`` in its stream module.
"""
from __future__ import annotations

import json

EXECUTABLE_KEYS = {"codex": "codex_path", "claude": "claude_path"}


def request_provider(request: dict) -> str:
    """The provider whose worker request carries this executable key."""
    providers = [name for name, key in EXECUTABLE_KEYS.items() if key in request]
    if len(providers) != 1:
        raise ValueError("worker request names no single provider executable")
    return providers[0]


def final_bytes(parsed: dict) -> bytes | None:
    """The exact final response bytes the stream selected, if any."""
    if "final_text" in parsed:
        return parsed["final_text"].encode("utf-8")
    if "structured_output" in parsed:
        return json.dumps(parsed["structured_output"], ensure_ascii=False, allow_nan=False).encode("utf-8")
    return None


def final_mismatch(parsed: dict, final: bytes) -> list[str]:
    """The final response must be the stream's own selected completion."""
    return [] if final == final_bytes(parsed) else ["final_response_mismatch"]
