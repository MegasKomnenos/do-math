"""The provider vocabulary a native final response is judged by (layer 1).

Which worker-request key names each provider's executable, and which final
bytes a parsed stream selected. The collector (the adapters) and the
native-final check (``native_final``) share these; each provider's stream parse
is ``parse_response`` in its stream module.
"""
from __future__ import annotations

import json

import jsonschema

from .values import strict_json_loads

EXECUTABLE_KEYS = {"codex": "codex_path", "claude": "claude_path"}
CODEX_OUTPUT_KEY = "output_json"


def output_contract(provider: str, schema: dict) -> dict:
    """The CLI's final-response contract, distinct from the caller's semantic schema.

    Codex requires every declared property and closed objects. One JSON string
    carries the complete semantic value without collapsing absence and null or
    translating arbitrary schema constraints. The property's description gives
    the model the original schema; the receiver still enforces that schema.
    Claude receives its original schema. Neither branch mutates the caller.
    """
    if provider == "codex":
        return {"type": "object", "additionalProperties": False,
                "properties": {CODEX_OUTPUT_KEY: {"type": "string", "description":
                    "Encode the complete response requested by the prompt as a JSON string here, not prose or a code fence. "
                    "Do not add defaults, omit supplied fields, or replace absent fields with null. "
                    "The JSON value inside this string must satisfy this original JSON Schema:\n"
                    + json.dumps(schema, ensure_ascii=False, sort_keys=True, allow_nan=False)}},
                "required": [CODEX_OUTPUT_KEY]}
    if provider == "claude":
        from copy import deepcopy
        return deepcopy(schema)
    raise ValueError("unsupported final-response provider: " + provider)


def semantic_output(provider: str, raw: bytes):
    """Decode the native final without rewriting it; callers validate the semantic schema next."""
    value = strict_json_loads(raw.decode("utf-8"))
    if provider == "codex":
        # The same contract constructs requests and rejects malformed envelopes.
        jsonschema.validate(value, output_contract(provider, {}))
        return strict_json_loads(value[CODEX_OUTPUT_KEY])
    if provider == "claude":
        return value
    raise ValueError("unsupported final-response provider: " + provider)


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
